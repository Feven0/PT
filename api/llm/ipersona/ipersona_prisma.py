import asyncio
from prisma import Prisma

async def create_session():
    try:
        db = Prisma()
        await db.connect()
        

        personasession = await db.personasession.create(
            {
                "alluser": "recieved.alluser",
                "userId": "recieved.userId",
                "jobId": "recieved.jobId",
                "username": "recieved.username",
                "persona": "recieved.persona",
                "generated_questions": "[{'user_type': 'candidate', 'response': 'I have a CS background'}]"
            }
        )

        print(f'created post: {personasession.model_dump()}') 
        return personasession.model_dump()
    except Exception as e:
        return {"error": str(e)}
       

async def create_chat():
    try:
        db = Prisma()
        await db.connect()        

        personamessage = await db.personamessage.create(
            {
                "personasessionId": 1, 
                "chathistory": "[{'user_type': 'candidate', 'response': 'i have a cs background'}, {'user_type': 'assistant', 'response': 'elborate more on you answer'}]",
            }
        )

        print(f'created post: {personamessage.model_dump()}') 
        return personamessage.model_dump()
    except Exception as e:
        return {"error": str(e)}
       

async def create_observer():
    try:
        db = Prisma()
        await db.connect()
        

        personaobserver = await db.personaobserver.create(
            {
                "personasessionId": 1, 
                "interview_evaluation": "[{'user_type': 'candidate', 'response': 'i have a cs background'}, {'user_type': 'assistant', 'response': 'elborate more on you answer'}]",
                "interview_evaluation_metrics": "[{'user_type': 'candidate', 'response': 'i have a cs background'}, {'user_type': 'assistant', 'response': 'elborate more on you answer'}]"
            }
        )

        print(f'created post: {personaobserver.model_dump()}') 
        return personaobserver.model_dump()
    except Exception as e:
        return {"error": str(e)}


async def fetch_session():
    try:
        db = Prisma()
        await db.connect()
        
        personasession = await db.personasession.find_many(
            include={
                "personamessages": True,
                "personaobservers": True
            }
        )
        if personasession:
            return personasession
        else:
            return {"error": f"Session with id {id} not found"}
    except Exception as e:
        return {"error": f"{str(e)}"}
    
    
async def fetch_session(id):
    try:
        db = Prisma()
        await db.connect()
        
        personasession = await db.personasession.find_unique(
            where={
                "id": id
            },
            include={
                "personamessages": True,
                "personaobservers": True
            }
        )
        if personasession:
            return personasession
        else:
            return {"error": f"Session with id {id} not found"}
    except Exception as e:
        return {"error": f"{str(e)}"}


async def update_session(id):
    async with Prisma() as db:
        user = {
                "alluser": "1",
                "userId": "2",
                "jobId": "3",
                "username": "recieved.username",
                "persona": "recieved.persona",
                "generated_questions": "[{'user_type': 'candidate', 'response': 'I have a CS background'}]"
            }
        data = await db.personasession.update(
            where={"id": id},
            data=user
        )
    return data


async def delete_session(id):
    async with Prisma() as db:
        data = await db.personasession.delete(
            where={"id": id}
        )
    return data