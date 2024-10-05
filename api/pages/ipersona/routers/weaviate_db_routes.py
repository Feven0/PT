import api.llm.ipersona.ipersona_schema as db
import api.llm.ipersona.ipersona_db as database
from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import JSONResponse
import api.pages.ipersona.models.persona as pemodel
import ast

route_weaviate = FastAPI(openapi_prefix="/wv")

@route_weaviate.post("/fetch_user_session")
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
    userId = recieved.userId   
    try:
        user_data = await db.fetch_session(userId)     
        if 'generated_questions' in user_data["latest_data"]:
            question_data = user_data["latest_data"]['generated_questions']
            if question_data:
                try:
                    user_data["latest_data"]['generated_questions'] = ast.literal_eval(question_data)
                except (ValueError, SyntaxError) as e:
                    print(f"Error parsing generated_questions: {e}")
                     
        data = {
            "all_user_data": user_data["all_data"],
            "latest_user_data": user_data["latest_data"]
        } 
        return data
    
    except Exception as e:
        print(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})
   
   
@route_weaviate.post("/fetch_chat_history")
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
        session_chathistory = await database.fecth_all_chathistory(recieved)

        return session_chathistory

    except Exception as e:
        print(f"Error fetching chat history: {e}")
        return None  
    
    except Exception as e:
        print(f"Error processing files: {e}")
        return JSONResponse(status_code=500, content={"error": "Error processing files"})
    
