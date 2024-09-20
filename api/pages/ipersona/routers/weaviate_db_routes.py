import api.llm.ipersona.ipersona_schema as db
import api.llm.ipersona.ipersona_db as database
from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import JSONResponse
import api.pages.ipersona.models.model_persona as pemodel
import ast

route_weaviate = FastAPI(openapi_prefix="/wv")

@route_weaviate.post("/fetch_user_session")
async def fetch_session(recieved: pemodel.SessionRequestRecieved):
    userId = recieved.userId   
    try:
        user_data = await db.fetch_session(userId)      
        data = {
            "all_user_data": user_data["all_data"],
            "latest_user_data": user_data["latest_data"]
        } 
        return data
    
    except Exception as e:
        print(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})
   
   
@route_weaviate.post("/fetch_session_job")
async def fetch_session_job(recieved: pemodel.SessionJobRequestRecieved):
    print("data", recieved)

    sessionId = recieved.sessionId
    jbId = recieved.jbId
   
    try:
        latest_session_job = await db.fetch_job(sessionId, jbId)
        latest_analysis = None
        latest_analysischat = None
        latest_interviewchat = None

        # Check and parse 'analysis'
        if 'analysis' in latest_session_job:
            analysis_data = latest_session_job['analysis']
            if analysis_data:
                try:
                    latest_analysis = ast.literal_eval(analysis_data)
                except (ValueError, SyntaxError) as e:
                    print(f"Error parsing analysis: {e}")

        # Check and parse 'analysischat'
        if 'analysischat' in latest_session_job:
            analysischat_data = latest_session_job['analysischat']
            if analysischat_data:
                try:
                    latest_analysischat = ast.literal_eval(analysischat_data)
                except (ValueError, SyntaxError) as e:
                    print(f"Error parsing analysischat: {e}")

        # Check and parse 'interviewchat'
        if 'interviewchat' in latest_session_job:
            interviewchat_data = latest_session_job['interviewchat']
            if interviewchat_data:
                try:
                    latest_interviewchat = ast.literal_eval(interviewchat_data)
                except (ValueError, SyntaxError) as e:
                    print(f"Error parsing interviewchat: {e}")

        # Prepare the data to return
        data = {
            "latest_user_data": latest_session_job,
            "latest_analysis": latest_analysis,
            "latest_analysischat": latest_analysischat,
            "latest_interviewchat": latest_interviewchat
        }
        
        return data
    
    except Exception as e:
        print(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})
    
@route_weaviate.post("/fetch_inter_metrics")
async def fetch_evaluation_metrics(recieved: pemodel.MetricsRequestRecieved):
    print("data metrics", recieved)

    userId = recieved.userId
    sessionId = recieved.sessionId
    jbId = recieved.jbId
   
    try:
        metrics_data = await db.fetch_evaluation_metrics(userId, sessionId, jbId)
        
        # Check and parse "improvement"
        if "improvement" in metrics_data['latest_user_metrics']:
            improvement_string = metrics_data['latest_user_metrics']['improvement']
            if improvement_string:
                try:
                    metrics_data['latest_user_metrics']['improvement'] = ast.literal_eval(improvement_string)
                except (ValueError, SyntaxError) as e:
                    print(f"Error parsing improvement: {e}")

        # Check and parse "strength"
        if "strength" in metrics_data['latest_user_metrics']:
            strength_string = metrics_data['latest_user_metrics']['strength']
            if strength_string:
                try:
                    metrics_data['latest_user_metrics']['strength'] = ast.literal_eval(strength_string)
                except (ValueError, SyntaxError) as e:
                    print(f"Error parsing strength: {e}")

        data = {
            "all_metrics_data": metrics_data['all_user_metrics'],
            "latest_evaluation_metrics": metrics_data['latest_user_metrics']
        }
        
        return data
    
    except Exception as e:
        print(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})