import ast
from prisma import Prisma

async def create_session(data):
    try:
        db = Prisma()
        await db.connect()
        personasession = await db.personasession.create(data)
        # print(f'created post: {personasession.model_dump()}') 
        personasession.alluser = int(personasession.alluser)
        personasession.userId = int(personasession.userId)
        personasession.jobId = int(personasession.jobId)
        personasession.generated_questions = ast.literal_eval(personasession.generated_questions)
        return personasession.model_dump()
    except Exception as e:
        return {"error": str(e)}
       

async def create_chat(sessionId, message, status):
    try:
        session_chathistory = await fetch_chat_history(sessionId)
        
        if len(session_chathistory) == 0:
            db = Prisma()
            await db.connect()        

            personamessage = await db.personamessage.create(
                {
                    "personasessionId": sessionId, 
                    "chathistory": str(message),
                    "status": status
                }
            )

            print(f'created chat') 
            return personamessage.model_dump()
        else:
            print("session interview exist")
            session_chathistory[0].chathistory.extend(message) 
            
            data = {
                "id": session_chathistory[0].id,
                "chathistory": session_chathistory[0].chathistory
            }
            updated = await update_session(data)     
            print("updated!")
            return updated
            
    except Exception as e:
        return {"error": str(e)}
       

async def create_observer(sessionId, interview_evaluation, interview_evaluation_metrics):
    try:
        db = Prisma()
        await db.connect()
        

        personaobserver = await db.personaobserver.create(
            {
                "personasessionId": sessionId, 
                "interview_evaluation": str(interview_evaluation),
                "interview_evaluation_metrics": str(interview_evaluation_metrics)
            }
        )

        print(f'created observer') 
        return personaobserver.model_dump()
    except Exception as e:
        return {"error": str(e)}


async def fetch_sessions(userId):
    try:
        db = Prisma()
        await db.connect()
        
        personasessions = await db.personasession.find_many(
            where={
                "userId": userId
            },
            include={
                "personamessages": True,
                "personaobservers": True
            }
        )
        
        length = len(personasessions)
        index = length - 1
        result = personasessions[index]
        user_data = {
            "all_data": personasessions,
            "latest_data": result
        }
        
        if user_data["latest_data"]:
            print(True)
            question_data = user_data["latest_data"].generated_questions
            if isinstance(question_data, str):
                try:
                    user_data["latest_data"].generated_questions = ast.literal_eval(question_data)
                except (ValueError, SyntaxError) as e:
                    print(f"Error parsing generated_questions: {e}")
            elif isinstance(question_data, list):
                user_data["latest_data"].generated_questions = question_data 
        else:
            print(False)      
                 
        data = {
            "all_user_data": user_data["all_data"],
            "latest_user_data": user_data["latest_data"]
        } 
        
        if data:
            return data
        else:
            return {"error": f"Session with id {userId} not found"}
    except Exception as e:
        return {"error": f"{str(e)}"}
       
    
async def fetch_chat_history(personasessionId):
    try:
        db = Prisma()
        await db.connect()
        
        personamessages = await db.personamessage.find_many(
            where={
                "personasessionId": int(personasessionId)
            },
        )
        
        messages_as_dicts = [message.__dict__ for message in personamessages]
        
        if isinstance(personamessages, list):
            for entry in personamessages:
                if entry:
                    chathistory_data = entry.chathistory
                    if isinstance(chathistory_data, str) and chathistory_data:  
                        try:
                            entry.chathistory = ast.literal_eval(chathistory_data)
                        except (ValueError, SyntaxError) as e:
                            print(f"Error parsing chathistory for entry {entry}: {e}")

        if personamessages:
            return personamessages
        else:
            return []
    except Exception as e:
        return {"error": f"{str(e)}"}


async def fetch_chat_observer(personasessionId):
    try:
        db = Prisma()
        await db.connect()
        
        personaobservers = await db.personaobserver.find_many(
            where={
                "personasessionId": int(personasessionId)
            },
        )
        
        messages_as_dicts = [message.__dict__ for message in personaobservers]
        
        if isinstance(personaobservers, list):
            for entry in personaobservers:
                if entry:
                    interview_evaluation_data = entry.interview_evaluation
                    interview_evaluation_metrics_data = entry.interview_evaluation_metrics
                    if isinstance(interview_evaluation_data, str) and interview_evaluation_data:  
                        if isinstance(interview_evaluation_metrics_data, str) and interview_evaluation_metrics_data: 
                            try:
                                entry.interview_evaluation = ast.literal_eval(interview_evaluation_data)
                                entry.interview_evaluation_metrics = ast.literal_eval(interview_evaluation_metrics_data)
                            except (ValueError, SyntaxError) as e:
                                print(f"Error parsing interview_evaluation for entry {entry}: {e}")

        if personaobservers:
            return personaobservers
        else:
            return []
    except Exception as e:
        return {"error": f"{str(e)}"}


async def update_session(data):
    try:
        async with Prisma() as db:
            updated_message = await db.personamessage.update(
                where={"id": int(data['id'])},
                data={
                    "chathistory": str(data['chathistory'])  # Update only the chathistory field
                }
            )
        return updated_message
    
    except Exception as e:
        return {"error": str(e)}


async def delete_session(id):
    async with Prisma() as db:
        data = await db.personasession.delete(
            where={"id": id}
        )
    return data