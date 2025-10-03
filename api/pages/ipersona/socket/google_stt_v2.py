"""
Google Cloud Speech-to-Text V2 Streaming Module

Uses the latest Speech V2 API with improved features:
- Better async support with SpeechAsyncClient
- Recognizer resources for reusable configurations
- Enhanced streaming with better latency
- More advanced features and models

Reference: https://cloud.google.com/python/docs/reference/speech/latest/google.cloud.speech_v2.services.speech.SpeechAsyncClient
"""

import asyncio
import os
import json
import time
from typing import Optional, Callable, Dict, Any, AsyncIterator
from dataclasses import dataclass

try:
    from api.utils.logger import LLPackerLogger
except ImportError:
    import logging
    LLPackerLogger = logging.getLogger

try:
    from google.cloud.speech_v2 import SpeechAsyncClient
    from google.cloud.speech_v2.types import (
        StreamingRecognizeRequest,
        StreamingRecognitionConfig,
        StreamingRecognitionFeatures,  # ✅ Separate class, not nested!
        RecognitionConfig,
        AutoDetectDecodingConfig,
        ExplicitDecodingConfig,
        RecognitionFeatures,
        SpeechAdaptation,
    )
    from google.api_core import exceptions as google_exceptions
    from google.api_core.client_options import ClientOptions
except ImportError:
    SpeechAsyncClient = None
    StreamingRecognizeRequest = None
    StreamingRecognitionConfig = None
    StreamingRecognitionFeatures = None
    RecognitionConfig = None
    AutoDetectDecodingConfig = None
    ExplicitDecodingConfig = None
    RecognitionFeatures = None
    SpeechAdaptation = None
    google_exceptions = None
    ClientOptions = None

logger = LLPackerLogger(os.path.basename(__file__))


# Optional: local testing overrides. DO NOT commit secrets.
# Example (uncomment and fill to test locally without exporting env vars):
# LOCAL_TEST_OVERRIDES = {
#     "GOOGLE_CLOUD_PROJECT": "your-project-id",
#     "GOOGLE_STT_V2_LOCATION": "global",
#     "GOOGLE_STT_V2_MODEL": "long",  # "long" model allows more self-correction vs "short"
#     "GOOGLE_STT_V2_LANGUAGES": "en-US",
#     "GOOGLE_STT_V2_INTERIM": "true",
#     "GOOGLE_STT_V2_PUNCTUATION": "true",
#     "GOOGLE_STT_V2_VAD_EVENTS": "true",
#     "GOOGLE_STT_V2_EMIT_INTERIM": "true",
#     "GOOGLE_STT_V2_EMIT_ONLY_FINAL": "false",
#     "GOOGLE_STT_V2_EMIT_ON_UTTERANCE_END": "true",
#     "GOOGLE_STT_V2_SELF_CORRECTION": "true",
#     "GOOGLE_STT_V2_ENDPOINT": "",
# }
LOCAL_TEST_OVERRIDES = {
    # Fallback configuration in case env vars are missing
    "GOOGLE_CLOUD_PROJECT": "tenx-saas",
    "GOOGLE_STT_V2_LOCATION": "global", 
    "GOOGLE_STT_V2_MODEL": "long",
    "GOOGLE_STT_V2_LANGUAGES": "en-US",
    "GOOGLE_STT_V2_INTERIM": "true",
    "GOOGLE_STT_V2_PUNCTUATION": "true",
    "GOOGLE_STT_V2_VAD_EVENTS": "true",
    "GOOGLE_STT_V2_EMIT_INTERIM": "true",
    "GOOGLE_STT_V2_EMIT_ONLY_FINAL": "false", 
    "GOOGLE_STT_V2_EMIT_ON_UTTERANCE_END": "false",
    "GOOGLE_STT_V2_SELF_CORRECTION": "true"
}


def _get_env(key: str, default: str | None = None) -> str | None:
    """Return configuration value with precedence:
    1) process env, 2) LOCAL_TEST_OVERRIDES, 3) provided default
    Values are returned as strings (None if not found).
    """
    try:
        value = os.environ.get(key)
        if value is not None and str(value).strip() != "":
            return value
        if key in LOCAL_TEST_OVERRIDES:
            override = LOCAL_TEST_OVERRIDES[key]
            return None if override is None else str(override)
        return default
    except Exception:
        return default


def _merge_env_from_json(json_path: str = ".envdir/tenx_env_vars.json") -> None:
    """Load environment variables from a JSON file into os.environ.

    - Does not overwrite vars that are already set in the process env
    - Silently returns if the file does not exist or is invalid JSON
    """
    try:
        if not os.path.exists(json_path):
            return
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return
        for key, value in data.items():
            if key in os.environ and str(os.environ.get(key, "")).strip() != "":
                continue
            # Only set simple types; coerce to string for env
            try:
                os.environ[key] = str(value)
            except Exception:
                # Skip non-coercible values
                continue
    except Exception as e:
        try:
            logger.debug(f"[GOOGLE_STT_V2][ENV] Skipping env JSON merge: {e}")
        except Exception:
            pass

# Merge env JSON at import time so subsequent os.getenv() calls see values
_merge_env_from_json()


@dataclass
class GoogleSTTV2Config:
    """Configuration for Google Speech-to-Text V2 streaming"""
    
    # Project and Recognizer
    project_id: Optional[str] = None  # Auto-detected from credentials if not set
    location: str = "global"  # or regional like "us-central1"
    recognizer_id: Optional[str] = None  # Use existing recognizer or create inline config
    
    # Audio configuration
    sample_rate_hz: int = 16000
    language_codes: list = None  # V2 supports multiple languages: ["en-US"]
    
    # Model selection
    model: str = "short"  # Options: short, long, chirp, chirp_2 (V2 uses different names than V1!)
    
    # Streaming configuration
    enable_interim_results: bool = True
    enable_automatic_punctuation: bool = True
    enable_word_time_offsets: bool = False
    enable_word_confidence: bool = False
    enable_spoken_punctuation: bool = False
    enable_spoken_emojis: bool = False
    
    # Voice Activity Detection
    enable_voice_activity_events: bool = False
    
    # Transcript Emission Strategy
    emit_interim_results: bool = True  # Send interim results to frontend
    emit_only_final: bool = False  # Only send final results (overrides emit_interim_results)
    emit_on_utterance_end: bool = True  # Send on END_OF_SINGLE_UTTERANCE event
    enable_self_correction: bool = True  # Allow interim results to update previous text
    
    # Multi-channel
    audio_channel_count: int = 1
    
    # Adaptation
    phrase_sets: list = None  # List of phrase set resource names
    custom_classes: list = None  # List of custom class resource names
    
    # Performance
    # Proactive rotation to avoid server ~65s timeout; can be overridden via env
    streaming_limit_seconds: int = 55
    chunk_size_bytes: int = 3200  # ~100ms of audio at 16kHz PCM16
    
    # Regional endpoint
    api_endpoint: Optional[str] = None  # e.g., "us-central1-speech.googleapis.com"
    
    def __post_init__(self):
        if self.language_codes is None:
            self.language_codes = ["en-US"]
    
    @classmethod
    def from_env(cls) -> "GoogleSTTV2Config":
        """Create configuration from environment variables with fallbacks"""
        lang_codes_str = _get_env("GOOGLE_STT_V2_LANGUAGES") or "en-US"
        lang_codes = [l.strip() for l in lang_codes_str.split(",")]
        
        return cls(
            project_id=_get_env("GOOGLE_CLOUD_PROJECT") or "tenx-saas",
            location=_get_env("GOOGLE_STT_V2_LOCATION") or "global",
            recognizer_id=_get_env("GOOGLE_STT_V2_RECOGNIZER_ID"),
            language_codes=lang_codes,
            model=_get_env("GOOGLE_STT_V2_MODEL") or "long",  # "long" model allows more self-correction vs "short"
            enable_interim_results=(_get_env("GOOGLE_STT_V2_INTERIM") or "true").lower() == "true",
            enable_automatic_punctuation=(_get_env("GOOGLE_STT_V2_PUNCTUATION") or "true").lower() == "true",
            enable_voice_activity_events=(_get_env("GOOGLE_STT_V2_VAD_EVENTS") or "false").lower() == "true",
            api_endpoint=_get_env("GOOGLE_STT_V2_ENDPOINT"),
            # Emission strategy controls
            emit_interim_results=(_get_env("GOOGLE_STT_V2_EMIT_INTERIM") or "true").lower() == "true",
            emit_only_final=(_get_env("GOOGLE_STT_V2_EMIT_ONLY_FINAL") or "false").lower() == "true",
            emit_on_utterance_end=(_get_env("GOOGLE_STT_V2_EMIT_ON_UTTERANCE_END") or "false").lower() == "true",
            enable_self_correction=(_get_env("GOOGLE_STT_V2_SELF_CORRECTION") or "true").lower() == "true",
            # Performance/rotation
            streaming_limit_seconds=int((_get_env("GOOGLE_STT_V2_STREAMING_LIMIT_SECONDS") or "55").strip()),
        )


class GoogleStreamingSTTV2:
    """
    Google Cloud Speech-to-Text V2 streaming client.
    
    Improvements over V1:
    - Better async support with native async client
    - Recognizer resources for reusable configurations
    - Improved models (chirp, chirp_2)
    - Better voice activity detection
    - Enhanced multi-language support
    """
    
    def __init__(
        self,
        sid: str,
        config: Optional[GoogleSTTV2Config] = None,
        on_transcript: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
        on_speech_event: Optional[Callable] = None,
        credentials_path: str = '.envdir/googleservice_tenxsaas.json'
    ):
        """
        Initialize Google STT V2 streaming client.
        
        Args:
            sid: Session ID for tracking
            config: Configuration object
            on_transcript: Async callback: async def callback(text: str, is_final: bool, result: dict)
            on_error: Async callback: async def callback(error: Exception)
            on_speech_event: Async callback for VAD events: async def callback(event_type: str, event: dict)
            credentials_path: Path to Google Cloud credentials JSON
        """
        if SpeechAsyncClient is None:
            raise RuntimeError(
                "google-cloud-speech V2 is not installed. "
                "Install: pip install 'google-cloud-speech>=2.20.0'"
            )
        
        self.sid = sid
        self.config = config or GoogleSTTV2Config.from_env()
        self.on_transcript = on_transcript
        self.on_error = on_error
        self.on_speech_event = on_speech_event
        
        # Initialize client
        self.client = self._initialize_client(credentials_path)
        self.project_id = self._get_project_id(credentials_path)
        
        # Stream management
        self._stop_event = asyncio.Event()
        self._stream_task: Optional[asyncio.Task] = None
        self._restart_timer_task: Optional[asyncio.Task] = None
        self._audio_queue: asyncio.Queue = asyncio.Queue()
        # Graceful-stop controls
        self._stop_requested: bool = False
        self._final_emitted_event: asyncio.Event = asyncio.Event()
        self._drain_mode: bool = False
        
        # Statistics
        self.total_audio_bytes = 0
        self.total_transcripts = 0
        self.restart_counter = 0
        self.stream_start_time = time.time()
        # Timing diagnostics
        self._last_audio_ts: Optional[float] = None
        self._last_response_ts: Optional[float] = None
        # Sequencing for deterministic client handling
        self.result_seq = 0  # increments on every recognition result (interim or final)
        self.utterance_seq = 0  # increments only on finals
        # Per-epoch accumulation of final transcripts for debugging and restart snapshots
        self._epoch_finals = {0: []}
        self._last_final_text = ""
        
    def _get_project_id(self, credentials_path: str) -> str:
        """Extract project ID from credentials"""
        if self.config.project_id:
            return self.config.project_id
        
        try:
            with open(credentials_path, 'r', encoding='utf-8') as f:
                service_account_data = json.load(f)
            project_id = service_account_data.get('project_id')
            if not project_id:
                raise ValueError("No project_id found in credentials or config")
            return project_id
        except Exception as e:
            logger.error(f"[GOOGLE_STT_V2][INIT] Failed to get project_id: {e}")
            raise
    
    def _initialize_client(self, credentials_path: str) -> SpeechAsyncClient:
        """Initialize Google Speech V2 async client"""
        try:
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(f"Credentials file not found: {credentials_path}")
            
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
            
            # Initialize client with optional regional endpoint
            client_options = None
            if self.config.api_endpoint:
                client_options = ClientOptions(api_endpoint=self.config.api_endpoint)
            
            client = SpeechAsyncClient(client_options=client_options)
            
            logger.info(
                f"[GOOGLE_STT_V2][INIT] Client initialized for sid={self.sid}, "
                f"endpoint={self.config.api_endpoint or 'default'}"
            )
            return client
            
        except Exception as e:
            logger.error(f"[GOOGLE_STT_V2][INIT] Failed to initialize client: {e}")
            raise
    
    def _create_streaming_config(self) -> StreamingRecognitionConfig:
        """Create V2 streaming configuration"""
        
        # Create recognition config
        recognition_config = RecognitionConfig(
            # Explicit decoding config for PCM16
            explicit_decoding_config=ExplicitDecodingConfig(
                encoding=ExplicitDecodingConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=self.config.sample_rate_hz,
                audio_channel_count=self.config.audio_channel_count,
            ),
            language_codes=self.config.language_codes,
            model=self.config.model,
            features=RecognitionFeatures(
                enable_automatic_punctuation=self.config.enable_automatic_punctuation,
                enable_word_time_offsets=self.config.enable_word_time_offsets,
                enable_word_confidence=self.config.enable_word_confidence,
                enable_spoken_punctuation=self.config.enable_spoken_punctuation,
                enable_spoken_emojis=self.config.enable_spoken_emojis,
            ),
        )
        
        # Add adaptation if configured
        if self.config.phrase_sets or self.config.custom_classes:
            phrase_sets = []
            if self.config.phrase_sets:
                phrase_sets = [
                    SpeechAdaptation.AdaptationPhraseSet(phrase_set=ps)
                    for ps in self.config.phrase_sets
                ]
            
            recognition_config.adaptation = SpeechAdaptation(
                phrase_sets=phrase_sets,
            )
        
        # Create streaming features (separate class in V2)
        streaming_features = StreamingRecognitionFeatures(
            interim_results=self.config.enable_interim_results,
            enable_voice_activity_events=self.config.enable_voice_activity_events,
        )
        
        # Create streaming config
        streaming_config = StreamingRecognitionConfig(
            config=recognition_config,
            streaming_features=streaming_features,  # ✅ Use the separate class
        )
        
        return streaming_config
    
    async def start(self):
        """Start the streaming session"""
        if self._stream_task is not None:
            logger.warn(f"[GOOGLE_STT_V2][START] Stream already running for sid={self.sid}")
            return
        
        self._stop_event.clear()
        # Reset graceful-stop flags for a fresh session
        try:
            self._stop_requested = False
            self._drain_mode = False
            if self._final_emitted_event.is_set():
                self._final_emitted_event.clear()
        except Exception:
            pass
        self.stream_start_time = time.time()
        
        # Start streaming task
        self._stream_task = asyncio.create_task(self._run_stream())
        
        # Start restart timer
        self._restart_timer_task = asyncio.create_task(self._restart_timer())
        
        logger.info(f"[GOOGLE_STT_V2][START] Stream started for sid={self.sid}")
    
    async def stop(self):
        """Stop the streaming session"""
        # True drain: continue sending already queued audio until queue empty and server quiets
        if not self._stop_requested:
            self._stop_requested = True
            self._drain_mode = True
            logger.info(f"[GOOGLE_STT_V2][STOP] Entering drain mode for sid={self.sid}")
            try:
                # Wait for audio queue to empty and last response to be recent, then a brief quiet period
                while True:
                    try:
                        empty = self._audio_queue.empty()
                    except Exception:
                        empty = True
                    now = time.time()
                    since_audio_ms = int((now - self._last_audio_ts) * 1000) if self._last_audio_ts else 9999
                    since_resp_ms = int((now - self._last_response_ts) * 1000) if self._last_response_ts else 9999
                    # Drain completes when queue empty and responses have settled for >= 250ms
                    if empty and since_audio_ms >= 150 and since_resp_ms >= 250:
                        break
                    await asyncio.sleep(0.05)
            except Exception:
                pass

        # After drain, give the server a brief window to deliver a final
        try:
            await asyncio.wait_for(self._final_emitted_event.wait(), timeout=2.0)
        except asyncio.TimeoutError:
            pass
        try:
            await asyncio.sleep(0.1)
        except Exception:
            pass

        # Hard stop: end generator and response loop
        self._stop_event.set()
        try:
            await self._audio_queue.put(None)
        except Exception:
            pass
        
        # On-stop snapshot: log last-final and full finals list for current epoch
        try:
            curr_epoch = self.restart_counter
            finals_list = self._epoch_finals.get(curr_epoch, []) if hasattr(self, '_epoch_finals') else []
            joined = " | ".join(finals_list)
            logger.info(
                f"[GOOGLE_STT_V2][STOP][SNAPSHOT] sid={self.sid} epoch={curr_epoch} "
                f"last_final='{getattr(self, '_last_final_text', '')}' finals_count={len(finals_list)}"
            )
            if joined:
                logger.info(
                    f"[GOOGLE_STT_V2][STOP][EPOCH_FINALS] sid={self.sid} epoch={curr_epoch} finals='{joined}'"
                )
            # Emit STOP_SNAPSHOT event to frontend so UI can persist final state
            if self.on_speech_event:
                await self.on_speech_event(
                    "STOP_SNAPSHOT",
                    {
                        "current_restart_epoch": curr_epoch,
                        "server_time_ms": int(time.time() * 1000),
                        "last_final_text": getattr(self, "_last_final_text", ""),
                        "full_epoch_finals": joined,
                    },
                )
        except Exception:
            pass

        # Cancel tasks
        if self._stream_task:
            self._stream_task.cancel()
            try:
                await self._stream_task
            except asyncio.CancelledError:
                pass
        
        if self._restart_timer_task:
            self._restart_timer_task.cancel()
            try:
                await self._restart_timer_task
            except asyncio.CancelledError:
                pass
        
        elapsed_s = time.time() - self.stream_start_time if self.stream_start_time else None
        since_audio_ms = int((time.time() - self._last_audio_ts) * 1000) if self._last_audio_ts else None
        since_resp_ms = int((time.time() - self._last_response_ts) * 1000) if self._last_response_ts else None
        logger.info(
            f"[GOOGLE_STT_V2][STOP] Stream stopped for sid={self.sid}, "
            f"total_bytes={self.total_audio_bytes}, "
            f"total_transcripts={self.total_transcripts}, "
            f"restarts={self.restart_counter}, "
            f"elapsed_s={elapsed_s:.3f} since_last_audio_ms={since_audio_ms} since_last_response_ms={since_resp_ms}"
        )
    
    async def add_audio(self, audio_bytes: bytes):
        """Add audio data to the streaming queue"""
        # Check if we're in the middle of a restart - if so, drop audio to prevent queue backup
        if self._stream_task is None or self._stream_task.done():
            logger.debug(
                f"[GOOGLE_STT_V2][ADD_AUDIO] Dropping audio during restart for sid={self.sid}, "
                f"chunk_size={len(audio_bytes)}"
            )
            return
        
        self.total_audio_bytes += len(audio_bytes)
        queue_size = self._audio_queue.qsize()
        
        # Prevent queue backup during restart - drop audio if queue is too full
        if queue_size > 10:  # Allow some buffering but prevent massive backup
            logger.debug(
                f"[GOOGLE_STT_V2][ADD_AUDIO] Dropping audio due to queue backup for sid={self.sid}, "
                f"chunk_size={len(audio_bytes)}, queue_size={queue_size}"
            )
            return
            
        await self._audio_queue.put(audio_bytes)
        self._last_audio_ts = time.time()
        logger.info(
            f"[GOOGLE_STT_V2][ADD_AUDIO] sid={self.sid}, "
            f"chunk_size={len(audio_bytes)}, "
            f"queue_size_before={queue_size}, "
            f"total_bytes={self.total_audio_bytes}"
        )
    
    async def _audio_request_generator(self) -> AsyncIterator[StreamingRecognizeRequest]:
        """
        Async generator for streaming requests.
        
        V2 uses async iterator instead of sync generator for better performance.
        """
        logger.info(f"[GOOGLE_STT_V2][GENERATOR] Generator called for sid={self.sid}")
        
        try:
            # First request: config
            logger.info(f"[GOOGLE_STT_V2][GENERATOR] Creating streaming config for sid={self.sid}")
            streaming_config = self._create_streaming_config()
            logger.info(f"[GOOGLE_STT_V2][GENERATOR] Streaming config created for sid={self.sid}")
            
            # Build recognizer path if using a specific recognizer
            if self.config.recognizer_id:
                recognizer = (
                    f"projects/{self.project_id}/"
                    f"locations/{self.config.location}/"
                    f"recognizers/{self.config.recognizer_id}"
                )
            else:
                # Use inline config (no specific recognizer)
                recognizer = (
                    f"projects/{self.project_id}/"
                    f"locations/{self.config.location}/"
                    f"recognizers/_"
                )
            
            logger.info(
                f"[GOOGLE_STT_V2][GENERATOR][CONFIG] sid={self.sid}\n"
                f"  recognizer={recognizer}\n"
                f"  model={self.config.model}\n"
                f"  languages={self.config.language_codes}\n"
                f"  sample_rate={self.config.sample_rate_hz}\n"
                f"  encoding=LINEAR16\n"
                f"  interim_results={self.config.enable_interim_results}"
            )
            
            logger.info(f"[GOOGLE_STT_V2][GENERATOR] About to yield first request (config) for sid={self.sid}")
            yield StreamingRecognizeRequest(
                recognizer=recognizer,
                streaming_config=streaming_config,
            )
            logger.info(f"[GOOGLE_STT_V2][GENERATOR] ✅ Config request yielded successfully for sid={self.sid}")
            
        except Exception as config_error:
            logger.error(
                f"[GOOGLE_STT_V2][GENERATOR] ❌ Error creating config for sid={self.sid}: "
                f"{type(config_error).__name__}: {config_error}",
                exc_info=True
            )
            raise
        
        # Stream audio chunks
        logger.info(f"[GOOGLE_STT_V2][GENERATOR] Starting audio chunk loop for sid={self.sid}")
        chunk_count = 0
        while True:
            try:
                chunk = await asyncio.wait_for(self._audio_queue.get(), timeout=0.1)
                if chunk is None:  # Sentinel to stop
                    logger.info(f"[GOOGLE_STT_V2][GENERATOR] Sentinel received, stopping generator for sid={self.sid}")
                    break
                chunk_count += 1
                logger.info(f"[GOOGLE_STT_V2][GENERATOR] Yielding audio chunk #{chunk_count}, size={len(chunk)} for sid={self.sid}")
                yield StreamingRecognizeRequest(audio=chunk)
                logger.info(f"[GOOGLE_STT_V2][GENERATOR] Audio chunk #{chunk_count} yielded for sid={self.sid}")
            except asyncio.TimeoutError:
                # In drain mode, if queue is empty, end generator
                if self._drain_mode:
                    try:
                        if self._audio_queue.empty():
                            logger.info(f"[GOOGLE_STT_V2][GENERATOR] Drain-mode empty queue, stopping generator for sid={self.sid}")
                            break
                    except Exception:
                        pass
                continue
            except Exception as e:
                logger.error(f"[GOOGLE_STT_V2][GENERATOR] Error: {e}")
                break
        
        logger.info(f"[GOOGLE_STT_V2][GENERATOR] Generator ended after {chunk_count} audio chunks for sid={self.sid}")
    
    async def _run_stream(self):
        """Main streaming loop using V2 async client"""
        try:
            logger.info(f"[GOOGLE_STT_V2][STREAM] Creating request generator for sid={self.sid}")
            
            # Create request generator
            requests = self._audio_request_generator()
            
            logger.info(f"[GOOGLE_STT_V2][STREAM] Generator created, calling streaming_recognize for sid={self.sid}")
            
            # Start streaming recognition (fully async in V2)
            try:
                logger.info(f"[GOOGLE_STT_V2][STREAM] About to await streaming_recognize for sid={self.sid}")
                response_stream = await self.client.streaming_recognize(requests=requests)
                logger.info(f"[GOOGLE_STT_V2][STREAM] ✅ streaming_recognize() returned successfully for sid={self.sid}")
            except Exception as stream_init_error:
                logger.error(
                    f"[GOOGLE_STT_V2][STREAM] ❌ Failed to call streaming_recognize for sid={self.sid}: "
                    f"{type(stream_init_error).__name__}: {stream_init_error}",
                    exc_info=True
                )
                raise
            
            logger.info(f"[GOOGLE_STT_V2][STREAM] Got response stream for sid={self.sid}")
            
            # Process responses
            response_count = 0
            logger.info(f"[GOOGLE_STT_V2][STREAM] Starting to consume response stream for sid={self.sid}")
            async for response in response_stream:
                response_count += 1
                logger.info(f"[GOOGLE_STT_V2][STREAM] 📥 Response #{response_count} received for sid={self.sid}")
                
                # If a hard stop is requested and not draining, break
                if self._stop_event.is_set() and not self._drain_mode:
                    break
                
                await self._process_response(response)
            
            logger.info(f"[GOOGLE_STT_V2][STREAM] Stream ended after {response_count} responses for sid={self.sid}")
            
            # Stream ended naturally - check if we should restart
            if not self._stop_event.is_set():
                logger.info(f"[GOOGLE_STT_V2][STREAM] Stream ended naturally, attempting restart for sid={self.sid}")
                await asyncio.sleep(0.5)  # Brief delay before restart
                await self._restart_stream()
                
        except google_exceptions.OutOfRange:
            elapsed_s = time.time() - self.stream_start_time if self.stream_start_time else None
            since_audio_ms = int((time.time() - self._last_audio_ts) * 1000) if self._last_audio_ts else None
            since_resp_ms = int((time.time() - self._last_response_ts) * 1000) if self._last_response_ts else None
            logger.info(
                f"[GOOGLE_STT_V2][STREAM] Time limit reached for sid={self.sid} "
                f"elapsed_s={elapsed_s:.3f} since_last_audio_ms={since_audio_ms} since_last_response_ms={since_resp_ms}"
            )
            if not self._stop_event.is_set():
                await self._restart_stream()
                
        except google_exceptions.GoogleAPICallError as api_error:
            # Extract status if available
            status_code = getattr(api_error, 'code', None)
            elapsed_s = time.time() - self.stream_start_time if self.stream_start_time else None
            since_audio_ms = int((time.time() - self._last_audio_ts) * 1000) if self._last_audio_ts else None
            since_resp_ms = int((time.time() - self._last_response_ts) * 1000) if self._last_response_ts else None
            logger.error(
                f"[GOOGLE_STT_V2][STREAM] API error for sid={self.sid}: {status_code or ''} {api_error} "
                f"elapsed_s={elapsed_s:.3f} since_last_audio_ms={since_audio_ms} since_last_response_ms={since_resp_ms}"
            )
            if self.on_error:
                await self.on_error(api_error)
            
            if not self._stop_event.is_set() and self._should_retry_error(api_error):
                await asyncio.sleep(1)
                await self._restart_stream()
                
        except (IOError, RuntimeError) as stream_error:
            logger.error(f"[GOOGLE_STT_V2][STREAM] Stream error for sid={self.sid}: {stream_error}")
            if self.on_error:
                await self.on_error(stream_error)
        
        except Exception as unexpected_error:
            logger.error(
                f"[GOOGLE_STT_V2][STREAM] Unexpected error for sid={self.sid}: "
                f"{type(unexpected_error).__name__}: {unexpected_error}",
                exc_info=True
            )
            if self.on_error:
                await self.on_error(unexpected_error)
    
    def _should_retry_error(self, error: Exception) -> bool:
        """Determine if error should trigger retry"""
        # Known retriable server-side conditions
        if isinstance(error, (
            google_exceptions.ServiceUnavailable,
            google_exceptions.DeadlineExceeded,
            google_exceptions.InternalServerError,
        )):
            return True
        # Google sometimes returns 409 when the stream idles: "Stream timed out after receiving no more client requests."
        try:
            code = getattr(error, 'code', None)
            if code is not None:
                # grpc StatusCode or numeric; accept either string/int comparison
                if str(int(code)) == '409' or str(code) == '409':
                    return True
        except Exception:
            pass
        if 'timed out after receiving no more client requests' in str(error).lower():
            return True
        return False
    
    async def _process_response(self, response):
        """Process V2 streaming response"""
        
        logger.info(f"[GOOGLE_STT_V2][PROCESS] Processing response for sid={self.sid}, has_results={bool(response.results)}")
        # Mark last response timestamp for inactivity diagnostics
        self._last_response_ts = time.time()
        
        # Handle speech event (VAD)
        if hasattr(response, 'speech_event_type') and response.speech_event_type:
            event_type = response.speech_event_type.name
            logger.info(f"[GOOGLE_STT_V2][EVENT] sid={self.sid}, type={event_type}")
            if self.on_speech_event:
                await self.on_speech_event(event_type, {"response": response})
        
        # Handle recognition results
        if not response.results:
            logger.info(f"[GOOGLE_STT_V2][PROCESS] ⚠️ No results in response for sid={self.sid}")
            return
        
        logger.info(f"[GOOGLE_STT_V2][PROCESS] ✅ Found {len(response.results)} results for sid={self.sid}")
        
        for result in response.results:
            if not result.alternatives:
                continue
            
            # Get top alternative
            alternative = result.alternatives[0]
            transcript = alternative.transcript
            
            if not transcript:
                continue
            
            # Normalize Google duration/timedelta fields into millis to avoid JSON issues
            def _duration_to_ms(value):
                try:
                    # Proto Duration may expose total_seconds()
                    if hasattr(value, 'total_seconds'):
                        return int(value.total_seconds() * 1000)
                    # Some responses use dict-like seconds/nanos
                    seconds = getattr(value, 'seconds', None)
                    nanos = getattr(value, 'nanos', None)
                    if seconds is not None or nanos is not None:
                        seconds = int(seconds or 0)
                        nanos = int(nanos or 0)
                        return int(seconds * 1000 + nanos / 1_000_000)
                except Exception:
                    pass
                return None

            # Build result dict with V2 specific fields
            result_dict = {
                "transcript": transcript,
                "is_final": result.is_final,
                "stability": result.stability if hasattr(result, 'stability') else None,
                "result_end_offset": _duration_to_ms(getattr(result, 'result_end_offset', None)),
                "language_code": result.language_code if hasattr(result, 'language_code') else None,
                # Server-provided sequencing metadata
                "restart_epoch": self.restart_counter,
                "server_time_ms": int(time.time() * 1000),
            }
            
            # Increment global result sequence and attach
            self.result_seq += 1
            result_dict["result_seq"] = self.result_seq

            if result.is_final:
                self.total_transcripts += 1
                # Increment utterance sequence only on finals
                self.utterance_seq += 1
                result_dict["utterance_seq"] = self.utterance_seq
                result_dict["confidence"] = alternative.confidence if hasattr(alternative, 'confidence') else None
                # Track last final and accumulate per-epoch finals for logging
                try:
                    self._last_final_text = transcript
                    if self.restart_counter not in self._epoch_finals:
                        self._epoch_finals[self.restart_counter] = []
                    self._epoch_finals[self.restart_counter].append(transcript)
                except Exception:
                    pass
                
                # Add word-level info if enabled
                if self.config.enable_word_time_offsets and hasattr(alternative, 'words'):
                    result_dict["words"] = [
                        {
                            "word": getattr(w, 'word', None),
                            "start_offset": _duration_to_ms(getattr(w, 'start_offset', None)),
                            "end_offset": _duration_to_ms(getattr(w, 'end_offset', None)),
                            "confidence": getattr(w, 'confidence', None),
                        }
                        for w in alternative.words
                    ]
                
                logger.info(
                    f"[GOOGLE_STT_V2][FINAL] sid={self.sid}, "
                    f"text='{transcript[:50]}...', "
                    f"lang={result_dict.get('language_code', 'unknown')}, "
                    f"epoch={result_dict.get('restart_epoch')}, "
                    f"result_seq={result_dict.get('result_seq')}, "
                    f"utterance_seq={result_dict.get('utterance_seq')}"
                )
                # Signal any waiters that at least one final has been emitted
                try:
                    if not self._final_emitted_event.is_set():
                        self._final_emitted_event.set()
                except Exception:
                    pass
            else:
                logger.debug(
                    f"[GOOGLE_STT_V2][INTERIM] sid={self.sid}, "
                    f"text='{transcript[:30]}...', "
                    f"stability={result_dict.get('stability', 0):.2f}, "
                    f"epoch={result_dict.get('restart_epoch')}, "
                    f"result_seq={result_dict.get('result_seq')}"
                )
            
            # Emit transcript
            if self.on_transcript:
                await self.on_transcript(transcript, result.is_final, result_dict)
    
    async def _restart_stream(self):
        """Restart the stream"""
        # Notify clients that we are about to restart; next epoch is restart_counter + 1
        try:
            if self.on_speech_event:
                # Include snapshot of current epoch so client can persist final text before restarting
                curr_epoch = self.restart_counter
                finals_list = self._epoch_finals.get(curr_epoch, []) if hasattr(self, '_epoch_finals') else []
                joined = " | ".join(finals_list)
                payload = {
                    "next_restart_epoch": curr_epoch + 1,
                    "current_restart_epoch": curr_epoch,
                    "server_time_ms": int(time.time() * 1000),
                    "last_final_text": getattr(self, "_last_final_text", ""),
                    "full_epoch_finals": joined,
                }
                await self.on_speech_event(
                    "STREAM_RESTARTING",
                    payload,
                )
                logger.info(
                    f"[GOOGLE_STT_V2][RESTART] Emitted STREAM_RESTARTING sid={self.sid} "
                    f"current_epoch={payload['current_restart_epoch']} next_epoch={payload['next_restart_epoch']}"
                )
                # Log the full last-final text and all finals in the current epoch
                try:
                    logger.info(
                        f"[GOOGLE_STT_V2][RESTART][SNAPSHOT] sid={self.sid} epoch={curr_epoch} "
                        f"last_final='{self._last_final_text}' finals_count={len(finals_list)}"
                    )
                    if joined:
                        logger.info(
                            f"[GOOGLE_STT_V2][RESTART][EPOCH_FINALS] sid={self.sid} epoch={curr_epoch} finals='{joined}'"
                        )
                except Exception:
                    pass
        except Exception:
            pass

        self.restart_counter += 1
        
        logger.info(
            f"[GOOGLE_STT_V2][RESTART] Restarting stream #{self.restart_counter} "
            f"for sid={self.sid}"
        )
        
        # Reset timing for new stream
        self.stream_start_time = time.time()
        self._last_response_ts = None
        self._last_audio_ts = None
        # Reset result sequencing for the new epoch
        self.result_seq = 0
        self.utterance_seq = 0
        # Initialize list for the new epoch
        try:
            if self.restart_counter not in self._epoch_finals:
                self._epoch_finals[self.restart_counter] = []
        except Exception:
            pass
        
        # Cancel current stream
        if self._stream_task:
            self._stream_task.cancel()
            try:
                await self._stream_task
            except asyncio.CancelledError:
                pass
        
        # Clear audio queue to prevent stale audio from previous stream
        await self._clear_audio_queue()
        
        # Restart
        self._stream_task = asyncio.create_task(self._run_stream())
    
    async def _clear_audio_queue(self):
        """Clear the audio queue to prevent stale audio from being processed"""
        cleared_count = 0
        try:
            while not self._audio_queue.empty():
                try:
                    await asyncio.wait_for(self._audio_queue.get(), timeout=0.001)
                    cleared_count += 1
                except asyncio.TimeoutError:
                    break
            if cleared_count > 0:
                logger.info(f"[GOOGLE_STT_V2][CLEAR_QUEUE] Cleared {cleared_count} stale audio chunks for sid={self.sid}")
        except Exception as e:
            logger.debug(f"[GOOGLE_STT_V2][CLEAR_QUEUE] Error clearing queue for sid={self.sid}: "
                       f"{type(e).__name__}: {e}")
    
    async def _restart_timer(self):
        """Periodic restart to avoid timeout"""
        while not self._stop_event.is_set():
            await asyncio.sleep(self.config.streaming_limit_seconds)
            
            if not self._stop_event.is_set():
                logger.info(
                    f"[GOOGLE_STT_V2][TIMER] Periodic restart for sid={self.sid}"
                )
                await self._restart_stream()


# Health check for V2
async def check_google_stt_v2_status(credentials_path: str = '.envdir/tenx-saas-3ff848c57fc5.json') -> Dict[str, Any]:
    """
    Check if Google Speech-to-Text V2 API is accessible.
    
    Returns:
        dict: Status information
    """
    try:
        if not os.path.exists(credentials_path):
            return {"error": f"Credentials file not found: {credentials_path}"}
        
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
        
        # Get project ID
        with open(credentials_path, 'r', encoding='utf-8') as f:
            service_account_data = json.load(f)
        
        project_id = service_account_data.get('project_id')
        if not project_id:
            return {"error": "No project_id in credentials"}
        
        # Try to create client
        try:
            client = SpeechAsyncClient()
            
            return {
                "project_id": project_id,
                "api_version": "v2",
                "client_initialized": True,
                "status": "ready",
            }
        except Exception as client_error:
            return {
                "project_id": project_id,
                "api_version": "v2",
                "client_initialized": False,
                "error": str(client_error),
            }
            
    except (IOError, ValueError, KeyError) as e:
        return {"error": str(e)}

