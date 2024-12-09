from warnings import filterwarnings
import os, sys

#
path = os.path.dirname(os.path.realpath(__file__))
if path not in sys.path:
    sys.path.append(path)
#

from api import config
from api.services.strapi_graphql import StrapiGraphql
_ = config.load_dotenv()


import ast
import json
import logging
import time
from pathlib import Path
from urllib.parse import urlencode

#
from pydantic import BaseModel
from typing import Union
from typing import Any, Callable, Dict
#
# from mangum import Mangum
#
import multiprocessing
#from gunicorn.app.base import BaseApplication
import uvicorn
#
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Body, Request, Depends
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
#
from api.services.secret import get_auth, is_lambda
from api.pages.base import api_router as pages_router
from api.pages.ipersona.routers.ipersona_test import routes_test
from api.pages.ipersona.routers.ipersona_routes import routes
from api.pages.ipersona.socket.ipersona_socket import get_socketio_app
from api.utils.logger import LLPackerLogger

logger = LLPackerLogger(__file__)

print('done importing modules!')    
###############################################################################


folders = config.folders
settings = config.settings
origins = config.fastapi.origins


def number_of_workers():
    return (multiprocessing.cpu_count() * 2) + 1

def include_router(app):
    app.include_router(pages_router)
    pass


def configure_static(app):
    #app.mount("/static", StaticFiles(directory=folders.static), name="static")
    pass

def configure_cors(app, origins=["*"]):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"])
    

def start_application():
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.PROJECT_VERSION,
        debug=False
        )                 
    configure_cors(app)
    include_router(app)        
    app.include_router(pages_router)   
    
 
            
    #configure_static(app)
    return app


###############################################################################
#   Define app that takes care of everything                                  #
###############################################################################

#[Depends(verify_token), Depends(verify_key)]
#app = FastAPI(dependencies=[Depends(verify_token)])


app = start_application()
print('start app..')
# fast_app = FastAPI(
#     title=settings.PROJECT_NAME,
#     description=settings.PROJECT_DESCRIPTION,
#     version=settings.PROJECT_VERSION,
#     debug=False
#     )
fast_app = app
from fastapi import Request, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json

# Middleware for checking token authentication
@app.middleware("http")
async def check_authentication(request: Request, call_next):
    origin = request.headers.get('referer', "")  
    x_real_ip = request.headers.get('x-real-ip', "")
    x_forwarded_for = request.headers.get('x-forwarded-for', "")   
    request_method = request.method
    
    # Allow OPTIONS requests for CORS preflight checks
    if request_method == 'OPTIONS':
        headers = {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        }
        return JSONResponse(status_code=200, headers=headers, content={"message": "OPTIONS request"})

    # Extract authorization token from the request header
    access_token = request.headers.get("Authorization", "").split()
    token = ""
    if len(access_token) == 2 and access_token[0].lower() == "bearer":
        token = access_token[1]

    # Simulate token validation logic (replace with actual validation)
    if not token or not is_token_valid(token):  # You need to implement is_token_valid
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"message": "Unauthorized!"})
    
    # Continue processing the request if token is valid
    response = await call_next(request)
    
    # Add CORS headers to the response
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    
    return response


# Token validation function (replace with your own logic)
def is_token_valid(token: str) -> bool:
    # Add actual token validation logic here, e.g., decoding JWT, checking DB
    return token == "my_valid_token"  # This is a placeholder for demonstration purposes


# CORS configuration function
def configure_cors(app, origins=["*"]):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

# Application startup function
def start_application():
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.PROJECT_VERSION,
        debug=False
    )
    configure_cors(app)
    include_router(app)        
    app.include_router(pages_router)
    return app


###############################################################################
# Define app that takes care of everything #
###############################################################################
print('start app..')
fast_app = start_application()

print('add middleware..')
routes_test.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

routes.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

fast_app.mount("/test", routes_test)
fast_app.mount("/api", routes)



  
def startup_event():
    pass
    logger.info("Starting up...")
    _ = config.pre_app_test()

def shutdown_event():
    pass
    logger.info("Shutting down...")
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    startup_event()
    yield
    # Clean up the ML models and release the resources
    shutdown_event()
    



print('start socket')
app = get_socketio_app(fast_app)


###############################################################################
#   Handler for AWS Lambda                                                    #
###############################################################################

# def handler(event, context):
#     #if event.get("some-key"):
#     #    # Do something or return, etc.
#     #    return

#     asgi_handler = Mangum(app)
#     response = asgi_handler(event, context) # Call the instance with the event arguments

#     return response
# if is_lambda():
#     print('============Creating Magnum handler=============')
#     handler = Mangum(app, lifespan="off")
#     print('============Magnum handler created=============')

###############################################################################
#   Run the self contained application                                        #
###############################################################################
# @app.middleware("http")
# async def check_authentication(request: Request, call_next): 
#     origin = request.headers.get('referer', "")  
#     x_real_ip = request.headers.get('x-real-ip', "")
#     x_forwarded_for = request.headers.get('x-forwarded-for', "")   
#     request_method = request.method
    
#     # check if it is an OPTIONS request
#     if request_method == 'OPTIONS':
#         headers = {}
#         headers["Access-Control-Allow-Origin"] = "*"
#         headers["Access-Control-Allow-Credentials"] = "true"
#         headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
#         headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"        
#         return JSONResponse(status_code=200,
#                             headers=headers, 
#                             content={"message":"OPTIONS request"})
    
#     # get origin
#     if '://' in origin:
#         origin = origin.split('://')[1]
#     if '/' in origin:
#         origin = origin.split('/')[0]
#     if 'www.' in origin:
#         origin = origin.split('www.')[1]        
    
#     # get token
#     # print('Headers', request.headers)
#     # print('Query params', request.query_params)
#     # print('Body', await request.json())
#     # print(request.headers.get("Authorization", ""))
#     access_token = request.headers.get("Authorization", "").split()
#     token = ""
#     user_token = ""
#     run_stage = ""
#     token_schema = "Bearer"
#     if len(access_token) == 2:
#         token_schema = access_token[0]
#         token = access_token[1]
    
#     try:
#         q_params = dict(request.query_params)     
#     except Exception as e:        
#         q_params = {}        
    
#     try:
#         qbody = await request.body()
#         qbody = json.loads(qbody.decode('utf-8'))
#         message_body = qbody.get('Message', qbody)
#         if isinstance(message_body, str):
#             message_body = json.loads(message_body)
#     except Exception as e:
#         logger.warn("Error parsing qbody: ", e)
#         qbody = {}
#         message_body = {}
        

               
#     # get run_stage and user_token
#     key_params = {'run_stage':'run_stage', 
#                   'user_token':'user_token',
#                   'strapi_token':'user_token'}
#     output = get_key_from_nested_dict(message_body, key_params)
#     run_stage = output.get('run_stage', "")
#     user_token = output.get('user_token', "").strip()
    
#     # print('run_stage', run_stage)
#     # print('user_token', user_token)
    
    
#     prefix = f"Origin={origin}, ip={x_real_ip}, fip={x_forwarded_for}"
#     try:
#         permission = False
#         for n, t in {'header_token':token, 'body_token':user_token}.items():                          
#             permission = check_permission(request.method, request.url.path, t, run_stage)
#             prefix += f', {n}_permission={permission}'
#             if permission:
#                 break
            
#         if not permission and len(user_token)>10:
#             permission = True
#             user = 'SNS'
#             prefix += f', SNS (GUESS) as we have invalid user_token in body'
#             logger.warn(f'{prefix} presented valid payload!')                   
            
#         user=config.fastapi.user_info.get('username',"")
#         if user:
#             prefix += f', user="{user.replace(" ","-")}"'
#         else:
#             prefix += f', user="Unknown"'
        
        
#         # check authentication   
#         if permission: #or any([x in origin for x in root_origins]) or len(origin)==0
#             logger.good(f'{prefix} presented valid token!')
#         else:                    
#             print('qbody',qbody)
#             print('run_stage',run_stage)
#             print('user_token',user_token)
#             logger.warn(f'{prefix} does NOT provide valid token!')       
#             return JSONResponse(status_code=400,
#                                 content = { 
#                                             'message':"Unauthorized!", 
#                                             "error": "Unauthorized"
#                                         }
#                                 )            
#     except Exception as e:
#         logger.error(f"Origin={origin} Error: {e}")
#         return JSONResponse(
#                             status_code=401, 
#                             content={'message':"Wrong Origin={origin}",
#                                      "WWW-Authenticate": token_schema}
#                             )
        
#     response = await call_next(request)
#     response.headers["Access-Control-Allow-Origin"] = "*"
#     response.headers["Access-Control-Allow-Credentials"] = "true"
#     response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
#     response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    
#     return response

# def get_key_from_nested_dict(d, kmap, output = {}):    
#     subd = []
#     for k, v in d.items():   
#         if isinstance(v, dict):
#             subd.append(v)
#         else:   
#             if k in kmap.keys():
#                 knew = kmap[k]
#                 if not output.get(knew):
#                     output[knew] = v                

#     for sd in subd:
#         res = get_key_from_nested_dict(sd, kmap, output=output)
#         output.update(res)
            
#     return output

# def check_permission(method, api, token, run_stage):
#     if method == 'GET' and api[1:] in ['docs', 'openapi.json', 'favicon.ico']:
#         logger.good(f'method={method}, api={api}, permission=True')
#         return True
#     else:
#         logger.info(f'method={method}, api={api}, permission=Checking ...', fg='pink')
        
#     sg = StrapiGraphql(run_stage=run_stage, token=token)
    
#     user_info = sg.get_user_info() 
#     config.fastapi.user_info = user_info
        
#     if user_info:       
#         return True
#     else:
#         return False
    

if __name__ == "__main__":
    
    #, reload=True
    port = os.environ.get("PORT", 9900)
    # nworkers = number_of_workers()
    # print(f"Starting FastAPI server on port {port} with {nworkers} workers")
        
    # if config.strapi_stage == "dev":
    #     logger.divider(f"Starting FastAPI server on port {port} with {nworkers} workers")
    #     options = {
    #         "bind": "%s:%s" % ("0.0.0.0", str(port)),
    #         "workers": nworkers,
    #         "worker_class": "uvicorn.workers.UvicornWorker",
    #     }
    #     StandaloneApplication(app, options).run()
    # else:
    
    # logger.divider(f"Starting FastAPI server on port {port} with 1 worker")
    uvicorn.run("app:app", host="0.0.0.0", port=port)
          
