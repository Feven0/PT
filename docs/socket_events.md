# tenx_ipersona Socket Events Documentation

This document describes all main socket.io events used in tenx_ipersona for both text and audio interview flows, including the expected payloads for both client and server, with detailed examples. Every event from the backend and frontend is addressed.

## Connection Events

### connect
- **Client:** No payload (but may include query string, e.g. `run_stage`)
  - Example: `wss://.../socket.io/?run_stage=dev`
- **Server:** No direct response, but session is established.

### disconnect
- **Client:** No payload
- **Server:** No direct response, but session is closed.

### initial connect
- **Client emits:**
  ```json
  { "run_stage": "dev" }
  ```
- **Server responds:**
  No direct response, but session is initialized.

## Audio Interview Events

### audio transcribe
- **Client emits:**
  ```json
  { "audioblob": "<base64-encoded-audio>" }
  ```
- **Server emits:**
  - Transcribed text as a string (interim and final transcripts)
    ```json
    "This is the transcribed text."
    ```

### audio chat sentence
- **Client emits:**
  ```json
  {
    "response": "Yes, I have experience with Python.",
    "user_session": {
      "id": 123,
      "attributes": { ... }
    },
    "template_id": "456", // optional
    "challenge_id": "789"  // optional
  }
  ```
- **Server emits:**
  - `audio chat sentence`:
    ```json
    [
      {
        "user_type": "assistant",
        "content_type": "question",
        "content": {
          "chunk_response": "Can you tell me about a time you solved a difficult problem?",
          "full_response": "Can you tell me about a time you solved a difficult problem?",
          "final": false,
          "realtime_evaluation": null,
          "time_limit": "60"
        }
      }
    ]
    ```
  - `audio_time_limit`:
    ```json
    { "content": { "time_limit": "60" } }
    ```
  - `audio_base64_chunks`:
    ```json
    { "content": { "audio_data": "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA=" } }
    ```
  - `audio-single-chunk`:
    (binary audio data, e.g. a single MP3 chunk)
  - `audio-one-chunk`:
    (binary audio data, e.g. a single MP3 chunk)
  - `audio-single-chunk-sentence`:
    ```json
    "This is a sentence from the audio."
    ```
  - `audio-single-text-chunk`:
    ```json
    "This is a text chunk."
    ```
  - `audio-single-text-chunk-done`:
    (no payload)
  - `audio_realtime`:
    ```json
    { "content": { "realtime_evaluation": "Good answer, clear and concise.", "full_response": "Yes, I have experience with Python." } }
    ```
  - `last_audio_realtime_evaluation`:
    ```json
    { "content": { "realtime_evaluation": "Excellent overall performance.", "full_response": "[full interview transcript]" } }
    ```
  - `interview done`:
    ```json
    { "message": "Interview complete." }
    ```

## Text Interview Events

### interview chat
- **Client emits:**
  ```json
  {
    "response": "I am a software engineer.",
    "user_session": {
      "id": 123,
      "attributes": { ... }
    },
    "template_id": "456", // optional
    "challenge_id": "789"  // optional
  }
  ```
- **Server emits:**
  - `interview chat`:
    ```json
    [
      {
        "user_type": "assistant",
        "content_type": "question",
        "content": {
          "chunk_response": "What programming languages are you most comfortable with?",
          "full_response": "What programming languages are you most comfortable with?",
          "final": false,
          "realtime_evaluation": null,
          "time_limit": "60"
        }
      }
    ]
    ```
  - `time_limit`:
    ```json
    { "content": { "time_limit": "60" } }
    ```
  - `realtime`:
    ```json
    { "content": { "realtime_evaluation": "Answer was relevant.", "full_response": "I am a software engineer." } }
    ```
  - `last_realtime_evaluation`:
    ```json
    { "content": { "realtime_evaluation": "Great interview.", "full_response": "[full interview transcript]" } }
    ```
  - `interview done`:
    ```json
    { "message": "Interview complete." }
    ```

## Error Events

### error
- **Server emits:**
  ```json
  { "error": "Session not found." }
  ```
  (on validation or processing errors)

**Note:**
- All events use socket.io and expect JSON payloads unless otherwise noted.
- Some events (like chunked audio) may use raw binary or string payloads.
- For exact payload structure, refer to backend and frontend code, but the above covers the main expected/response patterns. 