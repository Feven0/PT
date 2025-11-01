from nturl2path import url2pathname
import os
import requests
import json
from typing import Optional, Tuple
from api.utils.logger import LLPackerLogger
import api.llm.ipersona.ipersona_gpt as gpt
from api.services.redis.redis_config import RedisBase
import threading
import asyncio
from api.llm.ipersona.ipersona_strapi_schemas import (
    IpersonaTraineeSchema,
    IpersonaSessionSchema,
    IpersonaSessionObserverSchema,
    IpersonaSessionOverallObserverSchema
)
import api.llm.ipersona.ipersona_strapi as strapi
import api.modules.ipersona_parrot_gpt as util
from pydub import AudioSegment
from io import BytesIO
from api.socket.core import sio, emit_with_log

logger = LLPackerLogger(os.path.basename(__file__))

class AudioUtils:
    def __init__(self):
        pass
    
    def _get_active_task_id(self, job_profile_id, challenge_id, template_id, all_user_id):
        """
        Determine which task ID is non-zero and should be used.
        Returns tuple: (task_type, task_id)
        """
        # Check job_profile_id first (highest priority)
        if job_profile_id and str(job_profile_id).strip():
            try:
                job_id = int(job_profile_id)
                if job_id != 0:
                    return ("job", job_id)
            except (ValueError, TypeError):
                pass
        
        # Check challenge_id
        if challenge_id and str(challenge_id).strip():
            try:
                challenge_id_int = int(challenge_id)
                if challenge_id_int != 0:
                    return ("challenge", challenge_id_int)
            except (ValueError, TypeError):
                pass
        
        # Check template_id
        if template_id and str(template_id).strip():
            try:
                template_id_int = int(template_id)
                if template_id_int != 0:
                    return ("template", template_id_int)
            except (ValueError, TypeError):
                pass
        
        # Fallback to all_user_id
        if all_user_id and str(all_user_id).strip():
            return ("user", all_user_id)
        
        # Final fallback
        return ("unknown", job_profile_id or 'none')
    
    def _get_task_redis_key(self, task_type, task_id, key_suffix="audio_status"):
        """
        Generate Redis key using only the active task type and ID.
        """
        return f"parrot_celery_tasks:{key_suffix}:{task_type}:{task_id}"
    
    def _normalize_audio_path(self, audio_path: str) -> str:
        """
        Normalize audio path to work in both localhost and Docker environments.
        Converts localhost paths to Docker paths when running in Docker.
        """
        import os
        
        # Check if we're running in Docker (working directory is /app)
        is_docker = os.getcwd() == '/app'
        
        if is_docker and audio_path.startswith('/home/rehmet/tenx_ipersona/'):
            # Convert localhost path to Docker path
            relative_path = audio_path.replace('/home/rehmet/tenx_ipersona/', '')
            docker_path = f'/app/{relative_path}'
            return docker_path
        
        return audio_path
    
    def _build_upload_meta(self, s3_url: str, content_type: str, filename: str, audio_path: Optional[str] = None, contents: Optional[bytes] = None, text_size_bytes: Optional[int] = None) -> dict:
        """
        Build a basic upload metadata dict with url, s3_url, content_type, original_filename,
        and computed duration_secs (only for AV) and size_bytes.
        """
        is_av = ("audio" in content_type) or ("video" in content_type)
        duration_value: Optional[str] = None
        size_bytes_value: Optional[int] = None
        try:
            if is_av:
                if contents:
                    duration_secs_f = len(AudioSegment.from_file(BytesIO(contents), format='mp3')) / 1000.0
                    duration_value = f"{duration_secs_f} seconds"
                    size_bytes_value = len(contents)
                elif audio_path:
                    duration_secs_f = len(AudioSegment.from_file(audio_path)) / 1000.0
                    duration_value = f"{duration_secs_f} seconds"
                    import os as _os
                    size_bytes_value = _os.path.getsize(audio_path) if _os.path.exists(audio_path) else None
            else:
                size_bytes_value = text_size_bytes if text_size_bytes is not None else (len(contents) if contents else None)
        except Exception:
            # Best-effort; leave None on failure
            pass

        return {
            "url": s3_url,
            "content_type": content_type,
            "original_filename": filename,
            "duration_secs": duration_value,
            "size_bytes": size_bytes_value,
        }

    def _upload_and_get_duration(self, filename: str, content_type: str, contents: bytes) -> tuple[str, Optional[str], int]:
        """
        Uploads bytes to S3 under the appropriate prefix and returns (url, duration_string_or_None).
        Duration is computed only for audio/video inputs.
        """
        from api.utils import s3_client as _s3h
        def _pick_bucket():
            buckets = _s3h.list_buckets()
            if 'tenx-parrot-assets' not in buckets:
                raise Exception("tenx-parrot-assets bucket not found or not accessible")
            return 'tenx-parrot-assets'
        bucket = _pick_bucket()

        is_av = ("audio" in content_type) or ("video" in content_type)
        prefix = "audio" if is_av else "documents"
        key = f"{prefix}/{filename}"
        url, _ = _s3h.upload_bytes_and_get_url(bucket, contents, key=key)

        duration_str: Optional[str] = None
        size_bytes: int = len(contents)
        if is_av:
            try:
                fmt = content_type.split("/")[-1].lower()
                fmt = 'mp3' if fmt == 'mpeg' else fmt
                duration_secs = len(AudioSegment.from_file(BytesIO(contents), format=fmt)) / 1000.0
                duration_str = f"{duration_secs} seconds"
            except Exception:
                duration_str = None

        return url, duration_str, size_bytes
    
    def ai_validate_interview_content(self, transcript):
        """
        AI-Powered Content Validation for Interview Content
        
        This function uses AI to validate if the transcribed content represents
        a proper job interview with Q&A patterns, interviewer presence, and
        relevant evaluation content.
        
        Args:
            transcript (str): The transcribed content to validate
            
        Returns:
            dict: {"valid": bool, "reason": str}
        """
        try:
            logger.info(f"Starting AI validation for transcript ({len(transcript)} characters)")
            
            # Basic length check first
            if len(transcript.strip()) < 50:
                return {
                    "valid": False,
                    "reason": "Content too short - minimum 50 characters required for evaluation"
                }
            
            # AI validation prompt (stricter and explicit)
            validation_prompt = f"""
            Analyze this transcript and determine if it's a COMPLETE job interview suitable for evaluation.
            
            Transcript: {transcript}
            
            STRICT VALIDATION CRITERIA (ALL MUST BE TRUE TO BE VALID):
            1. It contains BOTH interviewer questions AND candidate answers.
            2. There are CLEAR question-answer exchanges (Q followed by A), not just a list of questions.
            3. Candidate responses are substantive (more than one-word replies like "yes/no/okay").
            4. The conversation is not one-sided, incomplete, or fragmented.
            
            AUTOMATICALLY INVALID IF ANY OF THE FOLLOWING IS TRUE:
            - Only questions without answers
            - Only answers without questions
            - Mostly interviewer prompts like "Can you...", "How do you...", "What's your..." and no candidate replies
            - Single-speaker monologue
            - Incomplete conversation with no evident back-and-forth
            
            Examples of VALID content:
            Interviewer: "Can you tell me about yourself?"
            Candidate: "I'm a software engineer with 5 years of experience in ..."
            Interviewer: "Describe a challenging project you worked on."
            Candidate: "I led the migration to microservices where ..."
            
            Return your analysis in this exact JSON format:
            {{
                "valid": true/false,
                "reason": "Focus on whether BOTH questions AND answers are present with Q&A pairs",
                "content_type": "interview/not_interview/incomplete/poor_quality",
                "has_questions": true/false,
                "has_answers": true/false,
                "interviewer_present": true/false,
                "suitable_for_evaluation": true/false,
                "conversation_completeness": "complete/incomplete/one_sided"
            }}
            """
            
            logger.info("Sending validation prompt to AI")
            response = gpt.openai_gpt_assistant_without_streaming(validation_prompt)
            
            logger.info("Received AI validation response")
            
            # Extract JSON from response
            validation_result = util.extract_json(response, quite=False)
            
            if not validation_result:
                logger.warn("Failed to extract JSON from validation response")
                return {
                    "valid": False,
                    "reason": "AI validation failed - unable to process response"
                }
            
            # Additional heuristic: detect question-only transcripts
            try:
                lower_tx = transcript.lower()
                question_mark_ratio = lower_tx.count('?')
                question_indicators = [
                    "can you", "could you", "would you", "how do", "how did", "how would",
                    "what is", "what's", "what are", "tell me", "describe", "explain",
                    "have you", "do you", "why did", "why do"
                ]
                answer_indicators = [
                    "i am ", "i have ", "i did ", "i work", "my experience", "i would",
                    "i think", "in my opinion", "i believe", "we implemented", "i led", "i solved"
                ]
                qi = sum(1 for k in question_indicators if k in lower_tx)
                ai = sum(1 for k in answer_indicators if k in lower_tx)
                # If many questions but very few answer cues, force invalid
                if (qi >= 3 and ai == 0) or (question_mark_ratio >= 3 and ai <= 1):
                    validation_result["valid"] = False
                    validation_result["has_answers"] = False
                    validation_result["suitable_for_evaluation"] = False
                    validation_result["content_type"] = validation_result.get("content_type", "incomplete")
                    validation_result["conversation_completeness"] = "one_sided"
                    validation_result["reason"] = (
                        "Detected mostly interviewer questions with insufficient candidate responses"
                    )
            except Exception:
                pass

            logger.info("AI validation completed successfully")
            return validation_result
            
        except Exception as e:
            logger.error(f"AI validation process failed: {str(e)}")
            return {
                "valid": False,
                "reason": f"AI validation process failed: {str(e)}"
            }
        
    def ai_validate_answer_content(self, answer_transcript, template_questions=None):
        """
        AI-Powered Answer Content Validation
        
        This function uses AI to validate if the transcribed answer content contains
        proper responses to questions rather than just questions, incomplete content,
        or irrelevant material.
        
        Args:
            answer_transcript (str or list): The transcribed answer content to validate
            template_questions (list, optional): Template questions for context
            
        Returns:
            dict: {"valid": bool, "reason": str, "confidence": float}
        """
        try:
            # Handle both string and list inputs
            if isinstance(answer_transcript, list):
                # Join list items into a single string, filtering out None/empty values
                answer_text = " ".join(str(item) for item in answer_transcript if item is not None and str(item).strip())
                logger.info(f"🤖 [DEBUG] Starting AI answer validation for transcript length: {len(answer_text)} (converted from list)")
            else:
                answer_text = str(answer_transcript) if answer_transcript is not None else ""
                logger.info(f"🤖 [DEBUG] Starting AI answer validation for transcript length: {len(answer_text)}")
            
            # Basic length check first
            if len(answer_text.strip()) < 30:
                return {
                    "valid": False,
                    "reason": "Answer content too short - minimum 30 characters required for meaningful answers",
                    "confidence": 1.0
                }
            
            # Prepare context information about questions if available
            questions_context = ""
            if template_questions:
                questions_list = []
                for i, q in enumerate(template_questions, 1):
                    question_text = q.get('question', '') if isinstance(q, dict) else str(q)
                    questions_list.append(f"{i}. {question_text}")
                questions_context = f"\n\nExpected Questions Context:\n" + "\n".join(questions_list)
            
            # AI validation prompt specifically for answer content - LENIENT APPROACH
            validation_prompt = f"""
            Analyze this transcript and determine if it contains REASONABLE ANSWERS suitable for interview evaluation.
            
            Answer Transcript: {answer_text}
            {questions_context}
            
            LENIENT ANSWER VALIDATION CRITERIA (BE GENEROUS - ACCEPT BASIC ANSWERS):
            1. Contains any reasonable responses/answers (not just questions or prompts)
            2. Responses are more than single words or "yes/no" replies
            3. Shows candidate attempting to answer questions (even if basic)
            4. Content demonstrates some effort to respond to interview-type questions
            5. NOT primarily composed of interviewer questions or prompts
            
            AUTOMATICALLY INVALID ONLY IF ANY OF THE FOLLOWING IS TRUE:
            - Mostly or only interviewer questions without candidate responses
            - Only brief acknowledgments like "yes", "okay", "sure", "mm-hmm" (with no actual answers)
            - Complete silence, background noise, or non-verbal content only
            - Primarily consists of question prompts like "Can you tell me...", "How would you..."
            - Completely irrelevant content (not related to interview questions)
            
            Examples of VALID answer content (BE LENIENT):
            "I have some experience with Python and JavaScript. I worked on a few projects at my previous job."
            "I think I would handle pressure by staying organized and asking for help when needed."
            "My experience with Power BI is basic, but I've used it to create some simple dashboards."
            "I believe in teamwork and communication. I try to be helpful to my colleagues."
            
            Examples of INVALID answer content:
            "Can you tell me about your experience? What technologies have you worked with? How do you handle pressure?"
            "Yes. Okay. Sure. I think so." (with no actual answers)
            "The audio quality is poor and I cannot make out the responses clearly."
            
            IMPORTANT: Be generous in validation. Accept basic answers even if they lack depth or examples.
            Focus on content validity, not interview performance quality.
            
            Return your analysis in this exact JSON format:
            {{
                "valid": true/false,
                "reason": "Specific explanation focusing on answer validity (be lenient)",
                "confidence": 0.0-1.0,
                "content_type": "proper_answers/mostly_questions/incomplete_answers/poor_quality/mixed_content",
                "has_substantive_answers": true/false,
                "answer_completeness": "complete/partial/minimal/none",
                "suitable_for_evaluation": true/false,
                "detected_issues": ["list of specific issues found"]
            }}
            """
            
            logger.info(f"📤 [DEBUG] Sending answer validation prompt to GPT")
            response = gpt.openai_gpt_assistant_without_streaming(validation_prompt)
            
            logger.info(f"📥 [DEBUG] Received GPT response for answer validation")
            
            # Extract JSON from response
            validation_result = util.extract_json(response, quite=False)
            
            if not validation_result:
                logger.info(f"❌ [DEBUG] Failed to extract JSON from answer validation response")
                return {
                    "valid": False,
                    "reason": "Answer validation failed - unable to process AI response",
                    "confidence": 0.0
                }
            
            # Additional heuristic checks for answer content
            try:
                lower_tx = answer_text.lower()
                
                # Check for question indicators (bad for answer file)
                question_indicators = [
                    "can you", "could you", "would you", "how do", "how did", "how would",
                    "what is", "what's", "what are", "tell me", "describe", "explain",
                    "have you", "do you", "why did", "why do", "please", "let's discuss"
                ]
                
                # Check for answer indicators (good for answer file)
                answer_indicators = [
                    "i am ", "i have ", "i did ", "i work", "my experience", "i would",
                    "i think", "in my opinion", "i believe", "we implemented", "i led", 
                    "i solved", "i developed", "i managed", "in my role", "when i",
                    "i learned", "i achieved", "my approach", "i handled", "i created"
                ]
                
                # Check for minimal response indicators (bad for answer file)
                minimal_indicators = [
                    " yes ", " no ", " okay ", " sure ", " mm-hmm", " uh-huh",
                    " right ", " exactly ", " correct ", " true ", " false "
                ]
                
                qi = sum(1 for k in question_indicators if k in lower_tx)
                ai = sum(1 for k in answer_indicators if k in lower_tx)
                mi = sum(1 for k in minimal_indicators if k in lower_tx)
                question_marks = lower_tx.count('?')
                
                # If many questions but few answer indicators, force invalid (MORE LENIENT)
                if (qi >= 6 and ai <= 0) or (question_marks >= 5 and ai <= 0):
                    validation_result["valid"] = False
                    validation_result["has_substantive_answers"] = False
                    validation_result["suitable_for_evaluation"] = False
                    validation_result["content_type"] = "mostly_questions"
                    validation_result["answer_completeness"] = "none"
                    validation_result["reason"] = (
                        "Detected mostly questions with no answer content"
                    )
                
                # If mostly minimal responses, reduce confidence (MORE LENIENT)
                elif mi >= 8 and ai <= 1:
                    validation_result["valid"] = False
                    validation_result["content_type"] = "incomplete_answers"
                    validation_result["answer_completeness"] = "minimal"
                    validation_result["reason"] = (
                        "Detected mostly minimal responses without any answer content"
                    )
                    
            except Exception as e:
                logger.info(f"⚠️ [DEBUG] Heuristic check failed: {str(e)}")
                pass

            logger.info(f"✅ [DEBUG] AI answer validation completed successfully")
            return validation_result
            
        except Exception as e:
            logger.info(f"❌ [DEBUG] AI answer validation process failed: {str(e)}")
            logger.error(f"AI answer validation process failed: {str(e)}")
            return {
                "valid": False,
                "reason": f"Answer validation process failed: {str(e)}",
                "confidence": 0.0
            }
        
    def update_task_progress(self, target, task_type, progress, status=None, error_message=None):
        """
        Helper method to update task progress in the task tracker
        This is optional and won't interfere with core logic if not called
        """
        try:
            from services.celery.task_tracker import task_tracker, TaskStatus
            if status:
                task_tracker.update_task_status(
                    target=target,
                    task_type=task_type,
                    status=status,
                    progress=progress,
                    error_message=error_message
                )
            else:
                task_tracker.update_task_status(
                    target=target,
                    task_type=task_type,
                    status=TaskStatus.PROCESSING,
                    progress=progress
                )
        except Exception as e:
            logger.info(f"⚠️ Failed to update task progress: {e}")

    async def process_upload_external_audio(
        self,
        filename,
        content_type,
        audio_path,
        job_profile_id,
        challenge_id,
        template_id,
        all_user_id,
        external,
        run_stage,
        user_sid=None):
        
        try:
            redis = RedisBase()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Failed to establish Redis connection: {str(e)}")
            return 'Redis connection failed'
        
        # S3 helpers - only use tenx-parrot-assets
        try:
            from api.utils import s3_client as _s3h
            def _pick_bucket():
                buckets = _s3h.list_buckets()
                if 'tenx-parrot-assets' not in buckets:
                    raise Exception("tenx-parrot-assets bucket not found or not accessible")
                return 'tenx-parrot-assets'
        except Exception as e:
            logger.error(f"S3 setup failed: {str(e)}")
            return f'S3 setup failed: {str(e)}'

        s3_audio_url = None
        s3_text_url = None
       
        try:
            logger.info(f"Starting audio processing for file: {filename}")
            
            # Set initial processing status
            task_type, task_id = self._get_active_task_id(job_profile_id, challenge_id, template_id, all_user_id)
            task_redis_key = self._get_task_redis_key(task_type, task_id)
            
            try:
                redis.set(task_redis_key, {"status": "processing", "message": ""})
                logger.info(f"Set Redis status to processing for {task_type}:{task_id}")
            except Exception as e:
                logger.error(f"Failed to set Redis status: {str(e)}")

            # Initialize processing variables
            message = ''
            template = False
            challenge = False  
            mode = None
            
            if "audio" in content_type or "video" in content_type:
                logger.info(f"Processing audio/video file with content type: {content_type}")
                
                try:
                    original_format = content_type.split("/")[-1].lower()
                    logger.info(f"Detected format: {original_format}")
                except Exception as e:
                    logger.error(f"Failed to extract format: {str(e)}")
                    return 'Format extraction failed'
                
                # Handle audio file processing (conversion + upload)
                try:
                    # Step 1: Convert to MP3 if needed
                    if original_format != "mpeg" and original_format != "mp3":
                        logger.info(f"Converting media file from {original_format} to mp3")
                        
                        # Read and convert file
                        normalized_audio_path = self._normalize_audio_path(audio_path)
                        with open(normalized_audio_path, "rb") as f:
                            contents = f.read()
                        
                        contents = util.convert_to_mp3(contents, original_format)
                        logger.info(f"MP3 conversion completed, new size: {len(contents)} bytes")
                        
                        # Save converted MP3 locally for transcription
                        converted_filename = filename.rsplit(".", 1)[0] + ".mp3"
                        converted_path = util.audio_path(converted_filename)
                        with open(converted_path, "wb") as f:
                            f.write(contents)
                        
                        # Update audio_path to point to converted file
                        audio_path = converted_path
                        filename = converted_filename
                        
                        # Upload converted file
                        bucket = _pick_bucket()
                        url, key = _s3h.upload_bytes_and_get_url(bucket, contents, key=f"audio/{converted_filename}")
                        s3_audio_url = url
                        logger.success(f"Converted and uploaded to S3: {url}")
                    else:
                        logger.info("File already in mp3 format. Skipping conversion, uploading to S3.")
                        # Read existing MP3 file
                        normalized_audio_path = self._normalize_audio_path(audio_path)
                        with open(normalized_audio_path, "rb") as f:
                            contents = f.read()
                        
                        # Upload existing MP3 file to S3
                        bucket = _pick_bucket()
                        url, key = _s3h.upload_bytes_and_get_url(bucket, contents, key=f"audio/{filename}")
                        s3_audio_url = url
                        logger.success(f"Uploaded existing MP3 to S3: {url}")
                        
                except Exception as e:
                    logger.error(f"Audio processing and upload failed: {str(e)}")
                    return f'Audio processing failed: {str(e)}'

                # Step 2: Transcribe the audio
                try:
                    logger.info("Starting audio transcription")
                    # Use normalized path for Docker compatibility
                    normalized_audio_path = self._normalize_audio_path(audio_path)
                    result = self.audio_transcription_logics(
                        filename=filename,
                        audio_path=normalized_audio_path,
                        content_type="audio/mpeg",
                    )
                    
                    if "error" in result:
                        error_msg = result.get('error')
                        logger.error(f"Transcription failed: {error_msg}")
                        redis.set(task_redis_key, {
                            "status": "failed",
                            "message": error_msg,
                            "details": result.get("details", "")
                        })
                        raise Exception("Transcription failed")
                    
                    transcript = result.get("content", "No transcription returned")
                    logger.success(f"Transcription completed: {len(transcript)} characters")
                    
                except Exception as e:
                    logger.error(f"Audio transcription failed: {str(e)}")
                    return 'Transcription failed'

                # # Step 3: Validate content and complete
                try:
                    # AI-Powered Content Validation (using sample for testing)
                    # import os
                    # project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    # transcript_path = os.path.join(project_root, "api", "utils", "sample_transcriptions", "gibberish.txt")
                    # test_transcript = util.file_reader(transcript_path)
                    
                    logger.info("Starting AI-powered content validation")
                    validation_result = self.ai_validate_interview_content(transcript)
                    
                    if not validation_result.get('valid', False):
                        error_reason = validation_result.get('reason', 'Content validation failed')
                        logger.warn(f"Content validation failed: {error_reason}")
                        
                        # Emit failure event and update Redis
                        try:
                            # if user_sid:
                            #     logger.info(f"[EMIT] event=processing_update_failed sid={user_sid} payload=status: Invalid interview content ...")
                                # await emit_with_log(
                                #     "processing_update_failed",
                                #     {"status": f"Invalid interview content: {error_reason}"},
                                #             sid=user_sid,
                                # )
                            logger.info(f"📢 [NOTIFICATION] Invoking save_notification for all_user_id={all_user_id}, error_reason='{error_reason}'")
                            self.save_notification(all_user_id, run_stage, f"Invalid interview content: {error_reason}")
                            logger.info(f"📢 [NOTIFICATION] save_notification invocation completed for all_user_id={all_user_id}")
                        except Exception as emit_exc:
                            logger.error(f"❌ [NOTIFICATION][ERROR] Failed to save notification - sid={user_sid} err={emit_exc}", exc_info=True)
                        
                        redis.set(task_redis_key, {
                            "status": "failed",
                            "message": f"Invalid interview content: {error_reason}"
                        })
                        logger.info(f"Invalid interview content: {error_reason}")
                        return f"Invalid interview content: {error_reason}"
                    
                    # Success: Mark transcription as complete
                    redis.set(task_redis_key, {
                        "status": "done",
                        "message": "Transcription complete",
                        "content": transcript
                    })
                    logger.success("Audio processing completed successfully")
                    
                except Exception as e:
                    logger.error(f"Content validation failed: {str(e)}")
                    redis.set(task_redis_key, {
                        "status": "failed",
                        "message": f"Content validation failed: {str(e)}"
                    })
                    return f"Content validation failed: {str(e)}"

            elif any(x in content_type for x in ["text", "pdf", "msword", "officedocument"]):                    
                    try:
                        # Read and upload document
                        normalized_audio_path = self._normalize_audio_path(audio_path)
                        with open(normalized_audio_path, "rb") as f:
                            contents = f.read()
                        logger.info(f"Read file contents, size: {len(contents)} bytes")
                        
                        # Upload original document to S3 (use bytes to avoid local path issues inside Docker)
                        bucket = _pick_bucket()
                        url, key = _s3h.upload_bytes_and_get_url(bucket, contents, key=f"documents/{filename}")
                        s3_text_url = url
                        text_size_bytes = len(contents)
                        logger.info(f"Document uploaded to S3: {url}")
                        
                    except Exception as e:
                        # if user_sid:
                        #     logger.info(f"[EMIT] event=processing_update_failed sid={user_sid} payload=status: Document processing failed ...")
                            # await emit_with_log(
                            #     "processing_update_failed",
                            #     {"status": f"Document processing failed: {str(e)}"},
                            #     sid=user_sid,
                            # )
                        try:
                            logger.info(f"📢 [NOTIFICATION] Invoking save_notification for DOCUMENT PROCESSING FAILED - all_user_id={all_user_id}, error={str(e)}")
                            self.save_notification(all_user_id, run_stage, f"Document processing failed: {str(e)}")
                            logger.info(f"📢 [NOTIFICATION] save_notification invocation completed for all_user_id={all_user_id}")
                        except Exception as emit_exc:
                            logger.error(f"❌ [NOTIFICATION][ERROR] Failed to save notification - err={emit_exc}", exc_info=True)
                        return f'Document processing failed: {str(e)}'
                    
                    # Extract text content
                    try:
                        logger.info("Extracting text content from document")
                        result = self.content_extraction_logics(filename, contents, content_type)
                        
                        if "error" in result:
                            logger.error(f"Text extraction failed: {result['error']}")
                            redis.set(task_redis_key, {
                                "status": "failed",
                                "message": result.get("error")
                            })
                            return
                    except Exception as e:
                        logger.error(f"Content extraction failed: {str(e)}")
                        return 'Content extraction failed'
                    
                    try:
                        transcript = result.get("content", "No content returned")
                        logger.info(f"📝 [DEBUG] Extracted content: {transcript[:50]}..." if len(str(transcript)) > 100 else f"📝 [DEBUG] Extracted content: {transcript}")
                        logger.success(f"✅ Text extraction successful: {filename}")
                    except Exception as e:
                        logger.info(f"❌ [DEBUG] Failed to extract content: {str(e)}")
                        return 'Content extraction failed'

                    # AI-Powered Content Validation for Text Documents
                    try:
                        validation_result = self.ai_validate_interview_content(transcript)
                        logger.info(f"📊 [DEBUG] Validation result: {validation_result}")
                        
                        if not validation_result.get('valid', False):
                            error_reason = validation_result.get('reason', 'Content validation failed')
                            logger.error(f"❌ [DEBUG] Content validation failed: {error_reason}")
                            try:
                                task_type, task_id = self._get_active_task_id(job_profile_id, challenge_id, template_id, all_user_id)
                                task_redis_key = self._get_task_redis_key(task_type, task_id)
                                redis.set(task_redis_key, {
                                    "status": "failed",
                                    "message": f"Invalid interview content: {error_reason}"
                                })
                                logger.info(f"📝 [DEBUG] Set Redis status to 'failed' for validation error using key: {task_redis_key}")
                            except Exception as e:
                                logger.error(f"❌ [DEBUG] Failed to set Redis validation error status: {str(e)}")
                            return f"Invalid interview content: {error_reason}"
                        
                        logger.success("✅ [SUCCESS] Content validation passed")
                        
                    except Exception as e:
                        try:
                            redis.set(f"parrot_celery_tasks:audio_status:{job_profile_id}", {
                                "status": "failed",
                                "message": f"Content validation failed: {str(e)}"
                            })
                            logger.error(f"📝 [ERROR] Set Redis status to 'failed' for validation process error")
                        except Exception as redis_e:
                            logger.error(f"❌ [DEBUG] Failed to set Redis validation error status: {str(redis_e)}")
                        return f"Content validation failed: {str(e)}"
                        
                    try:
                        task_type, task_id = self._get_active_task_id(job_profile_id, challenge_id, template_id, all_user_id)
                        task_redis_key = self._get_task_redis_key(task_type, task_id)
                        redis.set(task_redis_key, {
                            "status": "done",
                            "message": "Text content extracted successfully",
                            "content": result.get("content"),
                            "url": s3_text_url or s3_audio_url,
                            "size_bytes": text_size_bytes if 'text_size_bytes' in locals() else None,
                            "duration_secs": None
                        })
                        logger.info(f"📝 [DEBUG] Set Redis status to 'done' with content using key: {task_redis_key}")
                    except Exception as e:
                        logger.error(f"❌ [DEBUG] Failed to set Redis success status: {str(e)}")
            else:
                logger.warn(f"🚫 Unsupported file type: {content_type}")
                try:
                    redis.set(f"parrot_celery_tasks:audio_status:{job_profile_id}", {
                        "status": "failed",
                        "message": f"Unsupported file type: {content_type}"
                    })
                    logger.info(f"📝 [DEBUG] Set Redis status to 'failed' for unsupported type")
                except Exception as e:
                    logger.error(f"❌ [DEBUG] Failed to set Redis error status: {str(e)}")
                return 'Audio processing failed'


            # --- Existing logic continues here ---
            try:
                logger.info("Fetching trainee profile data")
                ipersona_user = IpersonaTraineeSchema(run_stage=run_stage)
                trainee_profile_data = ipersona_user.filter_by_alluser_id(
                    all_user_id=all_user_id, nopp=True, dataframe=False
                )
            except Exception as e:
                logger.error(f"Failed to fetch trainee profile data: {str(e)}")
                return 'Profile fetch failed'
            
            if not trainee_profile_data:
                logger.warn(f"No trainee user profiles found for all_user_id: {all_user_id}")
                return

            try:
                tinder_user_profile_id = trainee_profile_data.get('id')
                logger.info(f"Extracted tinder_user_profile_id: {tinder_user_profile_id}")
            except Exception as e:
                logger.error(f"Failed to extract tinder_user_profile_id: {str(e)}")
                return 'Profile ID extraction failed'
                
            if not tinder_user_profile_id:
                logger.error("Invalid trainee profile: missing ID")
                return

            try:
                logger.info("Reading external audio analysis prompt")
                external_audio_prompt = util.file_reader(util.prompt_path('external_audio_analysis.txt'))
                realtime_prompt = util.file_reader(util.prompt_path('realtime_evaluation.txt'))
                logger.info(f"Loaded prompts - external_audio_prompt length: {len(external_audio_prompt)}, realtime_prompt length: {len(realtime_prompt)}")
            except Exception as e:
                logger.error(f"Failed to read prompts: {str(e)}")
                return 'Prompt reading failed'

            try:
                logger.info("Replacing placeholders in prompts")
                external_aud_prompt = external_audio_prompt.replace("{transcription}", str(transcript)).replace("{realtime}", str(realtime_prompt))
                logger.info(f"Final prompt length: {len(external_aud_prompt)}")
            except Exception as e:
                logger.error(f"Failed to replace prompt placeholders: {str(e)}")
                return 'Prompt processing failed'

            try:
                logger.info("Sending prompt to GPT for analysis")
                data = gpt.openai_gpt_assistant_without_streaming(external_aud_prompt)
            except Exception as e:
                logger.error(f"GPT analysis failed: {str(e)}")
                return 'GPT analysis failed'
                
            try:
                # Extract JSON from the llm_client response (handled automatically by extract_json)
                response = util.extract_json(data, quite=False)
                logger.info("Response from GPT", response)
            except Exception as e:
                logger.error(f"Failed to extract JSON from GPT response: {str(e)}")
                return 'JSON extraction failed'
            
            if not response:
                logger.error("❌ Failed to process upload file: No data returned from transcription")
                return

            try:
                logger.info("Creating session for audio processing")

                base_meta = self._build_upload_meta(
                    s3_url=s3_audio_url or s3_text_url,
                    content_type=content_type,
                    filename=filename,
                    audio_path=audio_path,
                    contents=contents if 'contents' in locals() else None,
                    text_size_bytes=text_size_bytes if 'text_size_bytes' in locals() else None,
                )

                upload_metadata = {
                    "mode": "combined_mode",
                    "source": "uploaded_file",
                    "content": base_meta
                }

                saved_session = util.create_session(
                    run_stage,
                    mode,
                    template,
                    external,
                    challenge,
                    all_user_id,
                    tinder_user_profile_id,
                    job_profile_id,
                    template_id,
                    challenge_id,
                    message,
                    upload_metadata
                )
                logger.info(f"Session creation result: {saved_session}")
            except Exception as e:
                logger.error(f"Session creation failed: {str(e)}")
                return 'Session creation failed'

            if saved_session and isinstance(saved_session, dict):
                try:
                    sessionId = saved_session['id']
                    logger.info(f"📥 Session created successfully with ID: {sessionId}")
                except Exception as e:
                    logger.error(f"Failed to extract session ID: {str(e)}")
                    return 'Session ID extraction failed'
                    
                try:
                    logger.info("Saving transcribed chat to database")
                    saved = strapi.save_messages_to_db(response, sessionId)
                    logger.info(f"Save message result: {saved}")
                except Exception as e:
                    logger.error(f"Failed to save message to database: {str(e)}")
                    return 'Message save failed'

                try:
                    logger.info("Starting overall evaluation in a separate thread")
                    def run_overall():
                        try:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            logger.info("Created new event loop for overall evaluation")
                            overall = loop.run_until_complete(
                                self.overall_interview_evaluations_external(
                                    run_stage,
                                    response,
                                    'External',
                                    sessionId,
                                    all_user_id,
                                    tinder_user_profile_id,
                                    job_profile_id,
                                    challenge_id,
                                    template_id,
                                    'job_interview_config'
                                )
                            )

                            if overall:
                                logger.info("✅ Overall evaluation completed successfully")
                                redis.set(f"parrot_celery_tasks:audio_status:{job_profile_id}", {
                                    "status": "done",
                                    "message": "Chat Saved Successfully",
                                    "chat": saved,
                                    "overall": overall
                                })
                                    # Emit success event for template answer completion
                                try:
                                    from api.socket.core import emit_with_log
                                    # if user_sid:
                                    #     logger.info(f"[EMIT] event=processing_update_success sid={user_sid} payload=status: completed successfully ...")
                                        # loop.run_until_complete(
                                        #     emit_with_log(
                                        # "processing_update_success",
                                        # {"status": "✅ Uploaded file analysis completed successfully!"},
                                        #         sid=user_sid,
                                        #     )
                                        # )
                                    logger.info(f"📢 [NOTIFICATION] Invoking save_notification for SUCCESS - all_user_id={all_user_id}")
                                    self.save_notification(all_user_id, run_stage, f"Uploaded file analysis completed successfully!")
                                    logger.info(f"📢 [NOTIFICATION] save_notification SUCCESS invocation completed for all_user_id={all_user_id}")
                                except Exception as emit_error:
                                    logger.error(f"❌ [NOTIFICATION][ERROR] Failed to save SUCCESS notification - sid={user_sid} err={emit_error}", exc_info=True)
                            else:
                                logger.error("❌ Overall evaluation failed")
                        except Exception as e:
                            logger.error(f"Error in overall evaluation: {str(e)}")

                    t = threading.Thread(target=run_overall)
                    t.start()
                    logger.success("🎉 EXTERNAL AUDIO PROCESSED AND SAVED SUCCESSFULLY!")
               
                except Exception as e:
                    logger.error(f"❌ [ERROR] Failed to start overall evaluation thread: {str(e)}")
                    return 'Threading failed'
            elif isinstance(saved_session, str):
                logger.error(f"Session creation returned error string: {saved_session}")
                return f'Session creation failed: {saved_session}'
            else:
                logger.error(f"Session creation returned invalid result: {saved_session}")
                return 'Session creation returned invalid result'

        except Exception as e:
            # Only log if this is an unexpected system error, not a validation failure
            if "No Valuable matched question-answer data" not in str(e):
                logger.error(f"Critical error in audio processing: {str(e)}")
            
            try:
                task_type, task_id = self._get_active_task_id(job_profile_id, challenge_id, template_id, all_user_id)
                task_redis_key = self._get_task_redis_key(task_type, task_id)
                redis.set(task_redis_key, {"status": "failed", "message": str(e)})
                if "No Valuable matched question-answer data" not in str(e):
                    logger.info(f"Updated Redis status to failed for {task_type}:{task_id}")
            except Exception as redis_error:
                logger.error(f"Failed to update Redis status: {str(redis_error)}")
            
            # Re-raise the exception so Celery knows the task failed
            raise e
            
        logger.info("External audio processing completed successfully")
        return 'done'

    async def process_upload_external_files(
        self,
        question_filename,
        question_content_type,
        question_audio_path,
        question_contents,
        answer_filename,
        answer_content_type,
        answer_audio_path,
        answer_contents,
        job_profile_id,
        challenge_id,
        template_id,
        all_user_id,
        external,
        run_stage,
        user_sid=None
     ):
        redis = RedisBase()
        try:

            # --- Process Question File using helper ---
            question_transcript, question_error_msg = await self.process_and_transcribe_file(
                question_filename, question_content_type, question_contents, "Question"
            )

            if question_error_msg:
                error_msg = f"Question file processing failed: {question_error_msg}"
                task_type, task_id = self._get_active_task_id(job_profile_id, challenge_id, template_id, all_user_id)
                task_redis_key = self._get_task_redis_key(task_type, task_id)
                redis.set(task_redis_key, {"status": "failed", "message": error_msg})
                raise Exception(error_msg)

            # --- Process Answer File using helper ---
            logger.info(f"🔊 [DEBUG] Processing answer file: {answer_filename}, content_type: {answer_content_type}, size: {len(answer_contents)} bytes")
            answer_transcript, answer_error_msg = await self.process_and_transcribe_file(
                answer_filename, answer_content_type, answer_contents, "Answer"
            )
            logger.info(f"🔊 [DEBUG] Answer processing result - transcript: {answer_transcript[:100] if answer_transcript else 'None'}..., error: {answer_error_msg}")
            
            if answer_error_msg:
                error_msg = f"Answer file processing failed: {answer_error_msg}"
                task_type, task_id = self._get_active_task_id(job_profile_id, challenge_id, template_id, all_user_id)
                task_redis_key = self._get_task_redis_key(task_type, task_id)
                redis.set(task_redis_key, {"status": "failed", "message": error_msg})
                raise Exception(error_msg)

            # Ensure transcripts are not None after helper calls (should be handled by error_msg)
            if question_transcript is None or answer_transcript is None:
                error_msg = "One or both transcripts are missing after file processing. Cannot proceed."
                logger.error(error_msg)
                task_type, task_id = self._get_active_task_id(job_profile_id, challenge_id, template_id, all_user_id)
                task_redis_key = self._get_task_redis_key(task_type, task_id)
                redis.set(task_redis_key, {"status": "failed", "message": "Missing transcripts for analysis."})
                raise Exception(error_msg)

            logger.info("✅ Both question and answer files processed successfully.")

            # --- Upload both assets to S3 and collect URLs (simplified via helper) ---
            try:
                question_url, q_duration, q_size = self._upload_and_get_duration(question_filename, question_content_type, question_contents)
                answer_url, a_duration, a_size = self._upload_and_get_duration(answer_filename, answer_content_type, answer_contents)
            except Exception as s3e:
                task_type, task_id = self._get_active_task_id(job_profile_id, challenge_id, template_id, all_user_id)
                task_redis_key = self._get_task_redis_key(task_type, task_id)
                redis.set(task_redis_key, {"status": "failed", "message": f"S3 upload failed: {str(s3e)}"})
                raise

            # --- Remaining Original Logic (now much cleaner) ---
            logger.info("Fetching trainee profile data")
            ipersona_user = IpersonaTraineeSchema(run_stage=run_stage)
            trainee_profile_data = ipersona_user.filter_by_alluser_id(
                all_user_id=all_user_id, nopp=True, dataframe=False
            )
            if not trainee_profile_data:
                error_msg = f"No trainee user profiles found for all_user_id: {all_user_id}"
                logger.warn(error_msg)
                task_type, task_id = self._get_active_task_id(job_profile_id, challenge_id, template_id, all_user_id)
                task_redis_key = self._get_task_redis_key(task_type, task_id)
                redis.set(task_redis_key, {"status": "failed", "message": "No trainee user profiles found"})
                raise Exception(error_msg)

            tinder_user_profile_id = trainee_profile_data.get('id')
            logger.info(f"📋 [DEBUG] Tinder user profile ID: {tinder_user_profile_id}")
            if not tinder_user_profile_id:
                error_msg = "Invalid trainee profile: missing ID"
                logger.error(error_msg)
                task_type, task_id = self._get_active_task_id(job_profile_id, challenge_id, template_id, all_user_id)
                task_redis_key = self._get_task_redis_key(task_type, task_id)
                redis.set(task_redis_key, {"status": "failed", "message": "Invalid trainee profile: missing ID"})
                raise Exception(error_msg)

            logger.info("Reading external audio analysis prompt")
            external_audio_prompt = util.file_reader(util.prompt_path('external_audio_analysis_for_separate_inputs.txt'))
            external_all_file_prompt = util.file_reader(util.prompt_path('external_audio_analysis.txt'))
            answer_question_matching = util.file_reader(util.prompt_path('answer_question_match.txt'))
            realtime_prompt = util.file_reader(util.prompt_path('realtime_evaluation.txt'))

            # Keep hardcoded test data as-is (already proper Python lists)
            logger.success(f"📋 [DEBUG] Question transcript: {question_transcript}")
            logger.success(f"📋 [DEBUG] Answer transcript: {answer_transcript}")
            logger.success(f"📋 [DEBUG] Answer transcript length: {len(str(answer_transcript))}")
  
            answer_question_match_scoring = answer_question_matching.replace("{questions_data}", question_transcript)\
                                                           .replace("{answers_data}", answer_transcript)

            logger.info("Sending prompt to GPT for analysis")
            # logger.info(f"📋 [DEBUG] Answer question match scoring: {answer_question_match_scoring}")
            data = gpt.openai_gpt_assistant_without_streaming(answer_question_match_scoring)
            if data and hasattr(data, 'content'):
                data = data.content.text
            response = util.extract_json(data, quite=False)

            # Filter out items with relevance_score >= 90
            filtered_data = []
            for item in response:
                try:
                    # CRITICAL: Never assign default values to sensitive data
                    if 'relevance_score' not in item:
                        logger.error(f"❌ CRITICAL: Missing relevance_score in item: {item}")
                        logger.error(f"❌ Cannot assign default values to sensitive matching data")
                        continue
                    
                    relevance_score = item['relevance_score']
                    
                    # Handle None values (unmatched questions) - skip them
                    if relevance_score is None:
                        logger.info(f"ℹ️ Skipping unmatched question (relevance_score: None)")
                        continue
                    
                    # Convert to int for comparison
                    relevance_score = int(relevance_score)
                    if relevance_score >= 90:
                        filtered_data.append({
                            'question': item['question'], 
                            'answer': item['answer']
                        })
                except (ValueError, TypeError) as e:
                    # If relevance_score is not a valid number, skip this item
                    logger.error(f"❌ Invalid relevance_score in item: {item.get('relevance_score')} - Error: {e}")
                    logger.error(f"❌ Cannot process item with invalid score data")
                    continue
            
            # =========================
            # Use structured matching instead of LLM-based matching
            response = self._structured_question_answer_matching(question_transcript, answer_transcript)
            logger.info(f"📋 [DEBUG] Structured matching response: {response}")

            # Use all matched results directly - embedding matcher already handles filtering
            # Directly use structured matching output (already filtered to what we need)
            filtered_data = response

            logger.info(f"📋 [DEBUG] Filtered data count: {len(filtered_data)}")
            # =========================

            # Proceed even if all are unmatched; only fail on invalid matcher response
            if filtered_data is None or not isinstance(filtered_data, list):
                error_msg = "Failed to process template answer: invalid matcher response, you should reupload correct files and try again"
                # if user_sid:
                #     logger.info(f"[EMIT] event=processing_update_failed sid={user_sid} payload=status: invalid matcher response")
                # await emit_with_log(
                #     "processing_update_failed",
                #         {"status": f"{error_msg}"},
                #         sid=user_sid,
                # )
                try:
                    logger.info(f"📢 [NOTIFICATION] Invoking save_notification for INVALID MATCHER RESPONSE - all_user_id={all_user_id}")
                    self.save_notification(all_user_id, run_stage, f"Invalid matcher response: {error_msg}")
                    logger.info(f"📢 [NOTIFICATION] save_notification invocation completed for all_user_id={all_user_id}")
                except Exception as emit_exc:
                    logger.error(f"❌ [NOTIFICATION][ERROR] Failed to save notification - err={emit_exc}", exc_info=True)
                logger.error(error_msg)
                task_type, task_id = self._get_active_task_id(job_profile_id, challenge_id, template_id, all_user_id)
                task_redis_key = self._get_task_redis_key(task_type, task_id)
                redis.set(task_redis_key, {"status": "failed", "message": error_msg})
                raise Exception(error_msg)
                
            if all(item.get('relevance_score') is None for item in filtered_data):
                error_msg = "Failed to process template answer: all questions unmatched, you should reupload correct files and try again"
                
                # Optional: notify failure via SID
                try:
                    if user_sid:
                        logger.info(f"[EMIT] event=processing_update_failed sid={user_sid} payload=status: all questions unmatched")
                        # await emit_with_log(
                        #     "processing_update_failed",
                        #     {"status": f"{error_msg}"},
                        #     sid=user_sid,
                        # )
                    logger.info(f"📢 [NOTIFICATION] Invoking save_notification for all_user_id={all_user_id}, error_msg='{error_msg}'")
                    self.save_notification(all_user_id, run_stage, f"All questions unmatched: {error_msg}")
                    logger.info(f"📢 [NOTIFICATION] save_notification invocation completed for all_user_id={all_user_id}")
                except Exception as emit_exc:
                    logger.error(f"❌ [NOTIFICATION][ERROR] Failed to save notification - sid={user_sid} err={emit_exc}", exc_info=True)

                logger.error(error_msg)
                task_type, task_id = self._get_active_task_id(job_profile_id, challenge_id, template_id, all_user_id)
                task_redis_key = self._get_task_redis_key(task_type, task_id)
                redis.set(task_redis_key, {"status": "failed", "message": error_msg})
                raise Exception(error_msg)

            logger.info(f"📋 [DEBUG] Filtered data count: {len(filtered_data)}")
            logger.info(f"📋 [DEBUG] All relevance scores: {[item.get('relevance_score', 'N/A') for item in response]}")

            external_audio_prompt = external_audio_prompt.replace("{question_answer_data}", str(filtered_data))\
                                                           .replace("{realtime}", str(realtime_prompt))
            # logger.info(f"📋 [DEBUG] External audio prompt: {external_audio_prompt}")
            data = gpt.openai_gpt_assistant_without_streaming(external_audio_prompt)
            response = util.extract_json(data, quite=False)
            logger.info("Matched question-answer data returned from LLM analysis with the new interview structure")
            logger.info(f"📋 [DEBUG] Q Response: {response}")
           
            # Initialize these for util.create_session (as per original logic)
            message = ''
            template = False
            challenge = False
            mode = None

            # Build upload metadata with distinct URLs, optional durations, and sizes
            upload_metadata = {
                "mode": "qa_split_mode",
                "source": "uploaded_file",
                "question": {
                    "url": question_url,
                    "content_type": question_content_type,
                    "original_filename": question_filename,
                    "duration_secs": q_duration,
                    "size_bytes": q_size
                },
                "answer": {
                    "url": answer_url,
                    "content_type": answer_content_type,
                    "original_filename": answer_filename,
                    "duration_secs": a_duration,
                    "size_bytes": a_size
                }
            }
                        
            saved_session = util.create_session(
                run_stage,
                mode,
                template,
                external,
                challenge,
                all_user_id,
                tinder_user_profile_id,
                job_profile_id,
                template_id,
                challenge_id,
                message,
                upload_metadata
            )

            if saved_session:
                # Check if saved_session is a valid dictionary with an 'id' field
                if isinstance(saved_session, dict) and 'id' in saved_session:
                    sessionId = saved_session['id']
                    logger.info(f"📥 Session created successfully with ID: {sessionId}")
                    logger.info("Saving analyzed chat to database")
                    saved = strapi.save_messages_to_db(response, sessionId)
                else:
                    # Handle case where saved_session is not a valid session object
                    logger.error(f"❌ Invalid session data returned: {type(saved_session)} - {saved_session}")
                    logger.error("❌ Failed to save session - invalid session data")
                    task_type, task_id = self._get_active_task_id(job_profile_id, challenge_id, template_id, all_user_id)
                    task_redis_key = self._get_task_redis_key(task_type, task_id)
                    redis.set(task_redis_key, {"status": "failed", "message": "Invalid session data returned"})
                    return

                logger.info("Starting overall evaluation in a separate thread")
                def run_overall_sync_wrapper():
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)

                        overall = loop.run_until_complete(
                            self.overall_interview_evaluations_external(
                                run_stage,
                                response,
                                'External',
                                sessionId,
                                all_user_id,
                                tinder_user_profile_id,
                                job_profile_id,
                                challenge_id,
                                template_id,
                                'job_interview_config'
                            )
                        )
                        
                        if overall:
                            logger.info("✅ Overall evaluation completed successfully")
                            task_type, task_id = self._get_active_task_id(job_profile_id, challenge_id, template_id, all_user_id)
                            task_redis_key = self._get_task_redis_key(task_type, task_id)
                            redis.set(task_redis_key, {
                                "status": "done",
                                "message": "Chat Saved Successfully",
                                "chat": saved,
                                "overall": overall,
                                "emit_success": True  # Flag for socket emission
                            })
                            
                            # Emit success event for template answer completion
                            try:
                                from api.socket.core import emit_with_log
                                # Optional: notify failure via SID
                                # if user_sid:
                                #     asyncio.run(
                                #         emit_with_log(
                                #     "processing_update_success",
                                #     {"status": "✅ Uploaded file analysis completed successfully!"},
                                #             sid=user_sid,
                                #         )
                                #     )
                                logger.info(f"📢 [NOTIFICATION] Invoking save_notification for SUCCESS - all_user_id={all_user_id}")
                                self.save_notification(all_user_id, run_stage, f"Uploaded file analysis completed successfully!")
                                logger.info(f"📢 [NOTIFICATION] save_notification SUCCESS invocation completed for all_user_id={all_user_id}")
     
                            except Exception as emit_error:
                                logger.error(f"❌ [NOTIFICATION][ERROR] Failed to save SUCCESS notification - err={emit_error}", exc_info=True)
                        else:
                            logger.error("❌ Overall evaluation failed")
                            return False

                       
                    except Exception as e:
                        logger.error(f"Error in overall evaluation thread: {str(e)}", exc_info=True)
                        task_type, task_id = self._get_active_task_id(job_profile_id, challenge_id, template_id, all_user_id)
                        task_redis_key = self._get_task_redis_key(task_type, task_id)
                        redis.set(task_redis_key, {"status": "failed", "message": str(e)})

                t = threading.Thread(target=run_overall_sync_wrapper)
                t.start()
                
                # Wait for thread completion and emit socket event if successful
                t.join()  # Wait for thread to complete
                
                # Check if success was indicated
                task_type, task_id = self._get_active_task_id(job_profile_id, challenge_id, template_id, all_user_id)
                task_redis_key = self._get_task_redis_key(task_type, task_id)
                status_data = redis.get(task_redis_key)
            
            else:
                logger.error("❌ Failed to save session")
                task_type, task_id = self._get_active_task_id(job_profile_id, challenge_id, template_id, all_user_id)
                task_redis_key = self._get_task_redis_key(task_type, task_id)
                redis.set(task_redis_key, {"status": "failed", "message": "Session Not Saved"})

        except Exception as e:
            if job_profile_id:
                task_type, task_id = self._get_active_task_id(job_profile_id, challenge_id, template_id, all_user_id)
                task_redis_key = self._get_task_redis_key(task_type, task_id)
                redis.set(task_redis_key, {"status": "failed", "message": f"System error: {str(e)}"})
            # Re-raise the exception so Celery knows the task failed
 
    async def process_upload_external_answer_with_template(
        self,
        template_questions,
        answer_filename,
        answer_content_type,
        answer_audio_path,
        answer_contents,
        job_profile_id,
        challenge_id,
        template_id,
        all_user_id,
        external,
        run_stage,
        user_sid=None
    ):
        """
        Process answer file with template questions instead of question file.
        Uses template_questions directly instead of reading from question file.
        """
        redis = RedisBase()
        try:
     
            answer_transcript = False
            answer_error_msg = False
            # Process Answer File using helper
            if not answer_transcript:
                logger.info(f"🔊 [DEBUG] Processing answer file: {answer_filename}, content_type: {answer_content_type}, size: {len(answer_contents)} bytes")
                answer_transcript, answer_error_msg = await self.process_and_transcribe_file(
                    answer_filename, answer_content_type, answer_contents, "Answer"
                )
                import ast
                # Add detailed logs before parsing
                preview = str(answer_transcript)[:200] if answer_transcript is not None else 'None'
                logger.info(f"[PARSE] answer_transcript pre-parse type={type(answer_transcript)} len={len(str(answer_transcript)) if answer_transcript is not None else 0} preview={preview}")
                # Try safe parsing in order: literal_eval for python-like lists, then JSON
                if isinstance(answer_transcript, str):
                    parsed_ok = False
                    try:
                        answer_transcript = ast.literal_eval(answer_transcript)
                        parsed_ok = True
                        logger.info("[PARSE] literal_eval succeeded for answer_transcript")
                    except Exception as e:
                        logger.error(f"[PARSE][ERROR] literal_eval failed: {e}")
                        try:
                            answer_transcript = json.loads(answer_transcript)
                            parsed_ok = True
                            logger.info("[PARSE] json.loads succeeded for answer_transcript")
                        except Exception as je:
                            logger.error(f"[PARSE][ERROR] json.loads failed: {je}")
                    if not parsed_ok:
                        logger.info("[PARSE] Using raw string answer_transcript (parsing not applicable)")
                # If still a string, attempt to extract JSON structure
                answer_transcript = util.extract_json(answer_transcript, quite=False)
                logger.info(f"🔊 [DEBUG] Answer processing result - transcript: {type(answer_transcript)} : length {len(answer_transcript) if hasattr(answer_transcript,'__len__') else 'N/A'}..., error: {answer_error_msg}")

            logger.info(f"🔊 [DEBUG] Answer processing result - transcript: {type(answer_transcript)} : length {len(answer_transcript)}..., error: {answer_error_msg}")
            
            if answer_error_msg:
                error_msg = f"Answer file processing failed: {answer_error_msg}"
                task_type, task_id = self._get_active_task_id(job_profile_id, challenge_id, template_id, all_user_id)
                task_redis_key = self._get_task_redis_key(task_type, task_id)
                redis.set(task_redis_key, {"status": "failed", "message": error_msg})
                raise Exception(error_msg)

            # Ensure transcript is not None after helper call
            if answer_transcript is None:
                error_msg = "Answer transcript is missing after file processing. Cannot proceed."
                logger.error(error_msg)
                redis.set(f"parrot_celery_tasks:audio_status:{job_profile_id}", {"status": "failed", "message": "Missing answer transcript for analysis."})
                raise Exception(error_msg)

            logger.info("✅ Answer file processed successfully.")
            logger.info(f"🤖 [DEBUG] Answer transcript: {answer_transcript}")

            # AI Validation: Check if answer content is suitable for evaluation
            logger.info(f"🤖 [DEBUG] Starting AI validation for answer content")
            answer_validation = self.ai_validate_answer_content(answer_transcript, template_questions)
            logger.info(f"🤖 [DEBUG] Answer validation result: {answer_validation}")
        
            if not answer_validation.get("valid", False):
                error_msg = f"Answer content validation failed: {answer_validation.get('reason', 'Unknown validation error')}"
                logger.error(error_msg)
                # if user_sid:
                #     await emit_with_log(
                #         "processing_update_failed",
                #         {"status": f"{error_msg}"},
                #             sid=user_sid,
                #     )
                try:
                    logger.info(f"📢 [NOTIFICATION] Invoking save_notification for ANSWER VALIDATION FAILED - all_user_id={all_user_id}, error_msg='{error_msg}'")
                    self.save_notification(all_user_id, run_stage, f"Answer content validation failed: {error_msg}")
                    logger.info(f"📢 [NOTIFICATION] save_notification invocation completed for all_user_id={all_user_id}")
                except Exception as emit_exc:
                    logger.error(f"❌ [NOTIFICATION][ERROR] Failed to save notification - err={emit_exc}", exc_info=True)
                task_type, task_id = self._get_active_task_id(job_profile_id, challenge_id, template_id, all_user_id)
                task_redis_key = self._get_task_redis_key(task_type, task_id)
                redis.set(task_redis_key, {
                    "status": "failed", 
                    "message": error_msg,
                    "validation_details": answer_validation
                })
                raise Exception(error_msg)
            
            logger.info(f"✅ Answer content validation passed with confidence: {answer_validation.get('confidence', 'N/A')}")

            # Upload answer asset to S3 and prepare upload metadata
            try:
                answer_url, a_duration, a_size = self._upload_and_get_duration(
                    answer_filename, answer_content_type, answer_contents
                )
                
                upload_metadata = {
                    "mode": "answer_only_mode",
                    "source": "uploaded_file",
                    "answer": {
                        "url": answer_url,
                        "content_type": answer_content_type,
                        "original_filename": answer_filename,
                        "duration_secs": a_duration,
                        "size_bytes": a_size
                    }
                }
                 
                 
            except Exception as s3e:
                task_type, task_id = self._get_active_task_id(job_profile_id, challenge_id, template_id, all_user_id)
                task_redis_key = self._get_task_redis_key(task_type, task_id)
                redis.set(task_redis_key, {"status": "failed", "message": f"S3 upload failed: {str(s3e)}"})
                raise

            # Convert template_questions to question text format
            question_text = self.convert_template_questions_to_text(template_questions)
            logger.info(f"🤖 [DEBUG] Question text: {question_text}")
            logger.info(f"📋 Converted {len(template_questions)} template questions to text format")
            

            # Fetch trainee profile data
            logger.info("Fetching trainee profile data")
            ipersona_user = IpersonaTraineeSchema(run_stage=run_stage)
            trainee_profile_data = ipersona_user.filter_by_alluser_id(
                all_user_id=all_user_id, nopp=True, dataframe=False
            )
            if not trainee_profile_data:
                error_msg = f"No trainee user profiles found for all_user_id: {all_user_id}"
                logger.warn(error_msg)
                task_type, task_id = self._get_active_task_id(job_profile_id, challenge_id, template_id, all_user_id)
                task_redis_key = self._get_task_redis_key(task_type, task_id)
                redis.set(task_redis_key, {"status": "failed", "message": "No trainee user profiles found"})
                raise Exception(error_msg)

            tinder_user_profile_id = trainee_profile_data.get('id')
            logger.info(f"📋 [DEBUG] Tinder user profile ID: {tinder_user_profile_id}")
            if not tinder_user_profile_id:
                error_msg = "Invalid trainee profile: missing ID"
                logger.error(error_msg)
                task_type, task_id = self._get_active_task_id(job_profile_id, challenge_id, template_id, all_user_id)
                task_redis_key = self._get_task_redis_key(task_type, task_id)
                redis.set(task_redis_key, {"status": "failed", "message": "Invalid trainee profile: missing ID"})
                raise Exception(error_msg)

            # Use structured matching instead of LLM-based matching
            response = self._structured_question_answer_matching(template_questions, answer_transcript)
            logger.info(f"📋 [DEBUG] Structured matching response: {response}")

            # Use all matched results directly - embedding matcher already handles filtering
            # Directly use structured matching output (already filtered to what we need)
            filtered_data = response

            logger.info(f"📋 [DEBUG] Filtered data count: {len(filtered_data)}")
            
            # Proceed even if all are unmatched; only fail on invalid matcher response
            if filtered_data is None or not isinstance(filtered_data, list):
                error_msg = "Failed to process template answer: invalid matcher response, you should reupload correct files and try again"
                # if user_sid:
                #     logger.info(f"[EMIT] event=processing_update_failed sid={user_sid} payload=status: invalid matcher response")
                #     await emit_with_log(
                #         "processing_update_failed",
                #         {"status": f"{error_msg}"},
                #         sid=user_sid,
                #     )
                try:
                    logger.info(f"📢 [NOTIFICATION] Invoking save_notification for INVALID MATCHER RESPONSE - all_user_id={all_user_id}")
                    self.save_notification(all_user_id, run_stage, f"Invalid matcher response: {error_msg}")
                    logger.info(f"📢 [NOTIFICATION] save_notification invocation completed for all_user_id={all_user_id}")
                except Exception as emit_exc:
                    logger.error(f"❌ [NOTIFICATION][ERROR] Failed to save notification - err={emit_exc}", exc_info=True)
                logger.error(error_msg)
                task_type, task_id = self._get_active_task_id(job_profile_id, challenge_id, template_id, all_user_id)
                task_redis_key = self._get_task_redis_key(task_type, task_id)
                redis.set(task_redis_key, {"status": "failed", "message": error_msg})
                raise Exception(error_msg)
                
            if all(item.get('relevance_score') is None for item in filtered_data):
                error_msg = "Failed to process template answer: all questions unmatched, you should reupload correct files and try again"
                
                # Optional: notify failure via SID
                try:
                    # if user_sid:
                    #     logger.info(f"[EMIT] event=processing_update_failed sid={user_sid} payload=status: all questions unmatched")
                    #     await emit_with_log(
                    #         "processing_update_failed",
                    #         {"status": f"{error_msg}"},
                    #                 sid=user_sid,
                    #     )
                    logger.info(f"📢 [NOTIFICATION] Invoking save_notification for ALL QUESTIONS UNMATCHED - all_user_id={all_user_id}, error_msg='{error_msg}'")
                    self.save_notification(all_user_id, run_stage, f"All questions unmatched: {error_msg}")
                    logger.info(f"📢 [NOTIFICATION] save_notification invocation completed for all_user_id={all_user_id}")
                except Exception as emit_exc:
                    logger.error(f"❌ [NOTIFICATION][ERROR] Failed to save notification - sid={user_sid} err={emit_exc}", exc_info=True)

                logger.error(error_msg)
                task_type, task_id = self._get_active_task_id(job_profile_id, challenge_id, template_id, all_user_id)
                task_redis_key = self._get_task_redis_key(task_type, task_id)
                redis.set(task_redis_key, {"status": "failed", "message": error_msg})
                raise Exception(error_msg)

            logger.info("Replacing placeholders in prompts")
            
            realtime_prompt = util.file_reader(util.prompt_path('realtime_evaluation.txt'))
            external_audio_prompt = util.file_reader(util.prompt_path('external_audio_analysis_for_separate_inputs.txt'))
            external_audio_prompt = external_audio_prompt.replace("{question_answer_data}", json.dumps(filtered_data, ensure_ascii=False))\
                                                           .replace("{realtime}", str(realtime_prompt))
            data = gpt.openai_gpt_assistant_without_streaming(external_audio_prompt)
            response = util.extract_json(data, quite=False)
           
            # Initialize these for util.create_session (as per original logic)
            message = ''
            template = False
            challenge = False
            mode = None

            saved_session = util.create_session(
                run_stage,
                mode,
                template,
                external,
                challenge,
                all_user_id,
                tinder_user_profile_id,
                job_profile_id,
                template_id,
                challenge_id,
                message,
                upload_metadata
            )

            if saved_session:
                # Check if saved_session is a valid dictionary with an 'id' field
                if isinstance(saved_session, dict) and 'id' in saved_session:
                    sessionId = saved_session['id']
                    logger.info(f"📥 Session created successfully with ID: {sessionId}")
                    saved = strapi.save_messages_to_db(response, sessionId)
                else:
                    # Handle case where saved_session is not a valid session object
                    logger.error(f"❌ Invalid session data returned: {type(saved_session)} - {saved_session}")
                    logger.error("❌ Failed to save session - invalid session data")
                    task_type, task_id = self._get_active_task_id(job_profile_id, challenge_id, template_id, all_user_id)
                    task_redis_key = self._get_task_redis_key(task_type, task_id)
                    redis.set(task_redis_key, {"status": "failed", "message": "Invalid session data returned"})
                    return

                logger.info("Starting overall evaluation in a separate thread")
                def run_overall_sync_wrapper():
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)

                        overall = loop.run_until_complete(
                            self.overall_interview_evaluations_external(
                                run_stage,
                                response,
                                'External',
                                sessionId,
                                all_user_id,
                                tinder_user_profile_id,
                                job_profile_id,
                                challenge_id,
                                template_id,
                                'job_interview_config'
                            )
                        )

                        if overall:
                            logger.info("✅ Overall evaluation completed successfully")
                            task_type, task_id = self._get_active_task_id(job_profile_id, challenge_id, template_id, all_user_id)
                            task_redis_key = self._get_task_redis_key(task_type, task_id)
                            redis.set(task_redis_key, {
                                "status": "done",
                                "message": "Chat Saved Successfully",
                                "chat": saved,
                                "overall": overall
                            })
                            
                            # Emit success event for template answer completion
                            try:
                                from api.socket.core import emit_with_log
                                # if user_sid:
                                #     loop.run_until_complete(
                                #         emit_with_log(
                                #             "processing_update_success",
                                #             {"status": "✅ Uploaded file analysis completed successfully!"},
                                #             sid=user_sid,
                                #         )
                                #     )
                                logger.info(f"📢 [NOTIFICATION] Invoking save_notification for SUCCESS - all_user_id={all_user_id}")
                                self.save_notification(all_user_id, run_stage, f"Uploaded file analysis completed successfully!")
                                logger.info(f"📢 [NOTIFICATION] save_notification SUCCESS invocation completed for all_user_id={all_user_id}")
                            except Exception as emit_error:
                                logger.error(f"❌ [NOTIFICATION][ERROR] Failed to save SUCCESS notification - err={emit_error}", exc_info=True)
                        else:
                            logger.error("❌ Overall evaluation failed")
                    except Exception as e:
                        logger.error(f"Error in overall evaluation thread: {str(e)}", exc_info=True)
                        task_type, task_id = self._get_active_task_id(job_profile_id, challenge_id, template_id, all_user_id)
                        task_redis_key = self._get_task_redis_key(task_type, task_id)
                        redis.set(task_redis_key, {"status": "failed", "message": str(e)})

                t = threading.Thread(target=run_overall_sync_wrapper)
                t.start()
                logger.success("🎉 TEMPLATE ANSWER PROCESSED AND SAVED SUCCESSFULLY!")
            else:
                logger.error("❌ Failed to save session")
                task_type, task_id = self._get_active_task_id(job_profile_id, challenge_id, template_id, all_user_id)
                task_redis_key = self._get_task_redis_key(task_type, task_id)
                redis.set(task_redis_key, {"status": "failed", "message": "Session Not Saved"})

        except Exception as e:
            logger.error(f"🔥 Critical error in template answer background processing: {str(e)}")
            if job_profile_id:
                task_type, task_id = self._get_active_task_id(job_profile_id, challenge_id, template_id, all_user_id)
                task_redis_key = self._get_task_redis_key(task_type, task_id)
                redis.set(task_redis_key, {"status": "failed", "message": f"System error: {str(e)}"})
            # Re-raise the exception so Celery knows the task failed
            # raise e 

    def convert_template_questions_to_text(self, template_questions):
        """
        Convert template_questions array to text format for LLM processing.
        """
        if not template_questions:
            return ""
        
        question_text = ""
        for section in template_questions:
            if isinstance(section, dict) and 'questions' in section:
                section_type = section.get('sectionType', 'Unknown Section')
                questions = section.get('questions', [])
                
                question_text += f"\n--- {section_type} ---\n"
                for question in questions:
                    if isinstance(question, dict) and 'question' in question:
                        question_text += f"Q: {question['question']}\n"
                        if 'ideal_answer' in question:
                            question_text += f"Ideal Answer: {question['ideal_answer']}\n"
                        question_text += "\n"
        
        return question_text.strip()
 
    def _structured_question_answer_matching(self, template_questions, answer_transcript):
        """
        Use structured matching system instead of LLM-based matching.
        
        Args:
            template_questions: Raw template questions data
            answer_transcript: Raw answer transcript (str or list)
            
        Returns:
            List of matching results in the expected format
        """
        try:
            from api.utils.question_answer_matcher import QuestionAnswerMatcher
            logger.info(f"🔍 [DEBUG] Template questions: type {type(template_questions)} ::length {len(template_questions)}")
            logger.info(f"🔍 [DEBUG] Answer transcript: type {type(answer_transcript)} :: length {len(answer_transcript)}")
            # Initialize matcher
            matcher = QuestionAnswerMatcher()
            
            # Perform matching - pass the original answer_transcript (list or string)
            result = matcher.match_questions_answers(template_questions, answer_transcript)
            logger.info(f"🔍 [DEBUG] Result: type {type(result)} :: {result}")

            if "error" in result:
                logger.error(f"Structured matching error: {result['error']}")
                
                # Check if it's an OpenAI API key error
                if result.get("error") == "OpenAI API key required":
                    logger.error(f"❌ CRITICAL: OpenAI API key not configured")
                    logger.error(f"❌ Cannot use structured matching without valid embeddings")
                    logger.info("🔄 Falling back to LLM-based matching")
                    return self._fallback_llm_matching(template_questions, answer_transcript)
                else:
                    logger.error(f"❌ Structured matching failed with error: {result.get('details', 'Unknown error')}")
                    return []
            
            # Convert to expected format
            matches = []
            for match in result.get("matches", []):
                matches.append({
                    "question": match["question"],
                    "answer": match["answer"],
                    "relevance_score": match["relevance_score"],
                    "reason": match["reason"]
                })
            
            logger.info(f"Structured matching completed: {len(matches)} matches found")
            return matches
            
        except ImportError as e:
            logger.error(f"Failed to import QuestionAnswerMatcher: {e}")
            logger.info("Falling back to LLM-based matching")
            return self._fallback_llm_matching(template_questions, answer_transcript)
        except Exception as e:
            logger.error(f"Structured matching failed: {e}")
            logger.info("Falling back to LLM-based matching")
            return self._fallback_llm_matching(template_questions, answer_transcript)
    
    def _fallback_llm_matching(self, template_questions, answer_transcript):
        """
        Fallback to LLM-based matching if structured matching fails.
        
        Args:
            template_questions: Raw template questions data
            answer_transcript: Raw answer transcript (str or list)
            
        Returns:
            List of matching results
        """
        try:
            logger.info("Using fallback LLM-based matching")
            
            # Handle both string and list inputs for answer_transcript
            if isinstance(answer_transcript, list):
                # Join list items into a single string
                answer_text = " ".join(str(item) for item in answer_transcript if item)
                logger.info(f"Converting list transcript to string for LLM: {len(answer_transcript)} items")
            else:
                answer_text = str(answer_transcript)
            
            # Convert questions to text
            question_text = self.convert_template_questions_to_text(template_questions)
            
            # Read LLM prompt
            answer_question_matching = util.file_reader(util.prompt_path('answer_question_match.txt'))
            
            # Replace placeholders
            answer_question_match_scoring = answer_question_matching.replace("{questions_data}", question_text)\
                                                               .replace("{answers_data}", answer_text)
            
            # Send to GPT
            data = gpt.openai_gpt_assistant_without_streaming(answer_question_match_scoring)
            if data and hasattr(data, 'content'):
                data = data.content.text
            response = util.extract_json(data, quite=False)
            
            logger.info(f"Fallback LLM response: {response}")
            return response
            
        except Exception as e:
            logger.error(f"Fallback LLM matching also failed: {e}")
            return []
 


    def content_extraction_logics(self, filename: str, content: bytes, content_type: str) -> dict:
        try:
            files = {
                'file': (filename, content, content_type)
            }
            data = {
                'request_source': 'text_extraction_endpoint',
                'visual_description': 'false',
                'description_prompt': 'Extract readable content',
                'input_format': 'text'
            }
            endpoint_url = "https://content-extractor.10academy.org/content-extractor/extract"
            response = requests.post(endpoint_url, data=data, files=files, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result
        except requests.exceptions.HTTPError as e:
            return {
                "error": f"HTTP error: {e}",
                "details": e.response.text,
                "status_code": e.response.status_code
            }
        except Exception as e:
            return {
                "error": f"Unexpected error: {str(e)}",
                "status_code": 500
            }

    def audio_transcription_logics(self, filename: str, audio_path: str, content_type: str) -> dict:
        import time
        import os
        max_retries = 3
        base_timeout = 300  # 5 minutes
        max_file_size = 10 * 1024 * 1024  # 10MB
        
        # Check file size
        file_size = os.path.getsize(audio_path)
        logger.info(f"📏 [DEBUG] Audio file size: {file_size / (1024*1024):.2f} MB")
        
        if file_size > max_file_size:
            logger.info(f"⚠️ [DEBUG] File size ({file_size / (1024*1024):.2f} MB) exceeds limit ({max_file_size / (1024*1024):.2f} MB)")
            logger.info(f"🔄 [DEBUG] Attempting to compress audio file...")
            
            try:
                # Compress the audio file to reduce size
                logger.info(f"🔄 [DEBUG] Loading audio file: {audio_path}")
                
                # Detect file format and load accordingly
                if audio_path.lower().endswith('.mp4'):
                    audio = AudioSegment.from_file(audio_path, format="mp4")
                elif audio_path.lower().endswith('.mp3'):
                    audio = AudioSegment.from_mp3(audio_path)
                else:
                    # Try to auto-detect format
                    audio = AudioSegment.from_file(audio_path)
                
                logger.info(f"🔄 [DEBUG] Audio loaded successfully, duration: {len(audio)/1000:.2f}s")
                
                # Reduce quality to decrease file size
                compressed_audio = audio.export(format="mp3", bitrate="64k")
                
                # Create proper compressed filename
                base_name = audio_path.rsplit(".", 1)[0]
                compressed_path = f"{base_name}_compressed.mp3"
                logger.info(f"🔄 [DEBUG] Writing compressed file to: {compressed_path}")
                
                with open(compressed_path, "wb") as f:
                    f.write(compressed_audio.read())
                
                compressed_size = os.path.getsize(compressed_path)
                logger.info(f"✅ [DEBUG] Compressed file size: {compressed_size / (1024*1024):.2f} MB")
                audio_path = compressed_path
                filename = f"{filename.rsplit('.', 1)[0]}_compressed.mp3"
                
            except Exception as e:
                error_msg = f"Failed to compress audio file: {str(e)}"
                logger.error(f"❌ [DEBUG] {error_msg}")
            
                return {
                    "error": error_msg,
                    "status_code": 500
                }
        
        for attempt in range(max_retries):
            try:
                endpoint_url = "https://content-extractor.10academy.org/content-extractor/audio_transcript"
                # audio_path is already normalized when passed to this method
                with open(audio_path, 'rb') as audio_file:
                    files = {
                        'file': (filename, audio_file, content_type)
                    }
                    data = {
                        'request_id': 'audio-upload-001a',
                        'request_source': 'parrot_audio_upload',
                        'prompt': 'Extract the text from the audio file.',
                        'llm_provider': 'gemini',
                        'llm_model': 'gemini-2.5-flash'
                    }
                    logger.info(f"Sending audio file to external transcription endpoint... (Attempt {attempt + 1}/{max_retries})")
                    
                    # Exponential backoff timeout
                    current_timeout = base_timeout * (2 ** attempt)
                    response = requests.post(endpoint_url, files=files, data=data, timeout=current_timeout)
                    response.raise_for_status()
                    result = response.json()
                    return result
                    
            except requests.exceptions.Timeout as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 1, 2, 4 seconds
                    logger.info(f"⏳ [DEBUG] Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    return {
                        "error": f"Transcription timeout after {max_retries} attempts",
                        "details": f"Service timed out after {current_timeout}s on final attempt",
                        "status_code": 408
                    }
                    
            except requests.exceptions.HTTPError as e:
                logger.error(f"❌ [DEBUG] HTTP error on attempt {attempt + 1}: {str(e)}")
                if e.response.status_code == 504 and attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.info(f"⏳ [DEBUG] Gateway timeout, waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    return {
                        "error": f"HTTP error: {e}",
                        "details": e.response.text,
                        "status_code": e.response.status_code
                    }
                    
            except Exception as e:
                logger.error(f"❌ [DEBUG] Unexpected error on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.info(f"⏳ [DEBUG] Unexpected error, waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    return {
                        "error": f"Unexpected error: {str(e)}",
                        "status_code": 500
                    }
        
        return {
            "error": f"Transcription failed after {max_retries} attempts",
            "status_code": 500
        }

    def video_transcription_logics(self, filename: str, audio_path: str, content_type: str) -> dict:
        import time
        import os
        max_retries = 3
        base_timeout = 300  # 5 minutes
        max_file_size = 10 * 1024 * 1024  # 10MB
        
        # Check file size
        file_size = os.path.getsize(audio_path)
        logger.info(f"📏 [DEBUG] Audio file size: {file_size / (1024*1024):.2f} MB")
        
        if file_size > max_file_size:
            logger.info(f"⚠️ [DEBUG] File size ({file_size / (1024*1024):.2f} MB) exceeds limit ({max_file_size / (1024*1024):.2f} MB)")
            logger.info(f"🔄 [DEBUG] Attempting to compress audio file...")
            
            try:
                # Compress the audio file to reduce size
                logger.info(f"🔄 [DEBUG] Loading audio file: {audio_path}")
                
                # Detect file format and load accordingly
                if audio_path.lower().endswith('.mp4'):
                    audio = AudioSegment.from_file(audio_path, format="mp4")
                elif audio_path.lower().endswith('.mp3'):
                    audio = AudioSegment.from_mp3(audio_path)
                else:
                    # Try to auto-detect format
                    audio = AudioSegment.from_file(audio_path)
                
                logger.info(f"🔄 [DEBUG] Audio loaded successfully, duration: {len(audio)/1000:.2f}s")
                
                # Reduce quality to decrease file size
                compressed_audio = audio.export(format="mp3", bitrate="64k")
                
                # Create proper compressed filename
                base_name = audio_path.rsplit(".", 1)[0]
                compressed_path = f"{base_name}_compressed.mp3"
                logger.info(f"🔄 [DEBUG] Writing compressed file to: {compressed_path}")
                
                with open(compressed_path, "wb") as f:
                    f.write(compressed_audio.read())
                
                compressed_size = os.path.getsize(compressed_path)
                logger.info(f"✅ [DEBUG] Compressed file size: {compressed_size / (1024*1024):.2f} MB")
                audio_path = compressed_path
                filename = f"{filename.rsplit('.', 1)[0]}_compressed.mp3"
                
            except Exception as e:
                error_msg = f"Failed to compress audio file: {str(e)}"
                logger.error(f"❌ [DEBUG] {error_msg}")
         
                return {
                    "error": error_msg,
                    "status_code": 500
                }
        
        for attempt in range(max_retries):
            try:
                endpoint_url = "https://content-extractor.10academy.org/content-extractor/video_transcript"
                normalized_audio_path = self._normalize_audio_path(audio_path)
                with open(normalized_audio_path, 'rb') as audio_file:
                    files = {
                        'file': (filename, audio_file, content_type)
                    }
                    data = {
                        'url': '',
                        'user_prompt': 'Extract the text from the video file.',
                        'llm_provider': 'openai',
                        'gemini_model': 'gemini-2.5-flash',
                        'overwrite': 'false'
                    }
                    logger.info(f"Sending audio file to external transcription endpoint... (Attempt {attempt + 1}/{max_retries})")
                    logger.info(f"🔄 [DEBUG] Transcription attempt {attempt + 1}/{max_retries} with timeout: {base_timeout}s")
                    
                    # Exponential backoff timeout
                    current_timeout = base_timeout * (2 ** attempt)
                    response = requests.post(endpoint_url, files=files, data=data, timeout=current_timeout)
                    response.raise_for_status()
                    result = response.json()
                    logger.info(f"✅ [DEBUG] Transcription successful on attempt {attempt + 1}")
                    return result
                    
            except requests.exceptions.Timeout as e:
                logger.info(f"⏰ [DEBUG] Transcription timeout on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 1, 2, 4 seconds
                    logger.info(f"⏳ [DEBUG] Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    return {
                        "error": f"Transcription timeout after {max_retries} attempts",
                        "details": f"Service timed out after {current_timeout}s on final attempt",
                        "status_code": 408
                    }
                    
            except requests.exceptions.HTTPError as e:
                logger.info(f"❌ [DEBUG] HTTP error on attempt {attempt + 1}: {str(e)}")
                if e.response.status_code == 504 and attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.info(f"⏳ [DEBUG] Gateway timeout, waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    return {
                        "error": f"HTTP error: {e}",
                        "details": e.response.text,
                        "status_code": e.response.status_code
                    }
                    
            except Exception as e:
                logger.info(f"❌ [DEBUG] Unexpected error on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.info(f"⏳ [DEBUG] Unexpected error, waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    return {
                        "error": f"Unexpected error: {str(e)}",
                        "status_code": 500
                    }
        
        return {
            "error": f"Transcription failed after {max_retries} attempts",
            "status_code": 500
        }


    async def process_and_transcribe_file(self, filename: str, content_type: str, contents: bytes, file_type_label: str) -> Tuple[Optional[str], Optional[str]]:
        logger.info(f"🔊 Processing {file_type_label} file: {filename}")
        try:
            transcript: Optional[str] = None
            if "audio" in content_type or "video" in content_type:
                original_format = content_type.split("/")[-1].lower()
                logger.info(f"🔄 [DEBUG] {file_type_label} file format: {original_format}, content_type: {content_type}")
                logger.info(f"🔄 [DEBUG] Supported formats check: {original_format} in {['mpeg', 'mp3', 'wav', 'mp4', 'webm']}")
                
                if original_format not in ["mpeg", "mp3", "wav"]:
                    # Convert MP4, webm, and other formats to MP3 for consistent processing
                    logger.info(f"🔄 Converting {file_type_label} media file from {original_format} to mp3")
                    contents = util.convert_to_mp3(contents, original_format)
                    final_file_path = util.audio_path(filename.rsplit(".", 1)[0] + ".mp3")
                    with open(final_file_path, "wb") as f:
                        f.write(contents)
                    logger.success(f"🎧 {file_type_label} MP3 file saved to: {final_file_path}")
                    logger.info(f"🔄 [DEBUG] Converted to MP3: {final_file_path}")
                else:
                    logger.info(f"✅ {file_type_label} file already in supported audio format. Skipping re-saving.")
                    final_file_path = util.audio_path(filename)
                    logger.info(f"🔄 [DEBUG] Using original file path: {final_file_path}")
                result = self.audio_transcription_logics(
                    filename=filename,
                    audio_path=final_file_path,
                    content_type="audio/mpeg"
                )
                if "error" in result:
                    return None, f"Transcription failed: {result['error']}"
                
                transcript = result.get("content", "No transcription returned")
                
                # Validate transcription quality
                if not transcript or transcript.strip() == "":
                    return None, "Transcription failed: Empty or no content returned from audio processing"
                
                # Check for common error patterns in transcription (more specific)
                error_patterns = ["error processing", "failed to process", "unable to transcribe", "cannot transcribe", "no audio detected", "silence detected", "corrupted audio"]
                transcript_lower = transcript.lower()
                if any(pattern in transcript_lower for pattern in error_patterns):
                    return None, f"Transcription failed: Audio processing error detected in content: {transcript[:100]}..."
                
                # Only flag as too short if it's suspiciously short AND contains error-like content
                if len(transcript.strip()) < 5 and any(word in transcript_lower for word in ["error", "fail", "unable", "cannot"]):
                    return None, f"Transcription failed: Suspiciously short content with error indicators: {transcript}"
                prompt = f"""
                    You are given a raw block of text transcribed from an interview. This text may include either interview **questions** or **answers**, but not both at the same time.
                    Your task is to segment this text into a list of **logically grouped full responses** — where each item in the list represents **a complete question or answer**, not just an individual sentence or phrase.
                    🧠 IMPORTANT RULES:
                    - DO NOT break an answer or question into parts unless there's a **clear topic shift or speaker change**.
                    - Consider the **semantic flow** and meaning of the text — some responses are long and should remain as one block.
                    - DO NOT split just because a sentence ends. Multiple sentences can and often do belong to the same complete response.
                    - Only split when it is evident that a **new question** or **new response** has begun.
                    - If unsure whether to split or not — DO NOT split. Keep it as one unified chunk.
                    Your output must be a JSON list of grouped conversation turns, like:
                    [
                    "First full question or answer here.",
                    "Second full question or answer here.",
                    ...
                    ]
                    Now segment the following transcription:
                    {transcript}
                    """
                transcript = gpt.openai_gpt_assistant_without_streaming(prompt)
                # Extract text content from ModelResponse
                if transcript and hasattr(transcript, 'content'):
                    transcript = transcript.content.text
                logger.info(f"{file_type_label} transcription initialized")

            elif any(x in content_type for x in ["text", "pdf", "msword", "officedocument"]):
                logger.info(f"📝 {file_type_label} text-based file detected: {filename}")
                final_file_path = util.audio_path(filename)
                with open(final_file_path, "wb") as f:
                    f.write(contents)
                logger.success(f"💾 {file_type_label} text file saved to: {final_file_path}")
                result = self.content_extraction_logics(filename, contents, content_type)
                if "error" in result:
                    return None, f"Text extraction failed: {result['error']}"
                
                transcript = result.get("content", "No content returned")
                
                # Validate text extraction quality
                if not transcript or transcript.strip() == "":
                    return None, "Text extraction failed: Empty or no content returned from file processing"
                
                # Only flag as too short if it's suspiciously short AND contains error-like content
                if len(transcript.strip()) < 5 and any(word in transcript.lower() for word in ["error", "fail", "unable", "cannot", "corrupted"]):
                    return None, f"Text extraction failed: Suspiciously short content with error indicators: {transcript}"
                prompt = f"""
                    You are given a raw block of text transcribed from an interview. This text may include either interview **questions** or **answers**, but not both at the same time.
                    Your task is to segment this text into a list of **logically grouped full responses** — where each item in the list represents **a complete question or answer**, not just an individual sentence or phrase.
                    🧠 IMPORTANT RULES:
                    - DO NOT break an answer or question into parts unless there's a **clear topic shift or speaker change**.
                    - Consider the **semantic flow** and meaning of the text — some responses are long and should remain as one block.
                    - DO NOT split just because a sentence ends. Multiple sentences can and often do belong to the same complete response.
                    - Only split when it is evident that a **new question** or **new response** has begun.
                    - If unsure whether to split or not — DO NOT split. Keep it as one unified chunk.
                    Your output must be a JSON list of grouped conversation turns, like:
                    [
                    "First full question or answer here.",
                    "Second full question or answer here.",
                    ...
                    ]
                    Now segment the following transcription:
                    {transcript}
                    """
                transcript = gpt.openai_gpt_assistant_without_streaming(prompt)
                logger.info(f"🔄 [DEBUG] Transcript: {transcript}")
                # Extract text content from ModelResponse
                # if transcript and hasattr(transcript, 'content'):
                #     transcript = transcript.content.text
                # logger.success(f"✅ {file_type_label} text extraction successful: {filename}")
                # logger.info(f"{file_type_label} content extraction initialized")
            else:
                return None, f"Unsupported file type for {file_type_label}: {content_type}"
            return transcript, None

        except Exception as e:
            logger.error(f"❌ Error in {file_type_label} file processing: {e}", exc_info=True)
            return None, f"Processing failed for {file_type_label}: {e}"


    async def overall_interview_evaluations_external(
            self,
            run_stage, 
            data, 
            status, 
            sessionId, 
            all_user_id, 
            tinder_user_profile_id, 
            job_profile_id,
            challenge_id,
            template_id,
            type):
        """
        Evaluates the overall performance of a candidate in an interview.

        This asynchronous function assesses the candidate's overall performance 
        using their interview history and real-time evaluation results. It generates 
        overall evaluation metrics and saves the final chat history to the database.

        Parameters:
        ----------
        data : dict
            A dictionary containing session information, including the candidate's 
            responses and interview history.

        realtime_evaluation_response_json : dict
            A JSON object containing the results of the real-time evaluation.

        Returns:
        -------
        dict
            A JSON object containing the overall interview metrics and evaluation response, 
            or an error message if an exception occurs during processing.
        """
        try:
            # Convert string IDs to integers for proper boolean evaluation
            job_profile_id_int = None
            if job_profile_id and str(job_profile_id).strip():
                try:
                    job_profile_id_int = int(job_profile_id)
                except (ValueError, TypeError):
                    job_profile_id_int = None
            
            challenge_id_int = None
            if challenge_id and str(challenge_id).strip():
                try:
                    challenge_id_int = int(challenge_id)
                except (ValueError, TypeError):
                    challenge_id_int = None
            
            template_id_int = None
            if template_id and str(template_id).strip():
                try:
                    template_id_int = int(template_id)
                except (ValueError, TypeError):
                    template_id_int = None
            
            logger.info(f"🔍 [DEBUG] ID values - job_profile_id: '{job_profile_id}' -> {job_profile_id_int}, challenge_id: '{challenge_id}' -> {challenge_id_int}, template_id: '{template_id}' -> {template_id_int}")
            
            history_str = '\n'.join(str(item) for item in data)   
            overall_evaluation_msg = util.read_prompt_overall_evaluation(type, history_str)   
            overall_metrics_msg = util.read_prompt_interview_evaluation_metrics(type, history_str)

            persona = ''
            content = persona + overall_evaluation_msg
            overall_evaluation_response = gpt.openai_gpt_assistant_without_streaming(content)
            overall_evaluation_response_json = util.extract_json(overall_evaluation_response, quite=False)

            content = persona + overall_metrics_msg
            overall_interview_metrics_response = gpt.openai_gpt_assistant_without_streaming(content)
            overall_interview_metrics_json = util.extract_json(overall_interview_metrics_response, quite=False)

            relevancy = util.filter_the_relevancies_external(data)
            logger.info(f"[DEBUG] relevancy: {relevancy}...")
            
            # Handle case where relevancy is an error object
            if isinstance(relevancy, dict) and 'error' in relevancy:
                logger.info(f"[ERROR] Relevancy calculation failed: {relevancy['error']}")
                # Use default values
                relevancy = {
                    "relevancy": [],
                    "average": 0
                }
            
            percent_term = util.percentage_term(relevancy["average"])

            # Defensive access for 'overall_evaluation' and 'evaluation_metrics'
            try:
                overall_evaluation = overall_evaluation_response_json["overall_evaluation"]
            except KeyError as e:
                logger.info(f"[ERROR] KeyError accessing 'overall_evaluation': {e}")
                return {'error': str(e)}
            try:
                evaluation_metrics = overall_interview_metrics_json["evaluation_metrics"]
            except KeyError as e:
                logger.info(f"[ERROR] KeyError accessing 'evaluation_metrics': {e}")
                return {'error': str(e)}

            overall_evaluation["message"] = percent_term["term"]
            evaluation_metrics["message"] = percent_term["term"]
            evaluation_metrics["relevancy"] = relevancy["relevancy"]
            evaluation_metrics["overall_performance_score"] = relevancy["average"]
            evaluation_metrics["rating"] = percent_term["rating"]
            evaluation_metrics["competency"] = overall_evaluation["competency"]

            overall_interview_metrics_json = evaluation_metrics
            overall_evaluation_response_json = overall_evaluation
            overall_json = {
                    "attributes": {
                        "interview_evaluation": overall_evaluation_response_json,
                        "interview_evaluation_metrics": overall_interview_metrics_json,
                    },
                    "i_persona_session": sessionId,
                    "status": status            
                }

            ipersona_observer = IpersonaSessionObserverSchema(run_stage=run_stage)
            save_observer = ipersona_observer.save_observer(
                params=overall_json, 
                nopp=True, 
                dataframe=False)

            ipersona_session = IpersonaSessionSchema(run_stage=run_stage)
            if save_observer:
                logger.info("session observer to database")

            session_data = {
                "i_persona_session_id": sessionId, 
                "status": status,
            }
            updated_session = ipersona_session.update_session(
                params=session_data, 
                nopp=True, 
                dataframe=False, 
                return_object=True)
        
            if updated_session:
                logger.info("session status updated to closed")

            session = None
            if job_profile_id_int and job_profile_id_int != 0:            
                session = ipersona_session.filter_by_with_user_job_id(
                    user_profile_id=tinder_user_profile_id,
                    job_profile_id=job_profile_id_int, 
                    nopp=True, 
                    dataframe=False
                    ) 
            elif challenge_id_int and challenge_id_int != 0:
                session = ipersona_session.filter_by_with_user_challenge_id(
                    user_profile_id=tinder_user_profile_id,
                    challenge_id=challenge_id_int, 
                    nopp=True, 
                    dataframe=False
                    ) 
            elif template_id_int and template_id_int != 0:
                session = ipersona_session.filter_by_with_user_template_id(
                    user_profile_id=tinder_user_profile_id,
                    template_id=template_id_int, 
                    nopp=True, 
                    dataframe=False
                    ) 

            # Handle case where session is None
            if session is None:
                logger.info("No session data found for overall progress calculation")
                session_chatobserver = []
            else:
                session_chatobserver = util.extract_observers_metrics(session)

            if status == 'External':  
                await self.calculate_overall_progress_external(
                    run_stage, 
                    all_user_id, 
                    tinder_user_profile_id, 
                    job_profile_id, 
                    challenge_id,
                    template_id,
                    session_chatobserver) 
        
        
            response = {
                "overall_interview_metrics": overall_interview_metrics_json,
                "overall_evaluation_response": overall_evaluation_response_json
            }
            logger.info(f"[DEBUG] Final response keys: {list(response.keys())}")
            return response
        
        except Exception as e:
            logger.error(f"Overall evaluation process failed: ${str(e)}")
            return {'error': str(e)}    
 
    async def calculate_overall_progress_external(
            self,
            run_stage, 
            all_user_id,  
            tinder_user_profile_id, 
            job_profile_id, 
            challenge_id,
            template_id,
            data):
        try:
            logger.info(f"calculating overall progress for a job overtime")
            
            # Convert string IDs to integers for proper boolean evaluation
            job_profile_id_int = None
            if job_profile_id and str(job_profile_id).strip():
                try:
                    job_profile_id_int = int(job_profile_id)
                except (ValueError, TypeError):
                    job_profile_id_int = None
            
            challenge_id_int = None
            if challenge_id and str(challenge_id).strip():
                try:
                    challenge_id_int = int(challenge_id)
                except (ValueError, TypeError):
                    challenge_id_int = None
            
            template_id_int = None
            if template_id and str(template_id).strip():
                try:
                    template_id_int = int(template_id)
                except (ValueError, TypeError):
                    template_id_int = None
                        
            confidence_overtime = []  
            clarity_overtime = []     
            engagement_overtime = [] 
            overall_time_managements = []
            overall_competencies = []
            overall_performance_scores = []
            session_ids = [] 
            obs_ids = []              
            for entry in data:
                if isinstance(entry, dict):  
                    entry_ids = entry
                    entry = entry.get("evaluation_metrics", {})
                    iso_time = entry.get("createdAt", "")
                    created_time = util.convert_iso_to_readable_format(iso_time)
                    
                    # Skip entries with invalid dates to maintain chart integrity
                    if not created_time:
                        continue
                        
                    performance = entry.get("performance", [])
          
                    realtime = entry.get('communication_skills', []) 
                    # time = entry.get('time_management', {})
                    competency = entry.get('competency', [])
                    overall_performance_score = entry.get("overall_performance_score", "")
                    obs_id = entry_ids.get("obs_id")  
            
                    if obs_id:
                        obs_ids.append(int(obs_id))  
                    
                    # obj_time = {
                    #     "time": created_time,
                    #     "time_management": time
                    # }
                    # overall_time_managements.append(obj_time)
                    
                    obj_competency = {
                        "time": created_time,
                        "competency": competency
                    }
                    overall_competencies.append(obj_competency)   
                    
                    obj_score = {
                        "time": created_time,
                        "score": overall_performance_score
                    }
                    overall_performance_scores.append(obj_score)   
                    
                    if isinstance(performance, list):
                        for item in performance:
                            confidence_level = item.get('level', '').lower()
                            if confidence_level == 'poor':
                                value = 1
                            elif confidence_level == 'good':
                                value = 2
                            elif confidence_level == 'excellent':
                                value = 3
                            confidence = {"time": created_time, "level": confidence_level, "value": value}
                            confidence_overtime.append(confidence)                        
                
                    if isinstance(realtime, list):
                        for communication in realtime:  
                            if communication.get('skill') == "clarity":  
                                clarity_level = communication['level'].lower() 
                                value = 1 if clarity_level == 'poor' else 2 if clarity_level == 'good' else 3
                                clarity = {"time": created_time, "level": clarity_level, "value": value}
                                clarity_overtime.append(clarity)

                            if communication.get('skill') == "engagement":  
                                engagement_level = communication['level'].lower()  
                                value = 1 if engagement_level == 'poor' else 2 if engagement_level == 'good' else 3
                                engagement = {"time": created_time, "level": engagement_level, "value": value}
                                engagement_overtime.append(engagement)
                                
            ipersona_overall = IpersonaSessionOverallObserverSchema(run_stage=run_stage)
            ipersona_user = IpersonaTraineeSchema(run_stage=run_stage)

            trainee_profile_data = ipersona_user.filter_by_alluser_id(all_user_id=all_user_id, nopp=True, dataframe=False)
            if not trainee_profile_data:
                    logger.warn("No trainee user profiles found.")
                    return []
            tinder_user_profile_id = trainee_profile_data['id']    
            session_chatobserver = None
    
            if job_profile_id_int and job_profile_id_int != 0: 
                print(f"🎯 [DEBUG] Taking JOB_PROFILE path - job_profile_id: {job_profile_id_int}")
                session_chatobserver = ipersona_overall.filter_by_with_user_and_job_id(
                    user_profile_id = tinder_user_profile_id, 
                    job_profile_id = job_profile_id_int, 
                    nopp=True, 
                    dataframe=False)
                
            elif challenge_id_int and challenge_id_int != 0:
                print(f"🎯 [DEBUG] Taking CHALLENGE path - challenge_id: {challenge_id_int}")
                session_chatobserver = ipersona_overall.filter_by_with_user_and_challenge_id(
                    user_profile_id = tinder_user_profile_id, 
                    challenge_id = challenge_id_int, 
                    nopp=True, 
                    dataframe=False)   

            elif template_id_int and template_id_int != 0:
                print(f"🎯 [DEBUG] Taking TEMPLATE path - template_id: {template_id_int}")
                session_chatobserver = ipersona_overall.filter_by_with_user_and_template_id(
                    user_profile_id = tinder_user_profile_id, 
                    template_id = template_id_int, 
                    nopp=True, 
                    dataframe=False)    
                       
            
            if session_chatobserver and not session_chatobserver.get("error"): 
                logger.info(f"Session job overall observer data exists, so updating the data")          
        
                session_chatobserver_sessions = session_chatobserver['all_sessions']
                
                logger.info(f"Value of session_overall_observer_by_user_and_job: {len(session_chatobserver_sessions)}")
                    
                if len(session_chatobserver_sessions) > 0:
                    new_overall_data = {
                        "overall_confidence": confidence_overtime,
                        "overall_clarity": clarity_overtime,
                        "overall_engagement": engagement_overtime,
                        "overall_time_management": overall_time_managements,
                        "overall_competency": overall_competencies,
                        "overall_performance": overall_performance_scores
                    }
                    
                    # THESE IS WHERE THE EXISTING OBSERVER DATA IS COMBINED AND UPDATED WITH THE NEW DATA
                    existing_overall_data = session_chatobserver_sessions[0]
                    update_overall_data = util.append_new_session_metrics(existing_overall_data, new_overall_data)
                         
                    message_data = {
                        "i_persona_session_overall_observer_id": session_chatobserver['id'], 
                        "attributes": update_overall_data,
                        "i_persona_observers": obs_ids
                    }
                    if job_profile_id_int and job_profile_id_int != 0:
                        message_data["tinder_user_profile"] = tinder_user_profile_id
                        message_data["tinder_job_profile"] = job_profile_id_int
                    elif challenge_id_int and challenge_id_int != 0:
                        message_data["tinder_user_profile"] = tinder_user_profile_id
                        message_data["challenge_document"] = challenge_id_int
                    elif template_id_int and template_id_int != 0:
                        message_data["tinder_user_profile"] = tinder_user_profile_id
                        message_data["tinder_template"] = template_id_int

                    
                    response = ipersona_overall.update_session(
                        params=message_data, 
                        nopp=True, 
                        dataframe=False, 
                        return_object=True)

                    if response:
                        logger.success(f"session overall observer data update with new insert anlaysis")   
            
            else:  
                logger.info(f"Creating a new session job overall observer data")          
                ipersona_overall = IpersonaSessionOverallObserverSchema(run_stage=run_stage)
                # ipersona_user = IpersonaTraineeSchema(run_stage=run_stage)

                # trainee_profile_data = ipersona_user.filter_by_alluser_id(
                #     all_user_id=all_user_id, 
                #     nopp=True, 
                #     dataframe=False)
                
                # if not trainee_profile_data:
                #         logger.warn("No trainee user profiles found.")
                #         return []
                
                # tinder_user_profile_id = trainee_profile_data['id']    
                message_data = {
                    "attributes": {
                        "overall_confidence": confidence_overtime,
                        "overall_clarity": clarity_overtime,
                        "overall_engagement": engagement_overtime,
                        "overall_time_management": overall_time_managements,
                        "overall_competency": overall_competencies,
                        "overall_performance": overall_performance_scores
                    },
                    "i_persona_observers": obs_ids
                }

                # Add the correct attribute based on which ID is present
                if job_profile_id_int and job_profile_id_int != 0:
                    message_data["tinder_user_profile"] = tinder_user_profile_id
                    message_data["tinder_job_profile"] = job_profile_id_int
                elif challenge_id_int and challenge_id_int != 0:
                    message_data["tinder_user_profile"] = tinder_user_profile_id
                    message_data["challenge_document"] = challenge_id_int
                elif template_id_int and template_id_int != 0:
                    message_data["tinder_user_profile"] = tinder_user_profile_id
                    message_data["tinder_template"] = template_id_int

                response = ipersona_overall.save_Session_Overall_Observer(
                    params=message_data, 
                    nopp=True, 
                    dataframe=False)
                
                return response
        
        except Exception as e:
            logger.error(f"Process failed: ${str(e)}")
            return f'Error: {str(e)}'  
        
    def save_notification(self, all_user_id, run_stage, message):
        logger.info(f"📢 [NOTIFICATION] save_notification called - all_user_id={all_user_id}, run_stage={run_stage}, message='{message}'")
        
        try:
            logger.debug(f"📢 [NOTIFICATION] Building notification detail object...")
            detail = {
                    "topic": f"external upload data processing status",
                    "where": f"",
                    "notificationMessage": f"{message}",
                    # "traineeLink": f"/trainee/parrot",
                    # "staffLink": f"/trainee/parrot",
                    "traineeLink": f"#",
                    "staffLink": f"#",
                }
            logger.debug(f"📢 [NOTIFICATION] Detail created: {detail}")
                
            logger.info(f"📢 [NOTIFICATION] Fetching all_user data for user_id={all_user_id}, run_stage={run_stage}")
            from api.llm.ipersona.ipersona_strapi_schemas import IpersonaAllUserSchema
            ipersona_alluser = IpersonaAllUserSchema(run_stage=run_stage)
            ipersona_alluser_data = ipersona_alluser.get_alluser_by_id(all_user_id=all_user_id, nopp=True, dataframe=False, return_object=True)
            logger.debug(f"📢 [NOTIFICATION] Retrieved all_user_data: {ipersona_alluser_data}")

            nana_user_id = "2147"
            batch_id = ipersona_alluser_data.get('Batch')
            logger.debug(f"📢 [NOTIFICATION] Extracted batch_id from user data: {batch_id}")
            
            if batch_id:
                batch_id = [batch_id]
            else:
                batch_id = []
            logger.debug(f"📢 [NOTIFICATION] Processed batch_id list: {batch_id}")

            # Prepare GraphQL mutation payload
            notification_payload = {
                "sender": nana_user_id,
                "receiver": all_user_id,
                "Detail": detail,
                "BatchIDs": batch_id if batch_id else [],
                "origin": "leap"
            }
            logger.info(f"📢 [NOTIFICATION] Created notification payload: sender={nana_user_id}, receiver={all_user_id}, BatchIDs={batch_id if batch_id else []}")
            logger.debug(f"📢 [NOTIFICATION] Full payload: {notification_payload}")
            
            # Create instance of IpersonaNotificationSchema and call _create_notification
            logger.info(f"📢 [NOTIFICATION] Initializing IpersonaNotificationSchema with run_stage={run_stage}")
            from api.llm.ipersona.ipersona_strapi_schemas import IpersonaNotificationSchema
            notification_schema = IpersonaNotificationSchema(run_stage=run_stage)
            
            logger.info(f"📢 [NOTIFICATION] Calling _create_notification with payload...")
            notification_result = notification_schema._create_notification(notification_payload)
            logger.debug(f"📢 [NOTIFICATION] Notification result received: {notification_result}")
            
            if notification_result and 'data' in notification_result and 'createNotification' in notification_result['data']:
                notification_id = notification_result['data']['createNotification']['data']['id']
                logger.info(f"✅ [NOTIFICATION] Successfully sent notification with ID: {notification_id} to user {all_user_id}")
                return {"notification_id": notification_id, "status": "success"}
            else:
                error_msg = f"Failed to create notification: {notification_result}"
                logger.error(f"❌ [NOTIFICATION] {error_msg}")
                return {"error": error_msg, "status": "failed"}
                    
        except Exception as e:
            error_msg = f"Unexpected error in save_notification: {str(e)}"
            logger.error(f"❌ [NOTIFICATION] {error_msg}", exc_info=True)
            return {"error": error_msg, "status": "failed"}
