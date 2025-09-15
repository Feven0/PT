import asyncio
from api.services.celery.celery_worker import celery_app
from api.services.celery.task_tracker import task_tracker, TaskStatus, TaskType
from api.utils.audio_utils import AudioUtils
audio_util = AudioUtils()

@celery_app.task(bind=True)
def process_upload_external_audio_task(
    self,
    filename, content_type, audio_path, 
    job_profile_id, challenge_id, template_id, 
    session_id, all_user_id, external, run_stage
):
    # Register task with tracker - now supporting all target types
    target = task_tracker.create_target_dict(
        job_profile_id=job_profile_id,
        challenge_id=challenge_id,
        template_id=template_id,
        session_id=session_id,
        all_user_id=all_user_id
    )
    
    # Initialize task tracking
    task_registered = False
    
    try:
        print(f"🔧 [DEBUG] Registering audio_processing task for job_profile_id: {job_profile_id}")
        print(f"🔧 [DEBUG] Target: {target}")
        
        task_data = task_tracker.register_task(
            task_type="audio_processing",
            target=target,
            metadata={
                "filename": filename,
                "content_type": content_type,
                "external": external,
                "run_stage": run_stage,
                "celery_task_id": self.request.id
            }
        )
        print(f"✅ [DEBUG] Task registered successfully: {task_data}")
        task_registered = True
        
        # Update status to processing
        success = task_tracker.update_task_progress(
            target=target,
            task_type="audio_processing",
            progress=10,
            status=TaskStatus.PROCESSING
        )
        print(f"🔄 [DEBUG] Status update to processing: {'✅' if success else '❌'}")
        
    except Exception as e:
        print(f"❌ [DEBUG] Failed to register task: {e}")
        import traceback
        traceback.print_exc()
        # If we can't even register the task, we can't track it further
        raise e
    
    try:
        # Run the async function in a synchronous context
        result = asyncio.run(audio_util.process_upload_external_audio(
            filename, 
            content_type, 
            audio_path, 
            job_profile_id, 
            challenge_id, 
            template_id,
            all_user_id, 
            external, 
            run_stage
        ))
        
        # Update status to completed
        success = task_tracker.update_task_progress(
            target=target,
            task_type="audio_processing",
            progress=100,
            status=TaskStatus.COMPLETED
        )
        print(f"✅ [DEBUG] Status update to completed: {'✅' if success else '❌'}")
        
        return result
        
    except Exception as e:
        print(f"❌ [DEBUG] Task failed with error: {e}")
        
        # Only update status if task was registered
        if task_registered:
            success = task_tracker.update_task_progress(
                target=target,
                task_type="audio_processing",
                progress=0,
                status=TaskStatus.FAILED,
                error_message=str(e)
            )
            print(f"❌ [DEBUG] Status update to failed: {'✅' if success else '❌'}")
        else:
            print(f"❌ [DEBUG] Task not registered, cannot update status")
        
        # Re-raise the exception so Celery knows the task failed
        raise e

@celery_app.task(bind=True)
def process_upload_external_files_task(
    self,
    question_filename, question_content_type, question_audio_path, question_contents,
    answer_filename, answer_content_type, answer_audio_path, answer_contents,
    job_profile_id, challenge_id, template_id, session_id, all_user_id, 
    external, run_stage
):
    # Register task with tracker - now supporting all target types
    target = task_tracker.create_target_dict(
        job_profile_id=job_profile_id,
        challenge_id=challenge_id,
        template_id=template_id,
        session_id=session_id,
        all_user_id=all_user_id
    )
    
    # Initialize task tracking
    task_registered = False
    
    try:
        print(f"🔧 [DEBUG] Registering dual_audio_processing task for job_profile_id: {job_profile_id}")
        print(f"🔧 [DEBUG] Target: {target}")
        
        task_data = task_tracker.register_task(
            task_type="dual_audio_processing",
            target=target,
            metadata={
                "question_filename": question_filename,
                "answer_filename": answer_filename,
                "question_content_type": question_content_type,
                "answer_content_type": answer_content_type,
                "external": external,
                "run_stage": run_stage,
                "celery_task_id": self.request.id
            }
        )
        print(f"✅ [DEBUG] Task registered successfully: {task_data}")
        task_registered = True
        
        # Update status to processing
        success = task_tracker.update_task_progress(
            target=target,
            task_type="dual_audio_processing",
            progress=10,
            status=TaskStatus.PROCESSING
        )
        print(f"🔄 [DEBUG] Status update to processing: {'✅' if success else '❌'}")
        
    except Exception as e:
        print(f"❌ [DEBUG] Failed to register task: {e}")
        import traceback
        traceback.print_exc()
        # If we can't even register the task, we can't track it further
        raise e
    
    try:
        # Run the async function in a synchronous context
        result = asyncio.run(audio_util.process_upload_external_files(
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
            run_stage
        ))
        
        # Update status to completed
        success = task_tracker.update_task_progress(
            target=target,
            task_type="dual_audio_processing",
            progress=100,
            status=TaskStatus.COMPLETED
        )
        print(f"✅ [DEBUG] Status update to completed: {'✅' if success else '❌'}")
        
        return result
        
    except Exception as e:
        print(f"❌ [DEBUG] Task failed with error: {e}")
        
        # Only update status if task was registered
        if task_registered:
            success = task_tracker.update_task_progress(
                target=target,
                task_type="dual_audio_processing",
                progress=0,
                status=TaskStatus.FAILED,
                error_message=str(e)
            )
            print(f"❌ [DEBUG] Status update to failed: {'✅' if success else '❌'}")
        else:
            print(f"❌ [DEBUG] Task not registered, cannot update status")
        
        # Re-raise the exception so Celery knows the task failed
        raise e 

@celery_app.task(bind=True)
def process_upload_external_answer_file_task(
    self,
    question_filename, question_content_type, question_audio_path, question_contents,
    answer_filename, answer_content_type, answer_audio_path, answer_contents,
    job_profile_id, challenge_id, template_id, session_id, all_user_id, 
    external, run_stage
):
    # Register task with tracker - now supporting all target types
    target = task_tracker.create_target_dict(
        job_profile_id=job_profile_id,
        challenge_id=challenge_id,
        template_id=template_id,
        session_id=session_id,
        all_user_id=all_user_id
    )
    
    # Initialize task tracking
    task_registered = False
    
    try:
        print(f"🔧 [DEBUG] Registering dual_audio_processing task for job_profile_id: {job_profile_id}")
        print(f"🔧 [DEBUG] Target: {target}")
        
        task_data = task_tracker.register_task(
            task_type="dual_audio_processing",
            target=target,
            metadata={
                "question_filename": question_filename,
                "answer_filename": answer_filename,
                "question_content_type": question_content_type,
                "answer_content_type": answer_content_type,
                "external": external,
                "run_stage": run_stage,
                "celery_task_id": self.request.id
            }
        )
        print(f"✅ [DEBUG] Task registered successfully: {task_data}")
        task_registered = True
        
        # Update status to processing
        success = task_tracker.update_task_progress(
            target=target,
            task_type="dual_audio_processing",
            progress=10,
            status=TaskStatus.PROCESSING
        )
        print(f"🔄 [DEBUG] Status update to processing: {'✅' if success else '❌'}")
        
    except Exception as e:
        print(f"❌ [DEBUG] Failed to register task: {e}")
        import traceback
        traceback.print_exc()
        # If we can't even register the task, we can't track it further
        raise e
    
    try:
        # Run the async function in a synchronous context
        result = asyncio.run(audio_util.process_upload_external_files(
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
        ))
        
        # Update status to completed
        success = task_tracker.update_task_progress(
            target=target,
            task_type="dual_audio_processing",
            progress=100,
            status=TaskStatus.COMPLETED
        )
        print(f"✅ [DEBUG] Status update to completed: {'✅' if success else '❌'}")
        
        return result
        
    except Exception as e:
        print(f"❌ [DEBUG] Task failed with error: {e}")
        
        # Only update status if task was registered
        if task_registered:
            success = task_tracker.update_task_progress(
                target=target,
                task_type="dual_audio_processing",
                progress=0,
                status=TaskStatus.FAILED,
                error_message=str(e)
            )
            print(f"❌ [DEBUG] Status update to failed: {'✅' if success else '❌'}")
        else:
            print(f"❌ [DEBUG] Task not registered, cannot update status")
        
        # Re-raise the exception so Celery knows the task failed
        raise e 

@celery_app.task(bind=True)
def process_upload_external_answer_with_template_task(
    self,
    answer_filename, answer_content_type, answer_audio_path, answer_contents,
    job_profile_id, challenge_id, template_id, session_id, all_user_id,
    external, run_stage
):
    # Register task with tracker - now supporting all target types
    target = task_tracker.create_target_dict(
        job_profile_id=job_profile_id,
        challenge_id=challenge_id,
        template_id=template_id,
        session_id=session_id,
        all_user_id=all_user_id
    )
    
    # Initialize task tracking
    task_registered = False
    
    try:
        print(f"🔧 [DEBUG] Registering template_answer_processing task for job_profile_id: {job_profile_id}")
        print(f"🔧 [DEBUG] Target: {target}")
        
        task_data = task_tracker.register_task(
            task_type="template_answer_processing",
            target=target,
            metadata={
                "template_id": template_id,
                "answer_filename": answer_filename,
                "answer_content_type": answer_content_type,
                "external": external,
                "run_stage": run_stage,
                "celery_task_id": self.request.id
            }
        )
        print(f"✅ [DEBUG] Task registered successfully: {task_data}")
        task_registered = True
        
        # Update status to processing
        success = task_tracker.update_task_progress(
            target=target,
            task_type="template_answer_processing",
            progress=10,
            status=TaskStatus.PROCESSING
        )
        print(f"🔄 [DEBUG] Status update to processing: {'✅' if success else '❌'}")
        
    except Exception as e:
        print(f"❌ [DEBUG] Failed to register task: {e}")
        import traceback
        traceback.print_exc()
        # If we can't even register the task, we can't track it further
        raise e
    
    try:
        # Fetch template questions from database
        print(f"📋 [DEBUG] Fetching template questions for template_id: {template_id}")
        from api.llm.ipersona.ipersona_strapi_schemas import IpersonaTinderTemplateSchema
        
        ipersona_template = IpersonaTinderTemplateSchema()
        fetched_template = ipersona_template.get_tinder_template_id(
            templateId=template_id, 
            return_object=True, 
            nopp=True, 
            dataframe=False
        )
        
        # Extract template_questions from the fetched template
        template_questions = []
        if fetched_template and isinstance(fetched_template, dict):
            attributes = fetched_template.get("attributes", {})
            template_questions = attributes.get("attributes", {}).get("template_questions", [])
        
        print(f"📋 [DEBUG] Extracted {len(template_questions)} template questions")
        
        if not template_questions:
            error_msg = f"No template questions found for template_id: {template_id}"
            print(f"❌ [DEBUG] {error_msg}")
            if task_registered:
                task_tracker.update_task_progress(
                    target=target,
                    task_type="template_answer_processing",
                    progress=100,
                    status=TaskStatus.FAILED,
                    error_message=error_msg
                )
            return {"error": error_msg}
        
        # Run the async function in a synchronous context
        result = asyncio.run(audio_util.process_upload_external_answer_with_template(
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
            run_stage
        ))
        
        # Update status to completed
        success = task_tracker.update_task_progress(
            target=target,
            task_type="template_answer_processing",
            progress=100,
            status=TaskStatus.COMPLETED
        )
        print(f"✅ [DEBUG] Status update to completed: {'✅' if success else '❌'}")
        
        return result
        
    except Exception as e:
        print(f"❌ [DEBUG] Task failed with error: {e}")
        
        # Only update status if task was registered
        if task_registered:
            success = task_tracker.update_task_progress(
                target=target,
                task_type="template_answer_processing",
                progress=0,
                status=TaskStatus.FAILED,
                error_message=str(e)
            )
            print(f"❌ [DEBUG] Status update to failed: {'✅' if success else '❌'}")
        else:
            print(f"❌ [DEBUG] Task not registered, cannot update status")
        
        # Re-raise the exception so Celery knows the task failed
        raise e