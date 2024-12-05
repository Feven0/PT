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


#app = start_application()
print('start app..')
fast_app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    debug=False
    )


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
          
