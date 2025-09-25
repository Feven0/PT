import os, io, wave, array

# Whisper STT tuning (override via env if needed)
WHISPER_MODEL = os.getenv("OPENAI_STT_MODEL", "whisper-1")
# ~3s @ 16kHz mono PCM16 ≈ 96000 bytes
WHISPER_TARGET_BYTES = int(os.getenv("OPENAI_STT_BUFFER_TARGET_BYTES", "96000"))
# ~0.2s overlap ≈ 6400 bytes
WHISPER_OVERLAP_BYTES = int(os.getenv("OPENAI_STT_OVERLAP_BYTES", "6400"))
# Silence gate RMS threshold
WHISPER_RMS_THRESHOLD = int(os.getenv("OPENAI_STT_RMS_THRESHOLD", "600"))


def pcm16_mono_16k_to_wav_bytes(pcm_bytes: bytes) -> bytes:
    with io.BytesIO() as buffer:
        with wave.open(buffer, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(16000)
            wf.writeframes(pcm_bytes)
        return buffer.getvalue()


def is_silent_pcm16(pcm_bytes: bytes, rms_threshold: int = WHISPER_RMS_THRESHOLD) -> bool:
    try:
        if not pcm_bytes:
            return True
        samples = array.array('h')
        samples.frombytes(pcm_bytes)
        if len(samples) == 0:
            return True
        acc = 0
        for s in samples:
            acc += s * s
        rms = int((acc / len(samples)) ** 0.5)
        return rms < rms_threshold
    except Exception:
        return False


