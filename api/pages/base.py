from fastapi import APIRouter


# from api.pages.analysis.routers import api_cv_analysis
from api.pages.ipersona.routers import api_ipersona
from api.pages.ipersona.routers.socket import socket_app


#from api.pages.users import route_users


api_router = APIRouter()
# api_router.include_router(api_cv_analysis.router, prefix="/cv", tags=["CV Analysis"])
api_router.include_router(api_ipersona.router, prefix="/iper", tags=['Ipersona'])
api_router.include_router(api_ipersona.router, tags=['Ipersona socket'])




for route in api_router.routes:
    if route.path.endswith("/"):
        route.path = route.path[:-1]


