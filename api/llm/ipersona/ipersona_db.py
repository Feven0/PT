import api.llm.ipersona.ipersona_schema as db
import ast


async def save_to_db(recieved, jbPath):
    try:
        data = {
            "sessionId": recieved.sessionId,
            "jbId": recieved.jbId,
            "jbPath": jbPath,
            "persona": "",
            "analysis": "",
            "analysischat": "",
            "interviewchat": """[{"role":'assistant', "response": "Thank you for attending the interview for the position. I've reviewed your CV and look forward to discussing your qualifications. I'll ask a series of questions, and you can respond in writing or via audio, whichever you prefer. Are you ready to proceed?"}]""",
        }
        job_session_id = await db.Add_session_Job_schema_data(data)
        
        return job_session_id
    
    except Exception as e:
        return f'Error: {str(e)}' 


async def fetch_analysis_chat(sessionId, jbId):
    try:
        print("Updating data for ID:", jbId)
        latest_user_data = await db.fetch_job(sessionId, jbId)
        latest_analysischat = None

        if 'analysischat' in latest_user_data:
            analysischat_data = latest_user_data['analysischat']
            if analysischat_data:
                try:
                    latest_analysischat = ast.literal_eval(analysischat_data)
                except (ValueError, SyntaxError) as e:
                    print(f"Error parsing analysischat: {e}")

        return latest_analysischat
    
    except Exception as e:
        return f'Error: {str(e)}' 
    
    

async def fetch_interview_chat(userId):
    try:
        latest_user_data = await db.fetch_schema_data(userId)
        latest_interviewchat = None
        
        if 'interviewchat' in latest_user_data["latest_data"]:
            interviewchat_data = latest_user_data["latest_data"]['interviewchat']
            if interviewchat_data:
                try:
                    latest_interviewchat = ast.literal_eval(interviewchat_data)
                except (ValueError, SyntaxError) as e:
                    print(f"Error parsing interviewchat: {e}")

        return latest_interviewchat
    
    except Exception as e:
        return f'Error: {str(e)}' 
    
    
    
async def analyse_chat_to_db(data, message):
    if 'analysischat' in data['user'] and data["user"]['analysischat'] != "":
            try:
                latest_analysischat = ast.literal_eval(data["user"]['analysischat'])
                print("if print")
                if not isinstance(latest_analysischat, list):
                    latest_analysischat = []
                    
                latest_analysischat.extend(message)  
                
                data_to_db = { "id": data['user']['_additional']['id'], 'analysischat': latest_analysischat}
                res = await db.update_ipersona_data_new(data_to_db, fields_to_update=['analysischat'])
                # result = await fetch_analysis_chat(data['user']['sessionId'], data['user']['jbId'])
                # print(result) 
            except (ValueError, SyntaxError) as e:
                print(f"Error parsing analysis: {e}")
    else:
        print("else print")
        data_to_db = { "id": data['user']['_additional']['id'], 'analysischat': message}
        res = await db.update_ipersona_data_new(data_to_db, fields_to_update=['analysischat'])
        # result = await fetch_analysis_chat(data['user']['userId'])
        
async def interview_chat_to_db(data, message):
    if 'interviewchat' in data['user'] and data["user"]['interviewchat'] != "":
            try:
                latest_interviewchat = ast.literal_eval(data["user"]['interviewchat'])
             
                if not isinstance(latest_interviewchat, list):
                    latest_interviewchat = []
                    
                latest_interviewchat.extend(message)  
                data_to_db = { "id": data['user']['_additional']['id'], 'interviewchat': latest_interviewchat}
                res = await db.update_ipersona_data_new(data_to_db, fields_to_update=['interviewchat'])
                # result = await fetch_interview_chat(data['user']['userId'])
                # print(res) 
            except (ValueError, SyntaxError) as e:
                print(f"Error parsing analysis: {e}")
    else:
        data_to_db = { "id": data['user']['_additional']['id'], 'interviewchat': message}
        res = await db.update_ipersona_data_new(data_to_db, fields_to_update=['interviewchat'])
        # result = await fetch_interview_chat(data['user']['userId'])
        # print(res)