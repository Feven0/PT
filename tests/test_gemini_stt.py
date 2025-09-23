import os
import sys
import base64


def _repo_root() -> str:
    return os.path.dirname(os.path.abspath(__file__ + "/.."))


def _abs_path(*parts: str) -> str:
    return os.path.abspath(os.path.join(_repo_root(), *parts))


def main():
    # Ensure we can import the local api package
    repo_root = _repo_root()
    if repo_root not in sys.path:
        sys.path.append(repo_root)

    try:
        from api import config
    except Exception as e:
        print(f"Failed to import api.config: {e}")
        sys.exit(1)

    gemini_api_key = getattr(config.gemini, "api_key", None)
    if not gemini_api_key:
        print("Gemini API key not found in config.gemini.api_key")
        sys.exit(1)

    try:
        # pip install google-genai
        from google import genai
        from google.genai import types
    except Exception as e:
        print("Missing dependency 'google-genai'. Install it first: pip install google-genai")
        print(f"Import error: {e}")
        sys.exit(1)

    client = genai.Client(api_key=gemini_api_key)

    # Use repo audio sample or provide your own via GEMINI_TEST_AUDIO env
    audio_path = os.environ.get("GEMINI_TEST_AUDIO", _abs_path("audio", "test_audio.mp3"))
    if not os.path.exists(audio_path):
        print(f"Audio file not found: {audio_path}")
        sys.exit(1)

    # Detect mime type from extension
    ext = os.path.splitext(audio_path)[1].lower()
    mime = {
        ".mp3": "audio/mpeg",
        ".wav": "audio/wav",
        ".m4a": "audio/mp4",
        ".flac": "audio/flac",
        ".oga": "audio/ogg",
        ".ogg": "audio/ogg",
        ".webm": "audio/webm",
    }.get(ext, "audio/mpeg")

    with open(audio_path, "rb") as f:
        audio_bytes = f.read()

    # Build request: send audio and a short instruction to transcribe
    try:
        audio_blob = types.Blob(mime_type=mime, data=audio_bytes)
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_blob(audio_blob),
                    types.Part.from_text("Transcribe the audio. Return only the transcript text."),
                ],
            )
        ]

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
        )

        # Print best-effort text extraction
        text = getattr(response, "text", None)
        if text:
            print(text)
        else:
            # Fallback to raw structure
            print(response)

    except Exception as e:
        # Fallback to REST inlineData if SDK surface differs
        import json
        import requests

        print(f"SDK call failed, attempting REST fallback: {e}")

        b64 = base64.b64encode(audio_bytes).decode("utf-8")
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
        headers = {
            "x-goog-api-key": gemini_api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"inline_data": {"mime_type": mime, "data": b64}},
                        {"text": "Transcribe the audio. Return only the transcript text."},
                    ],
                }
            ]
        }
        r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
        r.raise_for_status()
        data = r.json()
        # Best-effort extraction
        try:
            print(data["candidates"][0]["content"]["parts"][0]["text"])
        except Exception:
            print(json.dumps(data, indent=2))


if __name__ == "__main__":
    main()




