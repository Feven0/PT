import os
from api.utils.logger import LLPackerLogger
from api import config
from openai import OpenAI

logger = LLPackerLogger(os.path.basename(__file__))
OPENAI_API_KEY = config.openai.api_key
client = OpenAI(api_key=OPENAI_API_KEY)

# -------------------------- S3 Background Upload -------------------------- #
async def upload_audio_to_s3_background(accumulated_audio, sid, sessionId, message_id, run_stage):
    """Background task to upload audio to S3 and update the specific message with URL."""
    try:
        from api.utils import s3_client as _s3h
        from datetime import datetime
        
        # Combine all audio chunks
        complete_audio = b''.join(accumulated_audio)
        logger.info(f"[S3 UPLOAD] Background upload started for sid={sid}, sessionId={sessionId}, message_id={message_id}, total_size={len(complete_audio)} bytes")
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"audio_{sid}_{timestamp}.wav"
        
        # Pick bucket
        def _pick_bucket():
            buckets = _s3h.list_buckets()
            if 'tenx-parrot-assets' not in buckets:
                raise Exception("tenx-parrot-assets bucket not found or not accessible")
            return 'tenx-parrot-assets'
        bucket = _pick_bucket()
        
        # Set prefix and key for audio files
        prefix = "audio"
        key = f"{prefix}/{filename}"
        
        # Upload using s3_client.upload_bytes_and_get_url
        audio_url, _ = _s3h.upload_bytes_and_get_url(bucket, complete_audio, key=key)
        logger.info(f"[S3 UPLOAD] Background upload completed for sid={sid}, sessionId={sessionId}, message_id={message_id}, URL: {audio_url}")
        
        # Update the specific message with the audio URL
        try:
            from api.llm.ipersona import ipersona_strapi as strapi
            success = strapi.update_message_with_audio_url(message_id, audio_url, run_stage)
            if success:
                logger.info(f"[S3 UPLOAD] Successfully updated message {message_id} with audio URL")
            else:
                logger.error(f"[S3 UPLOAD] Failed to update message {message_id} with audio URL")
        except Exception as db_error:
            logger.error(f"[S3 UPLOAD] Failed to update database for message_id={message_id}: {db_error}")
        
    except Exception as e:
        logger.error(f"[S3 UPLOAD] Background upload failed for sid={sid}, sessionId={sessionId}, message_id={message_id}: {e}")


async def synthesize_text(text):
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
