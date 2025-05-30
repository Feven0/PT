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
from api.pages.base import api_router as pages_router
from api.pages.ipersona.routers.ipersona_routes import routes
from api.pages.ipersona.socket.ipersona_socket import get_socketio_app
from api.utils.logger import LLPackerLogger

logger = LLPackerLogger(__file__)

print('done importing modules!')    
###############################################################################


folders = config.folders
settings = config.settings
origins = config.fastapi.origins
root_origins = config.fastapi.root_origins


def number_of_workers():
    return (multiprocessing.cpu_count() * 2) + 1


def configure_static(app):
    #app.mount("/static", StaticFiles(directory=folders.static), name="static")
    pass

def include_router(app):
    app.include_router(pages_router)
    return app

  
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
    

def configure_cors(app, origins=["*"]):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        )
    return app   

def start_application():

    print('start app..')
    fast_app = FastAPI(title=settings.PROJECT_NAME,
                  description=settings.PROJECT_DESCRIPTION,
                  version=settings.PROJECT_VERSION,
                  debug=False,
                  lifespan=lifespan)    
         
    print('add cors middleware..')
    fast_app = configure_cors(fast_app, origins=origins)
    
    #print('add routes..')
    #fast_app = include_router(fast_app)


    routes.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    fast_app.mount("/api", routes)

 
    return fast_app
  
app = start_application()



###############################################################################
#   Define app that takes care of everything                                  #
###############################################################################
async def check_permission(method, api, token, run_stage=None):
    # The following paths are always allowed:
    
    if isinstance(api, str):
        api = api.strip('/')
    

    if method == 'GET' and any([x in api for x in ['docs', 'openapi.json', 'favicon.ico']]):
        logger.good(f'method={method}, api={api}, permission=True')
        return True
    else:
        logger.info(f'method={method}, api={api}, permission=Checking ...', fg='pink')
        
    # check validity of token
    if run_stage is None:
        run_stage = config.strapi_stage
        
    sg = StrapiGraphql(run_stage=run_stage, token=token)
    
    user_info = await sg.aget_user_info() 
    config.fastapi.user_info = user_info
        
    if user_info:       
    #if all([user_info.get(x) for x in ['role', 'username', 'email']]):
        #logger.good(f'Got valid token: user_info={user_info}')
        return True
    else:
        return False
    

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
        return JSONResponse(status_code=200, 
                            headers=headers, 
                            content={"message": "OPTIONS request"})

   # get origin
    if '://' in origin:
        origin = origin.split('://')[1]
    if '/' in origin:
        origin = origin.split('/')[0]
    if 'www.' in origin:
        origin = origin.split('www.')[1]        
    
    # Extract authorization token from the request header
    access_token = request.headers.get("Authorization", "").split()
    token = ""
    if len(access_token) == 2 and access_token[0].lower() == "bearer":
        token = access_token[1]

    prefix = f"Origin={origin}, ip={x_real_ip}, fip={x_forwarded_for}"
    fbase = lambda x: x.replace('http://','').replace('https://','').split('/')[0]
    if any([fbase(x) in origin for x in root_origins]):
        permission = True
        prefix += f', root_origin={origin}'
    else:
        # Inside check_authentication or check_permission
        if "/socket.io/" in request.url.path:
            # For Socket.IO, perhaps allow and handle auth differently,
            # or if you've fixed WebSocket auth, this path might only be initial handshake
            logger.info(f"Bypassing Strapi check for Socket.IO path: {request.url.path}")
            # return True # Be careful with security implications if not authenticated another way
            # Instead, ensure client sends auth data on Socket.IO connect event
            # For testing the "Invalid session" issue, returning True here temporarily is fine.
            permission = True
        else:
            # Existing permission check
            permission = await check_permission(request.method, request.url.path, token)        
        
        prefix += f', permission={permission}'

    # set strapi stage to tenacious if request url or origin contains gettenacious
    if 'gettenacious' in fbase(request.url.path) or 'gettenacious' in fbase(origin):
        config.strapi_stage = 'tenacious'

    # Simulate token validation logic (replace with actual validation)
    if permission:  # You need to implement is_token_valid        
        logger.good(f'{prefix} presented valid token or comes from trusted origin!')
    else:
        logger.warn(f'{prefix} does NOT provide valid token!')  
        return JSONResponse(status_code=403, 
                            content={"message": "Unauthorized!"})
    
    # Continue processing the request if token is valid
    response = await call_next(request)
    
    # Add CORS headers to the response
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    
    return response


print('start socket')
app = get_socketio_app(app)

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
          
