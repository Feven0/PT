import warnings
warnings.filterwarnings("ignore", category=ResourceWarning, message="unclosed.*<ssl.SSLSocket.*>") 

from logging import root
import os, sys
import shutil

curdir = os.path.dirname(os.path.realpath(__file__))
cpath = os.path.dirname(curdir)
if not cpath in sys.path:
    sys.path.append(cpath)
    

import pandas as pd
import numpy as np
from datetime import date, datetime
import zipfile
#
import boto3
boto3.compat.filter_python_deprecation_warnings()
from botocore.exceptions import NoCredentialsError, ClientError
from botocore.config import Config 
#
import io
from io import StringIO
from io import BytesIO
import json
import pickle


from api.utils.logger import LLPackerLogger
logger = LLPackerLogger(os.path.basename(__file__))


# signature_version (string) - The signature version used when signing requests. 
# Note that the default version is Signature Version 4. 
# If you’re using a presigned URL with an expiry of greater than 7 days, you should specify Signature Version 2.
# https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html
my_config = Config(
    region_name = 'us-east-1',
    signature_version = 's3v4',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
)

if os.path.exists(".env/aws_config.json"):
    with open(".env/aws_config.json") as e:
        env = json.load(e)

    # Creating the low level functional client
    client = boto3.client(
        "s3",
        aws_access_key_id=env["aws_access_key_id"],
        aws_secret_access_key=env["aws_secret_access_key"],
        region_name=env["region_name"],
    )

    # Creating the high level object oriented interface
    resource = boto3.resource(
        "s3",
        aws_access_key_id=env["aws_access_key_id"],
        aws_secret_access_key=env["aws_secret_access_key"],
        region_name=env["region_name"],
    )

    # Fetch the list of existing buckets
    clientResponse = client.list_buckets()
    
    client.close()

def two_digit_str(xx):
    x = int(xx)
    if x < 10:
        return '0'+str(x)
    else:
        return str(x)
    
def get_s3_prefix(folder, year="", month="", day="", hour="", datefirst=False, dsep='/', hsep=' '):      
    
    if not datefirst and folder:
        PREFIX = folder
    else:
        PREFIX = ""
    
    for i, x in enumerate([year, month, day, hour]):
        if i==0:
            sep = '/'
        elif i==3:
            sep = hsep
        else:
            sep = dsep
        if x:
            if PREFIX:
                PREFIX = PREFIX + sep + str(x)
            else:
                PREFIX += str(x)
        else:
            break               
            
    if datefirst and folder:
        return PREFIX + '/' + folder
    else:
        return PREFIX    
    
def create_filename(datetime_obj = None, ext: str = ".txt", 
                    prefix: str = "",  suffix: str = "" ):
    """
    Function to create a filename with a datetime stamp
    """
    if datetime_obj is None:
        datetime_obj = datetime.now()
        
    
    # convert datetime obj to string
    str_dt_obj = str(datetime_obj)
    
    # create a file object along with extension
    file_name = prefix + str_dt_obj + suffix + ext
    
    return file_name
    

def get_public_url(bucket_name: str, s3_file_name: str, 
                   filename: str="", 
                   expiration: int=604799):
    
    # Generate a pre-signed URL for download
    s3_client = boto3.client("s3", config=my_config)
    
    #
    Params={'Bucket': bucket_name, 'Key': s3_file_name}
    if filename:
        Params['ResponseContentDisposition'] = 'attachment; filename='+filename
        
    url = s3_client.generate_presigned_url(
        ClientMethod='get_object',
        Params=Params,
        ExpiresIn=expiration
    )    
    
    s3_client.close()
    
    return url
    
def file_exists_in_s3(bucket_name, file_key):
    """
    Checks if a file exists in an S3 bucket.

    Args:
        bucket_name (str): The name of the S3 bucket.
        file_key (str): The key (path) of the file in the bucket.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    s3_client = boto3.client('s3')
    try:        
        s3_client.head_object(Bucket=bucket_name, Key=file_key)        
        res = True
    except Exception as e:        
        res = False
        
    s3_client.close()
    
    return res
    
def folder_exists_and_not_empty(bucket:str, path:str) -> bool:
    '''
    Folder should exists. 
    Folder should not be empty.
    '''
    s3_client = boto3.client('s3')
    if not path.endswith('/'):
        path = path+'/' 
    resp = s3_client.list_objects(Bucket=bucket, Prefix=path, Delimiter='/',MaxKeys=1)
    s3_client.close()
    return 'Contents' in resp
    
def folder_exists(bucket:str, path:str) -> bool:
    '''
    Folder should exists. 
    Folder could be empty.
    '''
    s3_client = boto3.client('s3')
    path = path.rstrip('/') 
    resp = s3_client.list_objects(Bucket=bucket, Prefix=path, Delimiter='/',MaxKeys=1)
    s3_client.close()
    return 'CommonPrefixes' in resp
    
def check_file_exists(bucket_name, file_key):
    return file_exists_in_s3(bucket_name, file_key)
    
def generate_upload_filename(s3_file_name, 
                             root_folder="", 
                             dtprefix=True, 
                             datefirst=False, 
                             dt=None,
                             **kwargs):
    s3root = root_folder.strip()
    if dtprefix and dt is not None:
        if isinstance(dt, datetime):            
            year = dt.year
            month = dt.month
            day = dt.day
            s3root = get_s3_prefix(s3root, year=str(year), 
                                        month=str(month), day=str(day), 
                                        datefirst=datefirst)
        
    if s3root.strip():
        file_name = os.path.join(s3root.strip(), s3_file_name)
    else:
        file_name = s3_file_name
        
    return file_name
    
def upload_folder_zip(local_file_list: list, bucket_name: str, s3_folder_name: str, 
                      zip_file_name: str="", 
                      dtprefix: bool=True, 
                      root_folder: str="",
                      datefirst: bool=False,
                      url: bool=False, **kwargs):
    
    try:
        if zip_file_name == "":
            zip_file_name = s3_folder_name.split('/')[-1] if '/' in s3_folder_name else s3_folder_name
        if '.zip' not in zip_file_name:
            zip_file_name = zip_file_name + '.zip'
            

        print('***********saving to zip file:', zip_file_name)
        zipf = zipfile.ZipFile( zip_file_name, 'w') #, zipfile.ZIP_DEFLATED
        
        for src in local_file_list:
            if os.path.exists(src):
                dst = os.path.basename(src)
                shutil.copyfile(src, dst)                
                zipf.write(dst)
                os.remove(dst)
        zipf.close()  
        
        res = upload_file(zip_file_name, bucket_name, s3_folder_name, 
                          root_folder=root_folder,
                          dtprefix=dtprefix, 
                          datefirst=datefirst,
                          url=url, **kwargs)
        
        return res
    except Exception as e:
        print(f"Error zipping folder: {e}")
        raise
          
              
def upload_file(local_file: str, bucket_name: str, s3_file_name: str, 
                dtprefix: bool=True, 
                root_folder: str="",
                datefirst: bool=False,
                url: bool=True, **kwargs):
    """
    Function to upload a file to an S3 bucket
    """
    # Upload the file to S3
    

    file_name = generate_upload_filename(s3_file_name, 
                                         root_folder=root_folder, 
                                         dtprefix=dtprefix, 
                                         datefirst=datefirst,
                                         dt=kwargs.get('dt', None)
    )

    s3_client = boto3.client("s3")
    try:
        s3_client.upload_file(local_file, bucket_name, file_name)
        print(local_file + " uploaded successfully")
        if url:
            res = get_public_url(bucket_name, file_name)        
        else:
            res = file_name
            
        s3_client.close()
        
        return res
    except FileNotFoundError:
        print("The file was not found")
        s3_client.close()
        return False
    except NoCredentialsError:
        print("Credentials not available")
        s3_client.close()
        return False
    
    

def list_files(bucket: str, **kwargs):
    """
    List files in a folder (prefix) in an S3 bucket.

    Args:
        folder_key (str): The key (prefix) of the folder in the S3 bucket.
        bucket_name (str): The name of the S3 bucket.

    Returns:
        list: List of file keys (paths) in the specified folder.
    """
    
    contents = []
    
    try:
        s3 = boto3.client("s3")
        # Use the paginator to retrieve the file paths for objects matching the prefix
        paginator = s3.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(Bucket=bucket, **kwargs)

        for page in page_iterator:
            if 'Contents' in page:
                for obj in page['Contents']:
                    contents.append(obj['Key'])                                            
        
        s3.close()
        
        return contents
    except Exception as e:
        print(f"Failed to list files in folder '{folder_key}': {e}")
        return []

def list_files_in_s3_folder(folder_key, bucket_name):
    return list_files(bucket_name, Prefix=folder_key)

    
def get_all_data(bucket, prefix, **kwargs):
    print(f'Getting data from S3 with filter bucket={bucket} and prefix={prefix} ..')
    filepaths = list_files(bucket, Prefix=prefix, MaxKeys=kwargs.get('maxkeys',2000) )
                    
    if kwargs.get('dataframe', True):
        df = get_s3_dataframe(bucket,  filepaths, ext=kwargs.get('ext','csv') )                
        return df    
    else:
        return filepaths

def download_file(file_name: str, bucket: str, output: str):
    """
    Function to download a given file from an S3 bucket
    """
    s3 = boto3.resource("s3")
    s3.Bucket(bucket).download_file(file_name, output)
    s3.close()
    print(f"{filename} downloaded successfully")

    return output

def get_s3_dataframe(bucket: str, pathlist: "str | list[str]", ext='csv'):
    """
    Function to get a dataframe an S3 bucket and key
    """   
    if isinstance(pathlist, str):
        pathlist = [pathlist]
        
    
    s3_client = boto3.client("s3")
    
    dflist = []
    for filename in pathlist:
        response = s3_client.get_object(Bucket=bucket, Key=filename)
        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
        if status == 200:
            if ext == 'csv':
                df = pd.read_csv(response.get("Body"))
            elif ext == 'json':
                df = pd.read_json(response.get("Body"))
            elif ext == 'parquet':
                df = pd.read_parquet(response.get("Body"))
            else:
                df = pd.read_csv(response.get("Body"))
                
            df['filename'] = filename
                
            dflist.append(df)
        else:
            print(f"Unsuccessful S3 get_object response. Status - {status}")
         
    s3_client.close()   
       
    dfall = pd.concat(dflist, ignore_index=True, sort=False)
    
    return dfall

def get_s3_csv_dataframe(bucket: str, filename: str):
    """
    Function to get a dataframe an S3 bucket and key
    """   
    return get_s3_dataframe(bucket, filename, ext='csv')

def get_s3_json_dataframe(bucket: str, filename: str):
    """
    Function to get a dataframe an S3 bucket and key
    """   
    return get_s3_dataframe(bucket, filename, ext='json')

def upload_dataframe_to_s3(dataframe, bucket_name, file_name):
    """
    Uploads a Pandas DataFrame directly to an S3 bucket as a CSV file.

    Args:
        dataframe (pandas.DataFrame): The DataFrame to upload.
        bucket_name (str): The name of the S3 bucket.
        file_name (str): The name of the file to be created in the bucket.
    """
    try:
        csv_buffer = io.StringIO()
        dataframe.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        csv_bytes = csv_buffer.getvalue().encode('utf-8')

        s3_client = boto3.client('s3')
        s3_client.put_object(Bucket=bucket_name, Key=file_name, Body=csv_bytes)
        s3_client.close()

        print(f"DataFrame uploaded to S3: {file_name}")
    except Exception as e:
        print(f"Upload failed: {e}")

def read_dataframe_from_s3(bucket_name, file_name):
    """
    Reads a CSV file from an S3 bucket into a Pandas DataFrame.

    Args:
        bucket_name (str): The name of the S3 bucket.
        file_name (str): The name of the file to be read from the bucket.

    Returns:
        pandas.DataFrame or None: The DataFrame containing the data from the CSV file,
                                  or None if an error occurred.
    """
    try:
        s3_client = boto3.client('s3')

        response = s3_client.get_object(Bucket=bucket_name, Key=file_name)
        csv_content = response['Body'].read().decode('utf-8')

        dataframe = pd.read_csv(StringIO(csv_content))

        s3_client.close()
        
        return dataframe
    except Exception as e:
        print(f"Error reading file from S3: {e}")
        return None    
    
def upload_file_to_s3(file_data, file_key, bucket_name, isfile=False):
    """
    Upload file data to an S3 bucket.

    Args:
        file_data (bytes): The binary data of the file to be uploaded.
        file_key (str): The key (path) of the file in the S3 bucket.
        bucket_name (str): The name of the S3 bucket.
    """
    try:
        s3_client = boto3.client('s3')

        if isfile:
            s3_client.upload_file(file_data, bucket_name, file_key)
        else:
            s3_client.put_object(Bucket=bucket_name, Key=file_key, Body=file_data.encode('utf-8'))

        s3_client.close()
        
        print(f"File uploaded to S3: {file_key}")
    except Exception as e:
        print(f"Upload failed: {e}")

def read_text_file_from_s3(bucket_name, file_key):
    """
    Read a text file from an S3 bucket.

    Args:
        file_key (str): The key (path) of the file in the S3 bucket.
        bucket_name (str): The name of the S3 bucket.

    Returns:
        str or None: The content of the file as a string, or None if the file doesn't exist or an error occurs.
    """
    try:
        s3_client = boto3.client('s3')

        file_buffer = BytesIO()
        s3_client.download_fileobj(bucket_name, file_key, file_buffer)
        file_buffer.seek(0)

        file_content = file_buffer.read().decode('utf-8')
        file_buffer.close()
        
        s3_client.close()
        
        return file_content
    except Exception as e:
        print(f"Read failed: {e}")
        return ""
    
    
def delete_file_from_s3(bucket_name, file_path):
    """
    Delete a file from an S3 bucket.
    """
    # Initialize S3 client
    s3 = boto3.client('s3')

    # Delete file from S3
    s3.delete_object(Bucket=bucket_name, Key=file_path)
    
    s3.close()
    
    print("File deleted from S3.")
    
def save_clustering_model(model, bucket_name, key):
    """
    Save the clustering model to an S3 bucket.

    Parameters:
        model (object): The clustering model object to save.
        bucket_name (str): The name of the S3 bucket to save the model to.
        key (str): The key or path within the bucket to save the model file.
    """
    try:
        # Serialize the model
        model_bytes = pickle.dumps(model)
        
        # Upload the serialized model to S3
        s3 = boto3.client('s3')
        s3.put_object(Body=model_bytes, Bucket=bucket_name, Key=key)
        s3.close()
        
        print("Model saved successfully to S3 bucket.")
    except Exception as e:
        print(f"An error occurred while saving the model to S3: {str(e)}")
        
def load_clustering_model(bucket_name, key):
    """
    Load the clustering model from an S3 bucket.

    Parameters:
        bucket_name (str): The name of the S3 bucket where the model is saved.
        key (str): The key or path within the bucket where the model file is located.

    Returns:
        object: The loaded clustering model object.
    """
    try:
        # Download the model file from S3
        s3 = boto3.client('s3')
        response = s3.get_object(Bucket=bucket_name, Key=key)
        model_bytes = response['Body'].read()
        s3.close()
        
        # Deserialize the model
        model = pickle.loads(model_bytes)
        print("Model loaded successfully from S3 bucket.")
        return model
    except Exception as e:
        print(f"An error occurred while loading the model from S3: {str(e)}")


class fileManager:
    def __init__(self, use_local_storage=False, bucket=None):
        self.use_local_storage = use_local_storage
        if not bucket:
            bucket = config.s3.zlm_bucket
        self.bucket = bucket
        
    def _save_to_file_cache(self, local_file, filename, key=""):                    
        
        file_key = os.path.basename(filename)
        if key:
            file_key = os.path.join(key, file_key)
                    
        if self.bucket:
            try:
                s3utils.upload_file_to_s3(local_file, file_key, self.bucket, isfile=True) 
            except Exception as e:
                logger.error(f"Error saving to S3: {os.path.basename(filename)}")
                print(e)
                    
        return file_key
          
    def _read_from_file_cache(self, filename, key=""):
        # get filename                   
        file_key = os.path.basename(filename)
        if key:
            file_key = os.path.join(key, file_key)
        
        try:        
            listobj = s3utils.read_text_file_from_s3(self.bucket, file_key)
        except Exception as e:
            logger.error(f"Error reading from S3: {os.path.basename(filename)}")
            print(e)
            listobj = ""
            
        return listobj
              
if __name__ == "__main__":
    foldername = "linkedlnScrapedJobs"
#    /home/mahlet/api.job-engine/2022-09-22 03:42:55.792442.csv
    filename = '2022-09-22 03:42:55.792442.csv'
    output = "newfile.csv"
    # Print the bucket names one by one
    # print('Printing bucket names...')
    # for bucket in clientResponse['Buckets']:
    #     print(f'Bucket Name: {bucket["Name"]}')

    upload_file(
        f"{filename}", "jobmodel", f"{foldername}/{filename}"
    )
    # download_file(f"{foldername}/{filename}", 'jobmodel', output)
