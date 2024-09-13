
import os, sys
import json
import time
from typing import List, Dict
import asyncio

#
curdir = os.path.dirname(os.path.realpath(__file__))
cpath = os.path.dirname(curdir)
if not cpath in sys.path:
    sys.path.append(cpath) 


#
from fastapi import APIRouter, BackgroundTasks
from fastapi import UploadFile, Form, File

#
import api.modules.cv_analysis as cv_analysis
from api.services.strapi_graphql import StrapiGraphql
from api.modules.utils.ioops import fileManager

#local config
from api import config
from api.pages.analysis.models import model_cv_analysis as camodel
from api.utils.logger import LLPackerLogger
from api.services import redis_client as rc

logger = LLPackerLogger(__file__)

router = APIRouter()

def get_run_stage(run_stage):
    if config.strapi_stage=='prod':
        run_stage_use = 'apply'
    else:
        run_stage_use = 'devapply' if not run_stage=='apply' else 'apply'
    
    return run_stage_use

@router.post("/upload")
async def upload_files(background_tasks: BackgroundTasks, 
                       file: UploadFile = File(...), 
                       userId: str = Form(...), 
                       email: str = Form(""),
                       run_stage: str = Form('devapply'),
                       test_mode: bool = Form(False),
                       overwrite: bool = Form(False)):
    
    
    funcname = sys._getframe().f_code.co_name 
    logger.divider(f'START: {funcname}')
    
    start_time_0 = time.time()
        
    output = {
                "userId": userId,
                "email": email,
                "data": None,
                "status": 400, 
                "message": "Failed",
                "time_to_wait": -1
            }
    
    m1 = f"file: {file.filename}, type: {file.content_type}"
    logger.good(f"Got {m1}, userId: {userId}", fg='pink')
    
    try:        
        payload = camodel.FileReceivedPayload(filename=file.filename, 
                                      content_type=file.content_type, 
                                      userId=userId, 
                                      email = email)        
        file_path = config.temp_path(payload.filename)        
        logger.good(f"Saving uploaded file to: {file_path}", fg='blue')
        with open(file_path, "wb") as f:
            contents = await file.read()
            f.write(contents)            
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        output['message'] = f"Error saving file: {str(e)}"
        return camodel.AnalysisResponse(**output)
    
    #    
    zauto = cv_analysis.CVAnalysisModel()
                
    # background task to generate competency
    async def bkfunc(resume_text, target_sfia):   
        await asyncio.sleep(0)             
        # Competency Generation
        logger.good(f"Starting competency generation in the background", fg='blue')        
        run_stage_use = get_run_stage(run_stage)
        m1 = f"run_stage={run_stage_use}"          
        start_time_1 = time.time()        
        analysis = None
        status = 400
        
        try:  
            analysis = await zauto.resume_sfia_analysis(resume_text, 
                                                        target_sfia=target_sfia)
            # if isinstance(analysis, dict):
            #     print(json.dumps(analysis, indent=2))
            # else:                
            #     print(f"EMPTY analysis returned: {analysis}")
                
            logger.good(f"Competency generation completed")                                            
            #                    
            if not test_mode:        
                if not analysis:
                    analysis = None
                    analysed=False
                    remark = {"failed": True, "message": "Failed to generate competency"}
                    logger.error(f"Failed to generate competency: {remark['message']}")
                else:
                    analysed=True
                    remark = {"failed": False, "message": "Successfully generated competency"}
                                                            
                sg = StrapiGraphql(run_stage=run_stage_use)
                _ = sg.create_cv_analysis(userId, analysis, analysed=analysed, remark=remark)
                
                logger.good(f"CV Analysis saved to Tenx run_stage={run_stage_use}")
                       
            status = 200                               
        except Exception as e:
            logger.error(f"Error generating competency: {str(e)}")       
            analysis = None
            status = 400           
            if not test_mode: 
                analysed=False
                remark = {"failed": True, "message": f"Failed to generate competency: {str(e)}"}
                logger.error(f"Failed to generate competency: {remark['message']}")
                                    
                run_stage_use = get_run_stage(run_stage)                            
                sg = StrapiGraphql(run_stage=run_stage_use)
                _ = sg.create_cv_analysis(userId, analysis, analysed=analysed, remark=remark)
                logger.good(f"Empty CV Analysis saved to Tenx {m1}", fg='blue')                          
            
        # save CV to S3
        try:
            _ = fileManager()._save_to_file_cache(file_path, 
                                                    payload.filename, 
                                                    key=userId
                                                )                                        
        except Exception as e:
            logger.error(f"Error saving CV to S3: {str(e)}")  
           
        try:
            end_time = time.time() 
            elapsed_time = end_time - start_time_1  
            print(f"Time taken to analyse CV: {elapsed_time:.2f} seconds")           
        except Exception as e:
            logger.error(f"Error calculating time taken: {str(e)}")
                        
        return analysis, status
    
    # process cv and schedule for background task if necessary
    try:
        result = await zauto.prepare_resume_sfia_analysis(file_path, overwrite=overwrite) 
    
        is_resume_or_cv = result.get('is_resume_or_cv', False)
        
        resume_text = result.get('resume_text', "")
        target_sfia = result.get('target_sfia', {})     
        analysis = result['analysis']
        
        output['status'] = result.get('status', 200)
        output['message'] = result.get('message', "")
        output['data'] = analysis    
          
        # request job cards in the backgroun  
        if analysis:
            logger.good(f"Analysis already done!")
            output['time_to_wait'] = 1        
            analysed=True
            remark = {"failed": False, "message": "Successfully generated competency"}
            
            if not analysis:
                analysis = None
                
            run_stage_use = get_run_stage(run_stage)                                           
            sg = StrapiGraphql(run_stage=run_stage_use)
            _ = sg.create_cv_analysis(userId, analysis, analysed=analysed, remark=remark)                
            
        elif is_resume_or_cv and resume_text:
            
            if test_mode:
                analysis, status = await bkfunc(resume_text, target_sfia)
                output['status'] = status
                output['data'] = analysis
                if status==200:
                    output["message"] = 'Successfully analysed the provided CV!'
                else:
                    output["message"] = 'Failed to analyse the CV!'
            else:
                background_tasks.add_task(bkfunc, resume_text, target_sfia)                
                m1 = "Background task scheduled to generate competency"
                output["status"] = 200
                output['time_to_wait'] = 25
                output["message"] = m1             
                logger.good(m1)
                
        else:
            logger.error(output.get('message', 'Failed to analyse the CV'))            
               
    except Exception as e:
        logger.error(f"Error processing CV: {str(e)}")
        output['message'] = f"Error processing CV: {str(e)}"         

    if not output.get('data',None):
        output['data'] = None
        
    result = camodel.AnalysisResponse(**output)
    
    end_time = time.time() 
    elapsed_time = end_time - start_time_0      
    logger.divider(f'END: {funcname}, time taken: {elapsed_time:.2f} seconds')
    
    return result

@router.post("/get_cv_analysis")
async def get_cv_analysis(
                       userId: str = Form(...), 
                       email: str = Form(""),
                       run_stage: str = Form('devapply'),
                       total_time_waited: int = Form(30)
                       ):
    
    funcname = sys._getframe().f_code.co_name 
    logger.divider(f'START: {funcname}')
        
    run_stage_use = get_run_stage(run_stage)
    

    try:
        sg = StrapiGraphql(run_stage=run_stage_use)    
        res = sg.get_cv_analysis(userId)  
        
        if not res:
            res = {}            
    #
        analysis = res.get('AnalysisResponse', {}) 
        done = res.get('analysed', False)
        remark = res.get('remark', {})
        if not remark:
            remark = {}
        failed = remark.get('failed', False)
        remark_msg = remark.get('message', "")
        print(f"done: {done}, failed: {failed}, remark: {remark_msg}")
        
        if done:
            status = 200
            time_to_wait = -1
            
            if analysis:
                m1 = f"CV analysis Done!"
                logger.good(m1)
            else:
                m1 = f"CV analysis Done, but has returned empty!"
                logger.warn(m1)
                
        elif failed:
            m1 = f"CV analysis failed: {remark_msg}"
            logger.error(m1)
            analysis = {}
            done = False
            time_to_wait = -1   
            status = 400     
                                                            
        else:
            status = 200
            if total_time_waited<35:
                m1 = f"CV analysis is still processing ..."
                time_to_wait = 5
            elif 35<total_time_waited<60:
                m1 = f"Background CV analysis is taking longer than expected ..."
                time_to_wait = 10
            else:
                m1 = f"Background CV analysis is assumed failed!"
                time_to_wait = -1
                
            logger.good(m1, fg='blue')            
            
    except Exception as e:
        m1 = f"Error getting CV analysis: {str(e)}"
        logger.error(m1)
        analysis = {}
        done = False
        time_to_wait = -1
        status = 400
    
    if not analysis:
        analysis = None
        
    output = {
                "userId": userId,
                "email": email,
                "data": analysis,
                "status": status, 
                "message": m1,
                "time_to_wait": time_to_wait
            }  
        
    result = camodel.AnalysisResponse(**output)
    logger.divider(f'END: {funcname}')
    
    return result        