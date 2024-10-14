import ast
import api.llm.ipersona.ipersona_schema as db


async def save_chathistory_to_db(recieved):
    try:
        data = {
            "userId": recieved['user_session']['userId'], 
            "sessionId": recieved['user_session']['sessionId'], 
            "jobId": recieved['user_session']['jobId'],
            "chathistory": str(recieved['history'])
        }
        job_chathistory_id = await db.Add_Interview_History(data)
        print("chat_history_added:", job_chathistory_id)

        return job_chathistory_id
    
    except Exception as e:
        return f'Error: {str(e)}' 
    
async def fecth_all_chathistory(recieved):
    sessionId = recieved.sessionId
   
    try:
        session_chathistory = await db.fetch_chat_history(sessionId)
            
        if isinstance(session_chathistory, list):
            for entry in session_chathistory:
                if 'chathistory' in entry:
                    chathistory_data = entry['chathistory']
                    if isinstance(chathistory_data, str) and chathistory_data:  
                        try:
                            entry['chathistory'] = ast.literal_eval(chathistory_data)
                        except (ValueError, SyntaxError) as e:
                            print(f"Error parsing chathistory for entry {entry}: {e}")

        return session_chathistory
    
    except Exception as e:
        print(f"Error processing files: {e}")
        return f'Error: {str(e)}'     

