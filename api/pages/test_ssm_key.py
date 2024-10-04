
import os 
import sys
print(os.getcwd())

path = os.path.dirname(os.path.realpath(__file__))
if path not in sys.path:
    sys.path.append(path)

from api.services.secret import get_auth

def get_assembly_ai_api_key(
    ssmkey="tenx/env/vars",
    envvar="tenx/env/vars",
    fconfig=".env/all_keys.json",
):
    apikey = get_auth(ssmkey=ssmkey, envvar=envvar, fconfig=fconfig)

    return apikey
