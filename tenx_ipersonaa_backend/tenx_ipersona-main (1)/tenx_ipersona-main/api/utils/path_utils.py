'''
-----------------------------------------------------------------------
File: utils.py
Creation Time: Dec 6th 2023, 7:09 pm
Author: Saurabh Zinjad
Developer Email: zinjadsaurabh1997@gmail.com
Copyright (c) 2023 Saurabh Zinjad. All rights reserved | GitHub: Ztrimus
-----------------------------------------------------------------------
'''

import os
import re
import time
import json
import base64
import platform
import subprocess
import zipfile
import shutil
import errno

from fpdf import FPDF
from pathlib import Path
from datetime import datetime

OS_SYSTEM = platform.system().lower()

curdir = os.path.dirname(os.path.realpath(__file__))
cpath = os.path.dirname(curdir)
root_directory = os.path.dirname(cpath)

    
def camel_to_snake(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

def remove_trailing_slash(path: str) -> str:    
    return path.rstrip("/")

def remove_leading_slash(path: str) -> str:
    return path.lstrip("/")

def write_file(file_path, data):
    with open(file_path, "w") as file:
        file.write(data)


def read_file(file_path, mode="r"):
    with open(file_path, mode) as file:
        file_contents = file.read()
    return file_contents


def write_json(file_path, data):
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=2)


def read_json(file_path: str):
    with open(file_path) as json_file:
        return json.load(json_file)

def zip_folder(folder_path: str, zip_file_path: str, s3url=True):
    """Zip the specified folder and save the zip file to the specified path.

    Args:
        folder_path (str): The path of the folder to be zipped.
        zip_file_path (str): The path where the zip file will be saved.
    """
    try:
        subprocess.run(["zip", "-r", zip_file_path, folder_path], check=True)
        
        zipfile_name = zip_file_path+'.zip'
    except subprocess.CalledProcessError as e:
        try:
            zipfile_name = zip_file_path+'.zip'

            zipf = zipfile.ZipFile( zipfile_name, 'w', zipfile.ZIP_DEFLATED)
            
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    zipf.write(os.path.join(root, file))
            zipf.close()  
            
            return zipfile_name
        except Exception as e:
            print(f"Error zipping folder: {e}")
            raise
        
    if s3url:
        return zipfile_name       


def delete_file(file_path: str):        
    os.remove(file_path, missing_ok=True)
    
def delete_folder(folder_path: str):
    shutil.rmtree(folder_path, ignore_errors=True)        
        
        
def unzip_file(zip_file_path: str, dest_folder_path: str):
    """Unzip the specified file to the specified destination folder.

    Args:
        zip_file_path (str): The path of the zip file to be unzipped.
        dest_folder_path (str): The path where the contents of the zip file will be extracted.
    """
    try:
        subprocess.run(["unzip", "-o", zip_file_path, "-d", dest_folder_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error unzipping file: {e}")
        

def delete_files_and_subdirectories(directory_path):
   try:
     with os.scandir(directory_path) as entries:
       for entry in entries:
         if entry.is_file():
            os.unlink(entry.path)
         else:
            shutil.rmtree(entry.path)
     print(f"!!!All files and subdirectories in {directory_path} are deleted successfully!!!")
   except OSError:
     print("Error occurred while deleting files and subdirectories in {directory_path}.")
      

def open_file(file: str):
    if OS_SYSTEM == "darwin":  # macOS
        os.system(f"open {file}")
    elif OS_SYSTEM == "linux":
        try:
            os.system(f"xdg-open {file}")
        except FileNotFoundError:
            print("Error: xdg-open command not found. Please install xdg-utils.")
    elif OS_SYSTEM == "windows":
        try:
            os.startfile(file)
        except AttributeError:
            print("Error: os.startfile is not available on this platform.")
    else:
        # Default fallback for other systems
        try:
            os.system(f"xdg-open {file}")
        except FileNotFoundError:
            print(f"Error: xdg-open command not found. Please install xdg-utils. Alternatively, open the file manually.")


def save_log(content: any, file_name: str):
    timestamp = int(datetime.timestamp(datetime.now()))
    file_path = f"logs/{file_name}_{timestamp}.txt"
    write_file(file_path, content)


def measure_execution_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        func_run_log = f"Function {func.__name__} took {execution_time:.4f} seconds to execute"
        print(func_run_log)

        return result

    return wrapper


def get_default_download_folder():    
    """Get the default download folder for the current operating system."""
    downlaod_folder_path = os.path.join(root_directory, "Downloads", "JobLLM_Resume_CV")
    #print(f"downlaod_folder_path: {downlaod_folder_path}")
    os.makedirs(downlaod_folder_path, exist_ok=True)
    return downlaod_folder_path

def get_default_output_folder():
    """Get the default output folder for the current operating system."""
    output_folder_path = os.path.join(root_directory, "Output", "JobLLM_Resume_CV")
    #print(f"output_folder_path: {output_folder_path}")
    os.makedirs(output_folder_path, exist_ok=True)
    return output_folder_path


def get_prompt(system_prompt_path: str) -> str:
        """
        Reads the content of the file at the given system_prompt_path and returns it as a string.

        Args:
            system_prompt_path (str): The path to the system prompt file.

        Returns:
            str: The content of the file as a string.
        """
        with open(system_prompt_path, encoding="utf-8") as file:
            return file.read().strip() + "\n"
