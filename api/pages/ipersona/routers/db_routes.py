import api.llm.ipersona.ipersona_schema as db
import api.llm.ipersona.ipersona_db as database
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import api.pages.ipersona.models.persona as pemodel
import ast
import api.llm.ipersona.ipersona_prisma as prisma
from api.services.strapi_ipersona import IpersonaManager

route_strapi = FastAPI(root_path="/wv")

@route_strapi.post("/fetch_user_session")
async def fetch_session(recieved: pemodel.SessionRequestRecieved):
    """
    Fetches user session data from the database.

    This asynchronous function retrieves the session data for a given user ID 
    and processes the latest data, particularly handling generated questions.

    Parameters:
    ----------
    recieved : pemodel.SessionRequestRecieved
        An object containing the user ID for which the session data is to be fetched.

    Returns:
    -------
    dict
        A dictionary containing all user data and the latest user data, or an 
        error response if an exception occurs during processing.
    """
    try:
        ipersona_manager = IpersonaManager(alluser=recieved.alluser, jobId=recieved.jobId, run_stage="dev")
        user_data = ipersona_manager.get_job_sessions()
        #user_data = ipersona_manager.get_job_sessions_observers()


        return user_data
    
    except Exception as e:
        print(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})
   
   
@route_strapi.post("/fetch_chat_history")
async def fetch_chat_history(recieved: pemodel.ChatHistoryRequestRecieved):  
    """
    Fetches the chat history from the database.

    This asynchronous function retrieves all chat history associated with the 
    specified session.

    Parameters:
    ----------
    recieved : pemodel.ChatHistoryRequestRecieved
        An object containing the necessary information to fetch the chat history.

    Returns:
    -------
    list
        A list containing the chat history for the session, or None if an 
        exception occurs during processing.
    """
    try:
        ipersona_manager = IpersonaManager(sessionId=recieved.sessionId, run_stage="dev")
        session_chathistory = ipersona_manager.get_messages()
  
        return session_chathistory

    except Exception as e:
        print(f"Error fetching chat history: {e}")
        return None  
    
    except Exception as e:
        print(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})
    

@route_strapi.post("/fetch_user_session_observers")
async def fetch_user_session_observer(recieved: pemodel.UserSessionRequestRecieved):  
    try:
        ipersona_manager = IpersonaManager(sessionId=recieved.alluser, jobId=recieved.jobId, run_stage="dev")
        session_chatobserver = ipersona_manager.get_job_sessions_observers()
         
        return session_chatobserver

    except Exception as e:
        print(f"Error fetching chat observer: {e}")
        return None  
    
    except Exception as e:
        print(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})
    
@route_strapi.post("/fetch_user_all_observer")
async def fetch_user_all_observer(recieved: pemodel.ChatHistoryRequestRecieved):  
    try:
        ipersona_manager = IpersonaManager(sessionId=recieved.sessionId, run_stage="dev")
        session_chatobserver = ipersona_manager.get_observers()
         
        return session_chatobserver

    except Exception as e:
        print(f"Error fetching chat observer: {e}")
        return None  
    
    except Exception as e:
        print(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})
    
@route_strapi.post("/fetch_single_session")
async def fetch_single_session(recieved: pemodel.ChatHistoryRequestRecieved):  
    try:
        ipersona_manager = IpersonaManager(sessionId=recieved.sessionId, run_stage="dev")
        session_fetched = ipersona_manager.get_session()
         
        return session_fetched

    except Exception as e:
        print(f"Error fetching chat observer: {e}")
        return None  
    
    except Exception as e:
        print(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})