import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
#
import os, sys
import json
import shutil
import importlib.util
import subprocess
import uuid
from pathlib import Path
import tempfile
import hashlib
from dataclasses import dataclass, astuple, asdict
from dotenv import load_dotenv
import boto3
# try:
#     from deepdiff import DeepDiff  # For Deep Difference of 2 objects
#     from deepdiff import Delta  # For creating delta of objects that can be applied later to other objects.
# except:
#     def DeepDiff(obj1, obj2, **kwargs):
#         return obj2
#     def Delta(obj1, **kwargs):
#         return obj1
    
#
import time
import random
import signal
from contextlib import contextmanager

#
from api.services.secret import get_auth
from api.llm import *
from api.utils.logger import LLPackerLogger, logme

logger = LLPackerLogger(os.path.basename(__file__))

strapi_stage =  os.environ.get('STRAPI_STAGE','dev')
logger.divider(f'using STRAPI_STAGE={strapi_stage}')

#
cdir = os.path.dirname(os.path.realpath(__file__))
efs_path = '/mnt/efs/leap-frog'
inaws = os.path.exists(efs_path)

#
if os.path.exists(efs_path):
    logger.info(f'**** using {efs_path} as root location to .env, conf, static/ and templates/ folders!')
    
#
apipath = os.path.dirname(os.path.realpath(__file__)) #./api
rootdir = os.path.dirname(apipath)
datadir = f'{rootdir}/data'

if os.path.exists(efs_path):
    model_path = f'{efs_path}/{strapi_stage}/'
else:
    model_path = f'{apipath}'
    
def get_strapi_params(stage):
    if stage.lower().startswith('devapply'):
        root='dev-apply-cms'
        ssmkey="APPLY_DEV_STRAPI_TOKEN"
    elif stage.lower().startswith('apply'):
        root='apply-cms'
        ssmkey="APPLY_PROD_STRAPI_TOKEN" 
    elif stage.lower().startswith('prod'):
        root='cms'
        ssmkey="TENX_PROD_STRAPI_TOKEN" 
    elif stage.lower().startswith('tenacious'):
        root='tenaciouscms'
        ssmkey="TENACIOUS_PROD_STRAPI_TOKEN"
    else:  #stage.lower().startswith('dev')
        root='dev-cms'
        ssmkey="TENX_DEV_STRAPI_TOKEN"  

    return root, ssmkey  
    
root, ssmkey = get_strapi_params(strapi_stage)
indev = root.startswith('dev')
inprod = not indev   
    
# def object_diff_delta(obj1, obj2, blob=True):
#     ddiff = DeepDiff(obj1, obj2, ignore_order=True)
#     delta = Delta(ddiff)
#     if blob:
#         delta = json.dumps(delta, indent=2) 
#     return delta

def data_file_name(file_name, **kwargs):
    folder = kwargs.get('folder', '')
    if folder:
        folder = os.path.join(datadir, folder.lstip('/'))
    else:
        folder = datadir
    if not os.path.exists(folder):
        os.mkdir(folder, exist_ok=True)
        
    file_path = os.path.join(folder, os.path.basename(file_name))
    
    return file_path


def write_file(file_name, data, folder="", mode="w", **kwargs):
    file_path = data_file_name(file_name, folder=folder)
    with open(file_path, mode) as file:
        file.write(data)
    return file_path


def read_file(file_path, mode="r", folder="", **kwargs):
    with open(file_path, mode) as file:
        file_contents = file.read()
    return file_contents


def write_json(file_name, data, folder="", mode="w", **kwargs):
    file_path = data_file_name(file_name, folder=folder)
    with open(file_path, mode) as json_file:
        json.dump(data, json_file, indent=2)


def read_json(file_path: str):
    with open(file_path) as json_file:
        return json.load(json_file)
        
def get_openapi_token(
    ssmkey='OPENAI_PARROT_API_KEY',
    envvar=None,
    fconfig=None,
):
    apikey = get_auth(ssmkey=ssmkey, envvar=envvar, fconfig=fconfig)

    return apikey

def rapidapi_header(ssmkey="RAPIDAPI_API_KEY",
                    envvar="rapidapi_api_key",
                    fconfig=".env/rapidapi_apikey.json",
                    name="jobs-api14"):
    if name.startswith('jobs'):
       api_name = "jobs-api14"
    elif name.startswith('jsearch'):
         api_name = "jsearch" 
    else:
        raise Exception(f'Invalid RAPID API api_name={api_name}')
    
    apikey = get_auth(ssmkey=ssmkey, envvar=envvar, fconfig=fconfig)
    headers = {
        'x-rapidapi-key': apikey,
        'x-rapidapi-host': f"{api_name}.p.rapidapi.com"
    }
        
    return headers

def random_id():
    '''
    Generate a random id
    '''

    return uuid.uuid4().hex

def shash(s):
    '''
    Generate a hash value from a string

    Args:
        s (str): string to hash        
    '''

    # Getting the hash value using the hashlib library
    hash_value = hashlib.md5(s.encode()).hexdigest()
    return hash_value

def random_file_name(ext='txt', prefix="", content=""):    

    # Get the path to the temporary directory
    temp_dir = tempfile.gettempdir()

    # Create a temporary file in the temporary directory
    if content:
        key = shash(content)
    else:
        key = random_id()
        
    return os.path.join(temp_dir, f"frog_{prefix.replace(' ', '_')[0:50]}{key}.{ext}")

def temp_path(filename, rid=False):    

    # Get the path to the temporary directory
    temp_dir = tempfile.gettempdir()

    # Create a temporary file in the temporary directory
    
    if rid:
        key = random_id()
        output = os.path.join(temp_dir, key, os.path.basename(filename))
    else:
        output = os.path.join(temp_dir, os.path.basename(filename))
        
    return output


def get_assistant_name(key, **kwargs):
    p = kwargs.get('assistant_name','')
    if p:
        return p
    
    if any([x.lower() in key for x in ['code', 'notebook', 'git']]):
        p = 'code_assignment_grader'
    elif any([x.lower() in key for x in ['report', 'slide']]):
        p = 'report_assignment_grader'            

    if len(p)==0:
        p = 'generic_assistent'
    
    return p

def get_overall_assesement_title(**kwargs):
    p = "Overall Assessment"
    return p

def get_openai_run_metadata_keys(**kwargs):
    p = ['submission_id', 'rubric_id']
    return p

def get_openai_run_keys(**kwargs):
    p = [
         'model',  
         'instructions', 
         'additional_instructions',
         'additional_messages',
         'tools',
         'metadata',
         'temperature',
         'top_p',
         'stream',
         'max_prompt_tokens',
         'max_completion_tokens',
         'truncation_strategy',
         'tool_choice',
         'parallel_tool_calls',
         'response_format'
         ]
    return p

def nvlist_to_str(nvlist, names=[], kn='name', kv='value', rk=True):
    output = ""
    for item in nvlist:
        k = item.get(kn,"")
        v = item.get(kv,"")
        if not (k and v):
            continue 
               
        kgroup = names if names else [k] 
        if k in kgroup:
            if rk:
                output = ", ".join([output, f"{k}: {v}"])    
            else:
                output = ", ".join([output, f"{v}"])
            
    return output         

@dataclass
class jobcardparams:
    # ndays since job profile is extracted
    ndays = 10
    # number of job profiles to extract
    limit = 1
    # how long far back to look to compute stats 
    stats_since = 30
    # how long far back to look to compute leaderboard
    leaderboard_since = 30
    # how long far back to look to show reactions table
    reaction_since = 30
    
@dataclass
class rapidapi:
    JSEARCH = "jsearch"
    JOBS = "jobs-api14"
    

@dataclass
class jobprofile:
    default = ""

@dataclass
class jpothers:
    profile_name = ""
    duties = "duties_responsibilities"
    summary = "summary"
    
    
@dataclass
class jpcompetencies:
    profile_name = "competencies"
    name = "name"
    skills = "skills"
    abilities = "abilities"
    knowledge = "knowledge"
    sfia_level = "sfia_level"
    other_attributes = "other_attributes"
    
@dataclass
class userprofile:
    user_profile = "user_profile"
    basics = 'basics'
    education = 'education'
    competencies = "competencies"
    programing_languages = "programing_languages"
    projects = 'projects'
    work_experience = 'work_experience'
    achievements = "achievements"
    awards = "awards"        
    languages = 'languages'
    interests = 'interests'
    references = 'references'
    certificates = "certificates"    
    publications = "publications"
    volunteer = "volunteer"        
            
@dataclass
class upbasics:
    profile_name = "basics"
    full_name = "full_name"
    role = "role"
    email = "email"
    personal_statement = "personal_statement"
    location = "location"
    name_title = "name_title"
    phone = "phone"
    image = "image"
    media = "media"

    
    def get_item(self, key: str, data: dict, skey: list=[]):
        sdefault = {'phone':['main'], 
                    'media':['github', 'linkedin']}
        if skey:
            sdefault[key] = skey if isinstance(skey, list) else [skey]            
        
        names = sdefault.get(key, [])
        
        output = {}
        if value := data.get(key, None):    
            if key == 'phone' and value:
                for item in value:
                    k = item.get('name','').lower() 
                    v = item.get('value','')
                    if k in names and v:
                        if k=='main': 
                            output['phone'] = item.get('value','')
                        else:
                            output[k] = v
            elif key=='location' and value:
                output = {k.lower(): v for k, v in value.items() if k and v}
                
            elif key=='media' and value:
                for item in value:
                    k = item.get('name','').lower() 
                    v = item.get('link','')                    
                    if k in names and v:
                        output[k] = v
                        
            elif isinstance(value, str):
                output = {key: value}
            else:
                logger.warn(f"Skipping {key}={value} as we are unable to parse.") 
        else:
            logger.warn(f"Skipping {key} as it is not found in user data.")
            
        return output
    
    @classmethod
    def get_map(cls, key: str, data: dict, skey: str=""):
        cc = cls()
        output = cc.get_item(key, data)
        if skey=='main':
            return output.get('phone', '')
        elif skey:
            return output.get(skey, '')
        else:
            return output
    
@dataclass
class upeducation:
    profile_name = "education"
    institution_name = "institution_name" 
    institution_url = "institution_url"
    study_area = "study_area"
    study_type = "study_type"
    start_date = "start_date"
    end_date = "end_date"
    gpa = "gpa"
    courses = "courses"
      
@dataclass
class upcompetencies:
    profile_name = "competencies"
    name = "name"
    description = "description"
    sfia_method = "sfia_estimation_method"
    sfia_level = "sfia_level"
    rationale = "rationale"
    skills = "skills"
    experience_level = "experience_level"
    evidence = "evidence"
    knowledge = "knowledge"
    attitude = "attitude"
    abilities = "abilities"
    others = "others"
    approved_list = ['approved', 'verified', 'reviewed']
    verifier_list = ['staff', 'admin', 'manager', 'supervisor']
       
@dataclass
class upskills:
    profile_name = "competencies"
    name = "name"
    sfia_level = "sfia_level"
    skills = "skills"
    experience_level = "experience_level"
    evidence = "evidence"
    
    
             
@dataclass
class upprojects:
    profile_name = "projects"
    url = "url"
    title = "title"
    focus_area = "focus_area"
    start_date = "start_date"
    end_date = "end_date"
    tools = "tools"
    highlights = "highlights"
    summary = "summary"
        
@dataclass
class upwexperience:
    profile_name = "work_experience"
    company = "company"
    company_url = "company_url"
    start_date = "start_date"
    end_date = "end_date"
    role = "role"
    summary = "summary"
    highlights = "highlights"
    location = "location"    
    
@dataclass
class upcertificates:
    profile_name = "certificates"
    name = "name"
    date = "date"
    issuer = "issuer"
    url = "url"

@dataclass
class upachievements:
    profile_name = "achievements"
    title = "title"
    date = "date"
    awarder = "awarder"
    summary = "summary"
    
@dataclass
class upawards:
    profile_name = "awards"
    title = "title"
    date = "date"
    awarder = "awarder"
    summary = "summary"
    
@dataclass
class uplanguages:
    profile_name = "languages"
    language = "language"
    fluency = "fluency"
    
@dataclass
class upinterests:
    profile_name = "interests"
    name = "name"
    keywords = "keywords"
    
@dataclass
class upreferences:
    profile_name = "references"
    name = "name"
    reference = "reference"
        
@dataclass
class sns_topics:
    if strapi_stage.lower().startswith('prod'):
        asset_generation = "leap-agr-event"   
        task_scheduler = "leap-task-scheduling-event"    
    else:
        asset_generation = "leap-dev-agr-event"
        task_scheduler = "leap-dev-task-scheduling-event"
    
@dataclass
class jobapplicationstatus:
    not_applied = "not_applied"
    applied = "applied"
    rejected = "rejected"
    shortlisted = "shortlisted"
    interview = "interview"
    offer = "offer"
    hired = "hired"
    other = "other"

@dataclass
class jobcontributionstatus:
    applied = "applied"
    want_to_apply = "want_to_apply"
    
@dataclass
class matchthresholds:
    if strapi_stage.lower().startswith('prod'):
        supermatch = 60        
        match = 40
        poormatch = 30
        verypoormatch = 15
    else:
        supermatch = 60
        match = 40
        poormatch = 30
        verypoormatch = 15

    
@dataclass
class fastapi:
    origins = [
        "http://frog.10academy.org",
        "https://leap.10academy.org",
        "https://dev-leap.10academy.org"
        "http://localhost",
        "http://localhost:5500",
        "http://localhost:5000",
        "https://leap.gettenacious.com",
        "https://dev-leap.gettenacious.com",
        "https://frog.gettenacious.com",
        "https://dev-frog.gettenacious.com"
    ]
    root_origins = ['10academy.org',
                    'gettenacious.com',
                    'localhost',
                    '127.0.0.1']
    user_info = {}    
    
@dataclass
class cache:
    MEMCACHED_HOST = os.getenv("MEMCACHED_HOST", "localhost")
    MEMCACHED_PORT = os.getenv("MEMCACHED_PORT", 11211)
    REDIS_HOST = "clustercfg.leap.kizxdo.use1.cache.amazonaws.com"
    REDIS_PORT = 6379
    REDIS_URL = f"rediss://{REDIS_HOST}:{REDIS_PORT}"
    
@dataclass
class shorturl:
    SHORTEN_URL = False
    API_NAME = "tinyurl"
    API_KEY = os.getenv("SHORTURL_API_KEY", "")
    
@dataclass
class resume:
    use_default_template = False
    default_template_id = 1
    default_template_name = "template1"
    template_list = ['templates1', 
                     'templates2', 
                     'templates3']
    templates = {k+1:v for k, v in enumerate(template_list)}
    templates.update({str(k):v for k, v in templates.items()})

@dataclass
class zlm:
    template_id = 1
    match_model = "vector"
    #zlm_bucket = os.environ.get('S3_ZLM_BUCKET', 'tenx-tinder4job')
    #prefix_cl = os.environ.get('S3_CL_PREFIX', 'cover_letter')
    #prefix_cv = os.environ.get('S3_CV_PREFIX', 'resume')

@dataclass 
class gdrive:
    deligated_user_email = "yabebal@10academy.org"

@dataclass
class s3:
    zlm_bucket = os.environ.get('S3_ZLM_BUCKET', 'tenx-tinder4job')
    prefix_cl = os.environ.get('S3_CL_PREFIX', 'cover_letter')
    prefix_cv = os.environ.get('S3_CV_PREFIX', 'resume')


def get_openapi_token(
    ssmkey,
    envvar=None,
    fconfig=None,
    ):
    
    if not ssmkey:
        raise Exception(f'Invalid ssmkey={ssmkey}')
    else:
        apikey = get_auth(ssmkey=ssmkey, envvar=envvar, fconfig=fconfig)    
        return apikey
      
@dataclass
class assemblyai:
    api_key = "af1b742664d64a40a7429081cd7cdc35"  
    
@dataclass
class openai:
    max_calls = 3  # max number of maximum calls per tool function call
    temperature = float(os.environ.get('OPENAI_TEMPERATURE',0.8))
    top_p = float(os.environ.get('OPENAI_TOP_P',1.0))
    top_k = int(os.environ.get('OPENAI_TOP_K',0))
    #https://platform.openai.com/docs/models/continuous-model-upgrades
    #MAX_INPUT =128k tokens, MAX_OUTPUT = 4096 tokens
    max_tokens = int(os.environ.get('OPENAI_MAX_TOKENS',128000))
    max_chars = int(os.environ.get('OPENAI_MAX_CHARACTERS',32768))
    stop = os.environ.get('OPENAI_STOP','\n')
    model = os.environ.get('OPENAI_MODEL',"gpt-4o-mini")
    cheap_model = os.environ.get('OPENAI_CHEAP_MODEL',"gpt-4o-mini")
    fast_model = os.environ.get('OPENAI_FAST_MODEL',"gpt-4o-mini")
    powerful_model = os.environ.get('OPENAI_POWERFUL_MODEL',"gpt-4o")
    vision_model = os.environ.get('OPENAI_VISION_MODEL',"gpt-4-vision-preview")
    api_key = get_openapi_token(ssmkey='OPENAI_PARROT_API_KEY')
    api_key_parrot = get_openapi_token(ssmkey='OPENAI_PARROT_API_KEY')
    api_key_job_profile = get_openapi_token(ssmkey="OPENAI_LEAP_JOBPROFILE_API_KEY")
    api_key_asset_generation = get_openapi_token(ssmkey="OPENAI_LEAP_ASSETGEN_API_KEY")


def get_strapi_params(stage):
    if not stage:
        print('WARNING: strapi_stage={stage} is not set! Using dev-cms as default.')
        root='dev-cms'
        ssmkey="TENX_DEV_STRAPI_TOKEN"
        
    if stage.lower().startswith('devapply'):
        root='dev-apply-cms'
        ssmkey="APPLY_DEV_STRAPI_TOKEN"
    elif stage.lower().startswith('apply'):
        root='apply-cms'
        ssmkey="APPLY_PROD_STRAPI_TOKEN" 
    elif stage.lower().startswith('prod'):
        root='cms'
        ssmkey="TENX_PROD_STRAPI_TOKEN" 
    elif stage.lower().startswith('tenacious'):
        root='tenaciouscms'
        ssmkey="TENACIOUS_PROD_STRAPI_TOKEN"
    else:  #stage.lower().startswith('dev')
        root='dev-cms'
        ssmkey="TENX_DEV_STRAPI_TOKEN"  

    return root, ssmkey   
    
root, ssmkey = get_strapi_params(strapi_stage)


@dataclass
class strapi:
    root = root
    ssmkey = ssmkey
    stage = strapi_stage


@dataclass
class folders:
    rootdir = rootdir
    if os.path.exists(f'{efs_path}/.env'):
        envdir = f"{efs_path}/.env"
    else:
        envdir = f"{rootdir}/.env"

    if os.path.exists(f'{efs_path}/conf'):
        kedroconfdir = f"{efs_path}/conf"
    else:
        kedroconfdir = f"{rootdir}/conf"
        
    #
    if os.path.exists(efs_path):
        templates: str = f'{efs_path}/templates'
        static: str = f'{efs_path}/static'
        test_data: str = f'{efs_path}/test_data'        
    else:
        templates: str = f'{apipath}/templates'
        static: str = f'{apipath}/static'
        test_data: str = f'{apipath}/test_data'        

@dataclass
class templates:
    folder: str = folders.templates
    login_page: str = f'index_login.html'
    index_page: str = f'home2.html'
    result_page: str = f'result.html'
    request_json: str = f'request.json'    
    #
    user_register: str = f"users/register.html"
    auth_login: str = f"auth/login.html"

@dataclass
class settings:
    PROJECT_NAME: str = "10 Academy Interviwer Persona Backend"
    PROJECT_DESCRIPTION = "Tenx AI Chatbot for Interviewer Persona"
    PROJECT_VERSION: str = "1.0.0"
    #
    USE_SQLITE_DB: str = "False"
    #
    SECRET_KEY: str = os.getenv("SECRET_KEY","")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30  # in mins
    AUTHENTICATED_USER = False
    #
    TEST_USER_EMAIL = "test@example.com"
   
@dataclass
class prefscore:
    collection_name = "FilterKeywords"
    user_pref_columns = ['keywords_include', 'keywords_exclude', 
                         'role', 'experence_level']
    job_pref_columns = ['skills', 'role', 'level']

@dataclass
class ratescore:
    collection_name = "filter_keywords"
    user_pref_columns = ['keywords_include', 'keywords_exclude', 
                         'role', 'experence_level']
    job_pref_columns = ['skills', 'role', 'level']


@dataclass
class SQDB:
    SQLITE_URL = f"sqlite:///{folders.templates}/user_table.db"

@dataclass
class PGDB:    
    POSTGRES_USER: str = os.getenv("POSTGRES_USER","")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD","")
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT: str = os.getenv(
        "POSTGRES_PORT", 5432
    )  # default postgres port is 5432
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "tdd")
    DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"



def keys_in_request(*keys, r={}):
    for key in keys:
        try:
            _element = r[key]
            if not _element:
                return False
        except KeyError:
            return False
    return True
     
def pre_app_test(**kwargs):
    # fpath = '/mnt/efs/autograde/debug_tests'
    # fpy = 'api_test.py'
    # if not os.path.exists(f'{fpath}/{fpy}'):
    #     logger.info(f'****No pre application run file={fpath}/{fpy} found!***')            
    #     return {"message":"No pre appliction run file found!"}
    
    # try:
    #     if fpath not in sys.path:
    #         sys.path.append(fpath)
            
    #     import api_test as apit
    #     print(apit.run(**kwargs))
    #     message = "Successfuly run {fpath}/{fpy} run() function"        
    # except Exception as e:
    #     print(e)
    #     message = "Failed to run {fpath}/{fpy} run() function" 
    message = ""
    
    return {"message":message}        
    

def get_score_function(sid):
    # '''
    # Example of loading modules dynamically - by copying from EFS or from S3
    # '''
    # fpath = folders.scorecards.format(sid=sid)
    # mname = "scorecard_preprocessing"
    # src = f'{fpath}/{mname}.py'
    # if not os.path.exists(src):
    #     src = f"api.InferencePreprocessing/{mname}.py"

    # logger.info(f'--Importing {src}...')    
    # spec = importlib.util.spec_from_file_location(mname, src)
    # mod = importlib.util.module_from_spec(spec)
    # sys.modules["module.name"] = mod
    # spec.loader.exec_module(mod)
    # return mod.calculate_credit_score

    pass

def import_param_file(fpath):
    '''
    Example of loading modules dynamically 
    '''
 
    logger.info(f'--Importing {fpath}...')    

    f = fpath
    src = os.path.dirname(f)
    mname = os.path.basename(f).split('.')[0]

    spec = importlib.util.spec_from_file_location(mname, f)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["module.name"] = mod
    spec.loader.exec_module(mod)
    return mod
    
class TimeoutException(Exception): pass

@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise TimeoutException("Timed out!")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

# Define a retry decorator
def retry_with_exponential_backoff(
    func,
    initial_delay: float = 1,
    exponential_base: float = 2,
    jitter: bool = True,
    max_retries: int = 3,
    errors: tuple = (Exception, ),
):
    """Retry a function with exponential backoff."""

    def wrapper(*args, **kwargs):
        num_retries = 0
        delay = initial_delay

        while True:
            try:
                return func(*args, **kwargs)

            except errors as e:
                print(e)

                num_retries += 1

                if num_retries > max_retries:
                    raise Exception(f"Maximum number of retries ({max_retries}) exceeded.")

                delay *= exponential_base * (1 + jitter * random.random())

                time.sleep(delay)

            except Exception as e:
                raise e

    return wrapper

@retry_with_exponential_backoff
def run_with_timelimit_and_retry(*args, **kwargs):
    
    logger.info(f'nargs={len(args)}, typea_args={type(args)}, kwargs={kwargs} ...')

    timeout = kwargs.pop("timeout", 120)
    func = args[0]
    if not callable(func):
        raise TypeError("The first argument must be callable")
    if len(args) == 1:
        args = ()
    else:
        args = args[1:]

    logger.info(f'--config.py: Running {func.__name__} with timeout={timeout} ...')
    try:
        with time_limit(timeout):
            res = func(*args, **kwargs)
            #res = preprocess_and_grade_submission(*args[1:], **kwargs)
    except TimeoutException as e:
        print("Timed out!")
        raise

    return res

def get_boto3_resource(name="sqs"):
    boto3kwargs = {"region_name": "us-east-1"}
        
    if os.getenv("AWS_ACCESS_KEY", "") != "" and os.getenv("AWS_SECRET_KEY", "") != "":
        # Load environment variables
        boto3kwargs["aws_access_key_id"] = os.getenv("AWS_ACCESS_KEY")
        boto3kwargs["aws_secret_access_key"] = os.getenv("AWS_SECRET_KEY")

    # Here we create a new session per thread
    session = boto3.session.Session(**boto3kwargs)

    return session.resource(name)    

def get_boto3_client(name="sqs"):
    boto3kwargs = {"region_name": "us-east-1"}
    if os.getenv("AWS_ACCESS_KEY", "") != "" and os.getenv("AWS_SECRET_KEY", "") != "":
        # Load environment variables
        boto3kwargs["aws_access_key_id"] = os.getenv("AWS_ACCESS_KEY")
        boto3kwargs["aws_secret_access_key"] = os.getenv("AWS_SECRET_KEY")

    session = boto3.session.Session(**boto3kwargs)
    func = sqs_link if name == 'sqs' else sns_link
    return boto3.client(name, 
                          endpoint_url=func(root=True, arn=False),
                          **boto3kwargs
                          )

def sns_link(t='grading-topic.fifo', 
            arn=True, 
            root=False,
            accountId='070096167435',
            aws_region='us-east-1'):
        
    if arn:
        if root:
            return f"arn:aws:sns:{aws_region}:{accountId}"
        else:
            return f"arn:aws:sns:{aws_region}:{accountId}:{t}"
    else:
        if root:
            return f"https://sns.{aws_region}.amazonaws.com"
        else:
            return f"https://sns.{aws_region}.amazonaws.com/{accountId}/{t}"
    
def sqs_link(q='submission-queue.fifo', 
            arn=True, 
            root=False,
            accountId='070096167435',
            aws_region='us-east-1'):


    if arn:
        if root:
            return f"arn:aws:sqs:{aws_region}:{accountId}"
        else:            
            return f"arn:aws:sqs:{aws_region}:{accountId}:{q}"
    else:
        if root:
            return f"https://sqs.{aws_region}.amazonaws.com"
        else:
            return f"https://sqs.{aws_region}.amazonaws.com/{accountId}/{q}"
    


def delete_all_messages_in_que(queue_name="preprocess_and_grade"):

    queue_url = sqs_link(queue_name, root=False, arn=False)
        
    try:
        sqs = get_boto3_client("sqs")
    except Exception as e:
        print(e)
        raise e

    queue_has_message = True
    while queue_has_message:
        # Receive message from SQS queue
        response = sqs.receive_message(
                                        QueueUrl=queue_url,
                                        AttributeNames=[
                                            'SentTimestamp'
                                        ],
                                        MaxNumberOfMessages=10,
                                        MessageAttributeNames=[
                                            'All'
                                        ],
                                        VisibilityTimeout=60,
                                        WaitTimeSeconds=20
        )

        if 'Messages' not in response:
            print('No messages in queue')
            return None

        if len(response['Messages'])==0:
            print('No messages in queue')
            return None
            
        # Process messages by printing out body and optional author name
        for message in response['Messages']:
            receipt_handle = message['ReceiptHandle']
            body = json.loads(message['Body']) 
            
            # Delete received message from queue
            sqs.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=receipt_handle
            )

            print('Received and deleted message: %s' % message)   
            

def load_envs():    
    logger.info('--config.py: Loading env files...')
    
    try:
        result = subprocess.run(["bash", f"{apipath}/env_setup.sh"], capture_output=True)    
        # print(result.stdout)
        # print(result.stderr)
        # print(result)
        for f in os.listdir(folders.envdir):
            if not f.startswith('.env') or '~' in f or '#' in f:
                continue
            #print(f'loading env file: {f}')
            load_dotenv(f"{folders.envdir}/{f}")        
    except Exception as e:
        logger.log_error(f'load_envs: loading env failed with error: {e}')        

def install_packages():
    logger.info('--config.py: installing python packages...')

    try:
        result = subprocess.run(["bash", f"{apipath}/install_packages.sh"], capture_output=True)
        print(result.stdout)
        print(result.stderr)
        print(result)
    except Exception as e:
        logger.log_error('install_packages','installing packages failed with error: {e}')   
    
def return_text(text_message, status=200, show=False):
    '''
    https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-develop-integrations-lambda.html
    '''
    if show:
        logger.info(f'{text_message}')
    return {
        "isBase64Encoded": False,        
        'statusCode': status,
        'headers': {'Content-Type': 'application/json'},
        'body': text_message
    }    
def return_json(json_message, status=200, show=False):
    if show:
        logger.info(f'{json_message}')
    if isinstance(json_message, dict):
        status = json_message.pop('status', status)
    return {
        "isBase64Encoded": False,        
        'statusCode': status,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(json_message)
    }

