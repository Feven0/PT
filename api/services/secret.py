import sys
import os
import time
import json
import base64
import boto3
import tempfile
from typing import Dict, Any, Optional
from botocore.exceptions import ClientError


from api.services.aws_config import get_secrets_manager_client
from api.utils.logger import LLPackerLogger
logger = LLPackerLogger(os.path.basename(__file__))

# Configuration
envdir = os.environ.get('ENVDIR', '.envdir')
region_name = os.environ.get('AWS_REGION_NAME', 'us-east-1')

# Simple in-memory cache with TTL
_secrets_cache: Dict[str, Dict[str, Any]] = {}
_cache_timestamps: Dict[str, float] = {}
_cache_ttl = 7*24*3600  # 1 week TTL



def atomic_write_json(data: Dict[str, Any], filepath: str) -> bool:
    """
    Atomically write JSON data to a file to prevent corruption.
    
    Args:
        data: The data to write
        filepath: The target file path
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        target_dir = os.path.dirname(filepath)
        if target_dir:
            try:
                os.makedirs(target_dir, exist_ok=True)
                logger.debug(f"Ensured directory exists: {target_dir}")
            except Exception as e:
                logger.error(f"Failed to create directory {target_dir}: {e}")
                return False
        
        # Write to temporary file first
        temp_filepath = f"{filepath}.tmp"
        try:
            with open(temp_filepath, 'w') as f:
                json.dump(data, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            
            # Verify temp file was created and has content
            if not os.path.exists(temp_filepath) or os.path.getsize(temp_filepath) == 0:
                logger.error(f"Temporary file {temp_filepath} was not created or is empty")
                return False
            
            # Atomic rename
            os.rename(temp_filepath, filepath)
            logger.debug(f"Successfully wrote {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to write or rename file: {e}")
            # Clean up temporary file if it exists
            try:
                if os.path.exists(temp_filepath):
                    os.remove(temp_filepath)
            except:
                pass
            return False
        
    except Exception as e:
        logger.error(f'Failed to write {filepath}: {e}')
        # Clean up temporary file if it exists
        try:
            if os.path.exists(temp_filepath):
                os.remove(temp_filepath)
        except:
            pass
        return False


def safe_read_json(filepath: str) -> Dict[str, Any]:
    """
    Safely read JSON from a file with basic validation.
    
    Args:
        filepath: The file path to read from
        
    Returns:
        dict: The parsed JSON data
        
    Raises:
        json.JSONDecodeError: If the file contains invalid JSON
        FileNotFoundError: If the file doesn't exist
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File {filepath} does not exist")
    
    if os.path.getsize(filepath) == 0:
        raise json.JSONDecodeError("File is empty", "", 0)
    
    with open(filepath, 'r') as f:
        content = f.read()
        if not content.strip():
            raise json.JSONDecodeError("File contains only whitespace", "", 0)
        return json.loads(content)


def get_ssm_secret(secret_name: str, max_retries: int = 3, retry_delay: int = 1) -> str:
    """
    Get secret from AWS Secrets Manager with retry mechanism.
    
    Args:
        secret_name: Name of the secret in Secrets Manager
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
        
    Returns:
        str: The secret value
        
    Raises:
        Exception: If unable to retrieve secret after all retries
    """
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            client = get_secrets_manager_client()

            try:
                get_secret_value_response = client.get_secret_value(
                    SecretId=secret_name
                )
            except ClientError as e:
                if e.response['Error']['Code'] == 'DecryptionFailureException':
                    raise e
                elif e.response['Error']['Code'] == 'InternalServiceErrorException':
                    if attempt < max_retries - 1:
                        logger.warn(f"Secrets Manager internal service error for {secret_name}, retrying in {retry_delay}s... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(retry_delay)
                        continue
                    raise e
                elif e.response['Error']['Code'] == 'InvalidParameterException':
                    raise e
                elif e.response['Error']['Code'] == 'InvalidRequestException':
                    raise e
                elif e.response['Error']['Code'] == 'ResourceNotFoundException':
                    raise e
                else:
                    if attempt < max_retries - 1:
                        logger.warn(f"Secrets Manager error for {secret_name}, retrying in {retry_delay}s... (attempt {attempt + 1}/{max_retries})")
                        time.sleep(retry_delay)
                        continue
                    raise e
            else:
                if 'SecretString' in get_secret_value_response:
                    secret = get_secret_value_response['SecretString']
                elif 'SecretBinary' in get_secret_value_response.keys():
                    secret = base64.b64decode(get_secret_value_response['SecretBinary'])
                else:
                    secret = get_secret_value_response

                logger.debug(f"Successfully retrieved secret {secret_name}")
                return secret

        except Exception as e:
            last_exception = e
            if attempt < max_retries - 1:
                logger.warn(f"Error getting secret {secret_name}, retrying in {retry_delay}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to get secret {secret_name} after {max_retries} attempts: {e}")
                raise last_exception
    
    raise last_exception


def config_from_string(sdata: Any, fname: Optional[str] = None, rfile: bool = False) -> Optional[Any]:
    """
    Convert string data to config and optionally save to file.
    
    Args:
        sdata: String data or dict
        fname: File name to save
        rfile: Return file object
        
    Returns:
        dict, str, or None: Parsed data, file path, or None on error
    """
    
    if isinstance(sdata, str):
        if "{" in sdata and "}" in sdata:
            try:
                data = json.loads(sdata)
            except:
                data = sdata
        else:
            data = sdata
    elif isinstance(sdata, dict):
        data = sdata
    else:
        data = sdata

    # if the data is still a string, return it directly
    if isinstance(data, str):
        return data

    try:        
        if rfile:
            if fname and atomic_write_json(data, fname):
                return fname
            return None
        else:
            return data

    except Exception as e:
        logger.warn(f'------warning: saving {fname} failed----')
        logger.error(f'Error in config_from_string: {e}')
        return None


def get_secret(pname: str, pvar: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Get secret from environment variable or AWS Secrets Manager.
    
    Args:
        pname: Secret name in AWS Secrets Manager
        pvar: Environment variable name
        fname: File name to save
        
    Returns:
        dict: The secret data or None on error
    """
    if pvar and pvar in os.environ:
        sdata = os.environ.get(pvar)
        try:
            return json.loads(sdata)
        except json.JSONDecodeError:
            return sdata
    else:
        sdata = get_ssm_secret(pname)
        try:
            # If sdata is already a dict, return it directly
            if isinstance(sdata, dict):
                return sdata
            # Otherwise try to parse as JSON string
            return json.loads(sdata)
        except Exception as e:
            return sdata




def is_lambda() -> bool:
    """
    Check if running in AWS Lambda environment.
    
    Returns:
        bool: True if running in Lambda
    """
    c1 = os.environ.get("LAMBDA_TASK_ROOT")
    c2 = os.environ.get("AWS_EXECUTION_ENV")
    c3 = os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
    
    if c1:
        logger.good(f'LAMBDA_TASK_ROOT: {c1}')
    if c2:
        logger.good(f'AWS_EXECUTION_ENV: {c2}')
    if c3:
        logger.good(f'AWS_LAMBDA_FUNCTION_NAME: {c3}')

    return bool(c1 or c2 or c3)


def lambda_friendly_path(fpath: str) -> str:
    """
    Get a Lambda-friendly file path.
    
    Args:
        fpath: Original file path
        
    Returns:
        str: Lambda-friendly file path
    """
    basename = os.path.basename(fpath)
    dirname = tempfile.gettempdir()
    
    try:        
        if is_lambda():
            f = f'/tmp/{basename}'
        else:
            os.makedirs(dirname, exist_ok=True)
            f = f"{dirname}/{basename}"
    except Exception as e:
        logger.error(f"Error creating lambda friendly path: {str(e)}")
        try:
            os.makedirs(dirname, exist_ok=True)
            f = f"{dirname}/{basename}"        
        except Exception as err:
            logger.error(f"Error creating directory {dirname}. Using basename. Error: {str(err)}")
            f = basename

    return f


def get_secrets_cache_filename(sname: str) -> str:
    """
    Get the cache filename for a given secret name.
    
    Args:
        sname: Secret name in AWS SSM
        
    Returns:
        str: The cache file path
    """
    return f'{envdir}/{sname.replace("/", "_")}.json'


def clear_secrets_cache(sname: str) -> Dict[str, Any]:
    """
    Clear both in-memory and file cache for a specific secret.
    
    Args:
        sname: Secret name in AWS SSM
        
    Returns:
        dict: Status information about cache clearing
    """
    result = {
        'secret_name': sname,
        'memory_cache_cleared': False,
        'file_cache_cleared': False,
        'file_cache_existed': False,
        'errors': []
    }
    
    try:
        # Clear in-memory cache
        if sname in _secrets_cache:
            del _secrets_cache[sname]
            result['memory_cache_cleared'] = True
            logger.debug(f"Cleared in-memory cache for {sname}")
        
        if sname in _cache_timestamps:
            del _cache_timestamps[sname]
            logger.debug(f"Cleared timestamp cache for {sname}")
        
        # Clear file cache
        cache_filename = get_secrets_cache_filename(sname)
        if os.path.exists(cache_filename):
            result['file_cache_existed'] = True
            try:
                os.remove(cache_filename)
                result['file_cache_cleared'] = True
                logger.info(f"Removed cache file: {cache_filename}")
            except Exception as e:
                error_msg = f"Could not remove cache file {cache_filename}: {e}"
                logger.warn(error_msg)
                result['errors'].append(error_msg)
        else:
            logger.debug(f"Cache file {cache_filename} does not exist")
            
    except Exception as e:
        error_msg = f"Error clearing cache for {sname}: {e}"
        logger.error(error_msg)
        result['errors'].append(error_msg)
    
    return result


def force_refresh_secrets(sname: str = 'tenx/env/vars') -> Dict[str, Any]:
    """
    Force refresh secrets from AWS SSM by clearing cache and fetching fresh data.
    
    Args:
        sname: Secret name in AWS SSM
        
    Returns:
        dict: The fresh secrets data
        
    Raises:
        Exception: If unable to retrieve or parse secrets
    """
    logger.info(f"Force refreshing secrets for {sname}")
    
    # Clear all caches first
    cache_result = clear_secrets_cache(sname)
    logger.debug(f"Cache clearing result: {cache_result}")
    
    # Now fetch fresh secrets - this will bypass cache since we just cleared it
    return get_all_secrets(sname)


def get_all_secrets(sname: str = 'tenx/env/vars') -> Dict[str, Any]:
    """
    Get all secrets from AWS SSM or local cache file with simplified caching.
    
    Args:
        sname: Secret name in AWS SSM
        
    Returns:
        dict: The secrets data
        
    Raises:
        Exception: If unable to retrieve or parse secrets
    """
    # Check in-memory cache first
    current_time = time.time()
    if sname in _secrets_cache and current_time - _cache_timestamps.get(sname, 0) < _cache_ttl:
        logger.debug(f"Returning cached secrets for {sname}")
        return _secrets_cache[sname]
    
    try: 
        rname = get_secrets_cache_filename(sname)
        
        # Try to read from local file first
        if os.path.exists(rname):
            try:
                authTemp = safe_read_json(rname)
                # Update cache
                _secrets_cache[sname] = authTemp
                _cache_timestamps[sname] = current_time
                return authTemp
            except Exception as e:
                logger.warn(f'Failed to read from local file {rname}: {e}')
                # Remove corrupted file
                try:
                    os.remove(rname)
                except:
                    pass
        
        # Fetch from AWS SSM
        logger.warn(f'Secret file {rname} does not exist, fetching from AWS SSM...')
        authTemp = get_secret(sname)
        if not authTemp:
            raise Exception(f"Failed to retrieve secrets from AWS SSM for {sname}")
        
        # Write to file and update cache
        if atomic_write_json(authTemp, rname):
            _secrets_cache[sname] = authTemp
            _cache_timestamps[sname] = current_time
            logger.good(f'Successfully cached secrets to {rname}')
        else:
            logger.warn(f'Failed to write secrets to file {rname}, but continuing with in-memory data')
            _secrets_cache[sname] = authTemp
            _cache_timestamps[sname] = current_time

        return authTemp
                
    except Exception as e:
        logger.error(f'Getting secret {sname} failed: {e}')
        raise


def get_auth(ssmkey: Optional[str] = None, 
             envvar: Optional[str] = None, 
             fconfig: Optional[str] = None, 
             rfile: bool = False, 
             rpath: bool = False,
             sname: str = 'tenx/env/vars') -> Any:
    """
    Wrapper to get auth from ssm, env or file.
    
    Args:
        ssmkey: Secret manager key
        envvar: Environment variable name
        fconfig: File name
        rfile: Return file object
        rpath: Return both auth data and file path
        
    Returns:
        dict, str, or tuple: Auth data, file path, or (auth_data, file_path)
        
    Raises:
        Exception: If credentials cannot be obtained
    """
    # Try file first
    if fconfig and os.path.exists(fconfig):
        try:
            logger.debug(f'Reading auth from file: {fconfig}')
            auth = safe_read_json(fconfig)
            return auth
        except Exception as e:
            logger.warn(f'Reading {fconfig} failed! Error: {e}')

    # Try environment variable
    if envvar and os.environ.get(envvar, '') not in ['', 'null', 'None']: 
        try:
            logger.debug(f'Getting {envvar} from environment')
            auth = config_from_string(os.environ.get(envvar, ''), fname=fconfig, rfile=rfile)
            return auth
        except Exception as e:
            logger.error(f'Getting env variable {envvar} failed: {e}')
                
    # Try AWS Secrets Manager
    if ssmkey:        
        if not fconfig:
            fconfig = f'{envdir}/auth_{ssmkey}.json'

        sname = 'tenx/env/vars'
        authTemp = get_all_secrets(sname=sname)

        keys = {
            'strapi/alml-cms/token': 'ALML_STRAPI_TOKEN',
            'staging/strapi/token': 'TENX_STAGING_STRAPI_TOKEN',
            'dev/strapi/token': 'TENX_DEV_STRAPI_TOKEN',
            'prod/strapi/token': 'TENX_PROD_STRAPI_TOKEN',
            'git_token_tenx': 'GIT_TOKEN_10ACADEMY',
            'tenx/db/strapi': {
                'STRAPI_PGDB_USERNAME': 'username',
                'STRAPI_PGDB_PASSWORD': 'password',
                'STRAPI_PGDB_ENGINE': 'engine',
                'STRAPI_PGDB_HOST': 'host',
                'STRAPI_PGDB_PORT': 'port',
                'STRAPI_PGDB_IDENTIFIER': 'dbInstanceIdentifier'
            },
            'strapi/prod/email': [
                'AWS_SES_KEY',
                'AWS_SES_SECRET'
            ]
        }

        try:
            if ssmkey in keys.keys() or ssmkey in authTemp.keys():
                if ssmkey in authTemp.keys():
                    auth = authTemp[ssmkey]
                else:
                    res = keys[ssmkey]

                    if isinstance(res, dict):
                        # res is dict
                        auth = {}
                        for kold, knew in res.items():
                            auth[knew] = authTemp[kold]
                    elif isinstance(res, list):
                        # res is list
                        auth = {}
                        for k in res:
                            auth[k] = authTemp[k]
                    else:
                        # res is string
                        auth = authTemp[res]
            else:
                logger.debug(f'Getting {ssmkey} from aws secret manager as it cannot be found in {sname}')
                auth = get_secret(ssmkey)   

            if rfile:
                # If asked to return file path only
                if os.path.exists(fconfig):
                    logger.debug(f'Returning {fconfig} from existing file')
                    return fconfig
                else:
                    logger.debug(f'Returning {fconfig} by writing to file')
                    return config_from_string(auth, fname=fconfig, rfile=rfile)   
            else:    
                # If asked to return auth + file (rpath=True) or just data only (rpath=False)
                try:      
                    if rpath:
                        if auth:              
                            with open(fconfig, 'w') as f:
                                json.dump(auth, f)                        
                        return auth, fconfig
                    else:
                        return auth
                except Exception as e:
                    logger.error(f"Error writing auth to file {fconfig}: {str(e)}")
                    raise Exception(f"Error writing auth to file {fconfig}: {str(e)}")
            
        except Exception as e:
            raise

    logger.error('Credential cannot be obtained. Params are')
    logger.error(f'ssmkey={ssmkey}, envvar={envvar}, fconfig={fconfig}')           
    raise Exception('Credential cannot be obtained')


def get_google_service_account(ssmkey: str = "gspread/config",
                              envvar: str = "gclass_credentials.json",
                              fconfig: str = f"{envdir}/gclass_credentials.json",
                              rfile: bool = True) -> str:
    """
    Get Google service account credentials.
    
    Args:
        ssmkey: Secret manager key
        envvar: Environment variable name
        fconfig: File path for credentials
        rfile: Return file path instead of data
        
    Returns:
        str: File path to credentials
    """
    caller_line_number = sys._getframe(1).f_lineno        
    caller_filename = sys._getframe(1).f_code.co_filename
    caller_filename = caller_filename.split('/')[-1] if '/' in caller_filename else caller_filename      
    caller_func_name = sys._getframe(1).f_code.co_name    
    logger.info(f'{caller_filename}:{caller_func_name}:{caller_line_number} Getting google service account', level=9)

    return get_auth(ssmkey=ssmkey,
                    envvar=envvar,
                    fconfig=fconfig, 
                    rfile=rfile)


def create_secret(secret_name: str, key: str, value: str) -> Any:
    """
    Create or update a secret in AWS Secrets Manager.
    
    Args:
        secret_name: Name of the secret
        key: Secret key
        value: Secret value
        
    Returns:
        dict: AWS response
    """
    client = get_secrets_manager_client()
    res = client.update_secret(SecretId=secret_name, SecretString=json.dumps({key: value}))
    return res


def update_secret(secret_name: str, kv: Dict[str, Any]) -> Any:
    """
    Update an existing secret in AWS Secrets Manager.
    
    Args:
        secret_name: Name of the secret
        kv: Key-value pairs to update
        
    Returns:
        dict: AWS response
    """
    client = get_secrets_manager_client()
    secret = get_secret(secret_name)
    secret.update(kv)
    res = client.update_secret(SecretId=secret_name, SecretString=json.dumps(secret))
    return res


if __name__ == "__main__":
    path = os.path.dirname(os.path.realpath(__file__))
    path = os.path.dirname(path)
    
    _ = get_auth(ssmkey="gspread/config",
                 fconfig=f'{path}/{envdir}/gclass.json',
                 envvar='rds_CONFIG',
                 )
    print(_)
	