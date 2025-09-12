
import os
import requests
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

logger = LLPackerLogger(os.path.basename(__file__))

class AudioUtils:
    def __init__(self):
        pass
        
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
            print(f"⚠️ Failed to update task progress: {e}")

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
        run_stage):
        print(f"🚀 [DEBUG] process_upload_external_audio STARTED")
        
        try:
            redis = RedisBase()
            print(f"🔗 [DEBUG] Redis connection established")
        except Exception as e:
            print(f"❌ [DEBUG] Failed to establish Redis connection: {str(e)}")
            return 'Redis connection failed'
        
        try:
            print(f"🔊 [DEBUG] Starting audio processing for file: {filename}")
            try:
                redis.set(f"audio_status:{job_profile_id}", {"status": "processing", "message": ""})
                print(f"📝 [DEBUG] Set Redis status to 'processing' for job_profile_id: {job_profile_id}")
            except Exception as e:
                print(f"❌ [DEBUG] Failed to set Redis status: {str(e)}")

            try:
                template_id = 0
                message = ''
                template = False
                challenge = False  
                mode = None
                print(f"🔧 [DEBUG] Initialized variables: template_id={template_id}, template={template}, challenge={challenge}, mode={mode}")
                
                if "audio" in content_type or "video" in content_type:
                    print(f"🎵 [DEBUG] Detected audio/video content type: {content_type}")
                    try:
                        original_format = content_type.split("/")[-1].lower()
                        print(f"📁 [DEBUG] Extracted original format: {original_format}")
                    except Exception as e:
                        print(f"❌ [DEBUG] Failed to extract original format: {str(e)}")
                        return 'Format extraction failed'
                    
                    if original_format != "mpeg" and original_format != "mp3":
                        print(f"🔄 [DEBUG] Converting media file from {original_format} to mp3")
                        try:
                            with open(audio_path, "rb") as f:
                                contents = f.read()
                            print(f"📖 [DEBUG] Read file contents, size: {len(contents)} bytes")
                        except Exception as e:
                            print(f"❌ [DEBUG] Failed to read audio file: {str(e)}")
                            return 'File read failed'
                        
                        try:
                            print(f"🔄 [DEBUG] Calling util.convert_to_mp3 with format: {original_format}")
                            contents = util.convert_to_mp3(contents, original_format)
                            print(f"✅ [DEBUG] MP3 conversion completed, new size: {len(contents)} bytes")
                        except Exception as e:
                            print(f"❌ [DEBUG] MP3 conversion failed: {str(e)}")
                            return 'MP3 conversion failed'
                        
                        try:
                            converted_filename = filename.rsplit(".", 1)[0] + ".mp3"
                            audio_path = audio_path.replace(filename, converted_filename)
                            print(f"📝 [DEBUG] New audio path: {audio_path}")
                            
                            with open(audio_path, "wb") as f:
                                f.write(contents)
                            print(f"💾 [DEBUG] MP3 file saved to: {audio_path}")
                            logger.success(f"🎧 MP3 file saved to: {audio_path}")
                        except Exception as e:
                            print(f"❌ [DEBUG] Failed to save MP3 file: {str(e)}")
                            return 'File save failed'
                    else:
                        print(f"✅ [DEBUG] File already in mp3 format. Skipping conversion.")
                        logger.info("✅ File already in mp3 format. Skipping conversion.")

                    try:
                        print(f"🎤 [DEBUG] Calling audio_transcription_logics")
                        result = self.audio_transcription_logics(
                            filename=filename,
                            audio_path=audio_path,
                            content_type="audio/mpeg",
                        )
                        # print(f"📊 [DEBUG] Transcription result: {result}")
                    except Exception as e:
                        print(f"❌ [DEBUG] Audio transcription failed: {str(e)}")
                        return 'Transcription failed'

                    if "error" in result:
                        print(f"❌ [DEBUG] Transcription failed with error: {result.get('error')}")
                        try:
                            redis.set(f"audio_status:{job_profile_id}", {
                                "status": "failed",
                                "message": result.get("error"),
                                "details": result.get("details", "")
                            })
                            print(f"📝 [DEBUG] Set Redis status to 'failed'")
                        except Exception as e:
                            print(f"❌ [DEBUG] Failed to set Redis error status: {str(e)}")
                        raise Exception("Transcription failed")

                    try:
                        transcript = result.get("content", "No transcription returned")
                        print(f"📝 [DEBUG] Extracted transcript: {transcript[:50]}..." if len(str(transcript)) > 100 else f"📝 [DEBUG] Extracted transcript")
                        logger.success("Initializing transcription")
                    except Exception as e:
                        print(f"❌ [DEBUG] Failed to extract transcript: {str(e)}")
                        raise Exception('Transcript extraction failed')

                    try:
                        redis.set(f"audio_status:{job_profile_id}", {
                            "status": "done",
                            "message": "Transcription complete",
                            "content": transcript
                        })
                        print(f"📝 [DEBUG] Set Redis status to 'done' with transcript")
                    except Exception as e:
                        print(f"❌ [DEBUG] Failed to set Redis success status: {str(e)}")

                elif any(x in content_type for x in ["text", "pdf", "msword", "officedocument"]):
                    print(f"📄 [DEBUG] Detected text-based content type: {content_type}")
                    logger.info(f"📝 Text-based file detected: {filename}")
                    try:
                        with open(audio_path, "rb") as f:
                            contents = f.read()
                        print(f"📖 [DEBUG] Read text file contents, size: {len(contents)} bytes")
                    except Exception as e:
                        print(f"❌ [DEBUG] Failed to read text file: {str(e)}")
                        return 'Text file read failed'
                    
                    try:
                        print(f"🔍 [DEBUG] Calling content_extraction_logics")
                        result = self.content_extraction_logics(filename, contents, content_type)
                        print(f"📊 [DEBUG] Content extraction result: {result}")
                    except Exception as e:
                        print(f"❌ [DEBUG] Content extraction failed: {str(e)}")
                        return 'Content extraction failed'
                    
                    if "error" in result:
                        print(f"❌ [DEBUG] Text extraction failed: {result['error']}")
                        logger.error(f"❌ Text extraction failed: {result['error']}")
                        try:
                            redis.set(f"audio_status:{job_profile_id}", {
                                "status": "failed",
                                "message": result.get("error")
                            })
                            print(f"📝 [DEBUG] Set Redis status to 'failed'")
                        except Exception as e:
                            print(f"❌ [DEBUG] Failed to set Redis error status: {str(e)}")
                        return
                    
                    try:
                        transcript = result.get("content", "No content returned")
                        print(f"📝 [DEBUG] Extracted content: {transcript[:50]}..." if len(str(transcript)) > 100 else f"📝 [DEBUG] Extracted content: {transcript}")
                        logger.success(f"✅ Text extraction successful: {filename}")
                    except Exception as e:
                        print(f"❌ [DEBUG] Failed to extract content: {str(e)}")
                        return 'Content extraction failed'
                        
                    try:
                        redis.set(f"audio_status:{job_profile_id}", {
                            "status": "done",
                            "message": "Text content extracted successfully",
                            "content": result.get("content")
                        })
                        print(f"📝 [DEBUG] Set Redis status to 'done' with content")
                    except Exception as e:
                        print(f"❌ [DEBUG] Failed to set Redis success status: {str(e)}")
                else:
                    print(f"🚫 [DEBUG] Unsupported file type: {content_type}")
                    logger.warn(f"🚫 Unsupported file type: {content_type}")
                    try:
                        redis.set(f"audio_status:{job_profile_id}", {
                            "status": "failed",
                            "message": f"Unsupported file type: {content_type}"
                        })
                        print(f"📝 [DEBUG] Set Redis status to 'failed' for unsupported type")
                    except Exception as e:
                        print(f"❌ [DEBUG] Failed to set Redis error status: {str(e)}")
                    return
                    
            except Exception as conversion_error:
                print(f"❌ [DEBUG] MP3 conversion failed: {conversion_error}")
                logger.error(f"❌ MP3 conversion failed: {conversion_error}", exc_info=True)
                try:
                    redis.set(f"audio_status:{job_profile_id}", {
                        "status": "failed",
                        "message": f"MP3 conversion failed: {conversion_error}"
                    })
                    print(f"📝 [DEBUG] Set Redis status to 'failed' for conversion error")
                except Exception as e:
                    print(f"❌ [DEBUG] Failed to set Redis error status: {str(e)}")
                return

            # --- Existing logic continues here ---
            try:
                print(f"👤 [DEBUG] Fetching trainee profile data for all_user_id: {all_user_id}")
                logger.debug("Fetching trainee profile data")
                ipersona_user = IpersonaTraineeSchema(run_stage=run_stage)
                trainee_profile_data = ipersona_user.filter_by_alluser_id(
                    all_user_id=all_user_id, nopp=True, dataframe=False
                )
                # print(f"📊 [DEBUG] Trainee profile data: {trainee_profile_data}")
            except Exception as e:
                print(f"❌ [DEBUG] Failed to fetch trainee profile data: {str(e)}")
                return 'Profile fetch failed'
            
            if not trainee_profile_data:
                print(f"⚠️ [DEBUG] No trainee user profiles found for all_user_id: {all_user_id}")
                logger.warn(f"No trainee user profiles found for all_user_id: {all_user_id}")
                return

            try:
                tinder_user_profile_id = trainee_profile_data.get('id')
                print(f"🆔 [DEBUG] Extracted tinder_user_profile_id: {tinder_user_profile_id}")
            except Exception as e:
                print(f"❌ [DEBUG] Failed to extract tinder_user_profile_id: {str(e)}")
                return 'Profile ID extraction failed'
                
            if not tinder_user_profile_id:
                print(f"❌ [DEBUG] Invalid trainee profile: missing ID")
                logger.error("Invalid trainee profile: missing ID")
                return

            try:
                print(f"📖 [DEBUG] Reading external audio analysis prompt")
                logger.debug("Reading external audio analysis prompt")
                external_audio_prompt = util.file_reader(util.prompt_path('external_audio_analysis.txt'))
                realtime_prompt = util.file_reader(util.prompt_path('realtime_evaluation.txt'))
                print(f"📝 [DEBUG] Loaded prompts - external_audio_prompt length: {len(external_audio_prompt)}, realtime_prompt length: {len(realtime_prompt)}")
            except Exception as e:
                print(f"❌ [DEBUG] Failed to read prompts: {str(e)}")
                return 'Prompt reading failed'

            try:
                print(f"🔧 [DEBUG] Replacing placeholders in prompts")
                logger.debug("Replacing placeholders in prompts")
                external_aud_prompt = external_audio_prompt.replace("{transcription}", str(transcript)).replace("{realtime}", str(realtime_prompt))
                print(f"📝 [DEBUG] Final prompt length: {len(external_aud_prompt)}")
            except Exception as e:
                print(f"❌ [DEBUG] Failed to replace prompt placeholders: {str(e)}")
                return 'Prompt processing failed'

            try:
                print(f"🤖 [DEBUG] Sending prompt to GPT for analysis")
                logger.debug("Sending prompt to GPT for analysis", external_aud_prompt)
                data = gpt.openai_gpt_assistant_without_streaming(external_aud_prompt)
                # print(f"📊 [DEBUG] Raw GPT response: {data[:100]}...") 
            except Exception as e:
                print(f"❌ [DEBUG] GPT analysis failed: {str(e)}")
                return 'GPT analysis failed'
                
            try:
                # Extract JSON from the llm_client response (handled automatically by extract_json)
                response = util.extract_json(data, quite=False)
                print(f"📋 [DEBUG] Extracted JSON response: {response}")
                logger.debug("Response from GPT", response)
            except Exception as e:
                print(f"❌ [DEBUG] Failed to extract JSON from GPT response: {str(e)}")
                return 'JSON extraction failed'
            
            if not response:
                print(f"❌ [DEBUG] Failed to process upload file: No data returned from transcription")
                logger.error("❌ Failed to process upload file: No data returned from transcription")
                return

            try:
                print(f"💾 [DEBUG] Creating session for audio processing")
                logger.debug("Creating session for audio processing")
                saved_session = util.create_session(
                    mode,
                    run_stage,
                    template,
                    external,
                    challenge,
                    all_user_id,
                    tinder_user_profile_id,
                    job_profile_id,
                    template_id,
                    challenge_id,
                    message
                )
                print(f"📊 [DEBUG] Session creation result: {saved_session}")
            except Exception as e:
                print(f"❌ [DEBUG] Session creation failed: {str(e)}")
                return 'Session creation failed'

            if saved_session and isinstance(saved_session, dict):
                try:
                    sessionId = saved_session['id']
                    print(f"✅ [DEBUG] Session created successfully with ID: {sessionId}")
                    logger.info(f"📥 Session created successfully with ID: {sessionId}")
                except Exception as e:
                    print(f"❌ [DEBUG] Failed to extract session ID: {str(e)}")
                    return 'Session ID extraction failed'
                    
                try:
                    print(f"💾 [DEBUG] Saving transcribed chat to database")
                    logger.debug("Saving transcribed chat to database")
                    # saved = await strapi.sav e_message(sessionId, response)
                    saved = strapi.save_messages_to_db(response, sessionId)
                    print(f"📊 [DEBUG] Save message result: {saved}")
                except Exception as e:
                    print(f"❌ [DEBUG] Failed to save message to database: {str(e)}")
                    return 'Message save failed'

                try:
                    logger.debug("Starting overall evaluation in a separate thread")
                    def run_overall():
                        try:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            print(f"🔄 [DEBUG] Created new event loop for overall evaluation")
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
                                redis.set(f"audio_status:{job_profile_id}", {
                                    "status": "done",
                                    "message": "Chat Saved Successfully",
                                    "chat": saved,
                                    "overall": overall
                                })
                            else:
                                logger.error("❌ Overall evaluation failed")
                        except Exception as e:
                            print(f"❌ [DEBUG] Error in overall evaluation: {str(e)}")
                            logger.error(f"Error in overall evaluation: {str(e)}")

                    t = threading.Thread(target=run_overall)
                    t.start()
                    print(f"🔄 [DEBUG] Overall evaluation thread started")
                    logger.success("🎉 EXTERNAL AUDIO PROCESSED AND SAVED SUCCESSFULLY!")
                except Exception as e:
                    print(f"❌ [DEBUG] Failed to start overall evaluation thread: {str(e)}")
                    return 'Threading failed'
            elif isinstance(saved_session, str):
                print(f"❌ [DEBUG] Session creation returned error string: {saved_session}")
                return f'Session creation failed: {saved_session}'
            else:
                print(f"❌ [DEBUG] Session creation returned invalid result: {saved_session}")
                return 'Session creation returned invalid result'

        except Exception as e:
            print(f"🔥 [DEBUG] Critical error in background audio processing: {str(e)}")
            print(f"🔥 [DEBUG] Error type: {type(e).__name__}")
            print(f"🔥 [DEBUG] Error details: {str(e)}")
            # logger.error(f"🔥 Error in background audio processing: {str(e)}")
            try:
                redis.set(f"audio_status:{job_profile_id}", {"status": "failed", "message": str(e)})
                print(f"📝 [DEBUG] Set Redis status to 'failed' for critical error")
            except Exception as redis_error:
                print(f"❌ [DEBUG] Failed to set Redis error status: {str(redis_error)}")
            # Re-raise the exception so Celery knows the task failed
            raise e
        print(f"🏁 [DEBUG] process_upload_external_audio COMPLETED")
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
        all_user_id,
        external,
        run_stage
     ):
        redis = RedisBase()
        try:
            if not job_profile_id:
                logger.error("job_profile_id is missing, cannot track processing status.")
                return

            redis.set(f"audio_status:{job_profile_id}", {"status": "processing", "message": "Starting dual file processing."})
            logger.info(f"🔊 Starting combined processing for Job ID: {job_profile_id}")

            # --- Process Question File using helper ---
            question_transcript, question_error_msg = await self.process_and_transcribe_file(
                question_filename, question_content_type, question_contents, "Question"
            )

            if question_error_msg:
                error_msg = f"Question file processing failed: {question_error_msg}"
                redis.set(f"audio_status:{job_profile_id}", {"status": "failed", "message": error_msg})
                raise Exception(error_msg)

            # --- Process Answer File using helper ---
            print(f"🔊 [DEBUG] Processing answer file: {answer_filename}, content_type: {answer_content_type}, size: {len(answer_contents)} bytes")
            answer_transcript, answer_error_msg = await self.process_and_transcribe_file(
                answer_filename, answer_content_type, answer_contents, "Answer"
            )
            print(f"🔊 [DEBUG] Answer processing result - transcript: {answer_transcript[:100] if answer_transcript else 'None'}..., error: {answer_error_msg}")
            
            if answer_error_msg:
                error_msg = f"Answer file processing failed: {answer_error_msg}"
                redis.set(f"audio_status:{job_profile_id}", {"status": "failed", "message": error_msg})
                raise Exception(error_msg)

            # Ensure transcripts are not None after helper calls (should be handled by error_msg)
            if question_transcript is None or answer_transcript is None:
                error_msg = "One or both transcripts are missing after file processing. Cannot proceed."
                logger.error(error_msg)
                redis.set(f"audio_status:{job_profile_id}", {"status": "failed", "message": "Missing transcripts for analysis."})
                raise Exception(error_msg)

            logger.info("✅ Both question and answer files processed successfully.")

            # --- Remaining Original Logic (now much cleaner) ---
            logger.debug("Fetching trainee profile data")
            ipersona_user = IpersonaTraineeSchema(run_stage=run_stage)
            trainee_profile_data = ipersona_user.filter_by_alluser_id(
                all_user_id=all_user_id, nopp=True, dataframe=False
            )
            if not trainee_profile_data:
                error_msg = f"No trainee user profiles found for all_user_id: {all_user_id}"
                logger.warn(error_msg)
                redis.set(f"audio_status:{job_profile_id}", {"status": "failed", "message": "No trainee user profiles found"})
                raise Exception(error_msg)

            tinder_user_profile_id = trainee_profile_data.get('id')
            print(f"📋 [DEBUG] Tinder user profile ID: {tinder_user_profile_id}")
            if not tinder_user_profile_id:
                error_msg = "Invalid trainee profile: missing ID"
                logger.error(error_msg)
                redis.set(f"audio_status:{job_profile_id}", {"status": "failed", "message": "Invalid trainee profile: missing ID"})
                raise Exception(error_msg)

            logger.info("Reading external audio analysis prompt")
            external_audio_prompt = util.file_reader(util.prompt_path('external_audio_analysis_for_separate_inputs.txt'))
            external_all_file_prompt = util.file_reader(util.prompt_path('external_audio_analysis.txt'))
            answer_question_matching = util.file_reader(util.prompt_path('answer_question_match.txt'))
            realtime_prompt = util.file_reader(util.prompt_path('realtime_evaluation.txt'))

            logger.info("Replacing placeholders in prompts")
            logger.success(f"📋 [DEBUG] Question transcript: {question_transcript}")
            logger.success(f"📋 [DEBUG] Answer transcript: {answer_transcript}")
            logger.success(f"📋 [DEBUG] Answer transcript length: {len(str(answer_transcript))}")
            answer_question_match_scoring = answer_question_matching.replace("{questions_data}", question_transcript)\
                                                           .replace("{answers_data}", answer_transcript)

            logger.debug("Sending prompt to GPT for analysis")
            # print(f"📋 [DEBUG] Answer question match scoring: {answer_question_match_scoring}")
            data = gpt.openai_gpt_assistant_without_streaming(answer_question_match_scoring)
            if data and hasattr(data, 'content'):
                data = data.content.text
            response = util.extract_json(data, quite=False)
            print(f"📋 [DEBUG] Raw LLM response: {response}")

            # Filter out items with relevance_score >= 90
            filtered_data = []
            for item in response:
                try:
                    relevance_score = int(item.get('relevance_score', 0))
                    if relevance_score >= 90:
                        filtered_data.append({
                            'question': item['question'], 
                            'answer': item['answer']
                        })
                except (ValueError, TypeError):
                    # If relevance_score is not a valid number, skip this item
                    logger.warning(f"Skipping item with invalid relevance_score: {item.get('relevance_score')}")
                    continue

            print(f"📋 [DEBUG] Filtered data count: {len(filtered_data)}")
            print(f"📋 [DEBUG] All relevance scores: {[item.get('relevance_score', 'N/A') for item in response]}")
            
            if not filtered_data:
                error_msg = "❌ Failed to process upload files: No Valuable matched question-answer data returned from LLM analysis"
                logger.error(error_msg)
                redis.set(f"audio_status:{job_profile_id}", {"status": "failed", "message": "No analysis data returned from LLM"})
                raise Exception(error_msg)

            logger.debug("Replacing placeholders in prompts")
            external_audio_prompt = external_audio_prompt.replace("{question_answer_data}", str(filtered_data))\
                                                           .replace("{realtime}", str(realtime_prompt))
            # print(f"📋 [DEBUG] External audio prompt: {external_audio_prompt}")
            data = gpt.openai_gpt_assistant_without_streaming(external_audio_prompt)
            response = util.extract_json(data, quite=False)
            logger.info("Matched question-answer data returned from LLM analysis with the new interview structure")
            print(f"📋 [DEBUG] Q Response: {response}")
           
            # Initialize these for util.create_session (as per original logic)
            template_id = 0
            message = ''
            template = False
            challenge = False
            mode = None

            saved_session = util.create_session(
                mode,
                run_stage,
                template,
                external,
                challenge,
                all_user_id,
                tinder_user_profile_id,
                job_profile_id,
                template_id,
                challenge_id,
                message
            )

            if saved_session:
                sessionId = saved_session['id']
                logger.info(f"📥 Session created successfully with ID: {sessionId}")
                logger.debug("Saving analyzed chat to database")
                saved = strapi.save_messages_to_db(response, sessionId)

                logger.debug("Starting overall evaluation in a separate thread")
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
                                0,  # template_id
                                'job_interview_config'
                            )
                        )
                        
                        if overall:
                            logger.info("✅ Overall evaluation completed successfully")
                            redis.set(f"audio_status:{job_profile_id}", {
                                "status": "done",
                                "message": "Chat Saved Successfully",
                                "chat": saved,
                                "overall": overall
                            })
                        else:
                            logger.error("❌ Overall evaluation failed")

                       
                    except Exception as e:
                        logger.error(f"Error in overall evaluation thread: {str(e)}", exc_info=True)
                        redis.set(f"audio_status:{job_profile_id}", {"status": "failed", "message": str(e)})

                t = threading.Thread(target=run_overall_sync_wrapper)
                t.start()
                logger.success("🎉 EXTERNAL DUAL AUDIO PROCESSED AND SAVED SUCCESSFULLY!")
            else:
                logger.error("❌ Failed to save session")
                redis.set(f"audio_status:{job_profile_id}", {"status": "failed", "message": "Session Not Saved"})

        except Exception as e:
            logger.error(f"🔥 Critical error in dual audio background processing: {str(e)}", exc_info=True)
            if job_profile_id:
                redis.set(f"audio_status:{job_profile_id}", {"status": "failed", "message": f"System error: {str(e)}"})
            # Re-raise the exception so Celery knows the task failed
            raise e 

    async def process_upload_external_answer_with_template(
        self,
        template_questions,
        answer_filename,
        answer_content_type,
        answer_audio_path,
        answer_contents,
        job_profile_id,
        challenge_id,
        all_user_id,
        external,
        run_stage
    ):
        """
        Process answer file with template questions instead of question file.
        Uses template_questions directly instead of reading from question file.
        """
        redis = RedisBase()
        try:
            if job_profile_id is None:
                logger.error("job_profile_id is missing, cannot track processing status.")
                return

            redis.set(f"audio_status:{job_profile_id}", {"status": "processing", "message": "Starting template answer processing."})
            logger.info(f"🔊 Starting template answer processing for Job ID: {job_profile_id}")

            # Process Answer File using helper
            print(f"🔊 [DEBUG] Processing answer file: {answer_filename}, content_type: {answer_content_type}, size: {len(answer_contents)} bytes")
            answer_transcript, answer_error_msg = await self.process_and_transcribe_file(
                answer_filename, answer_content_type, answer_contents, "Answer"
            )
            print(f"🔊 [DEBUG] Answer processing result - transcript: {answer_transcript[:100] if answer_transcript else 'None'}..., error: {answer_error_msg}")
            
            if answer_error_msg:
                error_msg = f"Answer file processing failed: {answer_error_msg}"
                redis.set(f"audio_status:{job_profile_id}", {"status": "failed", "message": error_msg})
                raise Exception(error_msg)

            # Ensure transcript is not None after helper call
            if answer_transcript is None:
                error_msg = "Answer transcript is missing after file processing. Cannot proceed."
                logger.error(error_msg)
                redis.set(f"audio_status:{job_profile_id}", {"status": "failed", "message": "Missing answer transcript for analysis."})
                raise Exception(error_msg)

            logger.info("✅ Answer file processed successfully.")

            # Convert template_questions to question text format
            question_text = self.convert_template_questions_to_text(template_questions)
            logger.info(f"📋 Converted {len(template_questions)} template questions to text format")

            # Fetch trainee profile data
            logger.debug("Fetching trainee profile data")
            ipersona_user = IpersonaTraineeSchema(run_stage=run_stage)
            trainee_profile_data = ipersona_user.filter_by_alluser_id(
                all_user_id=all_user_id, nopp=True, dataframe=False
            )
            if not trainee_profile_data:
                error_msg = f"No trainee user profiles found for all_user_id: {all_user_id}"
                logger.warn(error_msg)
                redis.set(f"audio_status:{job_profile_id}", {"status": "failed", "message": "No trainee user profiles found"})
                raise Exception(error_msg)

            tinder_user_profile_id = trainee_profile_data.get('id')
            print(f"📋 [DEBUG] Tinder user profile ID: {tinder_user_profile_id}")
            if not tinder_user_profile_id:
                error_msg = "Invalid trainee profile: missing ID"
                logger.error(error_msg)
                redis.set(f"audio_status:{job_profile_id}", {"status": "failed", "message": "Invalid trainee profile: missing ID"})
                raise Exception(error_msg)

            logger.info("Reading external audio analysis prompt")
            external_audio_prompt = util.file_reader(util.prompt_path('external_audio_analysis_for_separate_inputs.txt'))
            external_all_file_prompt = util.file_reader(util.prompt_path('external_audio_analysis.txt'))
            answer_question_matching = util.file_reader(util.prompt_path('answer_question_match.txt'))
            realtime_prompt = util.file_reader(util.prompt_path('realtime_evaluation.txt'))

            logger.info("Replacing placeholders in prompts")
            logger.success(f"📋 [DEBUG] Template questions: {question_text}")
            logger.success(f"📋 [DEBUG] Answer transcript: {answer_transcript}")
            logger.success(f"📋 [DEBUG] Answer transcript length: {len(str(answer_transcript))}")
            
            answer_question_match_scoring = answer_question_matching.replace("{questions_data}", question_text)\
                                                           .replace("{answers_data}", answer_transcript)

            logger.debug("Sending prompt to GPT for analysis")
            data = gpt.openai_gpt_assistant_without_streaming(answer_question_match_scoring)
            if data and hasattr(data, 'content'):
                data = data.content.text
            response = util.extract_json(data, quite=False)
            print(f"📋 [DEBUG] Raw LLM response: {response}")

            # Filter out items with relevance_score >= 90
            filtered_data = []
            for item in response:
                try:
                    relevance_score = int(item.get('relevance_score', 0))
                    if relevance_score >= 90:
                        filtered_data.append({
                            'question': item['question'], 
                            'answer': item['answer']
                        })
                except (ValueError, TypeError):
                    # If relevance_score is not a valid number, skip this item
                    logger.warning(f"Skipping item with invalid relevance_score: {item.get('relevance_score')}")
                    continue

            print(f"📋 [DEBUG] Filtered data count: {len(filtered_data)}")
            print(f"📋 [DEBUG] All relevance scores: {[item.get('relevance_score', 'N/A') for item in response]}")
            
            if not filtered_data:
                error_msg = "❌ Failed to process template answer: No Valuable matched question-answer data returned from LLM analysis"
                logger.error(error_msg)
                redis.set(f"audio_status:{job_profile_id}", {"status": "failed", "message": "No analysis data returned from LLM"})
                raise Exception(error_msg)

            logger.debug("Replacing placeholders in prompts")
            external_audio_prompt = external_audio_prompt.replace("{question_answer_data}", str(filtered_data))\
                                                           .replace("{realtime}", str(realtime_prompt))
            data = gpt.openai_gpt_assistant_without_streaming(external_audio_prompt)
            response = util.extract_json(data, quite=False)
            logger.info("Matched question-answer data returned from LLM analysis with the new interview structure")
            print(f"📋 [DEBUG] Q Response: {response}")
           
            # Initialize these for util.create_session (as per original logic)
            template_id = 0
            message = ''
            template = False
            challenge = False
            mode = None

            saved_session = util.create_session(
                mode,
                run_stage,
                template,
                external,
                challenge,
                all_user_id,
                tinder_user_profile_id,
                job_profile_id,
                template_id,
                challenge_id,
                message
            )

            if saved_session:
                sessionId = saved_session['id']
                logger.info(f"📥 Session created successfully with ID: {sessionId}")
                logger.debug("Saving analyzed chat to database")
                saved = strapi.save_messages_to_db(response, sessionId)

                logger.debug("Starting overall evaluation in a separate thread")
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
                        print(f"🎉 [DEBUG] Overall evaluation result: {overall}")
                        if overall:
                            logger.info("✅ Overall evaluation completed successfully")
                            redis.set(f"audio_status:{job_profile_id}", {
                                "status": "done",
                                "message": "Chat Saved Successfully",
                                "chat": saved,
                                "overall": overall
                            })
                        else:
                            logger.error("❌ Overall evaluation failed")
                    except Exception as e:
                        logger.error(f"Error in overall evaluation thread: {str(e)}", exc_info=True)
                        redis.set(f"audio_status:{job_profile_id}", {"status": "failed", "message": str(e)})

                t = threading.Thread(target=run_overall_sync_wrapper)
                t.start()
                logger.success("🎉 TEMPLATE ANSWER PROCESSED AND SAVED SUCCESSFULLY!")
            else:
                logger.error("❌ Failed to save session")
                redis.set(f"audio_status:{job_profile_id}", {"status": "failed", "message": "Session Not Saved"})

        except Exception as e:
            logger.error(f"🔥 Critical error in template answer background processing: {str(e)}", exc_info=True)
            if job_profile_id:
                redis.set(f"audio_status:{job_profile_id}", {"status": "failed", "message": f"System error: {str(e)}"})
            # Re-raise the exception so Celery knows the task failed
            raise e 

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
        print(f"📏 [DEBUG] Audio file size: {file_size / (1024*1024):.2f} MB")
        
        if file_size > max_file_size:
            print(f"⚠️ [DEBUG] File size ({file_size / (1024*1024):.2f} MB) exceeds limit ({max_file_size / (1024*1024):.2f} MB)")
            print(f"🔄 [DEBUG] Attempting to compress audio file...")
            
            try:
                # Compress the audio file to reduce size
                from pydub import AudioSegment
                print(f"🔄 [DEBUG] Loading audio file: {audio_path}")
                audio = AudioSegment.from_mp3(audio_path)
                print(f"🔄 [DEBUG] Audio loaded successfully, duration: {len(audio)/1000:.2f}s")
                # Reduce quality to decrease file size
                compressed_audio = audio.export(format="mp3", bitrate="64k")
                compressed_path = audio_path.replace(".mp3", "_compressed.mp3")
                print(f"🔄 [DEBUG] Writing compressed file to: {compressed_path}")
                with open(compressed_path, "wb") as f:
                    f.write(compressed_audio.read())
                
                compressed_size = os.path.getsize(compressed_path)
                print(f"✅ [DEBUG] Compressed file size: {compressed_size / (1024*1024):.2f} MB")
                audio_path = compressed_path
                filename = filename.replace(".mp3", "_compressed.mp3")
                
            except Exception as e:
                error_msg = f"Failed to compress audio file: {str(e)}"
                print(f"❌ [DEBUG] {error_msg}")
                print(f"❌ [DEBUG] Exception type: {type(e).__name__}")
                import traceback
                traceback.print_exc()
                return {
                    "error": error_msg,
                    "status_code": 500
                }
        
        for attempt in range(max_retries):
            try:
                endpoint_url = "https://content-extractor.10academy.org/content-extractor/audio_transcript"
                with open(audio_path, 'rb') as audio_file:
                    files = {
                        'file': (filename, audio_file, content_type)
                    }
                    data = {
                        'request_id': 'audio-upload-001',
                        'request_source': 'fastapi_audio_upload',
                        'prompt': 'Extract the text from the audio file.',
                        'llm_provider': 'openai',
                        'llm_model': 'gpt-4o'
                    }
                    logger.debug(f"Sending audio file to external transcription endpoint... (Attempt {attempt + 1}/{max_retries})")
                    print(f"🔄 [DEBUG] Transcription attempt {attempt + 1}/{max_retries} with timeout: {base_timeout}s")
                    
                    # Exponential backoff timeout
                    current_timeout = base_timeout * (2 ** attempt)
                    response = requests.post(endpoint_url, files=files, data=data, timeout=current_timeout)
                    response.raise_for_status()
                    result = response.json()
                    print(f"✅ [DEBUG] Transcription successful on attempt {attempt + 1}")
                    return result
                    
            except requests.exceptions.Timeout as e:
                print(f"⏰ [DEBUG] Transcription timeout on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 1, 2, 4 seconds
                    print(f"⏳ [DEBUG] Waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    return {
                        "error": f"Transcription timeout after {max_retries} attempts",
                        "details": f"Service timed out after {current_timeout}s on final attempt",
                        "status_code": 408
                    }
                    
            except requests.exceptions.HTTPError as e:
                print(f"❌ [DEBUG] HTTP error on attempt {attempt + 1}: {str(e)}")
                if e.response.status_code == 504 and attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"⏳ [DEBUG] Gateway timeout, waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
                else:
                    return {
                        "error": f"HTTP error: {e}",
                        "details": e.response.text,
                        "status_code": e.response.status_code
                    }
                    
            except Exception as e:
                print(f"❌ [DEBUG] Unexpected error on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    print(f"⏳ [DEBUG] Unexpected error, waiting {wait_time}s before retry...")
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
                print(f"🔄 [DEBUG] {file_type_label} file format: {original_format}, content_type: {content_type}")
                print(f"🔄 [DEBUG] Supported formats check: {original_format} in {['mpeg', 'mp3', 'wav', 'mp4', 'webm']}")
                
                if original_format not in ["mpeg", "mp3", "wav"]:
                    # Convert MP4, webm, and other formats to MP3 for consistent processing
                    logger.info(f"🔄 Converting {file_type_label} media file from {original_format} to mp3")
                    contents = util.convert_to_mp3(contents, original_format)
                    final_file_path = util.audio_path(filename.rsplit(".", 1)[0] + ".mp3")
                    with open(final_file_path, "wb") as f:
                        f.write(contents)
                    logger.success(f"🎧 {file_type_label} MP3 file saved to: {final_file_path}")
                    print(f"🔄 [DEBUG] Converted to MP3: {final_file_path}")
                else:
                    logger.info(f"✅ {file_type_label} file already in supported audio format. Skipping re-saving.")
                    final_file_path = util.audio_path(filename)
                    print(f"🔄 [DEBUG] Using original file path: {final_file_path}")
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
                logger.debug(f"{file_type_label} transcription initialized")

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
                # Extract text content from ModelResponse
                if transcript and hasattr(transcript, 'content'):
                    transcript = transcript.content.text
                logger.success(f"✅ {file_type_label} text extraction successful: {filename}")
                logger.debug(f"{file_type_label} content extraction initialized")
            else:
                return None, f"Unsupported file type for {file_type_label}: {content_type}"
            return transcript, None

        except Exception as e:
            logger.error(f"❌ Error in {file_type_label} file processing: {e}", exc_info=True)
            return None, f"Processing failed for {file_type_label}: {e}"

    def process_audio_and_celery(self, filename, content_type, audio_path, job_profile_id):
        redis = RedisBase()
        try:
            logger.info(f"🔊 Processing audio file: {filename}")
            redis.set(f"audio_status:{job_profile_id}", {"status": "processing", "message": ""})
            try:
                if "audio" in content_type or "video" in content_type:
                    original_format = content_type.split("/")[-1].lower()
                    if original_format != "mpeg" and original_format != "mp3":
                        logger.info(f"🔄 Converting media file from {original_format} to mp3")
                        with open(audio_path, "rb") as f:
                            contents = f.read()
                        contents = util.convert_to_mp3(contents, original_format)
                        converted_filename = filename.rsplit(".", 1)[0] + ".mp3"
                        audio_path = audio_path.replace(filename, converted_filename)
                        with open(audio_path, "wb") as f:
                            f.write(contents)
                        logger.success(f"🎧 MP3 file saved to: {audio_path}")
                    else:
                        logger.info("✅ File already in mp3 format. Skipping conversion.")

                    result = self.audio_transcription_logics(
                        filename=filename,
                        audio_path=audio_path,
                        content_type="audio/mpeg",
                    )

                    if "error" in result:
                        redis.set(f"audio_status:{job_profile_id}", {
                            "status": "failed",
                            "message": result.get("error"),
                            "details": result.get("details", "")
                        })
                        return

                    transcript = result.get("content", "No transcription returned")

                    redis.set(f"audio_status:{job_profile_id}", {
                        "status": "done",
                        "message": "Transcription complete",
                        "content": transcript
                    })

                elif any(x in content_type for x in ["text", "pdf", "msword", "officedocument"]):
                    logger.info(f"📝 Text-based file detected: {filename}")
                    with open(audio_path, "rb") as f:
                        contents = f.read()
                    result = self.content_extraction_logics(filename, contents, content_type)
                    if "error" in result:
                        logger.error(f"❌ Text extraction failed: {result['error']}")
                        redis.set(f"audio_status:{job_profile_id}", {
                            "status": "failed",
                            "message": result.get("error")
                        })
                        return
                    logger.success(f"✅ Text extraction successful: {filename}")
                    redis.set(f"audio_status:{job_profile_id}", {
                        "status": "done",
                        "message": "Text content extracted successfully",
                        "content": result.get("content")
                    })
                else:
                    logger.warning(f"🚫 Unsupported file type: {content_type}")
                    redis.set(f"audio_status:{job_profile_id}", {
                        "status": "failed",
                        "message": f"Unsupported file type: {content_type}"
                    })
            except Exception as conversion_error:
                logger.error(f"❌ MP3 conversion failed: {conversion_error}", exc_info=True)
                redis.set(f"audio_status:{job_profile_id}", {
                    "status": "failed",
                    "message": f"MP3 conversion failed: {conversion_error}"
                })
                return
        except Exception as e:
            logger.error(f"🔥 Error in background audio processing: {str(e)}", exc_info=True)
            redis.set(f"audio_status:{job_profile_id}", {"status": "failed", "message": str(e)})
        return 'done'

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
            print(f"[DEBUG] relevancy: {relevancy}...")
            
            # Handle case where relevancy is an error object
            if isinstance(relevancy, dict) and 'error' in relevancy:
                print(f"[ERROR] Relevancy calculation failed: {relevancy['error']}")
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
                print(f"[ERROR] KeyError accessing 'overall_evaluation': {e}")
                return {'error': str(e)}
            try:
                evaluation_metrics = overall_interview_metrics_json["evaluation_metrics"]
            except KeyError as e:
                print(f"[ERROR] KeyError accessing 'evaluation_metrics': {e}")
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
            if job_profile_id:            
                session = ipersona_session.filter_by_with_user_job_id(
                    user_profile_id=tinder_user_profile_id,
                    job_profile_id=job_profile_id, 
                    nopp=True, 
                    dataframe=False
                    ) 
            elif challenge_id:
                session = ipersona_session.filter_by_with_user_challenge_id(
                    user_profile_id=tinder_user_profile_id,
                    challenge_id=challenge_id, 
                    nopp=True, 
                    dataframe=False
                    ) 
            elif template_id:
                session = ipersona_session.filter_by_with_user_template_id(
                    user_profile_id=tinder_user_profile_id,
                    template_id=template_id, 
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
            print(f"[DEBUG] Final response keys: {list(response.keys())}")
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
                    performance = entry.get("performance", [])
                    # print("pp=======================================================================dpp")
                    # print(performance)
                    # print("pp=======================================================================dpp")

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
    
            if job_profile_id: 
                session_chatobserver = ipersona_overall.filter_by_with_user_and_job_id(
                    user_profile_id = tinder_user_profile_id, 
                    job_profile_id = job_profile_id, 
                    nopp=True, 
                    dataframe=False)
                
            elif challenge_id:
                session_chatobserver = ipersona_overall.filter_by_with_user_and_challenge_id(
                    user_profile_id = tinder_user_profile_id, 
                    challenge_id = challenge_id, 
                    nopp=True, 
                    dataframe=False)    

            elif template_id:
                session_chatobserver = ipersona_overall.filter_by_with_user_and_template_id(
                    user_profile_id = tinder_user_profile_id, 
                    template_id = template_id, 
                    nopp=True, 
                    dataframe=False)    
                       
            
            if not session_chatobserver.get("error"): 
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
                    if job_profile_id:
                        message_data["tinder_user_profile"] = tinder_user_profile_id
                        message_data["tinder_job_profile"] = job_profile_id
                    elif challenge_id:
                        message_data["tinder_user_profile"] = tinder_user_profile_id
                        message_data["challenge_document"] = challenge_id
                    elif template_id:
                        message_data["tinder_user_profile"] = tinder_user_profile_id
                        message_data["tinder_template"] = template_id

                    
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
                ipersona_user = IpersonaTraineeSchema(run_stage=run_stage)

                trainee_profile_data = ipersona_user.filter_by_alluser_id(
                    all_user_id=all_user_id, 
                    nopp=True, 
                    dataframe=False)
                
                if not trainee_profile_data:
                        logger.warn("No trainee user profiles found.")
                        return []
                
                tinder_user_profile_id = trainee_profile_data['id']    
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
                if job_profile_id:
                    message_data["tinder_user_profile"] = tinder_user_profile_id
                    message_data["tinder_job_profile"] = job_profile_id
                elif challenge_id:
                    message_data["tinder_user_profile"] = tinder_user_profile_id
                    message_data["challenge_document"] = challenge_id
                elif template_id:
                    message_data["tinder_user_profile"] = tinder_user_profile_id
                    message_data["tinder_template"] = template_id
                    
                response = ipersona_overall.save_Session_Overall_Observer(
                    params=message_data, 
                    nopp=True, 
                    dataframe=False)
                
                return response
        
        except Exception as e:
            logger.error(f"Process failed: ${str(e)}")
            return f'Error: {str(e)}'  
        