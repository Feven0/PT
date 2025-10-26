import asyncio, os, json
import re
import time
import io, wave
import queue
from datetime import datetime
from openai import OpenAI
import assemblyai as aai
from typing import Dict, Any, Optional, Set
import api.utils.parrot_utils as parrot_utils
from api import config
import api.modules.ipersona_parrot_gpt as util
import api.llm.ipersona.ipersona_strapi as strapi
from api.llm.ipersona.ipersona_strapi_schemas import (
    IpersonaSessionMessageSchema, 
    IpersonaSessionSchema, 
    IpersonaTinderTemplateSchema,
    IpersonaChallengeDocumentSchema
)

import urllib.parse  
from api.utils.logger import LLPackerLogger
from api.socket.core import sio, get_socket_asgi_app
import array
from .stt_utils import (
    WHISPER_MODEL,
    WHISPER_TARGET_BYTES,
    WHISPER_OVERLAP_BYTES,
    WHISPER_RMS_THRESHOLD,
    pcm16_mono_16k_to_wav_bytes,
    is_silent_pcm16,
)

# Redis imports for SID mapping persistence
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    redis = None
    REDIS_AVAILABLE = False

logger = LLPackerLogger(os.path.basename(__file__))

if not REDIS_AVAILABLE:
    logger.warn("[REDIS] Redis not available - SID mapping will use memory only")
# Google Cloud Speech-to-Text imports
# V1 (legacy)
try:
    from google.cloud import speech_v1 as speech
    from google.api_core.client_options import ClientOptions
except Exception:
    speech = None
    ClientOptions = None

# V2 (latest) - Import modular implementations
try:
    from .google_stt_v2 import GoogleStreamingSTTV2, GoogleSTTV2Config, check_google_stt_v2_status
    GOOGLE_STT_V2_AVAILABLE = True
except Exception as v2_import_error:
    GoogleStreamingSTTV2 = None
    GoogleSTTV2Config = None
    check_google_stt_v2_status = None
    GOOGLE_STT_V2_AVAILABLE = False
    logger.warn(f"[GOOGLE_STT_V2] Not available: {v2_import_error}")
try:
    from google import genai as google_genai
    from google.genai import types as genai_types
except Exception:
    google_genai = None
    genai_types = None
try:
    from faster_whisper import WhisperModel
except Exception:
    WhisperModel = None

logger = LLPackerLogger(os.path.basename(__file__))

# Initialize Redis connection for SID mapping persistence
redis_client = None
if REDIS_AVAILABLE:
    try:
        redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', '6379')),
            db=int(os.getenv('REDIS_DB', '0')),
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        # Test connection
        redis_client.ping()
        logger.info("[REDIS] Connected to Redis for SID mapping persistence")
    except Exception as e:
        logger.warn(f"[REDIS] Failed to connect to Redis: {e}")
        redis_client = None

aai.settings.api_key = config.assemblyai.api_key

OPENAI_API_KEY = config.openai.api_key
client = OpenAI(api_key=OPENAI_API_KEY)

# Improved transcriber management - track per session
transcribers: Dict[str, Any] = {}
assemblyai_streams: Dict[str, Any] = {}

# AssemblyAI session limits - Production settings
MAX_ASSEMBLYAI_SESSIONS = 80  # Leave buffer below 100 limit for paid accounts
ASSEMBLYAI_SOFT_CAP = int(os.getenv("ASSEMBLYAI_SOFT_CAP", "75"))
# Configuration flag for Google STT version
# Set to True to use old V1 implementation, False for new V2 (recommended)
USE_GOOGLE_STT_V1 = os.getenv("USE_GOOGLE_STT_V1", "false").lower() == "true"

# Start periodic cleanup task when first audio endpoint is called
cleanup_task_started = False
fw_model: Any = None
gemini_last_ts: Dict[str, float] = {}
audio_wav_storage: Dict[str, bytes] = {}

# Message queue for disconnected clients (legacy SID-based)
disconnected_message_queue: Dict[str, list] = {}

# Enhanced SID mapping storage using user_id
USER_ID_TO_SID: Dict[str, str] = {}  # user_id -> current_sid
SID_TO_USER_ID: Dict[str, str] = {}  # sid -> user_id

# Enhanced message queue with user_id as key
user_message_queue: Dict[str, list] = {}

whisper_buffers: Dict[str, bytearray] = {}
google_streams: Dict[str, Any] = {}  # V1 sessions (legacy)
google_streams_v2: Dict[str, Any] = {}  # V2 sessions (latest)
gemini_streams: Dict[str, Any] = {}
fw_buffers: Dict[str, bytearray] = {}

# Track active SIDs per user and globally for robust emits
ACTIVE_SIDS: Set[str] = set()
USER_ID_ACTIVE_SIDS: Dict[str, Set[str]] = {}

# Track number of SID changes per user (for observability)
USER_ID_SID_CHANGE_COUNT: Dict[str, int] = {}


# -------------------------- Debug Functions -------------------------- #

def debug_show_mappings():
    """Debug function to show current SID mappings"""
    logger.info(f"[DEBUG][MAPPINGS] Current USER_ID_TO_SID: {USER_ID_TO_SID}")
    logger.info(f"[DEBUG][MAPPINGS] Current SID_TO_USER_ID: {SID_TO_USER_ID}")
    logger.info(f"[DEBUG][MAPPINGS] Current user_message_queue keys: {list(user_message_queue.keys())}")
    logger.info(f"[DEBUG][MAPPINGS] Current disconnected_message_queue keys: {list(disconnected_message_queue.keys())}")
    logger.info(f"[DEBUG][MAPPINGS] Current sio.manager.rooms: {list(sio.manager.rooms.keys())}")
    logger.info(f"[DEBUG][MAPPINGS] Current USER_ID_SID_CHANGE_COUNT: {USER_ID_SID_CHANGE_COUNT}")
    
    # Show Redis status if available
    if redis_client:
        try:
            # Show SID mappings in Redis
            user_sid_keys = redis_client.keys("user_sid:*")
            sid_user_keys = redis_client.keys("sid_user:*")
            logger.info(f"[DEBUG][MAPPINGS] Redis user_sid keys: {user_sid_keys}")
            logger.info(f"[DEBUG][MAPPINGS] Redis sid_user keys: {sid_user_keys}")
            
            # Show queued messages in Redis
            redis_keys = redis_client.keys("queued_messages:*")
            logger.info(f"[DEBUG][MAPPINGS] Redis queued_messages keys: {redis_keys}")
        except Exception as e:
            logger.warn(f"[DEBUG][MAPPINGS] Failed to get Redis keys: {e}")
    else:
        logger.info(f"[DEBUG][MAPPINGS] Redis client not available")

# -------------------------- SID Mapping Utilities -------------------------- #

def load_sid_mappings_from_redis():
    """Load existing SID mappings from Redis on startup"""
    if not redis_client:
        logger.info("[SID_MAPPING] Redis not available, skipping mapping load")
        return
    
    try:
        logger.info("[SID_MAPPING] Loading existing mappings from Redis...")
        
        # Get all user_sid keys
        user_sid_keys = redis_client.keys("user_sid:*")
        logger.info(f"[SID_MAPPING] Found {len(user_sid_keys)} user_sid keys in Redis")
        
        loaded_count = 0
        for key in user_sid_keys:
            try:
                user_id = key.replace("user_sid:", "")
                current_sid = redis_client.get(key)
                
                if current_sid:
                    # Load into memory
                    USER_ID_TO_SID[user_id] = current_sid
                    SID_TO_USER_ID[current_sid] = user_id
                    loaded_count += 1
                    logger.info(f"[SID_MAPPING] Loaded mapping: user_id={user_id} -> sid={current_sid}")
                else:
                    # Clean up expired key
                    redis_client.delete(key)
                    logger.info(f"[SID_MAPPING] Cleaned up expired key: {key}")
                    
            except Exception as e:
                logger.warn(f"[SID_MAPPING] Failed to load mapping for key {key}: {e}")
        
        logger.info(f"[SID_MAPPING] Successfully loaded {loaded_count} mappings from Redis")
        logger.info(f"[SID_MAPPING] Current memory mappings: USER_ID_TO_SID={USER_ID_TO_SID}")
        logger.info(f"[SID_MAPPING] Current memory mappings: SID_TO_USER_ID={SID_TO_USER_ID}")
        
    except Exception as e:
        logger.error(f"[SID_MAPPING] Failed to load mappings from Redis: {e}")

# Load mappings on startup
load_sid_mappings_from_redis()

def get_user_id_from_sid(sid: str) -> Optional[str]:
    """Get user_id from SID - check Redis first, then memory"""
    # Check Redis first
    if redis_client:
        try:
            user_id = redis_client.get(f"sid_user:{sid}")
            if user_id:
                logger.info(f"[DEBUG][SID_MAPPING] get_user_id_from_sid (Redis): sid={sid} -> user_id={user_id}")
                return user_id
        except Exception as e:
            logger.warn(f"[REDIS] Failed to get user_id from Redis: {e}")
    
    # Fallback to memory
    user_id = SID_TO_USER_ID.get(sid)
    logger.info(f"[DEBUG][SID_MAPPING] get_user_id_from_sid (Memory): sid={sid} -> user_id={user_id}")
    return user_id

def get_current_sid_for_user(user_id: str) -> Optional[str]:
    """Get current SID for a user_id - check Redis first, then memory"""
    # Check Redis first
    if redis_client:
        try:
            current_sid = redis_client.get(f"user_sid:{user_id}")
            if current_sid:
                logger.info(f"[DEBUG][SID_MAPPING] get_current_sid_for_user (Redis): user_id={user_id} -> current_sid={current_sid}")
                return current_sid
        except Exception as e:
            logger.warn(f"[REDIS] Failed to get SID from Redis: {e}")
    
    # Fallback to memory
    current_sid = USER_ID_TO_SID.get(user_id)
    logger.info(f"[DEBUG][SID_MAPPING] get_current_sid_for_user (Memory): user_id={user_id} -> current_sid={current_sid}")
    return current_sid

def update_sid_mapping(user_id: str, sid: str):
    """Update SID mapping when user connects - store in Redis and memory"""
    logger.info(f"[DEBUG][SID_MAPPING] update_sid_mapping: user_id={user_id}, sid={sid}")
    logger.info(f"[DEBUG][SID_MAPPING] Before update - USER_ID_TO_SID: {USER_ID_TO_SID}")
    logger.info(f"[DEBUG][SID_MAPPING] Before update - SID_TO_USER_ID: {SID_TO_USER_ID}")
    
    # Remove old SID mapping if exists
    old_sid = USER_ID_TO_SID.get(user_id)
    if old_sid and old_sid != sid:
        SID_TO_USER_ID.pop(old_sid, None)
        logger.info(f"[DEBUG][SID_MAPPING] Removed old SID {old_sid} for user {user_id}")
        
        # Also remove old SID from active tracking
        try:
            if user_id in USER_ID_ACTIVE_SIDS and old_sid in USER_ID_ACTIVE_SIDS[user_id]:
                USER_ID_ACTIVE_SIDS[user_id].discard(old_sid)
                logger.info(f"[DEBUG][SID_MAPPING] Removed old SID {old_sid} from active tracking for user {user_id}")
                if not USER_ID_ACTIVE_SIDS[user_id]:
                    USER_ID_ACTIVE_SIDS.pop(user_id, None)
                    logger.info(f"[DEBUG][SID_MAPPING] No more active SIDs for user {user_id}")
        except Exception as e:
            logger.warn(f"[DEBUG][SID_MAPPING] Error cleaning up active tracking for user {user_id}: {e}")
        
        # Increment change counter (memory)
        USER_ID_SID_CHANGE_COUNT[user_id] = USER_ID_SID_CHANGE_COUNT.get(user_id, 0) + 1
        logger.info(f"[DEBUG][SID_MAPPING] SID change count for user {user_id}: {USER_ID_SID_CHANGE_COUNT[user_id]}")
        # Increment change counter (Redis)
        if redis_client:
            try:
                redis_client.incr(f"sid_changes:{user_id}")
            except Exception:
                pass
        
        # Also remove from Redis
        if redis_client:
            try:
                redis_client.delete(f"sid_user:{old_sid}")
                logger.info(f"[DEBUG][SID_MAPPING] Removed old SID {old_sid} from Redis")
            except Exception as e:
                logger.warn(f"[REDIS] Failed to remove old SID from Redis: {e}")
    
    # Store in Redis first (primary storage)
    if redis_client:
        try:
            redis_client.set(f"user_sid:{user_id}", sid, ex=3600)  # 1 hour TTL
            redis_client.set(f"sid_user:{sid}", user_id, ex=3600)  # 1 hour TTL
            logger.info(f"[DEBUG][SID_MAPPING] Stored mapping in Redis: user_id={user_id} -> sid={sid}")
        except Exception as e:
            logger.warn(f"[REDIS] Failed to store SID mapping in Redis: {e}")
    
    # Also store in memory for fast access
    USER_ID_TO_SID[user_id] = sid
    SID_TO_USER_ID[sid] = user_id
    
    logger.info(f"[DEBUG][SID_MAPPING] After update - USER_ID_TO_SID: {USER_ID_TO_SID}")
    logger.info(f"[DEBUG][SID_MAPPING] After update - SID_TO_USER_ID: {SID_TO_USER_ID}")
    logger.info(f"[SID_MAPPING] Mapped user {user_id} -> SID {sid}")

def queue_message_for_user(user_id: str, event: str, data: any):
    """Queue message using user_id instead of SID"""
    try:
        logger.info(f"[DEBUG][QUEUE] queue_message_for_user: user_id={user_id}, event={event}")
        logger.info(f"[DEBUG][QUEUE] Current user_message_queue keys: {list(user_message_queue.keys())}")
        
        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            logger.error(f"[ERROR][QUEUE] Invalid user_id: {user_id} (type: {type(user_id)})")
            return
            
        if not event or not isinstance(event, str):
            logger.error(f"[ERROR][QUEUE] Invalid event: {event} (type: {type(event)})")
            return
        
        if user_id not in user_message_queue:
            user_message_queue[user_id] = []
        
        message = {
            "event": event,
            "data": data,
            "timestamp": time.time()
        }
        
        user_message_queue[user_id].append(message)
        
        logger.info(f"[DEBUG][QUEUE] Added message to queue. Queue size for {user_id}: {len(user_message_queue[user_id])}")
        
        # Store in Redis for persistence
        if redis_client:
            try:
                redis_key = f"queued_messages:{user_id}"
                redis_client.lpush(redis_key, json.dumps(message))
                redis_client.expire(redis_key, 3600)  # 1 hour TTL
                logger.info(f"[DEBUG][REDIS] Stored message in Redis with key: {redis_key}")
            except Exception as e:
                logger.warn(f"[REDIS] Failed to store queued message: {e}")
        else:
            logger.info(f"[DEBUG][REDIS] Redis client not available, message stored in memory only")
        
        logger.info(f"[QUEUE] Queued {event} for user {user_id} (queue size: {len(user_message_queue[user_id])})")
        
    except Exception as e:
        logger.error(f"[ERROR][QUEUE] Failed to queue message for user {user_id}: {e}")
        logger.error(f"[ERROR][QUEUE] Error type: {type(e).__name__}")
        import traceback
        logger.error(f"[ERROR][QUEUE] Full traceback: {traceback.format_exc()}")

async def safe_emit_or_queue_by_user_id(user_id: str, event: str, data: any):
    """Send to user with SID validation - only emit to actually active SIDs"""
    try:
        logger.info(f"[DEBUG][EMIT] safe_emit_or_queue_by_user_id: user_id={user_id}, event={event}")

        # Validate inputs
        if not user_id or not isinstance(user_id, str):
            logger.error(f"[ERROR][EMIT] Invalid user_id: {user_id} (type: {type(user_id)})")
            return
            
        if not event or not isinstance(event, str):
            logger.error(f"[ERROR][EMIT] Invalid event: {event} (type: {type(event)})")
            return

        # Get active SIDs for this user (copy to avoid modification during iteration)
        active_sids = USER_ID_ACTIVE_SIDS.get(user_id, set()).copy()
        
        if not active_sids:
            logger.info(f"[DEBUG][EMIT] No active SIDs for user {user_id}, queuing message")
            await queue_message_for_user(user_id, event, data)
            return

        # Track if any SID was successfully used
        message_sent = False
        
        for sid in active_sids:
            try:
                # Check if SID is still active in Socket.IO's internal tracking
                if sid in sio.manager.rooms.get('/', {}):
                    await sio.emit(event, data, room=sid)
                    logger.info(f"[SOCKET EMIT] {event} sent to active SID {sid} for user {user_id}")
                    message_sent = True
                else:
                    # SID is dead, remove from our tracking
                    USER_ID_ACTIVE_SIDS[user_id].discard(sid)
                    logger.info(f"[CLEANUP] Removed dead SID {sid} from user {user_id}")
            except Exception as e:
                # SID is dead, remove from our tracking
                USER_ID_ACTIVE_SIDS[user_id].discard(sid)
                logger.error(f"[CLEANUP] Removed dead SID {sid} due to error: {e}")
                logger.error(f"[CLEANUP] Error type: {type(e).__name__}")

        # If no SIDs were successfully used, queue the message
        if not message_sent:
            logger.info(f"[DEBUG][EMIT] No active SIDs available for user {user_id}, queuing message")
            await queue_message_for_user(user_id, event, data)
            
    except Exception as e:
        logger.error(f"[ERROR][EMIT] Failed to emit to user {user_id}: {e}")
        logger.error(f"[ERROR][EMIT] Error type: {type(e).__name__}")
        import traceback
        logger.error(f"[ERROR][EMIT] Full traceback: {traceback.format_exc()}")
        
        # Try to queue the message as a fallback
        try:
            await queue_message_for_user(user_id, event, data)
        except Exception as queue_error:
            logger.error(f"[ERROR][EMIT] Failed to queue message as fallback: {queue_error}")

async def deliver_queued_messages_for_user(user_id: str, sid: str):
    """Deliver queued messages for a user"""
    logger.info(f"[DEBUG][DELIVERY] deliver_queued_messages_for_user: user_id={user_id}, sid={sid}")
    queued_messages = []
    
    # Get messages from memory
    logger.info(f"[DEBUG][DELIVERY] Checking memory queue for user {user_id}")
    logger.info(f"[DEBUG][DELIVERY] Memory queue keys: {list(user_message_queue.keys())}")
    
    if user_id in user_message_queue:
        queued_messages.extend(user_message_queue[user_id])
        logger.info(f"[DEBUG][DELIVERY] Found {len(user_message_queue[user_id])} messages in memory queue")
        del user_message_queue[user_id]
    else:
        logger.info(f"[DEBUG][DELIVERY] No messages found in memory queue for user {user_id}")
    
    # Get messages from Redis
    if redis_client:
        try:
            redis_key = f"queued_messages:{user_id}"
            logger.info(f"[DEBUG][DELIVERY] Checking Redis with key: {redis_key}")
            redis_messages = redis_client.lrange(redis_key, 0, -1)
            logger.info(f"[DEBUG][DELIVERY] Found {len(redis_messages)} messages in Redis")
            
            if redis_messages:
                for msg_json in redis_messages:
                    try:
                        msg = json.loads(msg_json)
                        queued_messages.append(msg)
                        logger.info(f"[DEBUG][DELIVERY] Parsed Redis message: {msg.get('event', 'unknown_event')}")
                    except Exception as e:
                        logger.warn(f"[REDIS] Failed to parse queued message: {e}")
                
                # Clear Redis queue
                redis_client.delete(redis_key)
                logger.info(f"[DEBUG][DELIVERY] Cleared Redis queue for user {user_id}")
        except Exception as e:
            logger.warn(f"[REDIS] Failed to retrieve queued messages: {e}")
    else:
        logger.info(f"[DEBUG][DELIVERY] Redis client not available, skipping Redis check")
    
    # Deliver messages
    total_messages = len(queued_messages)
    logger.info(f"[DEBUG][DELIVERY] Total messages to deliver: {total_messages}")
    
    if queued_messages:
        logger.info(f"[DELIVERY] Delivering {total_messages} queued messages to user {user_id}")
        
        for i, msg in enumerate(queued_messages):
            try:
                logger.info(f"[DEBUG][DELIVERY] Delivering message {i+1}/{total_messages}: {msg.get('event', 'unknown_event')}")
                await safe_emit_or_queue(sid, msg["event"], msg["data"])
                logger.info(f"[DELIVERY] Delivered queued {msg['event']} to user {user_id}")
            except Exception as e:
                logger.error(f"[DELIVERY] Failed to deliver message: {e}")
    else:
        logger.info(f"[DELIVERY] No queued messages for user {user_id}")

# -------------------------- Google Cloud STT Streaming -------------------------- #
@sio.event
async def connect(sid, environ):
    logger.info(f"####### Socket Connected with SID: {sid} #######")
    logger.info(f"[DEBUG][CONNECT] Full environ: {environ}")
    
    # CRITICAL: Check if this is the SID we're expecting
    if sid == "sA01oGbEBzACUn76AAAL":
        logger.info(f"🎯 [CRITICAL] FOUND EXPECTED SID: {sid}")
        logger.info(f"🎯 [CRITICAL] This should deliver queued messages for user 1688")
    
    # Track active SID globally
    try:
        ACTIVE_SIDS.add(sid)
        logger.info(f"[DEBUG][CONNECT] Added SID {sid} to ACTIVE_SIDS. Total active: {len(ACTIVE_SIDS)}")
    except Exception as e:
        logger.error(f"[DEBUG][CONNECT] Error adding SID to ACTIVE_SIDS: {e}")
    
    # Extract user_id from query parameters
    query_string = environ.get('QUERY_STRING', '')
    logger.info(f"[DEBUG][CONNECT] Query string: {query_string}")
    
    asgi_scope = environ.get('asgi.scope', {})
    scope_query = asgi_scope.get('query_string', b'').decode('utf-8')
    logger.info(f"[DEBUG][CONNECT] ASGI scope query string: {scope_query}")
    
    parsed_query = urllib.parse.parse_qs(query_string)
    user_id = parsed_query.get('user_id', [None])[0]
    run_stage = parsed_query.get('run_stage', ['dev'])[0]
    logger.info(f"[DEBUG][CONNECT] Parsed run_stage: {run_stage}")
    logger.info(f"[DEBUG][CONNECT] Parsed user_id: {user_id}")
    
    # Join the client to a room with its own SID for SID targeting (PRESERVE EXISTING)
    await sio.enter_room(sid, sid)
    logger.info(f"[DEBUG][CONNECT] Joined SID room: {sid}")
    
    # Store run_stage and user_id in session (ENHANCED)
    try:
        session_data = {'run_stage': run_stage}
        if user_id:
            session_data['user_id'] = user_id
        await sio.save_session(sid, session_data)
        session = await sio.get_session(sid)
        logger.info(f"[DEBUG][CONNECT] Session after save: {session}")
    except Exception as e:
        logger.info(f"[DEBUG][CONNECT] Session error: {e}")
    
    # Emit after session is saved so that downstream handlers can resolve user_id from session
    await safe_emit_or_queue(sid, "initial connect", {"message": "socket connection started"})
    
    # NEW: Handle user_id mapping if provided
    if user_id:
        logger.info(f"[DEBUG][CONNECT] Processing user_id mapping for user: {user_id}")
        update_sid_mapping(user_id, sid)
        # Also join a room with user_id for user-based targeting
        await sio.enter_room(sid, f"user_{user_id}")
        logger.info(f"[DEBUG][CONNECT] Joined user room: user_{user_id}")
        # Track active SIDs per user
        try:
            if user_id not in USER_ID_ACTIVE_SIDS:
                USER_ID_ACTIVE_SIDS[user_id] = set()
            USER_ID_ACTIVE_SIDS[user_id].add(sid)
            logger.info(f"[DEBUG][CONNECT] Added SID {sid} to USER_ID_ACTIVE_SIDS[{user_id}]. Active SIDs for user: {len(USER_ID_ACTIVE_SIDS[user_id])}")
        except Exception as e:
            logger.error(f"[DEBUG][CONNECT] Error adding SID to USER_ID_ACTIVE_SIDS: {e}")
        # Deliver any queued messages for this user
        logger.info(f"[DEBUG][CONNECT] About to deliver queued messages for user {user_id}")
        await deliver_queued_messages_for_user(user_id, sid)
        logger.info(f"[CONNECT] User {user_id} connected with SID {sid}")
        
        # Debug: Show current mappings after connection
        debug_show_mappings()
    else:
        logger.warn(f"[CONNECT] No user_id provided for SID {sid} - using legacy SID-only mode")

@sio.on("initial connect")
async def connect(sid):
    logger.info(f"####### Socket Connected with SID: {sid} #######")
    
    # Check if there are queued messages for this client (PRESERVE EXISTING)
    logger.info(f"[DEBUG][INITIAL_CONNECT] Checking legacy SID queue for {sid}")
    if sid in disconnected_message_queue:
        queued_messages = disconnected_message_queue[sid]
        logger.info(f"[DELIVERY] Delivering {len(queued_messages)} queued messages to {sid}")
        
        for msg in queued_messages:
            await safe_emit_or_queue(sid, msg["event"], msg["data"])
            logger.info(f"[DELIVERY] Delivered queued {msg['event']} to {sid}")
        
        # Clear the queue
        del disconnected_message_queue[sid]
        logger.info(f"[DELIVERY] Cleared message queue for {sid}")
    else:
        logger.info(f"[DELIVERY] No queued messages for {sid}")
    
    # NEW: Also check for user_id based queued messages
    try:
        session = await sio.get_session(sid)
        user_id = session.get('user_id')
        logger.info(f"[DEBUG][INITIAL_CONNECT] Session user_id: {user_id}")
        if user_id:
            logger.info(f"[DEBUG][INITIAL_CONNECT] Delivering user_id based messages for {user_id}")
            await deliver_queued_messages_for_user(user_id, sid)
        else:
            logger.info(f"[DEBUG][INITIAL_CONNECT] No user_id in session")
    except Exception as e:
        logger.info(f"[DEBUG][INITIAL_CONNECT] Session retrieval error: {e}")
    
    await safe_emit_or_queue(sid, "initial connect", {"message": "socket connection started"})

@sio.on("disconnect")
async def disconnect(sid):
    logger.info(f"Client disconnected with SID: {sid}")
    # Mark SID inactive
    try:
        ACTIVE_SIDS.discard(sid)
    except Exception:
        pass
    
    # Get user_id for this SID
    user_id = get_user_id_from_sid(sid)
    if user_id:
        logger.info(f"[DEBUG][DISCONNECT] User {user_id} disconnected from SID {sid}")
        logger.info(f"[DEBUG][DISCONNECT] Current mappings - USER_ID_TO_SID: {USER_ID_TO_SID}")
        logger.info(f"[DEBUG][DISCONNECT] Current mappings - SID_TO_USER_ID: {SID_TO_USER_ID}")
        
        # Do NOT remove mapping immediately; leave mapping so emits during reconnect window can still resolve user_id
        if USER_ID_TO_SID.get(user_id) == sid:
            logger.info(f"[DEBUG][DISCONNECT] Preserving mapping for user {user_id} -> {sid} during reconnect window")
        else:
            logger.info(f"[DEBUG][DISCONNECT] SID {sid} not the current mapping for user {user_id}")
        # Remove from active set for this user
        try:
            if user_id in USER_ID_ACTIVE_SIDS and sid in USER_ID_ACTIVE_SIDS[user_id]:
                USER_ID_ACTIVE_SIDS[user_id].discard(sid)
                if not USER_ID_ACTIVE_SIDS[user_id]:
                    USER_ID_ACTIVE_SIDS.pop(user_id, None)
        except Exception:
            pass
    else:
        logger.info(f"[DEBUG][DISCONNECT] No user_id found for SID {sid}")
    
    # PRESERVE ALL EXISTING CLEANUP LOGIC
    # Clean up any active transcribers for this session
    existing = transcribers.pop(sid, None)
    if existing is not None:
        try:
            if hasattr(existing, 'close') and callable(getattr(existing, 'close')):
                existing.close()
            elif hasattr(existing, 'disconnect') and callable(getattr(existing, 'disconnect')):
                existing.disconnect()
            elif hasattr(existing, 'terminate') and callable(getattr(existing, 'terminate')):
                existing.terminate()
            logger.info(f"Session closed cleanly on disconnect (sid={sid})")
        except Exception as e:
            logger.warn(f"Error while closing session on disconnect (sid={sid}): {e}")
    
    # Clean up Google STT V1 sessions (PRESERVE EXISTING)
    google_v1_session = google_streams.pop(sid, None)
    if google_v1_session is not None:
        try:
            await google_v1_session.stop()
            logger.info(f"[GOOGLE_V1][DISCONNECT] Session closed for sid={sid}")
        except Exception as e:
            logger.warn(f"[GOOGLE_V1][DISCONNECT] Error closing session for sid={sid}: {e}")
    
    # Clean up Google STT V2 sessions (PRESERVE EXISTING)
    google_v2_session = google_streams_v2.pop(sid, None)
    if google_v2_session is not None:
        try:
            await google_v2_session.stop()
            logger.info(f"[GOOGLE_V2][DISCONNECT] Session closed for sid={sid}")
        except Exception as e:
            logger.warn(f"[GOOGLE_V2][DISCONNECT] Error closing session for sid={sid}: {e}")
    
    # Clean up AssemblyAI Universal-Streaming sessions (PRESERVE EXISTING)
    logger.info(f"[ASSEMBLYAI][DEBUG][DISCONNECT] Cleaning up AssemblyAI session for sid={sid}")
    logger.info(f"[ASSEMBLYAI][DEBUG][DISCONNECT] Current AssemblyAI sessions: {list(assemblyai_streams.keys())}")
    
    assemblyai_session = assemblyai_streams.pop(sid, None)
    if assemblyai_session is not None:
        try:
            logger.info(f"[ASSEMBLYAI][DEBUG][DISCONNECT] Found session, calling disconnect for sid={sid}")
            await assemblyai_session.disconnect()
            logger.info(f"[ASSEMBLYAI][DEBUG][DISCONNECT] AssemblyAI session closed cleanly on disconnect (sid={sid})")
        except Exception as e:
            logger.warn(f"[ASSEMBLYAI][DEBUG][DISCONNECT] Error while closing AssemblyAI session on disconnect (sid={sid}): {e}")
            logger.warn(f"[ASSEMBLYAI][DEBUG][DISCONNECT] Error type: {type(e)}")
    else:
        logger.info(f"[ASSEMBLYAI][DEBUG][DISCONNECT] No AssemblyAI session found for sid={sid}")



@sio.on("subscribe_to_processing")
async def subscribe_to_processing(sid, data):
    """Subscribe to user-specific processing updates"""
    job_id = data.get("job_id")
    user_id = data.get("user_id")
    
    # Handle None/null job_id (common in Celery tasks)
    if job_id is None:
        job_id = "None"
    elif job_id == "any":
        job_id = "any"
    
    if user_id and (job_id or job_id == "None"):
        room = f"processing_{job_id}_{user_id}"
        await sio.enter_room(sid, room)
        await safe_emit_or_queue(sid, "processing_confirmed", {
            "job_id": job_id,
            "user_id": user_id,
            "room": room,
            "message": f"Subscribed to processing updates for job {job_id}, user {user_id}"
        }, room=sid)
        logger.info(f"📡 [DEBUG] User {user_id} subscribed to room {room} for job {job_id}")
    else:
        await safe_emit_or_queue(sid, "processing_error", {
            "error": f"Missing job_id or user_id for subscription. Got job_id={job_id}, user_id={user_id}"
        }, room=sid)
    
@sio.on("assemblyai_status")
async def get_assemblyai_status(sid):
    """Get current AssemblyAI session status for monitoring"""
    try:
        active_sessions = len([s for s in assemblyai_streams.values() if s is not None])
        total_sessions = len(assemblyai_streams)
        
        status = {
            "active_sessions": active_sessions,
            "total_sessions": total_sessions,
            "max_sessions": MAX_ASSEMBLYAI_SESSIONS,
            "utilization_percent": round((active_sessions / MAX_ASSEMBLYAI_SESSIONS) * 100, 2),
            "cleanup_task_running": cleanup_task_started
        }
        
        await safe_emit_or_queue(sid, "assemblyai_status_response", status)
        logger.info(f"[ASSEMBLYAI][STATUS] {status}")
        
    except Exception as e:
        logger.error(f"[ASSEMBLYAI][STATUS] Error getting status: {e}")
        await safe_emit_or_queue(sid, "assemblyai_status_error", {"error": str(e)})


# -------------------------- Whisper Batch Transcription -------------------------- #
@sio.on("audio transcribe whisper")
async def audio_transcribe_whisper(sid, data):
    audioblob = data.get('audioblob')

    if sid not in whisper_buffers:
        whisper_buffers[sid] = bytearray()

    if audioblob is None:
        buf = whisper_buffers.get(sid, bytearray())
        logger.info(f"[WHISPER][STOP] sid={sid} final_flush_bytes={len(buf)}")
        if len(buf) > 0:
            wav_bytes = _pcm16_mono_16k_to_wav_bytes(bytes(buf))
            try:
                result = client.audio.transcriptions.create(
                    model=WHISPER_MODEL,
                    file=("chunk.wav", wav_bytes, "audio/wav"),
                    language="en",
                )
                text = getattr(result, 'text', None) or (result.get('text') if isinstance(result, dict) else None)
                logger.info(f"[WHISPER][STOP] sid={sid} transcript_len={len(text or '')}")
                if text:
                    await safe_emit_or_queue(sid, "audio transcribe whisper", text)
            except Exception as e:
                logger.error(f"[WHISPER] Final flush error: {e}")
        whisper_buffers.pop(sid, None)
        return

    try:
        if hasattr(audioblob, 'buffer'):
            audio_bytes = bytes(audioblob)
        elif isinstance(audioblob, list):
            audio_bytes = bytes(audioblob)
        elif isinstance(audioblob, (bytes, bytearray, memoryview)):
            audio_bytes = bytes(audioblob)
        else:
            audio_bytes = audioblob
    except Exception:
        audio_bytes = audioblob

    # Skip silent chunks to avoid hallucinations on silence
    if _is_silent_pcm16(audio_bytes):
        logger.info(f"[WHISPER][SILENT] sid={sid} chunk_bytes={len(audio_bytes)} skipped (rms<th={WHISPER_RMS_THRESHOLD})")
        return

    whisper_buffers[sid].extend(audio_bytes)
    logger.info(f"[WHISPER][APPEND] sid={sid} chunk_bytes={len(audio_bytes)} buffer_bytes={len(whisper_buffers[sid])}")

    if len(whisper_buffers[sid]) >= WHISPER_TARGET_BYTES:
        buf = whisper_buffers[sid]
        carry = buf[-WHISPER_OVERLAP_BYTES:] if len(buf) > WHISPER_OVERLAP_BYTES else buf[:]
        whisper_buffers[sid] = bytearray(carry)
        wav_bytes = _pcm16_mono_16k_to_wav_bytes(bytes(buf))
        try:
            logger.info(f"[WHISPER][SEND] sid={sid} wav_bytes={len(wav_bytes)} pcm_bytes={len(buf)}")
            result = client.audio.transcriptions.create(
                model=WHISPER_MODEL,
                file=("chunk.wav", wav_bytes, "audio/wav"),
                language="en",
            )
            text = getattr(result, 'text', None) or (result.get('text') if isinstance(result, dict) else None)
            logger.info(f"[WHISPER][RECV] sid={sid} transcript_len={len(text or '')}")
            if text:
                await safe_emit_or_queue(sid, "audio transcribe whisper", text.strip())
        except Exception as e:
            logger.error(f"[WHISPER] Chunk transcription error: {e}")


# -------------------------- AssemblyAI Universal-Streaming -------------------------- #
class AssemblyAIStreamingSession:
    def __init__(self, sid: str):
        try:
            logger.info(f"[ASSEMBLYAI][SESSION][INIT] Starting session creation for sid={sid}")
            self.sid = sid
            self.connected = False
            self.client = None
            self.main_loop = None
            self.last_activity = time.time()  # Track last activity for cleanup
            # Accumulate raw audio bytes for the current turn; cleared at end_of_turn
            self.turn_buffer: bytearray = bytearray()
            # Accumulate all raw audio bytes across the session until stop/termination
            self.session_buffer: bytearray = bytearray()
            logger.info(f"[ASSEMBLYAI][SESSION][INIT] Basic attributes set for sid={sid}")
            self._setup_client()
            logger.info(f"[ASSEMBLYAI][SESSION][INIT] Session creation completed for sid={sid}")
        except ImportError as e:
            logger.error(f"[ASSEMBLYAI][SESSION][INIT] Failed to import Universal-Streaming for sid={sid}: {e}")
            raise RuntimeError("AssemblyAI Universal-Streaming not available")
        except Exception as e:
            logger.error(f"[ASSEMBLYAI][SESSION][INIT] Failed to create session for sid={sid}: {e}")
            raise

    def _setup_client(self):
        """Create a new StreamingClient instance"""
        try:
            logger.info(f"[ASSEMBLYAI][SETUP] Starting client setup for sid={self.sid}")
            from assemblyai.streaming.v3 import (
                StreamingClient,
                StreamingClientOptions,
                StreamingEvents,
                BeginEvent,
                TurnEvent,
                TerminationEvent,
                StreamingError,
            )
            logger.info(f"[ASSEMBLYAI][SETUP] Imports successful for sid={self.sid}")
            
            # Store reference to main event loop
            try:
                self.main_loop = asyncio.get_running_loop()
                logger.info(f"[ASSEMBLYAI][SETUP] Captured main event loop for sid={self.sid}")
            except RuntimeError:
                logger.warn(f"[ASSEMBLYAI][SETUP] No running event loop found for sid={self.sid}")
                self.main_loop = None
            
            # Create a fresh client instance
            logger.info(f"[ASSEMBLYAI][SETUP] Creating StreamingClient for sid={self.sid}")
            self.client = StreamingClient(
                StreamingClientOptions(
                    api_key=config.assemblyai.api_key,
                    api_host="streaming.assemblyai.com",
                )
            )
            logger.info(f"[ASSEMBLYAI][SETUP] StreamingClient created for sid={self.sid}")
                
            def on_begin(client, event: BeginEvent):
                self.connected = True
                logger.info(f"[ASSEMBLYAI][DEBUG][BEGIN] Connection established for sid={self.sid}")

            def on_turn(client, event: TurnEvent):
                try:
                    
                    if not event.transcript:
                        return
                    
                    # Only emit final formatted transcripts to avoid repetition
                    if event.end_of_turn and event.turn_is_formatted:
                        
                        # Use stored main event loop to emit to socket
                        if self.main_loop and not self.main_loop.is_closed():
                            
                            asyncio.run_coroutine_threadsafe(
                                safe_emit_or_queue(self.sid, "audio transcribe", event.transcript),
                                self.main_loop
                            )
                            logger.info(f"[ASSEMBLYAI][DEBUG][TURN] Final transcript emitted successfully for sid={self.sid}")
                            # Log accumulated bytes for this final transcript, then clear for next turn
                            try:
                                total_bytes = len(self.turn_buffer)
                                logger.info(f"[ASSEMBLYAI][DEBUG][TURN][BYTES] sid={self.sid} final_turn_audio_bytes={total_bytes}")
                            except Exception as be:
                                logger.warn(f"[ASSEMBLYAI][DEBUG][TURN][BYTES] Failed to compute length sid={self.sid}: {be}")
                            finally:
                                try:
                                    self.turn_buffer.clear()
                                except Exception:
                                    pass
                            
                            # Log end of turn but don't emit completion signal here
                            logger.info(f"[ASSEMBLYAI][DEBUG][TURN] End of turn detected for sid={self.sid}")
                        else:
                            logger.warn(f"[ASSEMBLYAI][DEBUG][TURN] Skipping emit - final transcript: '{event.transcript}'")
                    else:
                        # Log interim transcripts but don't emit them
                        if event.end_of_turn and not event.turn_is_formatted:
                            logger.info(f"[ASSEMBLYAI][DEBUG][TURN] Skipping interim transcript (waiting for formatted): '{event.transcript}'")
                        elif not event.end_of_turn:
                            logger.info(f"[ASSEMBLYAI][DEBUG][TURN] Skipping partial transcript (not end of turn): '{event.transcript}'")
                        
                except Exception as emit_err:
                    logger.error(f"[ASSEMBLYAI][DEBUG][TURN] Error type: {type(emit_err)}")

            def on_terminated(client, event: TerminationEvent):
                self.connected = False
                # Log total accumulated session bytes and clear the buffer
                try:
                    total_session_bytes = len(self.session_buffer)
                    logger.info(f"[ASSEMBLYAI][DEBUG][TERMINATED][BYTES] sid={self.sid} total_session_audio_bytes={total_session_bytes}")
                except Exception as se:
                    logger.warn(f"[ASSEMBLYAI][DEBUG][TERMINATED][BYTES] Failed to compute session bytes sid={self.sid}: {se}")
                finally:
                    try:
                        self.session_buffer.clear()
                    except Exception:
                        pass
                
                # Emit completion signal when transcription is fully terminated
                if self.main_loop:
                    asyncio.run_coroutine_threadsafe(
                        safe_emit_or_queue(self.sid, "transcription_complete", {
                            "status": "completed",
                            "message": "Audio transcription finished"
                        }), self.main_loop
                    )
                    logger.info(f"[ASSEMBLYAI][DEBUG][TERMINATED] transcription_complete emitted successfully for sid={self.sid}")
                else:
                    logger.warn(f"[ASSEMBLYAI][DEBUG][TERMINATED] No valid main event loop available for sid={self.sid}")

            def on_error(client, error: StreamingError):
                logger.error(f"[ASSEMBLYAI][DEBUG][ERROR] sid={self.sid}: {error}")

            # Register event handlers
            logger.info(f"[ASSEMBLYAI][SETUP] Registering event handlers for sid={self.sid}")
            self.client.on(StreamingEvents.Begin, on_begin)
            self.client.on(StreamingEvents.Turn, on_turn)
            self.client.on(StreamingEvents.Termination, on_terminated)
            self.client.on(StreamingEvents.Error, on_error)
            logger.info(f"[ASSEMBLYAI][SETUP] Event handlers registered successfully for sid={self.sid}")
            
        except Exception as e:
            logger.error(f"[ASSEMBLYAI][SETUP] Failed to setup client for sid={self.sid}: {e}")
            raise

    async def connect(self):
        """Connect to AssemblyAI streaming service"""
        try:
            
            if self.connected:
                logger.info(f"[ASSEMBLYAI][DEBUG][CONNECT] Already connected for sid={self.sid}")
                return
                
            from assemblyai.streaming.v3 import StreamingParameters
            
            params = StreamingParameters(
                sample_rate=16000,
                format_turns=True,
            )
            
            # Connect only once per client instance
            self.client.connect(params)
            # Note: connected state will be set to True in on_begin event handler
        except Exception as e:
            logger.debug(f"[ASSEMBLYAI][DEBUG][CONNECT] Failed for sid={self.sid}: {e}")
            # If threading error, reset client to allow recreation
            if "threads can only be started once" in str(e):
                logger.info(f"[ASSEMBLYAI][DEBUG][CONNECT] Threading error, resetting client for sid={self.sid}")
                self.client = None
                self.connected = False
                self._setup_client()
            raise

    async def stream_audio(self, audio_bytes: bytes):
        """Stream audio data to AssemblyAI"""
        try:
            # Update activity timestamp
            self.last_activity = time.time()
            
            # Connect only if not already connected
            if not self.connected:
                logger.info(f"[ASSEMBLYAI][DEBUG][STREAM] Not connected, calling connect() for sid={self.sid}")
                await self.connect()
                logger.info(f"[ASSEMBLYAI][DEBUG][STREAM] Connect completed, connected state: {self.connected}")
            
            # Send raw audio bytes directly to Universal-Streaming API
            try:
                # Append to current-turn accumulator for later logging at end_of_turn
                self.turn_buffer.extend(audio_bytes)
            except Exception as acc_err:
                logger.warn(f"[ASSEMBLYAI][DEBUG][STREAM][BYTES] Accumulate failed sid={self.sid}: {acc_err}")
            try:
                # Append to session-wide accumulator to represent entire recording until stop
                self.session_buffer.extend(audio_bytes)
            except Exception as sess_acc_err:
                logger.warn(f"[ASSEMBLYAI][DEBUG][STREAM][BYTES] Session accumulate failed sid={self.sid}: {sess_acc_err}")
            self.client.stream(audio_bytes)
            
        except Exception as e:
            # If threading error, recreate client and retry once
            if "threads can only be started once" in str(e):
                logger.debug(f"[ASSEMBLYAI][DEBUG][STREAM] Threading error detected for sid={self.sid}, recreating client")
                try:
                    # Reset client state
                    self.client = None
                    self.connected = False
                    self._setup_client()
                    
                    # Retry connection and streaming
                    await self.connect()
                    self.client.stream(audio_bytes)
                    logger.info(f"[ASSEMBLYAI][DEBUG][STREAM] Successfully recovered from threading error for sid={self.sid}")
                except Exception as retry_e:
                    logger.debug(f"[ASSEMBLYAI][DEBUG][STREAM] Retry failed for sid={self.sid}: {retry_e}")
                    raise
            else:
                raise

    async def disconnect(self):
        """Disconnect from AssemblyAI streaming service"""
        try:
          
            if not self.connected:
                logger.info(f"[ASSEMBLYAI][DEBUG][DISCONNECT] Already disconnected for sid={self.sid}")
                return
                
            self.client.disconnect(terminate=True)
            self.connected = False
        except Exception as e:
            logger.error(f"[ASSEMBLYAI][DEBUG][DISCONNECT] Error type: {type(e)}")
            self.connected = False

# Improved assembly streaming with proper session management
@sio.on("audio transcribe")
async def audio_endpoint(sid, data):
    """Handle audio transcribe event with improved session management using Universal-Streaming."""
    
    audioblob = data.get('audioblob')

    # Log incoming audio data
    if audioblob:
        blob_length = len(audioblob) if hasattr(audioblob, '__len__') else 'unknown'
        logger.info(f"[ASSEMBLYAI][DEBUG][ENDPOINT] audioblob length={blob_length}, type={type(audioblob)}")
    else:
        logger.info(f"[ASSEMBLYAI][DEBUG][ENDPOINT] audioblob=None (stop signal)")

    # Treat None audioblob as an explicit stop signal from client
    if audioblob is None:
        logger.info(f"Stop requested by client (sid={sid}). Closing session if active...")
        session = assemblyai_streams.pop(sid, None)
        if session is not None:
            try:
                await session.disconnect()
                logger.info(f"Session closed cleanly after stop (sid={sid})")
            except Exception as e:
                logger.warn(f"Error while closing session on stop (sid={sid}): {e}")
        else:
            logger.info(f"No active session to close on stop (sid={sid})")
        
        # Handle full_byte upload to S3 if provided
        full_bytes = data.get('full_bytes')
        session_id = data.get('sessionId')

        if full_bytes is not None and session_id is not None:
            try:
                # Normalize full_bytes similar to audioblob
                if hasattr(full_bytes, 'buffer'):
                    audio_bytes = bytes(full_bytes)
                elif isinstance(full_bytes, list):
                    audio_bytes = bytes(full_bytes)
                elif isinstance(full_bytes, (bytes, bytearray, memoryview)):
                    audio_bytes = bytes(full_bytes)
                else:
                    audio_bytes = full_bytes
                
                logger.info(f"[ASSEMBLYAI][FULL_BYTE] sid={sid} session_id={session_id} full_byte_length={len(audio_bytes)}")
                
                # Convert to WAV format and store in global dict keyed by session_id
                wav_bytes = _pcm16_mono_16k_to_wav_bytes(audio_bytes)
                audio_wav_storage[session_id] = wav_bytes
                logger.info(f"[ASSEMBLYAI][DEBUG] Stored WAV bytes for session_id={session_id}, total sessions: {len(audio_wav_storage)}")
                
            except Exception as e:
                logger.error(f"[ASSEMBLYAI][FULL_BYTE] Error processing full_byte for sid={sid}: {e}")
        
        return

    # Normalize audio bytes
    try:
        if hasattr(audioblob, 'buffer'):
            audio_bytes = bytes(audioblob)
        elif isinstance(audioblob, list):
            audio_bytes = bytes(audioblob)
        elif isinstance(audioblob, (bytes, bytearray, memoryview)):
            audio_bytes = bytes(audioblob)
        else:
            audio_bytes = audioblob
    except Exception:
        # Fallback: try best effort conversion
        audio_bytes = audioblob

    # Log normalized audio data
    normalized_length = len(audio_bytes) if hasattr(audio_bytes, '__len__') else 'unknown'
    
    # Start periodic cleanup task if not already started
    global cleanup_task_started
    if not cleanup_task_started:
        asyncio.create_task(periodic_assemblyai_cleanup())
        cleanup_task_started = True
        logger.info("[ASSEMBLYAI][STARTUP] Started periodic cleanup task")
    
    if sid not in assemblyai_streams or assemblyai_streams.get(sid) is None:
        logger.info(f"[ASSEMBLYAI][DEBUG][ENDPOINT] Creating new session for sid={sid}")
        # Clean up stale sessions first
        await cleanup_stale_assemblyai_sessions()
        
        # Admission control (global + per-SID)
        logger.info(f"[ASSEMBLYAI][DEBUG][ENDPOINT] Checking admission control for sid={sid}")
        ok = await _can_open_assemblyai_session(sid)
        if not ok:
            logger.warn(f"[ASSEMBLYAI][DEBUG][ENDPOINT] Admission control blocked session creation for sid={sid}")
            return
        
        try:
            logger.info(f"[ASSEMBLYAI][DEBUG][ENDPOINT] Creating AssemblyAIStreamingSession for sid={sid}")
            session = AssemblyAIStreamingSession(sid=sid)
            assemblyai_streams[sid] = session
            logger.info(f"[ASSEMBLYAI][DEBUG][ENDPOINT] Session created and stored for sid={sid}")
        except Exception as e:
            logger.error(f"[ASSEMBLYAI][DEBUG][ENDPOINT] Failed to create session for sid={sid}: {e}")
            return
    else:
        logger.info(f"[ASSEMBLYAI][DEBUG][ENDPOINT] Using existing session for sid={sid}")

    # Stream audio chunk for this sid
    try:
        await assemblyai_streams[sid].stream_audio(audio_bytes)
        logger.info(f"[ASSEMBLYAI][DEBUG][ENDPOINT] Audio streamed successfully for sid={sid}")
        # Update last activity for cleanup
        try:
            setattr(assemblyai_streams[sid], "last_activity", time.time())
        except Exception:
            pass
    except Exception as e:
        # If threading error, remove the session so a new one will be created
        if "threads can only be started once" in str(e):
            assemblyai_streams.pop(sid, None)
        elif "Attempted to send invalid message" in str(e):
            assemblyai_streams.pop(sid, None)
            logger.warn(f"[ASSEMBLYAI][DEBUG][ENDPOINT] Session removed due to invalid message error")
        elif "Too many concurrent sessions" in str(e) or "Unauthorized" in str(e):
            # Provider concurrency limit hit — cleanly close and inform client
            await _emit_transcription_error(sid, "Audio streaming limit reached. Please wait a few seconds and retry.")
            await _close_assemblyai_session(sid, reason="provider_concurrency_limit")
        else:
            # Generic failure: ensure cleanup so future attempts can recreate
            await _close_assemblyai_session(sid, reason="stream_error")


# -------------------------- Google STT -------------------------- #
class GoogleStreamingSession:
    def __init__(self, sid: str, language_code: str = None, sample_rate_hz: int = 16000, enable_interim_results: bool = True):
        if speech is None:
            raise RuntimeError("google-cloud-speech is not installed")
        if ClientOptions is None:
            raise RuntimeError("google-api-core is not installed")
            
        self.sid = sid
        self.language_code = language_code or os.getenv("GOOGLE_STT_LANGUAGE", "en-US")
        self.sample_rate_hz = sample_rate_hz
        self.enable_interim_results = enable_interim_results
        
        # Stream restart logic
        self.streaming_limit = 300  # 5 minutes
        self.restart_counter = 0
        self.audio_input = []
        self.last_audio_input = []
        self.bridging_offset = 0
        self.result_end_time = 0
        self.is_final_end_time = 0
        self.final_request_end_time = 0
        self.new_stream = True
        self.last_transcript_was_final = False
        self._restart_timer = None
        
        # Initialize Google Cloud Speech client with proper credentials
        try:
            from api.utils.gdrive import google_api
            gapi = google_api()
            
            # Set environment variables for Google Cloud
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = gapi.fauth
            
            # Extract project ID from service account file
            try:
                with open(gapi.fauth, 'r') as f:
                    service_account_data = json.load(f)
                project_id = service_account_data.get('project_id')
                if not project_id:
                    raise ValueError("No project_id found in service account file")
                os.environ['GOOGLE_CLOUD_PROJECT'] = project_id
                logger.info(f"[GOOGLE][INIT] Extracted project_id: {project_id}")
            except Exception as e:
                logger.error(f"[GOOGLE][INIT] Failed to extract project_id: {e}")
                raise RuntimeError(f"Failed to extract project_id from service account: {e}")
            
            # Initialize client with explicit project ID
            try:
                client_options = ClientOptions(quota_project_id=project_id)
                self.client = speech.SpeechClient(client_options=client_options)
                logger.info(f"[GOOGLE][INIT] Client initialized with project: {project_id}")
            except Exception as e:
                logger.warn(f"[GOOGLE][INIT] ClientOptions failed, using default: {e}")
                # Fallback to dictionary format
                try:
                    client_options = {"quota_project_id": project_id}
                    self.client = speech.SpeechClient(client_options=client_options)
                    logger.info(f"[GOOGLE][INIT] Client initialized with dict options, project: {project_id}")
                except Exception as e2:
                    logger.warn(f"[GOOGLE][INIT] Dict options failed, using default client: {e2}")
                    self.client = speech.SpeechClient()
                    logger.info(f"[GOOGLE][INIT] Client initialized with default settings")
                    
        except Exception as e:
            logger.error(f"[GOOGLE][INIT] Failed to initialize client: {e}")
            raise RuntimeError(f"Failed to initialize Google Speech client: {e}")
        
        # Use synchronous queue for compatibility with Google's streaming API
        self._queue: queue.Queue = queue.Queue()
        self._stop = asyncio.Event()
        self._task: asyncio.Task | None = None

    async def start(self):
        if self._task is None:
            self._task = asyncio.create_task(self._run())
            # Start periodic restart timer
            self._restart_timer = asyncio.create_task(self._periodic_restart())

    async def stop(self):
        self._stop.set()
        # Put sentinel to unblock generator
        self._queue.put(None)
        if self._task:
            try:
                await self._task
            except Exception:
                pass
        # Cancel restart timer
        if self._restart_timer:
            self._restart_timer.cancel()

    async def add_audio(self, audio_bytes: bytes):
        # Validate chunk size (10MB limit)
        if len(audio_bytes) > 10 * 1024 * 1024:
            logger.warn(f"[GOOGLE][CHUNK_SIZE] Chunk too large: {len(audio_bytes)} bytes, skipping")
            return
            
        # Store audio for bridging
        self.audio_input.append(audio_bytes)
        self._queue.put(audio_bytes)

    def _requests_generator(self):
        """Synchronous generator for streaming requests"""
        while not self._stop.is_set():
            try:
                chunk = self._queue.get(timeout=0.1)
                if chunk is None:
                    break
                if chunk:
                    # Handle bridging for stream restarts
                    if self.bridging_offset > 0:
                        # Send bridging audio
                        for audio_chunk in self.last_audio_input:
                            yield speech.StreamingRecognizeRequest(audio_content=audio_chunk)
                        self.bridging_offset = 0
                    
                    yield speech.StreamingRecognizeRequest(audio_content=chunk)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"[GOOGLE][GENERATOR] Error: {e}")
                break

    async def _run(self):
        loop = asyncio.get_event_loop()
        try:
            # Create streaming config
            streaming_config = speech.StreamingRecognitionConfig(
                config=speech.RecognitionConfig(
                    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                    sample_rate_hertz=self.sample_rate_hz,
                    language_code=self.language_code,
                    enable_automatic_punctuation=True,
                    model=os.getenv("GOOGLE_STT_MODEL", "latest_long"),
                ),
                interim_results=self.enable_interim_results,
                single_utterance=False,
            )
            
            # Use correct method signature: streaming_config, requests_generator
            responses = self.client.streaming_recognize(streaming_config, self._requests_generator())
            
            for response in responses:
                if self._stop.is_set():
                    break
                    
                for result in response.results:
                    if not result.alternatives:
                        continue
                        
                    transcript = result.alternatives[0].transcript
                    if not transcript:
                        continue
                    
                    # Update timing for stream restart logic
                    if result.result_end_time.seconds > 0:
                        self.result_end_time = result.result_end_time.seconds + result.result_end_time.nanos * 1e-9
                    
                    if result.is_final:
                        self.is_final_end_time = self.result_end_time
                        self.last_transcript_was_final = True
                        logger.info(f"[GOOGLE][FINAL] sid={self.sid} text='{transcript}'")
                        asyncio.run_coroutine_threadsafe(
                            safe_emit_or_queue(self.sid, "audio transcribe google", transcript),
                            loop,
                        )
                    else:
                        self.last_transcript_was_final = False
                        logger.info(f"[GOOGLE][INTERIM] sid={self.sid} text='{transcript}'")
                        
        except Exception as e:
            logger.error(f"[GOOGLE] streaming error sid={self.sid}: {e}")
            # Handle stream restart on specific errors
            if hasattr(e, 'code') and e.code == 11:  # RESOURCE_EXHAUSTED
                logger.info(f"[GOOGLE][RESTART] Stream exhausted, restarting sid={self.sid}")
                await self._restart_stream()

    async def _restart_stream(self):
        """Restart the streaming session with bridging"""
        self.restart_counter += 1
        logger.info(f"[GOOGLE][RESTART] Restarting stream #{self.restart_counter} for sid={self.sid}")
        
        # Reset timing variables
        self.result_end_time = 0
        self.is_final_end_time = 0
        self.final_request_end_time = 0
        self.new_stream = True
        
        # Copy current audio input for bridging
        self.last_audio_input = self.audio_input.copy()
        self.bridging_offset = self.final_request_end_time
        
        # Restart the run task
        if self._task:
            self._task.cancel()
        self._task = asyncio.create_task(self._run())

    async def _periodic_restart(self):
        """Periodically restart the stream to avoid timeout"""
        while not self._stop.is_set():
            await asyncio.sleep(self.streaming_limit)
            if not self._stop.is_set():
                logger.info(f"[GOOGLE][PERIODIC_RESTART] Restarting stream for sid={self.sid}")
                await self._restart_stream()

@sio.on("audio transcribe google")
async def audio_transcribe_google(sid, data):
    """
    Realtime Google Cloud STT via gRPC; expects 16kHz mono PCM16 chunks. Send audioblob=None to stop.
    
    Supports both V1 (legacy) and V2 (latest) APIs.
    Set use_v1=True in data or USE_GOOGLE_STT_V1 env var to use V1.
    """
    audioblob = data.get('audioblob') if isinstance(data, dict) else None
    
    # Determine which version to use
    use_v1 = data.get('use_v1', USE_GOOGLE_STT_V1) if isinstance(data, dict) else USE_GOOGLE_STT_V1
    
    if use_v1:
        # V1 Implementation (Legacy)
        await _audio_transcribe_google_v1(sid, audioblob, data)
    else:
        # V2 Implementation (Latest - Recommended)
        await _audio_transcribe_google_v2(sid, audioblob, data)


async def _audio_transcribe_google_v1(sid: str, audioblob, data=None):
    """V1 implementation (legacy)"""
    if audioblob is None:
        # stop and cleanup
        session: GoogleStreamingSession | None = google_streams.pop(sid, None)
        if session is not None:
            logger.info(f"[GOOGLE_V1][STOP] sid={sid}")
            try:
                await session.stop()
                # Emit transcription completion signal
                await safe_emit_or_queue(sid, "google_transcription_complete", {
                    "status": "completed",
                    "message": "Google STT transcription finished"
                })
                logger.info(f"[GOOGLE_V1][COMPLETE] transcription_complete emitted for sid={sid}")
            except Exception as e:
                logger.error(f"[GOOGLE_V1] stop error sid={sid}: {e}")
        else:
            logger.info(f"[GOOGLE_V1][STOP] no active session sid={sid}")
        
        # Handle full_byte upload to S3 if provided (same as AssemblyAI)
        if data and isinstance(data, dict):
            full_bytes = data.get('full_bytes')
            session_id = data.get('sessionId')
            
            if full_bytes is not None and session_id is not None:
                try:
                    # Normalize full_bytes similar to audioblob
                    if hasattr(full_bytes, 'buffer'):
                        audio_bytes = bytes(full_bytes)
                    elif isinstance(full_bytes, list):
                        audio_bytes = bytes(full_bytes)
                    elif isinstance(full_bytes, (bytes, bytearray, memoryview)):
                        audio_bytes = bytes(full_bytes)
                    else:
                        audio_bytes = full_bytes
                    
                    logger.info(f"[GOOGLE_V1][FULL_BYTE] sid={sid} session_id={session_id} full_byte_length={len(audio_bytes)}")
                    
                    # Convert to WAV format and store in global dict keyed by session_id
                    wav_bytes = _pcm16_mono_16k_to_wav_bytes(audio_bytes)
                    audio_wav_storage[session_id] = wav_bytes
                    logger.info(f"[GOOGLE_V1][DEBUG] Stored WAV bytes for session_id={session_id}, total sessions: {len(audio_wav_storage)}")
                    
                except Exception as e:
                    logger.error(f"[GOOGLE_V1][FULL_BYTE] Error processing full_byte for sid={sid}: {e}")
        
        return

    # normalize
    try:
        if hasattr(audioblob, 'buffer'):
            audio_bytes = bytes(audioblob)
        elif isinstance(audioblob, list):
            audio_bytes = bytes(audioblob)
        elif isinstance(audioblob, (bytes, bytearray, memoryview)):
            audio_bytes = bytes(audioblob)
        else:
            audio_bytes = audioblob
    except Exception:
        audio_bytes = audioblob

    # lazy-create session
    if sid not in google_streams:
        if speech is None:
            logger.error("[GOOGLE_V1] google-cloud-speech V1 is not installed")
            return
        logger.info(f"[GOOGLE_V1][START] sid={sid} lang={os.getenv('GOOGLE_STT_LANGUAGE','en-US')}")
        session = GoogleStreamingSession(sid=sid)
        google_streams[sid] = session
        await session.start()

    session = google_streams[sid]
    try:
        await session.add_audio(audio_bytes)
    except Exception as e:
        logger.error(f"[GOOGLE_V1] add_audio error sid={sid}: {e}")


async def _audio_transcribe_google_v2(sid: str, audioblob, data=None):
    """V2 implementation (latest - recommended)"""
    
    # Minimal debug logging - only log full_bytes length when present
    if data and isinstance(data, dict) and 'full_bytes' in data:
        full_bytes = data.get('full_bytes')
        if full_bytes is not None:
            logger.info(f"[GOOGLE_V2][FULL_BYTE] sid={sid} full_byte_length={len(full_bytes)}")
    
    if audioblob is None:
        # stop and cleanup
        session = google_streams_v2.pop(sid, None)
        if session is not None:
            logger.info(f"[GOOGLE_V2][STOP] sid={sid}")
            try:
                await session.stop()
                # Emit transcription completion signal
                await safe_emit_or_queue(sid, "google_transcription_complete", {
                    "status": "completed",
                    "message": "Google STT transcription finished"
                })
                logger.info(f"[GOOGLE_V2][COMPLETE] transcription_complete emitted for sid={sid}")
            except Exception as e:
                logger.error(f"[GOOGLE_V2] stop error sid={sid}: {e}")
        else:
            logger.info(f"[GOOGLE_V2][STOP] no active session sid={sid}") 
        
        # Handle full_byte upload to S3 if provided (same as AssemblyAI)
        if data and isinstance(data, dict):
            full_bytes = data.get('full_bytes')
            session_id = data.get('sessionId')
            
            # If sessionId not provided directly, try to get it from latest.id
            if session_id is None and 'latest' in data:
                latest = data.get('latest')
                if isinstance(latest, dict) and 'id' in latest:
                    session_id = latest.get('id')
                    logger.info(f"[GOOGLE_V2][DEBUG] Extracted sessionId from latest.id: {session_id}")

            if full_bytes is not None and session_id is not None:
                try:
                    # Normalize full_bytes similar to audioblob
                    if hasattr(full_bytes, 'buffer'):
                        audio_bytes = bytes(full_bytes)
                    elif isinstance(full_bytes, list):
                        audio_bytes = bytes(full_bytes)
                    elif isinstance(full_bytes, (bytes, bytearray, memoryview)):
                        audio_bytes = bytes(full_bytes)
                    else:
                        audio_bytes = full_bytes
                    
                    logger.info(f"[GOOGLE_V2][FULL_BYTE] sid={sid} session_id={session_id} full_byte_length={len(audio_bytes)}")
                    
                    # Convert to WAV format and store in global dict keyed by session_id
                    wav_bytes = _pcm16_mono_16k_to_wav_bytes(audio_bytes)
                    audio_wav_storage[session_id] = wav_bytes
                    logger.info(f"[GOOGLE_V2][DEBUG] Stored WAV bytes for session_id={session_id}, total sessions: {len(audio_wav_storage)}")
                    
                except Exception as e:
                    logger.error(f"[GOOGLE_V2][FULL_BYTE] Error processing full_byte for sid={sid}: {e}")
        
        return

    # normalize
    try:
        if hasattr(audioblob, 'buffer'):
            audio_bytes = bytes(audioblob)
        elif isinstance(audioblob, list):
            audio_bytes = bytes(audioblob)
        elif isinstance(audioblob, (bytes, bytearray, memoryview)):
            audio_bytes = bytes(audioblob)
        else:
            audio_bytes = audioblob
    except Exception:
        audio_bytes = audioblob

    # lazy-create session
    if sid not in google_streams_v2:
        if GoogleStreamingSTTV2 is None:
            logger.error("[GOOGLE_V2] google-cloud-speech V2 is not installed. Install: pip install 'google-cloud-speech>=2.20.0'")
            return
        
        # Define callbacks
        # Track state for self-correction and deduplication
        transcript_state = {
            "last_interim": "",      # Last interim text sent
            "last_final": "",        # Last final text sent
            "utterance_buffer": ""   # Buffer for utterance end
        }
        
        async def on_transcript(text: str, is_final: bool, result: dict):
            """Callback for transcripts with smart deduplication and self-correction"""
            
            if is_final:
                # Final result - emit if different from last final
                if text.strip() and text != transcript_state["last_final"]:
                    # Emit structured payload so frontend appends into finals history
                    payload = {
                        "text": text,
                        "is_final": True,
                        "language": result.get("language_code") or "en-US",
                        "restart_epoch": result.get("restart_epoch"),
                        "result_seq": result.get("result_seq"),
                    }
                    await safe_emit_or_queue(sid, "audio transcribe google", payload)
                    transcript_state["last_final"] = text
                    transcript_state["last_interim"] = ""  # Clear interim
                    transcript_state["utterance_buffer"] = ""  # Clear buffer
                    logger.info(f"[GOOGLE_V2][TRANSCRIPT][FINAL] sid={sid}, text='{text}...'")
            else:
                # Interim result - smart filtering
                text_stripped = text.strip()
                if not text_stripped:
                    return  # Skip empty
                
                # Store for utterance end
                transcript_state["utterance_buffer"] = text
                
                # Only emit interim if configured and text changed significantly
                if config.emit_interim_results and not config.emit_only_final:
                    # Check if this is actually new content (not just repetition)
                    last = transcript_state["last_interim"]
                    
                    # Smart deduplication: only emit if text is different AND longer or more stable
                    if text != last:
                        # Only emit if it's a meaningful update (not just same text repeating)
                        words_last = set(last.lower().split())
                        words_current = set(text.lower().split())
                        new_words = words_current - words_last
                        
                        # Emit if: new words added OR text is substantially different
                        if new_words or len(text) > len(last) + 2:
                            # Keep interim as string for lightweight, backward-compatible updates
                            await safe_emit_or_queue(sid, "audio transcribe google", text)
                            transcript_state["last_interim"] = text
                            logger.info(f"[GOOGLE_V2][TRANSCRIPT][INTERIM] sid={sid}, new_words={len(new_words)}, text='{text[:30]}...'")
        
        async def on_error(error: Exception):
            """Callback for errors"""
            logger.error(f"[GOOGLE_V2][ERROR] sid={sid}: {error}")
            await safe_emit_or_queue(sid, "transcription_error", {"error": str(error), "version": "v2"})
        
        async def on_speech_event(event_type: str, event: dict):
            """Callback for speech events (VAD)"""
            logger.info(f"[GOOGLE_V2][EVENT] sid={sid}, type={event_type}")
            
            # On utterance end, emit buffered text if configured
            if event_type == "END_OF_SINGLE_UTTERANCE":
                if config.emit_on_utterance_end and transcript_state["utterance_buffer"]:
                    logger.info(f"[GOOGLE_V2][EVENT][UTTERANCE_END] Emitting: '{transcript_state['utterance_buffer'][:50]}...'")
                    await safe_emit_or_queue(sid, "audio transcribe google", {
                        "text": transcript_state["utterance_buffer"],
                        "is_final": False,
                        "is_utterance_end": True,
                        "language": "en-US"
                    })
                    transcript_state["utterance_buffer"] = ""
            
            await safe_emit_or_queue(sid, "speech_event", {"type": event_type, "sid": sid})
        
        # Create config
        config = GoogleSTTV2Config.from_env()
        
        logger.info(
            f"[GOOGLE_V2][START] sid={sid}, "
            f"model={config.model}, "
            f"languages={config.language_codes}"
        )
        
        # Create session
        session = GoogleStreamingSTTV2(
            sid=sid,
            config=config,
            on_transcript=on_transcript,
            on_error=on_error,
            on_speech_event=on_speech_event,
        )
        
        google_streams_v2[sid] = session
        await session.start()

    session = google_streams_v2[sid]
    try:
        await session.add_audio(audio_bytes)
    except Exception as e:
        logger.error(f"[GOOGLE_V2] add_audio error sid={sid}: {e}")



# ------------------------------------------- Audio Chat --------------------------------------------------- #
# method to save audio chat to database
# TODO: integrate with audio chat function
@sio.on("audio chat sentence")
async def audio_end_point(sid, data):
    session = await sio.get_session(sid)        
        
    run_stage = session.get('run_stage', None)  
    if run_stage is None:
        logger.info(f"Run stage not found in session for sid: {sid}")
    else:
        logger.info(f"Run stage retrieved: {run_stage}")
        
    
    # Normalize and extract user_session.id from flexible inputs
    # Accept dict, JSON string, list/tuple candidates; also accept 'session_id' alias
    import json as _json
    def _extract_session_id(payload):
        if not isinstance(payload, dict):
            return None
        user_session = payload.get('user_session')
        # If user_session is a JSON string, try to parse
        if isinstance(user_session, str):
            try:
                user_session = _json.loads(user_session)
            except Exception:
                user_session = None
        # If user_session is a list/tuple, select first dict with an id
        if isinstance(user_session, (list, tuple)):
            for item in user_session:
                if isinstance(item, dict) and (item.get('id') or item.get('session_id')):
                    return item.get('id') or item.get('session_id')
            return None
        # If dict, check common keys
        if isinstance(user_session, dict):
            return user_session.get('id') or user_session.get('session_id')
        return None

    sessionId = _extract_session_id(data)
    if not sessionId:
        error_msg = "Invalid user_session: missing id/session_id"
        logger.warn(error_msg)
        await safe_emit_or_queue(sid, "error", {"error": error_msg})
        return
    logger.info(f"[AUDIO_CHAT] Processing interview chat for session ID: {sessionId}")
    
    try:
        chat_count = 1  
        # sessionId already extracted above
        realtime_evaluation = "null"
        accumulated_message = ""
        full_accumulated_message = ""
        template_id = data.get('template_id', "null")
        challenge_id = data.get('challenge_id', "null")
        total_questions = 0
        template = data.get('template', False)

        
        #-----------------------------------------------------------------------------------#
        try:
            if data.get('template'):
                    try:
                        template_id = data.get('template_id')
                        if not template_id:
                            logger.warn("Template flag set but no template_id provided")
                            return {"error": "Template ID is required"}
                            
                        ipersona_template = IpersonaTinderTemplateSchema()
                        saved_template = ipersona_template.get_tinder_template_id(
                            templateId=template_id, 
                            return_object=True, 
                            nopp=True, 
                            dataframe=False
                        )
                        
                        if not saved_template:
                            logger.warn(f"No template found for template ID: {template_id}")
                            return {"error": f"Template not found: {template_id}"}
                            
                        data['user_session'] = saved_template
                        # Safely extract template questions
                        user_attrs = (data.get('user_session') or {}).get('attributes') or {}
                        nested_attrs = user_attrs.get('attributes') or {}
                        collection = nested_attrs.get('template_questions') or nested_attrs.get('generated_questions') or nested_attrs.get('challenge_questions')
                        if isinstance(collection, str):
                            try:
                                collection = json.loads(collection)
                            except Exception:
                                collection = []
                        if not isinstance(collection, list):
                            collection = []
                        question_counts = {section.get('sectionType'): len(section.get('questions', [])) for section in collection if isinstance(section, dict)}
                        total_questions = sum(question_counts.values())
                    
                    except Exception as template_error:
                        logger.error(f"Error retrieving template: {str(template_error)}")
                        return {"error": f"Template retrieval failed: {str(template_error)}"}
                    
            else: 
                ipersona_user = IpersonaSessionSchema(run_stage=run_stage)
                session_fetched = ipersona_user.get_session_by_id(
                    sessionId=sessionId, 
                    nopp=True, 
                    dataframe=False
                )
              
                data['user_session'] = session_fetched
                all_questions = data['user_session']['attributes']['attributes']
                collection = all_questions.get('generated_questions') or all_questions.get('challenge_questions')
           
                question_counts = {section['sectionType']: len(section['questions']) for section in collection}
                total_questions = sum(question_counts.values())
                
                if not session_fetched:
                    logger.warn(f"No session found for session ID: {sessionId}")
                    return f"No session found for session ID: {sessionId}"
                
        except Exception as data_prep_error:
            logger.error(f"Error in data preparation in Audio Socket: {str(data_prep_error)}")
            return {"error": f"Data preparation failed: {str(data_prep_error)}"}
        #------------------------------------------------------------------------------------#

        
        # Fetch session chat history
        try:
            ipersona_message = IpersonaSessionMessageSchema(run_stage=run_stage)
            session_chathistory = ipersona_message.filter_by_session_id(
                sessionId=sessionId, 
                nopp=True, 
                dataframe=False
            )

            if not session_chathistory:
                logger.warn(f"Failed to retrieve chat history for session {sessionId}")
                chat = 0
            else:
                chat = session_chathistory.get('count', 0)

            if chat != 0:  
                try:
                    chat_total = session_chathistory.get('total', [])
                    assistant_count = sum(1 for entry in chat_total if entry.get("user_type") == "assistant")
                    chat_count += assistant_count
                except Exception as count_error:
                    logger.error(f"Error counting assistant messages: {str(count_error)}")
                    # Continue with default chat_count if count fails
            else:
                logger.info(f"No chat history found for session ID: {sessionId}")
        except Exception as history_error:
            logger.error(f"Error retrieving chat history: {str(history_error)}")


        # Insert the user's response if provided
        try:
            if data.get('response') and data.get('resume') is False:
                try:
                    # Insert message first to get message_id
                    message_id = strapi.step1_insert_message(
                        run_stage, 
                        data, 
                        sessionId)
                    
                    # Check for audio WAV bytes from AssemblyAI and upload to S3
                    logger.info(f"[AUDIO_CHAT][DEBUG] Looking for WAV bytes for sessionId={sessionId}")
                    logger.info(f"[AUDIO_CHAT][DEBUG] Available sessions in storage: {list(audio_wav_storage.keys())}")
                    audio_wav_bytes = audio_wav_storage.get(sessionId)
                    if audio_wav_bytes:
                        logger.info(f"[AUDIO_CHAT] Found WAV bytes for sessionId={sessionId}, length={len(audio_wav_bytes)} bytes")
                    else:
                        logger.info(f"[AUDIO_CHAT] No WAV bytes found for sessionId={sessionId}")
                    if audio_wav_bytes:
                        del audio_wav_storage[sessionId]  # Clean up
                        logger.info(f"[AUDIO_CHAT] Uploading audio from AssemblyAI for sessionId={sessionId}, message_id={message_id}")
                        
                        # Upload to S3 and update message with URL
                        upload_task = asyncio.create_task(
                            parrot_utils.upload_audio_to_s3_background([audio_wav_bytes], sid, sessionId, message_id, run_stage)
                        )


                except Exception as insert_error:
                    logger.error(f"Failed to insert user message: {str(insert_error)}")
                    # Continue despite insertion failure
            else:
                logger.info("No user response to insert")
        except Exception as response_error:
            logger.error(f"Error processing user response: {str(response_error)}")

                 
        try:
            # 🔍 DEBUG: About to call generate_interview_question
            logger.info(f"🔍 [DEBUG] === CALLING generate_interview_question ===")
            logger.info(f"🔍 [DEBUG] SID: {sid}, SessionID: {sessionId}")
            logger.info(f"🔍 [DEBUG] Chat count: {chat_count}, Total questions: {total_questions}")
            
            response = await util.generate_interview_question(
                run_stage, 
                data, 
                total_questions, 
                template_id, 
                challenge_id, 
                sessionId,
                template)
            
            # 🔍 DEBUG: generate_interview_question completed
            logger.info(f"🔍 [DEBUG] === generate_interview_question COMPLETED ===")
            logger.info(f"🔍 [DEBUG] SID: {sid}")
            logger.info(f"🔍 [DEBUG] Response status: {response.get('status', 'None')}")
            logger.info(f"🔍 [DEBUG] Response realtime: {response.get('realtime', 'None')}")
            logger.info(f"🔍 [DEBUG] SID still exists: {sid in sio.manager.rooms}")
            
            if not response:
                logger.error("Failed to generate interview question: empty response")
                # Safely emit or queue the message
                await safe_emit_or_queue(sid, "error", {"error": "Failed to generate next question"})
                return
            
        except Exception as generate_error:
            logger.error(f"Error generating interview question: {str(generate_error)}")
            # Safely emit or queue the message
            await safe_emit_or_queue(sid, "error", {"error": f"Question generation failed: {str(generate_error)}"})
            return
             
        if response.get("interview") is not None:

            assistant_next_question = "" if response.get("interview") is None else response["interview"]       
            message = [
                        {
                            "user_type": "assistant",
                            "content_type": "question",
                            "content": {
                                "time_taken": "null",  
                                "time_limit": "null",
                                "chunk_response": accumulated_message,
                                "full_response": "",
                                "final": "false",
                                "realtime_evaluation": "null"
                            }
                        }
                    ]
            
            # Safely emit or queue the message
            await safe_emit_or_queue(sid, "audio chat sentence", message)
            
            tasks = []
            for chunk in assistant_next_question:
                accumulated_message += chunk 
                full_accumulated_message += chunk            
                while True:
                    last_period = accumulated_message.rfind('.')
                    last_question = accumulated_message.rfind('?')

                    last_end_pos = max(last_period, last_question)
                    
                    if last_end_pos != -1:
                        complete_sentence = accumulated_message[:last_end_pos + 1]
                        message = [{
                            "content": {
                                "chunk_response": complete_sentence
                            }
                        }]  
                                
                        # Safely emit or queue the message
                        logger.info(f"[SOCKET EMIT] Sending chunk response to sid={sid}: '{complete_sentence}'")
                        await safe_emit_or_queue(sid, "audio chat sentence", message)
                        tasks.append(parrot_utils.synthesize_text(complete_sentence))
                    
                        accumulated_message = accumulated_message[last_end_pos + 1:].strip()                        
                    else:
                        break   
                    
            # Calculate and emit time limit
            try:
                if template:
                    # Use synchronous processing for template questions to ensure timelimit is available for database save
                    logger.info(f"[SYNC] Starting time limit calculation for template question")
                    
                    # Get the section data for time limit matching
                    user_attributes = data['user_session']['attributes']['attributes']
                    collection = user_attributes.get('generated_questions') or user_attributes.get('template_questions') or user_attributes.get('challenge_questions')
                    section = json.loads(collection) if isinstance(collection, str) else collection
                    
                    # Calculate time limit synchronously
                    timelimit = await util.calculate_template_time_limit_sync(
                        full_accumulated_message,
                        section,
                        sessionId,
                        run_stage,
                        sio,
                        sid,
                        chat=False
                    )
                    
                    logger.info(f"[SYNC] Time limit calculated: {timelimit}")
                else:
                    # Use synchronous processing for non-template questions
                    timelimit = strapi.calculate_time_limit(response)
                    message = [{
                                "content": {
                                    "time_limit": timelimit.get("time_limit", "null"),
                                }
                            }]
                    # Safely emit or queue the message
                    logger.info(f"[SOCKET EMIT] Sending time limit to sid={sid}: {timelimit.get('time_limit', 'null')}")
                    await safe_emit_or_queue(sid, "time_limit", message)

            except Exception as timelimit_error:
                logger.error(f"Failed to calculate or emit time limit: {str(timelimit_error)}")
                timelimit = {"time_limit": "null"}
                # Continue despite time limit failure

               
            audio_chunks = await asyncio.gather(*tasks)
            
            # Accumulate audio data for S3 upload
            accumulated_audio = []
            
            for i, audio_data in enumerate(audio_chunks):
                if isinstance(audio_data, dict) and 'error' in audio_data:
                    logger.error(f"Error: {audio_data['error']}")
                    continue
                
                # Accumulate audio data
                if audio_data:
                    accumulated_audio.append(audio_data)
                
                # Log blob length instead of full content
                blob_length = len(audio_data) if audio_data else 0
                logger.info(f"[SOCKET EMIT] Sending audio_base64_chunks to sid={sid}: chunk_{i+1}, blob_length={blob_length} bytes")
                
                message = [{
                        "content": {
                            "audio_data": audio_data,
                        }
                    }]                    
                # Safely emit or queue the message
                await safe_emit_or_queue(sid, "audio_base64_chunks", message)
                
                logger.info(f"[SOCKET EMIT] Sending audio-single-chunk to sid={sid}: chunk_{i+1}, blob_length={blob_length} bytes")
                await safe_emit_or_queue(sid, "audio-single-chunk", audio_data)
                
            # Safely emit or queue the message
            logger.info(f"[SOCKET EMIT] Sending audio-single-text-chunk-done to sid={sid}")
            await safe_emit_or_queue(sid, "audio-single-text-chunk-done", None)
            
            # Prepare for background S3 upload
            audio_upload_data = accumulated_audio if accumulated_audio else None

            # Perform real-time response evaluation if applicable
            if data['response'] is not [None, ""]:
                type = 'job_interview_config'
                # Determine if this is the last response (interview is over)
                # chat_count represents number of questions asked, so when chat_count >= total_questions,
                # the response we're evaluating is the answer to the last question
                is_last_response = False
                logger.info(f"🔍 [DEBUG] Audio chat - chat_count: {chat_count}, total_questions: {total_questions}, is_last_response: {is_last_response}")
                
                realtime_evaluation_response_json = util.realtime_response_evaluation(
                                run_stage, 
                                data, 
                                sessionId, 
                                type,
                                is_last_response=is_last_response)
                realtime_evaluation = "null" if realtime_evaluation_response_json is None else realtime_evaluation_response_json.get("realtime_evaluation")
                logger.success(f"Realtime evaluation is: {realtime_evaluation}")
            
                message = [{
                    "content": {
                        "realtime_evaluation": realtime_evaluation,
                        "full_response": accumulated_message
                    }
                }]
                status = "start"
                await safe_emit_or_queue(sid, "realtime_status", status)
                # Check if client is still connected before emitting
                # Safely emit or queue the message
                logger.info(f"[SOCKET EMIT] Sending audio_realtime to sid={sid}: {realtime_evaluation}")
                logger.info(f"[DEBUG] audio_realtime payload: {message}")
                await safe_emit_or_queue(sid, "audio_realtime", message)
                status = "end"
                await safe_emit_or_queue(sid, "realtime_status", status)
             
       
        # Insert the message or conclude the interview if the chat count exceeds the limit
        if chat_count < total_questions + 1:
            final = 'false'
            # Save message first and get message ID
            message_id = strapi.step2_insert_message(
                run_stage, 
                data, 
                timelimit, 
                full_accumulated_message, 
                realtime_evaluation, 
                final,
                sessionId,
                None)  # No audio URL initially
            
            # Start background S3 upload if we have audio data
            # if audio_upload_data and message_id:
            #     upload_task = asyncio.create_task(
            #         parrot_utils.upload_audio_to_s3_background(audio_upload_data, sid, sessionId, message_id)
            #     )
            #     logger.info(f"[S3 UPLOAD] Started background upload task for sid={sid}, sessionId={sessionId}, message_id={message_id}")
        else:
            # 🔍 DEBUG: Interview completion flow starts
            logger.info(f"🔍 [DEBUG] === INTERVIEW COMPLETION FLOW STARTED ===")
            logger.info(f"🔍 [DEBUG] SID: {sid}, SessionID: {sessionId}")
            logger.info(f"🔍 [DEBUG] Chat count: {chat_count}, Total questions: {total_questions}")
            logger.info(f"🔍 [DEBUG] Response status: {response.get('status', 'None')}")
            logger.info(f"🔍 [DEBUG] Response realtime: {response.get('realtime', 'None')}")
            
            message = 'interview over'
            
            # Add small delay to ensure client is still connected
            await asyncio.sleep(0.1)
            # Safely emit or queue the message
            await safe_emit_or_queue(sid, "interview done", message)
            
            # 🔍 DEBUG: Check SID status after interview done
            logger.info(f"🔍 [DEBUG] SID status after 'interview done': {sid in sio.manager.rooms}")
            logger.info(f"🔍 [DEBUG] Active SIDs after 'interview done': {list(sio.manager.rooms.keys())}")

            final = 'true'
            # Always send last_audio_realtime_evaluation regardless of status
            try:
                message = [{
                        "user_type": "assistant",
                        "content_type": "question",
                        "content": {
                            "time_taken": "null",
                            "time_limit": "null",                        
                            "chunk_response": '',
                            "full_response": accumulated_message,
                            "final": "true",
                            "realtime_evaluation": response.get("realtime", "null")
                        }
                    }]
                
                # 🔍 DEBUG: Before sending last_audio_realtime_evaluation
                logger.info(f"🔍 [DEBUG] === ABOUT TO SEND last_audio_realtime_evaluation ===")
                logger.info(f"🔍 [DEBUG] SID: {sid}")
                logger.info(f"🔍 [DEBUG] SID exists in rooms: {sid in sio.manager.rooms}")
                logger.info(f"🔍 [DEBUG] All active SIDs: {list(sio.manager.rooms.keys())}")
                logger.info(f"🔍 [DEBUG] Realtime evaluation: {response.get('realtime', 'null')}")
                
                # Add small delay to ensure client is still connected
                await asyncio.sleep(0.1)
                # Safely emit or queue the message
                logger.info(f"[DEBUG] last_audio_realtime_evaluation payload: {message}")
                await safe_emit_or_queue(sid, "last_audio_realtime_evaluation", message)
                
                # 🔍 DEBUG: After sending last_audio_realtime_evaluation
                logger.info(f"🔍 [DEBUG] === last_audio_realtime_evaluation SENT SUCCESSFULLY ===")
                logger.info(f"🔍 [DEBUG] SID: {sid}")
                logger.info(f"🔍 [DEBUG] SID still exists: {sid in sio.manager.rooms}")

            except Exception as final_emit_error:
                logger.error(f"❌ [ERROR] Failed to emit final evaluation: {str(final_emit_error)}")
                logger.error(f"❌ [ERROR] SID at error time: {sid}")
                logger.error(f"❌ [ERROR] SID exists at error time: {sid in sio.manager.rooms}")
            
            # 🔍 DEBUG: Interview completion flow ends
            logger.info(f"🔍 [DEBUG] === INTERVIEW COMPLETION FLOW COMPLETED ===")
            # strapi.step3_insert_message(data, realtime_evaluation, final)
   
    except Exception as e:
        logger.error(f'❌ [ERROR] Audio endpoint error: {str(e)}')
        logger.error(f'❌ [ERROR] Error type: {type(e).__name__}')
        logger.error(f'❌ [ERROR] SID: {sid}')
        logger.error(f'❌ [ERROR] SID exists: {sid in sio.manager.rooms if sid else "N/A"}')
        
        # Try to send error notification to client if possible
        try:
            if sid and sid in sio.manager.rooms:
                await safe_emit_or_queue(sid, "error", {
                    "message": "An error occurred while processing your request",
                    "error_type": type(e).__name__,
                    "timestamp": datetime.now().isoformat()
                })
        except Exception as emit_error:
            logger.error(f'❌ [ERROR] Failed to emit error notification: {str(emit_error)}')
        
        # Log the full traceback for debugging
        import traceback
        logger.error(f'❌ [ERROR] Full traceback: {traceback.format_exc()}')
        


        
# ------------------------------------------- Text Chat --------------------------------------------------- #
# handle for text to text chat
@sio.on("interview chat")
async def interview_endpoint(sid, data):
    """
    Handle interview socket.io endpoint with comprehensive error handling.
    
    Args:
        sid (str): Socket.io session ID
        data (dict): Interview data containing user session and response
        
    Returns:
        None: Responses are sent via socket.io events
    """
    try:
        logger.info(f"Received interview request with template_id: {data.get('template_id')}, job: {data.get('job_profile_id', None)}, challenge: {data.get('challenge_id', None)}")
        
        # Validate input data
        if not isinstance(data, dict):
            error_msg = "Invalid data format: expected a dictionary"
            logger.error(error_msg)
            # Safely emit or queue the message
            await safe_emit_or_queue(sid, "error", {"error": error_msg})
            return
            
        if 'user_session' not in data:
            error_msg = "Missing required field: user_session"
            logger.error(error_msg)
            # Safely emit or queue the message
            await safe_emit_or_queue(sid, "error", {"error": error_msg})
            return
        
        # Initialize variables
        # try:
        #     session = await sio.get_session(sid)
        # except Exception as session_error:
        #     logger.error(f"Failed to get socket session: {str(session_error)}")
        #     return {"error": f"Retrieval failed for session:, {sid}"}
        
        chat_count = 1  
        sessionId = None
        realtime_evaluation = "null"
        accumulated_message = ""     
        template_id = data.get('template_id', "null")
        challenge_id = data.get('challenge_id', "null")
        timelimit = {"time_limit": "null"}
        total_questions = 0
        template = data.get('template', False)
        collection = []
        # Get run stage from session
        try:
            session = await sio.get_session(sid)        
            run_stage = session.get('run_stage', None)  
            if run_stage is None:
                logger.warn(f"Run stage not found in session for sid: {sid}, using default")
                run_stage = 'dev'  # Default to production if not specified
            else:
                logger.info(f"Run stage retrieved: {run_stage}")
        except Exception as stage_error:
            logger.error(f"Error retrieving run stage: {str(stage_error)}")
            run_stage = 'dev'  # Default to production if error occurs

        # Get session ID with error handling
        try:
            if isinstance(data.get('user_session'), dict) and 'id' in data['user_session']:
                sessionId = data['user_session']['id']
                logger.info(f"Processing interview chat for session ID: {sessionId}")
            else:
                error_msg = "Invalid user_session format: missing ID"
                logger.error(error_msg)
                return {"error": error_msg}
        except Exception as session_id_error:
            logger.error(f"Error extracting session ID: {str(session_id_error)}")
            return {"error": f"Failed to identify session: {sid}" }
        
        #-----------------------------------------------------------------------------------#
        # Handle template-based or session-based interviews

        try:
            if data.get('template'):
                try:
                    template_id = data.get('template_id')
                    if not template_id:
                        logger.warn("Template flag set but no template_id provided")
                        return {"error": "Template ID is required"}
                        
                    ipersona_template = IpersonaTinderTemplateSchema()
                    saved_template = ipersona_template.get_tinder_template_id(
                        templateId=template_id, 
                        return_object=True, 
                        nopp=True, 
                        dataframe=False
                    )
                    
                    if not saved_template:
                        logger.warn(f"No template found for template ID: {template_id}")
                        return {"error": f"Template not found: {template_id}"}
                        
                    data['user_session'] = saved_template
                    # Safely extract template questions
                    user_attrs = (data.get('user_session') or {}).get('attributes') or {}
                    nested_attrs = user_attrs.get('attributes') or {}
                    collection = nested_attrs.get('template_questions') or nested_attrs.get('generated_questions') or nested_attrs.get('challenge_questions')
                    if isinstance(collection, str):
                        try:
                            collection = json.loads(collection)
                        except Exception:
                            collection = []
                    if not isinstance(collection, list):
                        collection = []
                    question_counts = {section.get('sectionType'): len(section.get('questions', [])) for section in collection if isinstance(section, dict)}
                    total_questions = sum(question_counts.values())
                
                except Exception as template_error:
                    logger.error(f"Error retrieving template: {str(template_error)}")
                    return {"error": f"Template retrieval failed: {str(template_error)}"}
 
            else:    
                try:
                    # Fetch session by ID if user_session is already a dict
                    ipersona_user = IpersonaSessionSchema(run_stage=run_stage)
                    session_fetched = ipersona_user.get_session_by_id(
                        sessionId=sessionId, 
                        nopp=True, 
                        dataframe=False
                    )
                    
                    if not session_fetched:
                        logger.warn(f"No session found for session ID: {sessionId}")
                        return {"error": f"Session not found: {sessionId}"}
                        
                    data['user_session'] = session_fetched
                    all_questions = data['user_session']['attributes']['attributes']
                    collection = all_questions.get('generated_questions') or all_questions.get('challenge_questions')
                    collection = json.loads(collection) if isinstance(collection, str) else collection

                    question_counts = {section['sectionType']: len(section['questions']) for section in collection}
                    total_questions = sum(question_counts.values())

                except Exception as session_fetch_error:
                    logger.error(f"Error generated session: {str(session_fetch_error)}")
                    return {"error": f"Session retrieval failed: {str(session_fetch_error)}"}
                
        except Exception as data_prep_error:
            logger.error(f"Error in data preparation: {str(data_prep_error)}")
            return {"error": f"Data preparation failed: {str(data_prep_error)}"}
        #------------------------------------------------------------------------------------#
       
        # Fetch session chat history
        try:
            ipersona_message = IpersonaSessionMessageSchema(run_stage=run_stage)
            session_chathistory = ipersona_message.filter_by_session_id(
                sessionId=sessionId, 
                nopp=True, 
                dataframe=False
            )

            if not session_chathistory:
                logger.warn(f"Failed to retrieve chat history for session {sessionId}")
                chat = 0
            else:
                chat = session_chathistory.get('count', 0)

            if chat != 0:  
                try:
                    chat_total = session_chathistory.get('total', [])
                    assistant_count = sum(1 for entry in chat_total if entry.get("user_type") == "assistant")
                    
                    chat_count += assistant_count
                except Exception as count_error:
                    logger.error(f"Error counting assistant messages: {str(count_error)}")
            else:
                logger.info(f"No chat history found for session ID: {sessionId}")

        except Exception as history_error:
            logger.error(f"Error retrieving chat history: {str(history_error)}")
            # Continue without chat history

        # Insert the user's response if provided
        try:
            if data.get('response') and data.get('resume') is False:
                try:
                    audio_url = None
                    strapi.step1_insert_message(
                        run_stage, 
                        data, 
                        sessionId,
                        audio_url)
                except Exception as insert_error:
                    logger.error(f"Failed to insert user message: {str(insert_error)}")
                    # Continue despite insertion failure
            else:
                logger.info("No user response to insert")
        except Exception as response_error:
            logger.error(f"Error processing user response: {str(response_error)}")
            # Continue despite error
            
        # Generate the next interview question
        try:
            response = await util.generate_interview_question(
                run_stage, 
                data, 
                total_questions, 
                template_id, 
                challenge_id, 
                sessionId,
                template)
            if not response:
                logger.error("Failed to generate interview question: empty response")
                return {"error": "Failed to generate next question"}

        except Exception as generate_error:
            logger.error(f"Error generating interview question: {str(generate_error)}")
            return {"error": f"Question generation failed: {str(generate_error)}"}
       
        # Process and emit the assistant's response
        try:
            if response.get("interview") is not None:
                assistant_next_question = response.get("interview", "")
                
                # Prepare initial message
                try:
                    message = [
                        {
                            "user_type": "assistant",
                            "content_type": "question",
                            "content": {
                                "time_taken": "null",  
                                "time_limit": "null",
                                "chunk_response": accumulated_message,
                                "full_response": "",
                                "final": "false",
                                "realtime_evaluation": "null"
                            }
                        }
                    ]
                    # Safely emit or queue the message
                    await safe_emit_or_queue(sid, "interview chat", message)

                except Exception as initial_emit_error:
                    logger.error(f"Failed to emit initial message: {str(initial_emit_error)}")
                    # Continue despite emission failure

                
                # Process and emit the assistant's message in chunks
                
                is_generator = hasattr(assistant_next_question, '__iter__') and hasattr(assistant_next_question, '__next__')
               
                try:
                    if not is_generator:
                        logger.warn("Expected list for assistant_next_question, converting to list")
                        if isinstance(assistant_next_question, str):
                            assistant_next_question = [assistant_next_question]
                        else:
                            assistant_next_question = [str(assistant_next_question)]
                            
                    for i, chunk in enumerate(assistant_next_question):
                        try:
                            accumulated_message += chunk
                            message = [{
                                "content": {
                                    "chunk_response": chunk
                                }
                            }]
                            # Safely emit or queue the message
                            logger.info(f"[SOCKET EMIT] Sending interview chat chunk to sid={sid}: chunk_{i+1}, content='{chunk}'")
                            await safe_emit_or_queue(sid, "interview chat", message)
                            
                        except Exception as chunk_error:
                            logger.error(f"Error processing chunk: {str(chunk_error)}")
                            # Continue with next chunk despite error
                    logger.success("All chunks processed successfully", accumulated_message)
                except Exception as chunks_error:
                    logger.error(f"Error processing message chunks: {str(chunks_error)}")
                    # Continue despite chunks processing failure

                # Calculate and emit time limit
                try:
                    if template:
                        # Use synchronous processing for template questions to ensure timelimit is available for database save
                        logger.info(f"[SYNC] Starting time limit calculation for template question")
                        
                        # Get the section data for time limit matching
                        user_attributes = data['user_session']['attributes']['attributes']
                        collection = user_attributes.get('generated_questions') or user_attributes.get('template_questions') or user_attributes.get('challenge_questions')
                        section = json.loads(collection) if isinstance(collection, str) else collection
                        
                        # Calculate time limit synchronously
                        timelimit = await util.calculate_template_time_limit_sync(
                            accumulated_message,
                            section,
                            sessionId,
                            run_stage,
                            sio,
                            sid,
                            chat=True
                        )
                        
                        logger.info(f"[SYNC] Time limit calculated: {timelimit}")
                    else:
                        # Use synchronous processing for non-template questions
                        timelimit = strapi.calculate_time_limit(response)
                        message = [{
                                    "content": {
                                        "time_limit": timelimit.get("time_limit", "null"),
                                    }
                                }]
                        # Safely emit or queue the message
                        logger.info(f"[SOCKET EMIT] Sending time limit to sid={sid}: {timelimit.get('time_limit', 'null')}")
                        await safe_emit_or_queue(sid, "time_limit", message)

                except Exception as timelimit_error:
                    logger.error(f"Failed to calculate or emit time limit: {str(timelimit_error)}")
                    timelimit = {"time_limit": "null"}
                    # Continue despite time limit failure

                # Perform real-time response evaluation if applicable
                try:
                    if data.get('response') not in [None, "", []]:
                        try:
                            eval_type = 'job_interview_config'
                            # Determine if this is the last response (interview is over)
                            # chat_count represents number of questions asked, so when chat_count >= total_questions,
                            # the response we're evaluating is the answer to the last question
                            is_last_response = False
                            logger.info(f"🔍 [DEBUG] chat_count: {chat_count}")
                            logger.info(f"🔍 [DEBUG] total_questions: {total_questions}")
                            logger.info(f"🔍 [DEBUG] is_last_response: {is_last_response}")
                            logger.info(f"🔍 [DEBUG] Text chat - chat_count: {chat_count}, total_questions: {total_questions}, is_last_response: {is_last_response}")
                            
                            realtime_evaluation_response_json = util.realtime_response_evaluation(
                                run_stage, 
                                data, 
                                sessionId, 
                                eval_type,
                                is_last_response=is_last_response
                                )
                            logger.info(f"🔍 [DEBUG] realtime_evaluation_response_json: {realtime_evaluation_response_json}")
                            realtime_evaluation = "null" if realtime_evaluation_response_json is None else realtime_evaluation_response_json.get("realtime_evaluation")
                            logger.info(f"🔍 [DEBUG] Computed realtime_evaluation: {realtime_evaluation}")
                        except Exception as eval_compute_error:
                            logger.error(f"Failed to compute realtime evaluation: {str(eval_compute_error)}")
                            realtime_evaluation = "null"
                        
                        try:
                            message = [{
                                "content": {
                                    "realtime_evaluation": realtime_evaluation,
                                    "full_response": accumulated_message
                                }
                            }]

                            status = "started"
                            await safe_emit_or_queue(sid, "realtime_status", status)
                            # Safely emit or queue the message
                            logger.info(f"[SOCKET EMIT] Sending realtime evaluation to sid={sid}: {realtime_evaluation}")
                            await safe_emit_or_queue(sid, "realtime", message)
                            status = "finished"
                            await safe_emit_or_queue(sid, "realtime_status", status)

                        except Exception as eval_emit_error:
                            logger.error(f"Failed to emit realtime evaluation: {str(eval_emit_error)}")

                except Exception as realtime_error:
                    logger.error(f"Error in realtime evaluation: {str(realtime_error)}")

            else:
                logger.warn("No interview question generated in the response")

        except Exception as response_process_error:
            logger.error(f"Error processing response: {str(response_process_error)}")
            return {"error": f"Error processing response: {str(response_process_error)}"}
                
        # Insert the message or conclude the interview
        try:
            if chat_count < total_questions + 1:
                final = 'false'
                try:
                    # Save message first and get message ID
                    message_id = strapi.step2_insert_message(
                        run_stage, 
                        data, 
                        timelimit, 
                        accumulated_message, 
                        realtime_evaluation, 
                        final,
                        sessionId,
                        None)  # No audio URL initially
                    
                    # Note: No S3 upload for interview endpoint as it doesn't handle audio
                        
                except Exception as insert_message_error:
                    logger.error(f"Failed to insert assistant message: {str(insert_message_error)}")

            else:
                # Handle interview conclusion
                try:
                    message = 'interview over'
                    
                    # Add small delay to ensure client is still connected
                    await asyncio.sleep(0.1)
                    # Safely emit or queue the message
                    await safe_emit_or_queue(sid, "interview done", message)
                    final = 'true'
                    temp_id = data.get('template_id') if data.get('template_id') is not None else "null"
                    challenge_id = data.get('challenge_id') if data.get('challenge_id') is not None else "null"

                    if response.get("status") is not None:
                        try:
                            message = [{
                                "user_type": "assistant",
                                "content_type": "question",
                                "content": {
                                    "time_taken": "null",
                                    "time_limit": "null",                        
                                    "chunk_response": '',
                                    "full_response": accumulated_message,
                                    "final": "true",
                                    "realtime_evaluation": response.get("realtime", "null")
                                }
                            }]
                            # Add small delay to ensure client is still connected
                            await asyncio.sleep(0.1)
                            # Safely emit or queue the message
                            await safe_emit_or_queue(sid, "last_realtime_evaluation", message)
                        
                        except Exception as final_emit_error:
                            logger.error(f"Failed to emit final evaluation: {str(final_emit_error)}")

                except Exception as conclusion_error:
                    logger.error(f"Error concluding interview: {str(conclusion_error)}")
                    return f"Error concluding interview: {str(conclusion_error)}"
                
        except Exception as final_step_error:
            logger.error(f"Error in final processing step: {str(final_step_error)}")
            return  {"error": "Error in final processing step"}

    except Exception as e:
        error_message = f"Error processing interview chat: {str(e)}"
        logger.error(error_message, exc_info=True)
        return error_message

def get_socketio_app(fast_app):
    return get_socket_asgi_app(fast_app)

async def _emit_transcription_error(sid: str, message: str):
    try:
        await safe_emit_or_queue(sid, "transcription_error", {"error": message, "provider": "assemblyai"})
    except Exception as emit_err:
        logger.warn(f"[ASSEMBLYAI][EMIT][ERROR] sid={sid}: {emit_err}")

def _has_active_assemblyai_session(sid: str) -> bool:
    session = assemblyai_streams.get(sid)
    logger.info(f"[ASSEMBLYAI][HAS_ACTIVE] Checking sid={sid}, session_exists={session is not None}")
    
    if not session:
        logger.info(f"[ASSEMBLYAI][HAS_ACTIVE] No session found for sid={sid}")
        return False
    
    # Consider presence as active; prefer attribute check when available
    if hasattr(session, "connected"):
        try:
            connected = bool(session.connected)
            logger.info(f"[ASSEMBLYAI][HAS_ACTIVE] Session has connected attr for sid={sid}, connected={connected}")
            return connected
        except Exception as e:
            logger.warn(f"[ASSEMBLYAI][HAS_ACTIVE] Error checking connected attr for sid={sid}: {e}")
            return True
    
    logger.info(f"[ASSEMBLYAI][HAS_ACTIVE] Session exists but no connected attr for sid={sid}, assuming active")
    return True

async def _can_open_assemblyai_session(sid: str) -> bool:
    # Global cap guard
    active = len([s for s in assemblyai_streams.values() if s is not None])
    logger.info(f"[ASSEMBLYAI][ADMIT] Checking admission for sid={sid}, active_sessions={active}, soft_cap={ASSEMBLYAI_SOFT_CAP}")
    
    if active >= ASSEMBLYAI_SOFT_CAP:
        logger.warn(f"[ASSEMBLYAI][ADMIT][BLOCK] active={active} >= soft_cap={ASSEMBLYAI_SOFT_CAP}")
        await _emit_transcription_error(sid, "Service is busy right now. Please try again in a few seconds.")
        return False
    
    # Per-SID guard
    has_active = _has_active_assemblyai_session(sid)
    logger.info(f"[ASSEMBLYAI][ADMIT] Per-SID check for sid={sid}, has_active_session={has_active}")
    
    if has_active:
        logger.warn(f"[ASSEMBLYAI][ADMIT][BLOCK] sid={sid} already has an active session")
        await _emit_transcription_error(sid, "A streaming session is already active for this tab. Please stop it before starting another.")
        return False
    
    logger.info(f"[ASSEMBLYAI][ADMIT][ALLOW] Session creation allowed for sid={sid}")
    return True

async def _close_assemblyai_session(sid: str, reason: str = ""):
    session = assemblyai_streams.pop(sid, None)
    if session:
        logger.info(f"[ASSEMBLYAI][CLOSE] sid={sid} reason={reason}")
        try:
            if hasattr(session, "disconnect"):
                await session.disconnect()
        except Exception as e:
            logger.warn(f"[ASSEMBLYAI][CLOSE][ERROR] sid={sid}: {e}")

async def cleanup_stale_assemblyai_sessions():
    """Clean up stale AssemblyAI sessions that may not have been properly disconnected"""
    try:
        stale_sessions = []
        current_time = time.time()
        
        for sid, session in assemblyai_streams.items():
            if session is None:
                stale_sessions.append(sid)
                continue
                
            # Check if session is disconnected but still in dict
            if hasattr(session, 'connected') and not session.connected:
                stale_sessions.append(sid)
                continue
                
            # Check if session has been inactive for too long (2 minutes for production)
            if hasattr(session, 'last_activity'):
                if current_time - session.last_activity > 120:  # 2 minutes
                    stale_sessions.append(sid)
        
        # Remove stale sessions
        for sid in stale_sessions:
            logger.info(f"[ASSEMBLYAI][CLEANUP] Removing stale session for sid={sid}")
            session = assemblyai_streams.pop(sid, None)
            if session and hasattr(session, 'disconnect'):
                try:
                    await session.disconnect()
                except Exception as e:
                    logger.warn(f"[ASSEMBLYAI][CLEANUP] Error disconnecting stale session {sid}: {e}")
                    
        if stale_sessions:
            logger.info(f"[ASSEMBLYAI][CLEANUP] Cleaned up {len(stale_sessions)} stale sessions. Active sessions: {len(assemblyai_streams)}")
            
    except Exception as e:
        logger.error(f"[ASSEMBLYAI][CLEANUP] Error during cleanup: {e}")

# Periodic cleanup task for production
async def periodic_assemblyai_cleanup():
    """Run periodic cleanup every 30 seconds"""
    while True:
        try:
            await asyncio.sleep(30)  # Run every 30 seconds
            await cleanup_stale_assemblyai_sessions()
            
            # Log current session count
            active_count = len([s for s in assemblyai_streams.values() if s is not None])
            if active_count > 50:  # Log warn when getting close to limit
                logger.warn(f"[ASSEMBLYAI][MONITOR] High session count: {active_count}/{MAX_ASSEMBLYAI_SESSIONS}")
                
        except Exception as e:
            logger.error(f"[ASSEMBLYAI][PERIODIC] Error in periodic cleanup: {e}")

async def safe_emit_or_queue(sid: str, event: str, data: any):
    """Enhanced function that tries user_id mapping first, falls back to SID"""
    logger.info(f"[DEBUG][SAFE_EMIT] safe_emit_or_queue called: sid={sid}, event={event}")
    
    # Try to get user_id from SID
    user_id = get_user_id_from_sid(sid)
    logger.info(f"[DEBUG][SAFE_EMIT] Retrieved user_id: {user_id}")
    
    if user_id:
        # Use user_id based delivery
        logger.info(f"[DEBUG][SAFE_EMIT] Using user_id based delivery for user: {user_id}")
        await safe_emit_or_queue_by_user_id(user_id, event, data)
    else:
        # Try to find user_id from session data, then emit by user_id
        try:
            session = await sio.get_session(sid)
            if session is None:
                logger.warn(f"[DEBUG][SAFE_EMIT] Session is None for SID {sid}")
                return
                
            session_user_id = session.get('user_id')
            logger.info(f"[DEBUG][SAFE_EMIT] Session user_id for SID {sid}: {session_user_id}")
            if session_user_id:
                logger.info(f"[DEBUG][SAFE_EMIT] Found user_id in session, creating mapping for: {session_user_id}")
                update_sid_mapping(session_user_id, sid)
                logger.info(f"[DEBUG][SAFE_EMIT] Created mapping, using user_id delivery: {session_user_id}")
                await safe_emit_or_queue_by_user_id(session_user_id, event, data)
                return
        except Exception as e:
            logger.error(f"[DEBUG][SAFE_EMIT] Failed to get session for SID {sid}: {e}")
            logger.error(f"[DEBUG][SAFE_EMIT] Error type: {type(e).__name__}")
            # Don't re-raise the exception, just log it and continue

        # No user_id available; skip SID emit per policy and log clearly
        logger.warn(f"[SAFE_EMIT] Skipping emit of '{event}' for SID {sid}: no user_id available during reconnect window")

# New function for direct user_id usage
async def emit_to_user(user_id: str, event: str, data: any):
    """Emit directly to user by user_id"""
    logger.info(f"[DEBUG][EMIT_TO_USER] emit_to_user called: user_id={user_id}, event={event}")
    await safe_emit_or_queue_by_user_id(user_id, event, data)

# Enhanced queue_message_for_client to work with both systems
def queue_message_for_client(sid: str, event: str, data: any):
    """Enhanced function that queues by user_id if available, otherwise by SID"""
    logger.info(f"[DEBUG][QUEUE_CLIENT] queue_message_for_client called: sid={sid}, event={event}")
    
    user_id = get_user_id_from_sid(sid)
    logger.info(f"[DEBUG][QUEUE_CLIENT] Retrieved user_id: {user_id}")
    
    if user_id:
        logger.info(f"[DEBUG][QUEUE_CLIENT] Using user_id based queuing for user: {user_id}")
        queue_message_for_user(user_id, event, data)
    else:
        # Fallback to original SID-based queuing (PRESERVE EXISTING)
        logger.info(f"[DEBUG][QUEUE_CLIENT] No user_id found, using SID fallback for: {sid}")
        if sid not in disconnected_message_queue:
            disconnected_message_queue[sid] = []
        
        disconnected_message_queue[sid].append({
            "event": event,
            "data": data,
            "timestamp": time.time()
        })
        logger.info(f"[QUEUE] Queued {event} for disconnected client {sid} (queue size: {len(disconnected_message_queue[sid])})")


def _pcm16_mono_16k_to_wav_bytes(pcm_bytes: bytes) -> bytes:
    # Backward compatibility wrapper
    return pcm16_mono_16k_to_wav_bytes(pcm_bytes)

def _is_silent_pcm16(pcm_bytes: bytes, rms_threshold: int = WHISPER_RMS_THRESHOLD) -> bool:
    # Backward compatibility wrapper
    return is_silent_pcm16(pcm_bytes, rms_threshold)


