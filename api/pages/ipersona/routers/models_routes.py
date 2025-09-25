import os
import tempfile
from typing import Optional
import asyncio
import base64
import subprocess
import httpx
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from api.utils.audio_utils import AudioUtils
from pydub import AudioSegment
from api import config
from api.utils.logger import LLPackerLogger
from google import genai as genai_mod
from google.genai import types as genai_types  # if available in your installed SDK
try:
    from faster_whisper import WhisperModel
except Exception:
    WhisperModel = None

logger = LLPackerLogger(__file__)

try:
    from google import genai as google_genai
    from google.genai import types as genai_types
except Exception:
    google_genai = None
    genai_types = None

router = APIRouter(prefix="/stt", tags=["STT"])



_fw_model = None

def _get_fw_model():
    global _fw_model
    if _fw_model is not None:
        return _fw_model
    if WhisperModel is None:
        raise HTTPException(status_code=500, detail="faster-whisper not installed")
    model_size = os.getenv("FW_MODEL", "base")
    device = os.getenv("FW_DEVICE", "cpu")
    compute_type = os.getenv("FW_COMPUTE_TYPE", "int8")
    logger.info(f"[FW][INIT] model={model_size} device={device} compute={compute_type}")
    _fw_model = WhisperModel(model_size, device=device, compute_type=compute_type)
    return _fw_model

@router.post("/whisper-upload")
async def stt_upload(file: UploadFile = File(...), language: Optional[str] = None):
    if file is None:
        raise HTTPException(status_code=400, detail="No file uploaded")
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file")
    try:
        model = _get_fw_model()
        # Normalize language input (e.g., "english" -> "en", "en-US" -> "en")
        lang_norm: Optional[str] = None
        if language:
            l = language.strip().lower()
            name_to_code = {
                "english": "en",
                "eng": "en",
                "arabic": "ar",
                "spanish": "es",
                "french": "fr",
                "german": "de",
                "italian": "it",
                "portuguese": "pt",
                "russian": "ru",
                "chinese": "zh",
                "japanese": "ja",
                "korean": "ko",
                "hindi": "hi",
            }
            # map en-us style to en
            if len(l) >= 2 and "-" in l:
                l = l.split("-")[0]
            lang_norm = name_to_code.get(l, l if len(l) == 2 else None)
        logger.info(f"[FW][UPLOAD] name={file.filename} bytes={len(contents)} lang={lang_norm or language or 'auto'}")
        # Run transcription from memory
        # faster-whisper expects a path or numpy/array; use temporary file for simplicity
        import tempfile
        with tempfile.NamedTemporaryFile(delete=True, suffix=f"_{file.filename}") as tmp:
            tmp.write(contents)
            tmp.flush()
            segments, info = model.transcribe(tmp.name, language=lang_norm)
        text_parts = []
        for seg in segments:
            text_parts.append(seg.text.strip())
        transcript = " ".join([t for t in text_parts if t])
        logger.info(f"[FW][RESULT] len={len(transcript)}")
        return JSONResponse({"text": transcript, "language": info.language, "language_probability": getattr(info, 'language_probability', None)})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[FW][ERROR] {e}")
        # Helpful hint for language values
        if language:
            return JSONResponse(status_code=400, content={
                "error": str(e),
                "hint": "Use ISO 639-1 code like 'en' (not 'english'). Examples: en, es, fr.",
            })
        raise HTTPException(status_code=500, detail=str(e))


# Gemini STT ========================================
@router.post("/gemini-upload")
async def stt_gemini_upload(file: UploadFile = File(...), language: Optional[str] = None):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        # Create Gemini client using same env var as the app’s config.GEMINI
        api_key = config.gemini.api_key
        if not api_key:
            raise HTTPException(status_code=500, detail="Missing GOOGLE_GEMINI_API_KEY")
        client = genai_mod.Client(api_key=api_key)

        # Model: keep consistent with app (text: gemini-1.5-flash)
        model = os.getenv("GEMINI_BATCH_MODEL", "gemini-1.5-flash")

        instruction = (
            "Transcribe the user's speech verbatim in English. "
            "Return plain text only, no extra words. If not English, return nothing."
        )

        # Upload to Gemini Files API
        with tempfile.NamedTemporaryFile(delete=True, suffix=f"_{file.filename}") as tmp:
            tmp.write(data)
            tmp.flush()
            # prefer 'path=' in newer SDKs
            gfile = None
            try:
                gfile = client.files.upload(path=tmp.name, display_name=file.filename)
            except TypeError:
                gfile = client.files.upload(file=tmp.name)

        # Wait until file is processed/active (important for audio)
        # Depending on SDK, 'state' is on the file object or retrieved via files.get()
        name = getattr(gfile, "name", None)
        if not name:
            raise HTTPException(status_code=500, detail="Gemini upload missing file name")
        for _ in range(30):
            f = client.files.get(name=name)
            state = getattr(f, "state", None)
            if state == "ACTIVE":
                gfile = f
                break
            await asyncio.sleep(1)
        if getattr(gfile, "state", None) != "ACTIVE":
            raise HTTPException(status_code=500, detail="Gemini file not ready")

        file_uri = getattr(gfile, "uri", None) or getattr(gfile, "file_uri", None)
        if not file_uri:
            raise HTTPException(status_code=500, detail="Gemini file upload missing uri")

        mime = file.content_type or "audio/mpeg"

        # Build contents with instruction + file_data part
        contents = [
            genai_types.Content(
                role="user",
                parts=[
                    genai_types.Part(text=instruction),
                    genai_types.Part(
                        file_data=genai_types.FileData(file_uri=file_uri, mime_type=mime)
                    ),
                ],
            )
        ]

        res = client.models.generate_content(model=model, contents=contents)

        # Extract plain text
        text = getattr(res, "text", None)
        if not text:
            cands = getattr(res, "candidates", []) or []
            for c in cands:
                content = getattr(c, "content", None)
                parts = getattr(content, "parts", None) if content else None
                if isinstance(parts, list) and parts:
                    chunks = []
                    for p in parts:
                        val = getattr(p, "text", None)
                        if val:
                            chunks.append(val)
                    if chunks:
                        text = " ".join(chunks).strip()
                        break

        return JSONResponse({"text": (text or "").strip()})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[GEMINI][ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))

# OpenAI STT ========================================
@router.post("/openai-upload")
async def stt_openai_upload(file: UploadFile = File(...)):
    if file is None:
        raise HTTPException(status_code=400, detail="No file uploaded")
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")

    content_type = file.content_type or "audio/mpeg"
    # Persist to temp file, because AudioUtils expects a filesystem path
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp:
            tmp.write(data)
            tmp_path = tmp.name
        logger.info(f"[OAI][UPLOAD] name={file.filename} bytes={len(data)} ctype={content_type} path={tmp_path}")

        # If it's a video or a large file (>10MB), extract/convert to MP3 @64k to ensure audio input
        final_path = tmp_path
        final_ctype = content_type
        try:
            size_mb = len(data) / (1024*1024)
            if content_type.startswith("video/") or size_mb > 10:
                aud = AudioSegment.from_file(tmp_path)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as mp3tmp:
                    aud.export(mp3tmp.name, format="mp3", bitrate="64k")
                    final_path = mp3tmp.name
                    final_ctype = "audio/mpeg"
                logger.info(f"[OAI][CONVERT] -> {final_path} ctype={final_ctype}")
        except Exception as ce:
            logger.warn(f"[OAI][CONVERT][SKIP] {ce}")

        au = AudioUtils()
        # This calls your existing logic which posts to the OpenAI-backed service
        result = au.audio_transcription_logics(filename=file.filename, audio_path=final_path, content_type=final_ctype)
        logger.info(f"[OAI][RESULT] keys={list(result.keys())}")
        return JSONResponse(result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[OAI][ERROR] {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)
            if 'final_path' in locals() and final_path != tmp_path and os.path.exists(final_path):
                os.remove(final_path)
        except Exception:
            pass



# Google STT ========================================
def _infer_google_encoding(filename: str) -> Optional[str]:
    name = filename.lower()
    if name.endswith(".wav"):
        # If WAV with PCM, Google can infer from header; leave unspecified
        return None
    if name.endswith(".flac"):
        return "FLAC"
    if name.endswith(".mp3"):
        return "MP3"
    if name.endswith(".ogg") or name.endswith(".oga"):
        return "OGG_OPUS"
    if name.endswith(".webm"):
        return "WEBM_OPUS"
    if name.endswith(".amr"):
        return "AMR"
    if name.endswith(".awb"):
        return "AMR_WB"
    return None


@router.post("/google-upload")
async def google_stt_upload(file: UploadFile = File(...), language: str = Form("") ):
    api_key = getattr(getattr(config, "cloud", None), "api_key", None)
    if not api_key:
        raise HTTPException(status_code=400, detail="Google API key not configured (config.cloud.api_key)")

    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Empty file")

    encoding = _infer_google_encoding(file.filename or "")
    lang = (language or os.getenv("GOOGLE_STT_LANGUAGE") or "en-US").strip()

    # If payload too large, try to transcode to FLAC mono 16k to shrink size
    if len(raw) > 9_500_000:
        try:
            with tempfile.NamedTemporaryFile(suffix=os.path.splitext(file.filename or 'in')[1] or '.wav', delete=True) as src, \
                 tempfile.NamedTemporaryFile(suffix='.flac', delete=True) as dst:
                src.write(raw)
                src.flush()
                # Requires ffmpeg available in PATH
                cmd = [
                    'ffmpeg','-y','-i',src.name,
                    '-ac','1','-ar','16000','-vn','-acodec','flac',
                    dst.name
                ]
                proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if proc.returncode == 0 and os.path.exists(dst.name):
                    with open(dst.name,'rb') as f:
                        raw = f.read()
                    # Update encoding hint
                    encoding = 'FLAC'
        except Exception:
            # Ignore transcode failure; will proceed with original bytes
            pass

    # If still too large for inline content, bail with guidance (GCS URI required for larger files)
    if len(raw) > 9_500_000:
        raise HTTPException(status_code=400, detail="Audio too large for inline recognize. Reduce size or provide a GCS URI (requires Google Cloud credentials).")

    # Build config now that encoding may have changed
    cfg: dict = {
        "languageCode": lang,
        "enableAutomaticPunctuation": True,
    }
    if encoding:
        cfg["encoding"] = encoding

    b64 = base64.b64encode(raw).decode("ascii")
    payload = {
        "config": cfg,
        "audio": {"content": b64},
    }

    # Use recognize for <= ~9.5MB payloads; otherwise longrunningrecognize
    recognize_url = f"https://speech.googleapis.com/v1/speech:recognize?key={api_key}"
    longrun_url = f"https://speech.googleapis.com/v1/speech:longrunningrecognize?key={api_key}"

    async with httpx.AsyncClient(timeout=180) as client:
        if len(raw) <= 9_500_000:
            resp = await client.post(recognize_url, json=payload)
            if resp.status_code != 200:
                raise HTTPException(status_code=resp.status_code, detail=resp.text[:500])
            data = resp.json()
        else:
            # Kick off async job and poll operation
            start = await client.post(longrun_url, json=payload)
            if start.status_code != 200:
                raise HTTPException(status_code=start.status_code, detail=start.text[:500])
            op = start.json().get("name")
            if not op:
                raise HTTPException(status_code=500, detail="Missing operation name from longrunningrecognize")
            operations_url = f"https://speech.googleapis.com/v1/operations/{op}?key={api_key}"
            # Poll up to ~2 minutes
            for _ in range(60):
                status = await client.get(operations_url)
                if status.status_code != 200:
                    raise HTTPException(status_code=status.status_code, detail=status.text[:500])
                body = status.json()
                if body.get("done"):
                    data = body.get("response") or {}
                    break
                await asyncio.sleep(2)
            else:
                raise HTTPException(status_code=504, detail="Google longrunningrecognize timed out")
    results = data.get("results") or []
    transcripts: list[str] = []
    for r in results:
        alts = r.get("alternatives") or []
        if alts:
            t = (alts[0].get("transcript") or "").strip()
            if t:
                transcripts.append(t)

    text = " ".join(transcripts).strip()
    return JSONResponse({
        "text": text,
        "results": results,
        "language": lang,
        "status_code": 200,
        "message": "Transcript extracted successfully" if text else "No transcript",
    })


