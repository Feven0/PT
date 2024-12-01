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
import sys
import re
import time
import json
import base64
import platform
import subprocess
import zipfile
import shutil
import errno
import ast
from fpdf import FPDF
from pathlib import Path
from datetime import datetime
# from langchain_core.output_parsers import JsonOutputParser

#
from api.utils.logger import LLPackerLogger
logger = LLPackerLogger(os.path.basename(__file__))

#
OS_SYSTEM = platform.system().lower()

curdir = os.path.dirname(os.path.realpath(__file__))
cpath = os.path.dirname(curdir)
root_directory = os.path.dirname(cpath)

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

      
    
def job_doc_name(job_details: dict, output_dir: str = "output", kind: str = "", prefix: str=""):
    # make path keyword list
    plist = []
    company_name = job_details.get("company_name", "")
    if company_name:
        plist.append(clean_string(company_name))
        
    job_title = job_details.get("title", "")    
    if job_title:
        plist.append(clean_string(job_title))
        
    if plist:    
        doc_name = "_".join(plist)
    else:
        doc_name = "job_asset"
    
    if not prefix:
        prefix=""
        
    # make directory    
    if prefix.strip():
        doc_dir = os.path.join(output_dir, clean_string(prefix.strip()))
    else:    
        doc_dir = os.path.join(output_dir, clean_string(company_name))
        
    os.makedirs(doc_dir, exist_ok=True)

    if kind == "jd":
        return os.path.join(doc_dir, f"{doc_name}_JD.json")
    elif kind == "resume":
        return os.path.join(doc_dir, f"{doc_name}_resume.json")
    elif kind == "stat" or kind == "stats":
        return os.path.join(doc_dir, f"{doc_name}_stats.json")    
    elif kind == "cv" or kind == "cl":
        return os.path.join(doc_dir, f"{doc_name}_cl.txt")
    elif kind == "zip":
        return os.path.join(doc_dir, f"{doc_name}.zip")
    elif kind == 'base':
        return os.path.join(doc_dir, f"{doc_name}")
    elif kind == "folder":
        return os.path.join(doc_dir, f"{doc_name}")
    else:
        return os.path.join(doc_dir, f"{doc_name}_")


def clean_string(text: str):
    text = text.title().replace(" ", "").strip()
    text = re.sub(r"[^a-zA-Z0-9]+", "", text)
    return text

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
        if args:
            if hasattr(args[0], 'api_key_name'):
                apikeyname = args[0].api_key_name
                logger.good(f"!!!!!! Using {apikeyname} OpeanAI API Key !!!!!!")
                
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        if caller:= kwargs.get("caller"):
            func_run_log = f"Function {func.__name__} called by {caller} took {execution_time:.4f} seconds to execute"
        else:
            func_run_log = f"----TIME---> Function {func.__name__} took {execution_time:.4f} seconds to execute"     
           
        if execution_time > 1 and execution_time < 3:
            fg = 'pink'
        elif execution_time >= 3:
            fg = 'yellow'
        else:
            fg = 'green'        
        
        logger.good(func_run_log, fg=fg)
        # Append execution_time to the result tuple
        if kwargs.get("return_exectime", False):
            if isinstance(result, tuple):
                return result + (execution_time,)
            else:
                return result, execution_time
        else:
            return result
        
    return wrapper


def text_to_pdf(text: str, file_path: str):
    """Converts the given text to a PDF and saves it to the specified file path.

    Args:
        text (str): The text to be converted to PDF.
        file_path (str): The file path where the PDF will be saved.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    # Encode the text explicitly using 'latin-1' encoding
    encoded_text = text.encode('utf-8').decode('latin-1')
    pdf.multi_cell(0, 5, txt=encoded_text)
    pdf.output(file_path)
    # try:
    #     open_file(file_path)
    # except Exception as e:
    #     print("Unable to open the PDF file.")

def save_latex_as_pdf(tex_file_path: str, dst_path: str , use_xelatex : bool = False) :
    # Call pdflatex to convert LaTeX to PDF
    
    prev_loc = os.getcwd()
    ldir = os.path.dirname(tex_file_path)
    os.chdir(ldir)
    print(f'---Converting LaTeX to PDF: dir={ldir}---')
    result = subprocess.run(
        [ "pdflatex" if not use_xelatex else "xelatex", tex_file_path, "&>/dev/null"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    print('---Converting LaTeX to PDF: Done---')
    
    os.chdir(prev_loc)
    resulted_pdf_path = tex_file_path.replace(".tex", ".pdf")

    print(f".....moving files from  src={resulted_pdf_path} to dst={dst_path}")
    
    try:
        shutil.move(resulted_pdf_path, dst_path)
    except Exception as e:
        print(result)
        raise
        
    shutil.move(tex_file_path, dst_path.replace(".pdf", ".tex"))

    # with open(dst_path, "rb") as pdf_file:
    #     PDFbyte = pdf_file.read()


    if result.returncode != 0:
        print("Exit-code not 0, check result!")
    try:
        pass
        # open_file(dst_path)
    except Exception as e:
        print("Unable to open the PDF file.")
        print("Unable to open the PDF file.")

    filename_without_ext = os.path.basename(tex_file_path).split(".")[0]
    unnessary_files = [
        file
        for file in os.listdir(os.path.dirname(os.path.realpath(tex_file_path)))
        if file.startswith(filename_without_ext)
    ]

    for file in unnessary_files:
        file_path = os.path.join(os.path.dirname(tex_file_path), file)
        if os.path.exists(file_path):
            os.remove(file_path)

    # with open(dst_path, "rb") as f:
    #     pdf_data = f.read()


    print(f"PDF file saved at: {dst_path}")
    
    return dst_path, dst_path.replace(".pdf", ".tex")


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

def parse_json_markdown(json_string: str) -> dict:
    try:
        # Try to find JSON string within first and last triple backticks
        if json_string[3:13].lower() == "typescript":
            json_string = json_string.replace(json_string[3:13], "",1)
        
        if 'JSON_OUTPUT_ACCORDING_TO_RESUME_DATA_SCHEMA' in json_string:
            json_string = json_string.replace("JSON_OUTPUT_ACCORDING_TO_RESUME_DATA_SCHEMA", "",1)
        
        if json_string[3:7].lower() == "json":
            json_string = json_string.replace(json_string[3:7], "",1)
        

        # match = re.search(r"""```*
        #                     (?:json)?
        #                     (.*)```""", json_string, flags=re.DOTALL|re.VERBOSE)

        # # If no match found, assume the entire string is a JSON string
        # if match is None:
        #     json_str = json_string
        # else:
        #     # If match found, use the content within the backticks
        #     json_str = match.group(1)

        # # Strip whitespace and newlines from the start and end
        # json_str = json_str.strip()

        # # Parse the JSON string into a Python dictionary while allowing control characters by setting strict to False
        # parsed = json.loads(json_str)
        # parser = JsonOutputParser()
        parsed = parser.parse(json_string)

        return parsed
    except Exception as e:
        print(e)
        return None

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


def key_value_chunking(data, prefix=""):
    """Chunk a dictionary or list into key-value pairs.

    Args:
        data (dict or list): The data to chunk.
        prefix (str, optional): The prefix to use for the keys. Defaults to "".

    Returns:
        A list of strings representing the chunked key-value pairs.
    """
    chunks = []
    stop_needed = lambda value: '.' if not isinstance(value, (str, int, float, bool, list)) else ''
    
    if isinstance(data, dict):
        for key, value in data.items():
            if value is not None:
                chunks.extend(key_value_chunking(value, prefix=f"{prefix}{key}{stop_needed(value)}"))
    elif isinstance(data, list):
        for index, value in enumerate(data):
            if value is not None:
                chunks.extend(key_value_chunking(value, prefix=f"{prefix}_{index}{stop_needed(value)}"))
    else:
        if data is not None:
            chunks.append(f"{prefix}: {data}")
    
    return chunks

def generate_code(name):
    #    return name[:3].lower()  # to use only first 3 letters of the first word
    words = name.split()
    code = ''.join(word[:3].lower() for word in words)
    return code

def generate_codes(data):
    for key, value in data.items():
        if isinstance(value, dict):
            if "name" in value:
                outer_code = generate_code(value["name"])
                value["code"] = outer_code
            if "attributes" in value:
                for attr in value["attributes"]:
                    if "name" in attr:
                        inner_code = generate_code(attr["name"])
                        attr["code"] = outer_code + inner_code
            generate_codes(value)


def handle_json_keys(data):

        # Mapping full month names to their abbreviated forms
        MONTH_ABBREVIATIONS = {
            "January": "Jan",
            "February": "Feb",
            "March": "Mar",
            "April": "Apr",
            "May": "May",
            "June": "Jun",
            "July": "Jul",
            "August": "Aug",
            "September": "Sept", 
            "October": "Oct",
            "November": "Nov",
            "December": "Dec"
        }
        def reformat_date(date_str):
            """
            Converts a date string from 'dd-mm-yyyy' or 'd-m-yyyy' format to 'dd Month yyyy' format.
            """

            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                month_abbr = MONTH_ABBREVIATIONS[date_obj.strftime("%B")]
                return date_obj.strftime(f"%d {month_abbr} %Y")

                # return date_obj.strftime("%d %B %Y") # uncomment this line if you want to use month full names
            except ValueError:
                return date_str
            
        def clean_summary(summary):
            summary_str = " ".join(summary)
            sentences = re.split(r'\.\s*', summary_str)  # Split sentences
            cleaned_sentences = [re.sub(r'[^\w\s,]', '', sentence).strip() for sentence in sentences if sentence]
            return cleaned_sentences
        
        if 'projects' in data:
            for project in data['projects']:
                if isinstance(project['summary'], str):
                    project['summary'] = [project['summary']]
                    if isinstance(project['summary'], list):
                        project['summary'] = clean_summary(project['summary'])
                    elif isinstance(project['summary'], str):
                        project['summary'] = clean_summary([project['summary']])


                if project['link'] == "None":
                    project['link'] = ""

                if project['tools'] == "[]":
                    project['tools'] = []
                
        if 'work_experience' in data:
            for experience in data['work_experience']:
                if isinstance(experience['summary'], str):
                    experience['summary'] = [experience['summary']]
                    if isinstance(experience['summary'], list):
                        experience['summary'] = clean_summary(experience['summary'])
                    elif isinstance(experience['summary'], str):
                        experience['summary'] = clean_summary([experience['summary']])
                experience['summary'] = [sentence.strip() for sentence in experience["summary"][0].split('.') if sentence.strip()]


        if 'education' in data:
            for edu in data['education']:
                if 'coursework' in edu:
                    
                    # Case 1: course is a string representation of an empty list "[]"
                    if edu['coursework'] == "[]":
                        edu['coursework'] = []
                    
                    # Case 2: course is already an empty list
                    if isinstance(edu['coursework'], list) and len(edu['coursework']) == 0:
                        edu['coursework']= []

                    # Case 3: course is a string representation of a list (e.g., "['item1', 'item2']")
                    if isinstance(edu['coursework'], str):
                        try:
                            parsed_course = ast.literal_eval(edu['coursework'])
                            if isinstance(parsed_course, list):
                                edu['coursework'] = parsed_course
                        except (ValueError, SyntaxError):
                            pass
                    
                    # Case 4: course is already a list
                    if isinstance(edu['coursework'], list):
                        edu['coursework'] = edu['coursework']

        def process_dates(data):
            for key, value in data.items():
                if isinstance(value, str):
                    if 'from_date' in key.lower() or 'to_date' in key.lower() or 'date' in key.lower():
                        data[key] = reformat_date(value)

                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            process_dates(item)
                elif isinstance(value, dict):
                    process_dates(value)

        process_dates(data)

        return data

def clean_summary(summary):
    """Clean the summary by removing hyphens and underscores."""
    if isinstance(summary, str):
        return summary.replace('-', '').replace('_', '')
    elif isinstance(summary, list):
        return [s.replace('-', '').replace('_', '') for s in summary]
    return summary

def preprocess_user_data(data):
    """Recursively search for 'summary' keys and clean them."""
    if isinstance(data, dict):
        for key, value in data.items():
            if key == 'summary':
                data[key] = clean_summary(value)
            else:
                preprocess_user_data(value)
    elif isinstance(data, list):
        for item in data:
            preprocess_user_data(item)
    return data