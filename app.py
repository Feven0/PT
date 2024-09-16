from warnings import filterwarnings
import os, sys

#
path = os.path.dirname(os.path.realpath(__file__))
if path not in sys.path:
    sys.path.append(path)
#

# from api import config
# from api.services.strapi_graphql import StrapiGraphql
# _ = config.load_dotenv()


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
from gunicorn.app.base import BaseApplication
import uvicorn
#
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Body, Request, Depends
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
#
# from api.services.secret import get_auth, is_lambda
from api.pages.base import api_router as pages_router
from api.pages.ipersona.routers.api_ipersona import routes
from api.pages.ipersona.socket.ipersona_socket import socket_app
# from api.utils.logger import LLPackerLogger

# logger = LLPackerLogger(__file__)

print('done importing modules!')    
###############################################################################

#
# folders = config.folders
# settings = config.settings
# origins = config.fastapi.origins


# def number_of_workers():
#     return (multiprocessing.cpu_count() * 2) + 1

# def include_router(app):
#     app.include_router(pages_router)
#     pass


# def configure_static(app):
#     #app.mount("/static", StaticFiles(directory=folders.static), name="static")
#     pass

# def configure_cors(app, origins=["*"]):
#     app.add_middleware(
#         CORSMiddleware,
#         allow_origins=origins,
#         allow_credentials=True,
#         allow_methods=["*"],
#         allow_headers=["*"])
    

# def start_application():
#     app = FastAPI(
#         # title=settings.PROJECT_NAME,
#         # description=settings.PROJECT_DESCRIPTION,
#         # version=settings.PROJECT_VERSION,
#         # debug=False
#         )
        
         
#     configure_cors(app)
#     include_router(app)
        
#     app.include_router(pages_router)   
    
 
            
#     #configure_static(app)
#     return app

# class StandaloneApplication(BaseApplication):
#     '''
#     REF:
#     https://gist.github.com/Kludex/c98ed6b06f5c0f89fd78dd75ef58b424
#     https://github.com/fastapi/fastapi/discussions/9585
#     https://www.uvicorn.org/deployment/
#     '''
#     def __init__(self, application: Callable, options: Dict[str, Any] = None):
#         self.options = options or {}
#         self.application = application
#         super().__init__()

#     def load_config(self):
#         config = {
#             key: value
#             for key, value in self.options.items()
#             if key in self.cfg.settings and value is not None
#         }
#         for key, value in config.items():
#             self.cfg.set(key.lower(), value)

#     def load(self):
#         return self.application

###############################################################################
#   Define app that takes care of everything                                  #
###############################################################################

#[Depends(verify_token), Depends(verify_key)]
#app = FastAPI(dependencies=[Depends(verify_token)])


#app = start_application()
print('start app..')
app = FastAPI(
    # title=settings.PROJECT_NAME,
    # description=settings.PROJECT_DESCRIPTION,
    # version=settings.PROJECT_VERSION,
    # debug=False
    )


print('add middleware..')
routes.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/api", routes)

print('start socket')
app.mount("/", socket_app)
  

def check_permission(method, api, token, run_stage):
    # The following paths are always allowed:
    
    
    if method == 'GET' and api[1:] in ['docs', 'openapi.json', 'favicon.ico']:
        # logger.good(f'method={method}, api={api}, permission=True')
        return True
    else:
        # logger.info(f'method={method}, api={api}, permission=Checking ...', fg='pink')
        pass
        
        
        ##############################################################
    # check validity of token
    # sg = StrapiGraphql(run_stage=run_stage, token=token)
    # user_info = sg.get_user_info() 
            
    # if all([user_info.get(x) for x in ['role', 'username', 'email']]):
    #     logger.good(f'Got valid token: user_info={user_info}')
    #     return True
    # else:
    #     logger.warn(f'Valid token not found in request headers. Permission denied!')
    #     return False
        ##############################################################

#@app.middleware("http")
async def check_authentication(request: Request, call_next): 
    origin = request.headers.get('referer', "") 
    # logger.good(f'Origin: {origin}')
    
    # get token
    access_token = request.headers.get("Authorization", "").split()
    token = ""
    token_schema = "Bearer"
    if len(access_token) == 2:
        token_schema = access_token[0]
        token = access_token[1]
    
    # get run_stage
    try:
        # get request query parameters
        q_params = dict(request.query_params)        
    except Exception as e:        
        q_params = {}        
    
    # get request body
    try:
        qbody = await request.json()
    except Exception as e:
        qbody = {}
        
    run_stage = q_params.get('run_stage', qbody.get('run_stage', ""))
    
    try:
        # check authentication   
        if origin.startswith('http://localhost'):
            pass
        else:                
            if not check_permission(request.method, request.url.path, token, run_stage):
                # new_url = create_target_url(request.url.path)
                # return RedirectResponse(url=new_url)
                pass           
                #return {'status':400, 'message':"Please pass valid Strapi JWT Token", "error": "Unauthorized"}
    except Exception as e:
        print(e)
        #return JSONResponse(None, 401, {"WWW-Authenticate": token_schema})
        
    return await call_next(request)  


  
def startup_event():
    pass
    # logger.info("Starting up...")
    # _ = config.pre_app_test()

def shutdown_event():
    pass
    # logger.info("Shutting down...")
    
@asynccontextmanager
async def lifespan(app: FastAPI):
    startup_event()
    yield
    # Clean up the ML models and release the resources
    shutdown_event()
    
    
print('add routes..')
app.include_router(pages_router)  


@routes.get("/")
async def root():
    # return config.return_text(settings.PROJECT_NAME)
    pass


@routes.get("/test")
def read_root( request: Request ):
    try:
        client_host = request.client.host
        print(f'Test endpoint requested from client_ip/host = {client_host}')
        print('** Other request.client info are:')
        print(request.client)
        # return config.return_json({"client_host": client_host})
        return {"client_host": client_host}
    except Exception as e:
        print(e)
        return {"error_message":str(e)}
        # return config.return_json({"error_message":str(e)})
    
#auth_scheme = HTTPBearer()



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

if __name__ == "__main__":
    
    #, reload=True
    port = os.environ.get("PORT", 5500)
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
          

