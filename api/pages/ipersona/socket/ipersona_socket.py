import asyncio, os, json
import re
import time
import io, wave
from openai import OpenAI
import assemblyai as aai
from typing import Dict, Any

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
try:
    from google.cloud import speech_v1 as speech
except Exception:
    speech = None
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


aai.settings.api_key = config.assemblyai.api_key


OPENAI_API_KEY = config.openai.api_key
client = OpenAI(api_key=OPENAI_API_KEY)

# Improved transcriber management - track per session
transcribers: Dict[str, Any] = {}
whisper_buffers: Dict[str, bytearray] = {}
google_streams: Dict[str, Any] = {}
gemini_streams: Dict[str, Any] = {}
fw_buffers: Dict[str, bytearray] = {}
fw_model: Any = None
gemini_last_ts: Dict[str, float] = {}

 

def _pcm16_mono_16k_to_wav_bytes(pcm_bytes: bytes) -> bytes:
    # Backward compatibility wrapper
    return pcm16_mono_16k_to_wav_bytes(pcm_bytes)

def _is_silent_pcm16(pcm_bytes: bytes, rms_threshold: int = WHISPER_RMS_THRESHOLD) -> bool:
    # Backward compatibility wrapper
    return is_silent_pcm16(pcm_bytes, rms_threshold)

# -------------------------- Google Cloud STT Streaming -------------------------- #
class GoogleStreamingSession:
    def __init__(self, sid: str, language_code: str = None, sample_rate_hz: int = 16000, enable_interim_results: bool = True):
        if speech is None:
            raise RuntimeError("google-cloud-speech is not installed")
        self.sid = sid
        self.language_code = language_code or os.getenv("GOOGLE_STT_LANGUAGE", "en-US")
        self.sample_rate_hz = sample_rate_hz
        self.enable_interim_results = enable_interim_results
        self.client = speech.SpeechClient()
        self._queue: asyncio.Queue = asyncio.Queue()
        self._stop = asyncio.Event()
        self._task: asyncio.Task | None = None

    async def start(self):
        if self._task is None:
            self._task = asyncio.create_task(self._run())

    async def stop(self):
        self._stop.set()
        # Put sentinel to unblock generator
        await self._queue.put(None)
        if self._task:
            try:
                await self._task
            except Exception:
                pass

    async def add_audio(self, audio_bytes: bytes):
        await self._queue.put(audio_bytes)

    async def _requests_generator(self):
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
        yield speech.StreamingRecognizeRequest(streaming_config=streaming_config)
        while not self._stop.is_set():
            chunk = await self._queue.get()
            if chunk is None:
                break
            if chunk:
                yield speech.StreamingRecognizeRequest(audio_content=chunk)

    async def _run(self):
        loop = asyncio.get_event_loop()
        try:
            responses = self.client.streaming_recognize(requests=self._requests_generator())
            async for response in responses:  # type: ignore
                for result in response.results:
                    if not result.alternatives:
                        continue
                    transcript = result.alternatives[0].transcript
                    if not transcript:
                        continue
                    # Emit interim/final similar to Assembly behavior
                    if result.is_final:
                        logger.info(f"[GOOGLE][FINAL] sid={self.sid} text='{transcript}'")
                        asyncio.run_coroutine_threadsafe(
                            sio.emit("audio transcribe google", transcript, room=self.sid),
                            loop,
                        )
                    else:
                        logger.info(f"[GOOGLE][INTERIM] sid={self.sid} text='{transcript}'")
        except Exception as e:
            logger.error(f"[GOOGLE] streaming error sid={self.sid}: {e}")


@sio.on("audio transcribe google")
async def audio_transcribe_google(sid, data):
    """Realtime Google Cloud STT via gRPC; expects 16kHz mono PCM16 chunks. Send audioblob=None to stop."""
    audioblob = data.get('audioblob') if isinstance(data, dict) else None

    if audioblob is None:
        # stop and cleanup
        session: GoogleStreamingSession | None = google_streams.pop(sid, None)
        if session is not None:
            logger.info(f"[GOOGLE][STOP] sid={sid}")
            try:
                await session.stop()
            except Exception as e:
                logger.error(f"[GOOGLE] stop error sid={sid}: {e}")
        else:
            logger.info(f"[GOOGLE][STOP] no active session sid={sid}")
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
            logger.error("google-cloud-speech is not installed. Please add google-cloud-speech to requirements.txt")
            return
        logger.info(f"[GOOGLE][START] sid={sid} lang={os.getenv('GOOGLE_STT_LANGUAGE','en-US')}")
        session = GoogleStreamingSession(sid=sid)
        google_streams[sid] = session
        await session.start()

    session = google_streams[sid]
    try:
        await session.add_audio(audio_bytes)
    except Exception as e:
        logger.error(f"[GOOGLE] add_audio error sid={sid}: {e}")

# -------------------------- faster-whisper Local Batch STT -------------------------- #
def _get_fw_model() -> Any:
    global fw_model
    if fw_model is None:
        if WhisperModel is None:
            raise RuntimeError("faster-whisper is not installed")
        device = os.getenv("FW_DEVICE", "cpu")
        compute_type = os.getenv("FW_COMPUTE_TYPE", "int8")
        model_size = os.getenv("FW_MODEL", "base")
        fw_model = WhisperModel(model_size, device=device, compute_type=compute_type)
        logger.info(f"[FW][INIT] model={model_size} device={device} compute_type={compute_type}")
    return fw_model

@sio.on("audio transcribe fw")
async def audio_transcribe_fw(sid, data):
    """Local faster-whisper batch on buffered chunks. Send audioblob=None to flush and stop."""
    audioblob = data.get('audioblob') if isinstance(data, dict) else None

    if sid not in fw_buffers:
        fw_buffers[sid] = bytearray()

    if audioblob is None:
        buf = fw_buffers.get(sid, bytearray())
        logger.info(f"[FW][STOP] sid={sid} final_flush_bytes={len(buf)}")
        if len(buf) > 0:
            try:
                model = _get_fw_model()
                # Write temp wav and transcribe
                wav_bytes = _pcm16_mono_16k_to_wav_bytes(bytes(buf))
                # faster-whisper expects file path or bytes via numpy array; use temp file for simplicity
                with io.BytesIO(wav_bytes) as b:
                    # Save to temp path to support large chunks
                    tmp_path = os.path.join("/tmp", f"fw_{sid}.wav")
                    with open(tmp_path, "wb") as f:
                        f.write(b.getvalue())
                segments, info = model.transcribe(tmp_path, language="en", beam_size=1)
                text_parts = [seg.text for seg in segments]
                text = (" ".join(text_parts)).strip()
                logger.info(f"[FW][STOP][RECV] sid={sid} lang={getattr(info,'language','?')} text_len={len(text)}")
                if text:
                    await sio.emit("audio transcribe fw", text, room=sid)
            except Exception as e:
                logger.error(f"[FW] Final flush error: {e}")
        fw_buffers.pop(sid, None)
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

    if _is_silent_pcm16(audio_bytes):
        logger.info(f"[FW][SILENT] sid={sid} chunk_bytes={len(audio_bytes)} skipped")
        return

    fw_buffers[sid].extend(audio_bytes)
    logger.info(f"[FW][APPEND] sid={sid} chunk_bytes={len(audio_bytes)} buffer_bytes={len(fw_buffers[sid])}")

    target = int(os.getenv("FW_TARGET_BYTES", "96000"))
    if len(fw_buffers[sid]) >= target:
        buf = fw_buffers[sid]
        fw_buffers[sid] = bytearray()
        try:
            model = _get_fw_model()
            wav_bytes = _pcm16_mono_16k_to_wav_bytes(bytes(buf))
            tmp_path = os.path.join("/tmp", f"fw_{sid}.wav")
            with open(tmp_path, "wb") as f:
                f.write(wav_bytes)
            segments, info = model.transcribe(tmp_path, language="en", beam_size=1)
            text_parts = [seg.text for seg in segments]
            text = (" ".join(text_parts)).strip()
            logger.info(f"[FW][RECV] sid={sid} text_len={len(text)}")
            if text:
                await sio.emit("audio transcribe fw", text, room=sid)
        except Exception as e:
            logger.error(f"[FW] Chunk transcription error: {e}")

# -------------------------- Gemini Live API Streaming -------------------------- #
class GeminiLiveSession:
    def __init__(self, sid: str, model: str | None = None):
        if google_genai is None or genai_types is None:
            raise RuntimeError("google-genai is not installed")
        self.sid = sid
        self.model = model or os.getenv("GEMINI_LIVE_MODEL", "gemini-live-2.5-flash-preview")
        # Use API key from central config
        self.client = google_genai.Client(api_key=config.gemini.api_key)
        self.session = None
        self._queue: asyncio.Queue = asyncio.Queue()
        self._stop = asyncio.Event()
        self._task: asyncio.Task | None = None

    async def start(self):
        if self._task is None:
            self._task = asyncio.create_task(self._run())

    async def stop(self):
        self._stop.set()
        await self._queue.put(None)
        if self._task:
            try:
                await self._task
            except Exception:
                pass
        try:
            if self.session is not None:
                await self.session.aclose()
        except Exception:
            pass

    async def add_audio(self, audio_bytes: bytes):
        await self._queue.put(audio_bytes)

    def _looks_english(self, text: str) -> bool:
        letters = re.findall(r"[A-Za-z]", text)
        if not text:
            return False
        ratio = (len(letters) / max(1, len(text)))
        return ratio >= float(os.getenv("GEMINI_ENGLISH_RATIO", "0.8"))

    async def _run(self):
        loop = asyncio.get_event_loop()
        config = {
            "response_modalities": ["TEXT"],
            "system_instruction": (
                "You are a transcription engine. Transcribe VERBATIM in English only. "
                "Do NOT translate or answer. If audio is not English, return nothing. "
                "Return plain text only, no prefixes or extra words."
            ),
        }
        response_interval = float(os.getenv("GEMINI_RESPONSE_INTERVAL_SEC", "1.0"))
        keepalive_interval = float(os.getenv("GEMINI_KEEPALIVE_SEC", "5.0"))
        silence_trigger_ms = int(os.getenv("GEMINI_SILENCE_TRIGGER_MS", "400"))
        gemini_rms_th = int(os.getenv("GEMINI_RMS_THRESHOLD", "600"))
        silence_bytes = b"\x00" * 3200  # ~100ms of silence @16kHz PCM16
        watchdog_sec = float(os.getenv("GEMINI_WATCHDOG_SEC", "3.0"))
        restart_silence_ms = int(os.getenv("GEMINI_RESTART_SILENCE_MS", "1200"))

        while not self._stop.is_set():
            last_response_ts = time.time()
            last_keepalive_ts = time.time()
            last_speech_ts = time.time()
            in_flight_response = False
            try:
                async with self.client.aio.live.connect(model=self.model, config=config) as session:
                    self.session = session
                    missing_response_api_logged = False
                    last_text_ts = time.time()
                    last_chunk_ts = time.time()

                    async def receiver():
                        nonlocal last_text_ts
                        try:
                            async for message in session.receive():
                                try:
                                    server_content = getattr(message, "server_content", None)
                                    if server_content and getattr(server_content, "model_turn", None):
                                        parts = getattr(server_content.model_turn, "parts", []) or []
                                        text_chunks = []
                                        for part in parts:
                                            text_val = getattr(part, "text", None)
                                            if text_val:
                                                text_chunks.append(text_val)
                                        if text_chunks:
                                            text = "".join(text_chunks).strip()
                                            if text:
                                                if not self._looks_english(text):
                                                    logger.info(f"[GEMINI][TEXT][SKIP_NON_EN] sid={self.sid} sample='{text[:20]}'")
                                                    continue
                                                logger.info(f"[GEMINI][TEXT] sid={self.sid} len={len(text)}")
                                                logger.info(f"[SOCKET EMIT] Sending final transcript to sid={self.sid}: '{text}'")
                                                # mark last text time for watchdog
                                                last_text_ts = time.time()
                                                asyncio.run_coroutine_threadsafe(
                                                    sio.emit("audio transcribe gemini", text, room=self.sid),
                                                    loop,
                                                )
                                except Exception as parse_err:
                                    logger.error(f"[GEMINI] parse error sid={self.sid}: {parse_err}")
                        except Exception as recv_err:
                            logger.error(f"[GEMINI] receive error sid={self.sid}: {recv_err}")

                    recv_task = asyncio.create_task(receiver())

                    while not self._stop.is_set():
                        now = time.time()
                        # Send keepalive occasionally
                        if now - last_keepalive_ts >= keepalive_interval:
                            try:
                                await session.send_realtime_input(
                                    audio=genai_types.Blob(
                                        data=silence_bytes,
                                        mime_type="audio/pcm;rate=16000",
                                    )
                                )
                                logger.info(f"[GEMINI][KEEPALIVE] sid={self.sid} 100ms silence sent")
                            except Exception as send_err:
                                logger.error(f"[GEMINI] keepalive error sid={self.sid}: {send_err}")
                            last_keepalive_ts = now

                        # Drain at least one queued chunk if available
                        try:
                            chunk = await asyncio.wait_for(self._queue.get(), timeout=0.2)
                        except asyncio.TimeoutError:
                            chunk = None

                        if chunk is not None:
                            if chunk:
                                # Log inter-arrival and size
                                prev = gemini_last_ts.get(self.sid, now)
                                gemini_last_ts[self.sid] = now
                                dt_ms = int((now - prev) * 1000)
                                logger.info(f"[GEMINI][CHUNK] sid={self.sid} bytes={len(chunk)} dt_ms={dt_ms}")
                                last_chunk_ts = now
                                # Update last_speech_ts based on RMS silence gate
                                try:
                                    if not is_silent_pcm16(chunk, gemini_rms_th):
                                        last_speech_ts = now
                                        logger.info(f"[GEMINI][VAD] sid={self.sid} speech_detected rms_th={gemini_rms_th}")
                                    else:
                                        logger.info(f"[GEMINI][VAD] sid={self.sid} silence rms_th={gemini_rms_th}")
                                except Exception as vad_err:
                                    logger.error(f"[GEMINI][VAD] error sid={self.sid}: {vad_err}")
                                try:
                                    await session.send_realtime_input(
                                        audio=genai_types.Blob(
                                            data=chunk,
                                            mime_type="audio/pcm;rate=16000",
                                        )
                                    )
                                except Exception as send_err:
                                    logger.error(f"[GEMINI] send error sid={self.sid}: {send_err}")
                            elif chunk is None:
                                break

                        # Trigger a response turn either on cadence or after brief silence, ensure single in-flight
                        silence_ms = int((now - last_speech_ts) * 1000)
                        should_request = (now - last_response_ts >= response_interval) or (silence_ms >= silence_trigger_ms)
                        if should_request and not in_flight_response:
                            try:
                                # Commit buffered audio (if API is available), then request a response
                                input_buf = getattr(session, "input_audio_buffer", None)
                                if input_buf and hasattr(input_buf, "commit"):
                                    try:
                                        await input_buf.commit()
                                        logger.info(f"[GEMINI][COMMIT] sid={self.sid} input_audio_buffer.commit sent")
                                    except Exception as c_err:
                                        logger.error(f"[GEMINI] commit error sid={self.sid}: {c_err}")
                                # Prefer explicit response.create if available in SDK
                                response_api = getattr(session, "response", None)
                                if response_api and hasattr(response_api, "create"):
                                    in_flight_response = True
                                    logger.info(f"[GEMINI][REQUEST] sid={self.sid} reason={'cadence' if (now - last_response_ts >= response_interval) else 'silence'} silence_ms={silence_ms} response.create issued")
                                    await response_api.create()
                                    in_flight_response = False
                                else:
                                    if not missing_response_api_logged:
                                        logger.error(f"[GEMINI] response API missing create() sid={self.sid} — relying on auto-turns after commit")
                                        missing_response_api_logged = True
                            except Exception as req_err:
                                logger.error(f"[GEMINI] response request error sid={self.sid}: {req_err}")
                                in_flight_response = False
                            last_response_ts = now

                        # Watchdog: if we keep receiving chunks but no text for too long, recycle session
                        no_text_for = now - last_text_ts
                        since_last_chunk = now - last_chunk_ts
                        if no_text_for >= watchdog_sec and since_last_chunk < watchdog_sec * 2:
                            logger.info(f"[GEMINI][RESTART] sid={self.sid} reason=watchdog no_text_for={no_text_for:.2f}s")
                            break

                        # Restart on long silence between speech segments
                        if silence_ms >= restart_silence_ms:
                            logger.info(f"[GEMINI][RESTART] sid={self.sid} reason=silence silence_ms={silence_ms}")
                            break

                    try:
                        await recv_task
                    except Exception:
                        pass
            except Exception as e:
                logger.error(f"[GEMINI] session error sid={self.sid}: {e}")
                if self._stop.is_set():
                    break
                # Auto-reconnect after brief delay
                logger.info(f"[GEMINI][RECONNECT] sid={self.sid} retrying in 0.5s")
                await asyncio.sleep(0.5)


@sio.on("audio transcribe gemini")
async def audio_transcribe_gemini(sid, data):
    """Realtime Gemini Live API; expects 16kHz mono PCM16 chunks. Send audioblob=None to stop."""
    audioblob = data.get('audioblob') if isinstance(data, dict) else None

    if audioblob is None:
        session: GeminiLiveSession | None = gemini_streams.pop(sid, None)
        if session is not None:
            logger.info(f"[GEMINI][STOP] sid={sid}")
            try:
                await session.stop()
            except Exception as e:
                logger.error(f"[GEMINI] stop error sid={sid}: {e}")
        else:
            logger.info(f"[GEMINI][STOP] no active session sid={sid}")
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

    if sid not in gemini_streams:
        if google_genai is None:
            logger.error("google-genai is not installed. Please add google-genai to requirements.txt and set GOOGLE_API_KEY env var")
            return
        logger.info(f"[GEMINI][START] sid={sid} model={os.getenv('GEMINI_LIVE_MODEL','gemini-live-2.5-flash-preview')}")
        session = GeminiLiveSession(sid=sid)
        gemini_streams[sid] = session
        await session.start()

    session = gemini_streams[sid]
    try:
        await session.add_audio(audio_bytes)
    except Exception as e:
        logger.error(f"[GEMINI] add_audio error sid={sid}: {e}")

@sio.event
async def connect(sid, environ):
    print(f"####### Socket Connected with SID: {sid} #######")
    # Join the client to a room with its own SID for SID targeting
    await sio.enter_room(sid, sid)
    print(f"####### Client {sid} joined room {sid} #######")
    await sio.emit("initial connect", {"message": "socket connection started"}, room=sid)
    
    query_string = environ.get('QUERY_STRING', '')
    print(f"Query string: {query_string}")
    
    asgi_scope = environ.get('asgi.scope', {})
    scope_query = asgi_scope.get('query_string', b'').decode('utf-8')
    print(f"ASGI scope query string: {scope_query}")
    
    parsed_query = urllib.parse.parse_qs(query_string)
    run_stage = parsed_query.get('run_stage', [''])[0]
    print(f"Parsed run_stage: {run_stage}")
        
    # Also try the session method
    try:
        await sio.save_session(sid, {'run_stage': run_stage})
        session = await sio.get_session(sid)
        print(f"Session after save: {session}")
    except Exception as e:
        print(f"Session error: {e}")

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
        await sio.emit("processing_confirmed", {
            "job_id": job_id,
            "user_id": user_id,
            "room": room,
            "message": f"Subscribed to processing updates for job {job_id}, user {user_id}"
        }, room=sid)
        print(f"📡 [DEBUG] User {user_id} subscribed to room {room} for job {job_id}")
    else:
        await sio.emit("processing_error", {
            "error": f"Missing job_id or user_id for subscription. Got job_id={job_id}, user_id={user_id}"
        }, room=sid)
    
@sio.on("initial connect")
async def connect(sid):
    print("####### Socket Connected #######")
    await sio.emit(
        "initial connect",
        {"message": "socket connection started"}, 
        room=sid)
    
@sio.on("disconnect")
async def disconnect(sid):
    logger.info(f"Client disconnected with SID: {sid}")
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
# Improved assembly streaming with proper session management
@sio.on("audio transcribe")
async def audio_endpoint(sid, data):
    """Handle audio transcribe event with improved session management."""
    loop = asyncio.get_event_loop()
    audioblob = data.get('audioblob')

    # Log incoming audio data
    if audioblob:
        blob_length = len(audioblob) if hasattr(audioblob, '__len__') else 'unknown'
        logger.info(f"[AUDIO RECEIVED] sid={sid}, audioblob length={blob_length}, type={type(audioblob)}")
    else:
        logger.info(f"[AUDIO RECEIVED] sid={sid}, audioblob=None (stop signal)")

    # Treat None audioblob as an explicit stop signal from client
    if audioblob is None:
        logger.info(f"Stop requested by client (sid={sid}). Closing session if active...")
        existing = transcribers.pop(sid, None)
        if existing is not None:
            try:
                if hasattr(existing, 'close') and callable(getattr(existing, 'close')):
                    existing.close()
                elif hasattr(existing, 'disconnect') and callable(getattr(existing, 'disconnect')):
                    existing.disconnect()
                elif hasattr(existing, 'terminate') and callable(getattr(existing, 'terminate')):
                    existing.terminate()
                logger.info(f"Session closed cleanly after stop (sid={sid})")
            except Exception as e:
                logger.warn(f"Error while closing session on stop (sid={sid}): {e}")
        else:
            logger.info(f"No active session to close on stop (sid={sid})")
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
    logger.info(f"[AUDIO NORMALIZED] sid={sid}, normalized_length={normalized_length}")

    def on_open(session_opened: aai.RealtimeSessionOpened):
        logger.info(f"Session opened: {session_opened.session_id} (sid={sid})")

    def on_data(transcript: aai.RealtimeTranscript):
        try:
            if not transcript.text:
                return
            # Preserve legacy behavior: emit bare string only on final
            if isinstance(transcript, aai.RealtimeFinalTranscript):
                logger.info(f"Final transcript (sid={sid}): {transcript.text}")
                logger.info(f"[SOCKET EMIT] Sending final transcript to sid={sid}: '{transcript.text}'")
                asyncio.run_coroutine_threadsafe(
                    sio.emit("audio transcribe", transcript.text, room=sid),
                    loop
                )
                logger.info(f"[SOCKET EMIT] Final transcript sent successfully to sid={sid}")
                
            else:
                # Interim log (lighter)
                logger.info(f"Interim transcript (sid={sid}): {transcript.text}")
        except Exception as emit_err:
            logger.error(f"Emit error: {emit_err}")

    def on_error(error: aai.RealtimeError):
        logger.error(f"An error occurred: {error}")

    def on_close():
        logger.info(f"Closing Session (sid={sid})")
        transcribers.pop(sid, None)

        asyncio.run_coroutine_threadsafe(
            sio.emit("transcription_complete", {
                "status": "completed",
                "message": "Audio transcription finished"
            }, room=sid), loop
        )
        logger.info(f"[SOCKET EMIT] transcription_complete sent successfully to sid={sid}")

    # Create a session-scoped transcriber if missing
    if sid not in transcribers or transcribers.get(sid) is None:
        logger.info(f"Creating new transcriber for sid={sid}")
        transcribers[sid] = aai.RealtimeTranscriber(
            sample_rate=16000,
            on_data=on_data,
            on_error=on_error,
            on_open=on_open,
            on_close=on_close
        )
        transcribers[sid].connect()
        logger.info(f"Transcriber connected for sid={sid}")

    # Stream audio chunk for this sid
    try:
        logger.info(f"[AUDIO STREAM] Streaming audio to transcriber for sid={sid}, length={normalized_length}")
        transcribers[sid].stream(audio_bytes)
        logger.info(f"[AUDIO STREAM] Audio streamed successfully for sid={sid}")
    except Exception as e:
        logger.error(f"Error in audio streaming for sid={sid}: {str(e)}")

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
                    await sio.emit("audio transcribe whisper", text, room=sid)
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
                await sio.emit("audio transcribe whisper", text.strip(), room=sid)
        except Exception as e:
            logger.error(f"[WHISPER] Chunk transcription error: {e}")

# executor = ThreadPoolExecutor(max_workers=105)  

async def synthesize_text(text):
    print("Received text for synthesis:", text)
    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="nova",
            input=text
        )

        audio_data = response.read()

        if len(audio_data) == 0 or len(audio_data) < 500:  
            return {"error": "Received insufficient audio data."}

        return audio_data  

    except Exception as e:
        return {"error": str(e)}

# method to save audio chat to database
# TODO: integrate with audio chat function
@sio.on("audio chat sentence")
async def audio_end_point(sid, data):
    session = await sio.get_session(sid)        
        
    run_stage = session.get('run_stage', None)  

    if run_stage is None:
        print(f"Run stage not found in session for sid: {sid}")
    else:
        print(f"Run stage retrieved: {run_stage}")
        
    logger.info("audio socket response", data["response"], data['user_session']['id'])
    try:
        chat_count = 1  
        sessionId = data['user_session']['id']
        realtime_evaluation = "null"
        accumulated_message = ""
        full_accumulated_message = ""
        template_id = data.get('template_id', "null")
        challenge_id = data.get('challenge_id', "null")
        total_questions = 0
        template = data.get('template', False)

         # Get session ID with error handling
        try:
            if isinstance(data.get('user_session'), dict) and 'id' in data['user_session']:
                sessionId = data['user_session']['id']
                logger.info(f"Processing interview chat for session ID: {sessionId}")
            else:
                error_msg = "Invalid user_session format: missing ID"
                logger.error(error_msg)
                logger.info(f"[SOCKET EMIT] Sending error to sid={sid}: {error_msg}")
                await sio.emit("error", {"error": error_msg}, room=sid)
                logger.info(f"[SOCKET EMIT] Error sent successfully to sid={sid}")
                return
        except Exception as session_id_error:
            logger.error(f"Error extracting session ID: {str(session_id_error)}")
            logger.info(f"[SOCKET EMIT] Sending error to sid={sid}: Failed to identify session")
            await sio.emit("error", {"error": "Failed to identify session"}, room=sid)
            logger.info(f"[SOCKET EMIT] Error sent successfully to sid={sid}")
            return
        
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
                    strapi.step1_insert_message(
                        run_stage, 
                        data, 
                        sessionId)
                except Exception as insert_error:
                    logger.error(f"Failed to insert user message: {str(insert_error)}")
                    # Continue despite insertion failure
            else:
                logger.info("No user response to insert")
        except Exception as response_error:
            logger.error(f"Error processing user response: {str(response_error)}")

                 
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
                logger.info(f"[SOCKET EMIT] Sending error to sid={sid}: Failed to generate next question")
                await sio.emit("error", {"error": "Failed to generate next question"}, room=sid)
                logger.info(f"[SOCKET EMIT] Error sent successfully to sid={sid}")
                return
            
        except Exception as generate_error:
            logger.error(f"Error generating interview question: {str(generate_error)}")
            logger.info(f"[SOCKET EMIT] Sending error to sid={sid}: Question generation failed")
            await sio.emit("error", {"error": f"Question generation failed: {str(generate_error)}"}, room=sid)
            logger.info(f"[SOCKET EMIT] Error sent successfully to sid={sid}")
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
            
            logger.info(f"[SOCKET EMIT] Sending initial audio chat sentence to sid={sid}: {message}")
            await sio.emit("audio chat sentence", message, room=sid)  
            logger.info(f"[SOCKET EMIT] Initial audio chat sentence sent successfully to sid={sid}")
            
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
                                
                        logger.info(f"[SOCKET EMIT] Sending chunk response to sid={sid}: '{complete_sentence}'")
                        await sio.emit("audio chat sentence", message, room=sid)
                        logger.info(f"[SOCKET EMIT] Chunk response sent successfully to sid={sid}")
                        tasks.append(synthesize_text(complete_sentence))
                    
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
                        accumulated_message,
                        section,
                        sessionId,
                        run_stage,
                        sio,
                        sid
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
                    logger.info(f"[SOCKET EMIT] Sending time limit to sid={sid}: {timelimit.get('time_limit', 'null')}")
                    await sio.emit("time_limit", message, room=sid)
                    logger.info(f"[SOCKET EMIT] Time limit sent successfully to sid={sid}")

            except Exception as timelimit_error:
                logger.error(f"Failed to calculate or emit time limit: {str(timelimit_error)}")
                timelimit = {"time_limit": "null"}
                # Continue despite time limit failure

               
            audio_chunks = await asyncio.gather(*tasks)
            
            for i, audio_data in enumerate(audio_chunks):
                if isinstance(audio_data, dict) and 'error' in audio_data:
                    print(f"Error: {audio_data['error']}")
                    continue
                
                # Log blob length instead of full content
                blob_length = len(audio_data) if audio_data else 0
                logger.info(f"[SOCKET EMIT] Sending audio_base64_chunks to sid={sid}: chunk_{i+1}, blob_length={blob_length} bytes")
                
                message = [{
                        "content": {
                            "audio_data": audio_data,
                        }
                    }]                    
                await sio.emit("audio_base64_chunks", message, room=sid) 
                logger.info(f"[SOCKET EMIT] audio_base64_chunks sent successfully to sid={sid}: chunk_{i+1}")
                
                logger.info(f"[SOCKET EMIT] Sending audio-single-chunk to sid={sid}: chunk_{i+1}, blob_length={blob_length} bytes")
                await sio.emit("audio-single-chunk", audio_data, room=sid)
                logger.info(f"[SOCKET EMIT] audio-single-chunk sent successfully to sid={sid}: chunk_{i+1}")
                
            logger.info(f"[SOCKET EMIT] Sending audio-single-text-chunk-done to sid={sid}")
            await sio.emit("audio-single-text-chunk-done", room=sid)
            logger.info(f"[SOCKET EMIT] audio-single-text-chunk-done sent successfully to sid={sid}")

            # Perform real-time response evaluation if applicable
            if data['response'] is not [None, ""]:
                type = 'job_interview_config'
                realtime_evaluation_response_json = util.realtime_response_evaluation(
                                run_stage, 
                                data, 
                                sessionId, 
                                type)
                realtime_evaluation = "null" if realtime_evaluation_response_json is None else realtime_evaluation_response_json.get("realtime_evaluation")
                logger.success(f"Realtime evaluation is: {realtime_evaluation}")
            
                message = [{
                    "content": {
                        "realtime_evaluation": realtime_evaluation,
                        "full_response": accumulated_message
                    }
                }]
                status = "start"
                await sio.emit("realtime_status", status, room=sid)  
                logger.info(f"[SOCKET EMIT] Sending audio_realtime to sid={sid}: {realtime_evaluation}")
                await sio.emit("audio_realtime", message, room=sid)  
                logger.info(f"[SOCKET EMIT] audio_realtime sent successfully to sid={sid}")
                status = "end"
                await sio.emit("realtime_status", status, room=sid)  
             
       
        # Insert the message or conclude the interview if the chat count exceeds the limit
        if chat_count < total_questions + 1:
            print("Full MESSAGE -=====")
            print(full_accumulated_message)
            print("Full MESSAGE -=====")
            final = 'false'
            strapi.step2_insert_message(
                run_stage, 
                data, 
                timelimit, 
                full_accumulated_message, 
                realtime_evaluation, 
                final,
                sessionId)
        else:
            message = 'interview over'
            logger.info(f"[SOCKET EMIT] Sending interview done to sid={sid}: {message}")
            await sio.emit("interview done", message, room=sid)
            logger.info(f"[SOCKET EMIT] interview done sent successfully to sid={sid}")

            final = 'true'
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
                    logger.info(f"[SOCKET EMIT] Sending last_audio_realtime_evaluation to sid={sid}")
                    await sio.emit("last_audio_realtime_evaluation", message, room=sid)   
                    logger.info(f"[SOCKET EMIT] last_audio_realtime_evaluation sent successfully to sid={sid}")

                except Exception as final_emit_error:
                            logger.error(f"Failed to emit final evaluation: {str(final_emit_error)}")
            # strapi.step3_insert_message(data, realtime_evaluation, final)
   
    except Exception as e:
        logger.error(f'Error: {str(e)}')  
        

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
            await sio.emit("error", {"error": error_msg}, room=sid)
            return
            
        if 'user_session' not in data:
            error_msg = "Missing required field: user_session"
            logger.error(error_msg)
            await sio.emit("error", {"error": error_msg}, room=sid)
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
                run_stage = 'democms'  # Default to production if not specified
            else:
                logger.info(f"Run stage retrieved: {run_stage}")
        except Exception as stage_error:
            logger.error(f"Error retrieving run stage: {str(stage_error)}")
            run_stage = 'democms'  # Default to production if error occurs

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
                print("Template flag is set, processing template-based interview")
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
                    strapi.step1_insert_message(
                        run_stage, 
                        data, 
                        sessionId)
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
                    logger.info(f"[SOCKET EMIT] Sending initial interview chat to sid={sid}: {message}")
                    await sio.emit("interview chat", message, room=sid)
                    logger.info(f"[SOCKET EMIT] Initial interview chat sent successfully to sid={sid}")

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
                            logger.info(f"[SOCKET EMIT] Sending interview chat chunk to sid={sid}: chunk_{i+1}, content='{chunk}'")
                            await sio.emit("interview chat", message, room=sid)
                            logger.info(f"[SOCKET EMIT] Interview chat chunk sent successfully to sid={sid}: chunk_{i+1}")
                            
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
                            sid
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
                        logger.info(f"[SOCKET EMIT] Sending time limit to sid={sid}: {timelimit.get('time_limit', 'null')}")
                        await sio.emit("time_limit", message, room=sid)
                        logger.info(f"[SOCKET EMIT] Time limit sent successfully to sid={sid}")

                except Exception as timelimit_error:
                    logger.error(f"Failed to calculate or emit time limit: {str(timelimit_error)}")
                    timelimit = {"time_limit": "null"}
                    # Continue despite time limit failure

                # Perform real-time response evaluation if applicable
                try:
                    if data.get('response') not in [None, "", []]:
                        try:
                            type = 'job_interview_config'
                            realtime_evaluation_response_json = util.realtime_response_evaluation(
                                run_stage, 
                                data, 
                                sessionId, 
                                type)
                            realtime_evaluation = "null" if realtime_evaluation_response_json is None else realtime_evaluation_response_json.get("realtime_evaluation")
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
                            await sio.emit("realtime_status", status, room=sid)  
                            logger.info(f"[SOCKET EMIT] Sending realtime evaluation to sid={sid}: {realtime_evaluation}")
                            await sio.emit("realtime", message, room=sid)
                            logger.info(f"[SOCKET EMIT] Realtime evaluation sent successfully to sid={sid}")
                            status = "finished"
                            await sio.emit("realtime_status", status, room=sid)  

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
                    strapi.step2_insert_message(
                        run_stage, 
                        data, 
                        timelimit, 
                        accumulated_message, 
                        realtime_evaluation, 
                        final,
                        sessionId)
                except Exception as insert_message_error:
                    logger.error(f"Failed to insert assistant message: {str(insert_message_error)}")

            else:
                # Handle interview conclusion
                try:
                    message = 'interview over'
                    logger.info(f"[SOCKET EMIT] Sending interview done to sid={sid}: {message}")
                    await sio.emit("interview done", message, room=sid)
                    logger.info(f"[SOCKET EMIT] Interview done sent successfully to sid={sid}")
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
                            logger.info(f"[SOCKET EMIT] Sending last_realtime_evaluation to sid={sid}")
                            await sio.emit("last_realtime_evaluation", message, room=sid)
                            logger.info(f"[SOCKET EMIT] last_realtime_evaluation sent successfully to sid={sid}")
                        
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

