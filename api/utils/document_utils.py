'''
-----------------------------------------------------------------------
File: data_extraction.py
Creation Time: Oct 31st 2023 2:17 pm
Author: Saurabh Zinjad, Amey Bhilegonkar
Developer Email: zinjadsaurabh1997@gmail.com, abhilega@asu.edu
Copyright (c) 2023 Saurabh Zinjad. All rights reserved | GitHub: Ztrimus, ameygoes
-----------------------------------------------------------------------
'''
import os, sys
import re
import json
import time

#
import requests
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import pymupdf # imports the pymupdf library

#
from api import config
import api.utils.s3_utils as s3utils
from api.utils.logger import LLPackerLogger
logger = LLPackerLogger(os.path.basename(__file__))

def extract_text_from_html(soup):
    # Get the whole body tag
    tag = soup.body
    text_content = ""
    
    # TODO: Preprocessing of data, like remove html tags, remove unwanted content, etc.
    # Print each string recursively
    for string in tag.strings:
        string = string.strip()
        if string:
            text_content += string + "\n"
            
    return text_content

        
def get_url_content(url: str, max_trials: int = 3, test=False, bucket=""):
    """ Extract text content from any given web page

    Args:
        url (str): Webpage web link
    """    
    
    # If bucket is not provided, use the default bucket
    if not bucket:
        bucket = config.s3.zlm_bucket
        
    # Hash the URL to get a unique identifier
    url_hash = config.shash(url)
    local_path_jd = f'/tmp/job_description.txt'        
    remote_path_jd = f"job_profile_from_link/{url_hash}/job_description.txt"
                    
    # Try to extract the text from the URL  
    trial = 0
    while True:
        try:
            #
            if s3utils.file_exists_in_s3(bucket, remote_path_jd):
                logger.good(f"Job description extracted from url already exists in S3: {remote_path_jd}")
                content = s3utils.read_text_file_from_s3(bucket, remote_path_jd)
            else:
                res = requests.get(url)
                res.raise_for_status()
                
                # Initialize the object with the document
                soup = BeautifulSoup(res.content, "html.parser")
                content = extract_text_from_html(soup)
                
                if content:
                    #write_file(local_path_jd, content)                         
                    s3utils.upload_file_to_s3(content, remote_path_jd, bucket) 
                        
                    logger.good(f"Job description extracted from url uploaded to S3: {remote_path_jd}")                       
        
        
            if content:
                output = {'status':200, 
                            'message':"Link works! Successfully scheduled for job extraction background task!"
                        }    
            else:
                output = {'status':200, 
                            'message':"Unable to extract text from link!"
                        }                                                  
            break
        except Exception as e:
            print(e)
            trial += 1
            print(f"Request Trial: {trial}")
            if trial >= max_trials:
                output = {'status':200, 
                        'message':f"Unable to extract text from link! Error: {e}!"
                        }                       
                break
            else:
                time.sleep(1)
        
    if test:
        return output
    
    if output['status'] == 200:
        return content
    else:
        return ""


def pdf_to_text(pdf_path: str, max_pages: int = 0, 
                 return_first_page: bool = False):
    resume_text = ""
    first_page = ""
    doc = pymupdf.open(pdf_path) # open a document
    ipage = 1
    for page in doc: # iterate the document pages
        text = page.get_text() # get plain text encoded as UTF-8

        if max_pages and ipage > max_pages:
            break
        
        # Remove Unicode characters from each line
        cleaned_text = [re.sub(r'[^\x00-\x7F]+', '', line) for line in text]

        # Join the lines into a single string
        cleaned_text_string = '\n'.join(cleaned_text)
        resume_text += cleaned_text_string
        nfirst_page = len(first_page.strip())
        ncleaned_text= len(cleaned_text_string.strip())
        
        if ipage == 1 or (nfirst_page < 50 and ncleaned_text > 50):
            first_page = cleaned_text_string
            
        ipage += 1
    
    if return_first_page:
        return resume_text, first_page
    else:
        return resume_text
    

def extract_text_by_page(pdf_path):
    """Extract raw text by page."""
    with pymupdf.open(pdf_path) as doc:
        for page in doc:
            yield page.get_text()

def parse_cv_sections(text):
    """Parse sections from the CV text."""
    # Define potential section headers
    sections = ["Education", "Experience", "Skills", "Projects", "Certifications", "Languages"]
    # Initialize dictionary to hold the parsed CV
    cv_dict = {}
    current_section = None
    
    for line in text.split('\n'):
        # Check if the line is a section header
        normalized_line = line.strip()
        if normalized_line in sections:
            current_section = normalized_line
            cv_dict[current_section] = []
        elif current_section:
            cv_dict[current_section].append(line)
    
    # Convert list of lines back to strings for each section
    for section in cv_dict:
        cv_dict[section] = '\n'.join(cv_dict[section]).strip()
    
    return cv_dict

def parse_cv(pdf_path, format='dict'):
    """Parse sections from a CV PDF."""
    text = ""
    for page_text in extract_text_by_page(pdf_path):
        text += f"{page_text}\n"
    
    if format == 'text':
        return text
    else:
        cv_sections = parse_cv_sections(text)        
        return cv_sections
    
    
def get_elements(url, tag='', search={}, fname=None):
    """
    Downloads a page specified by the url parameter
    and returns a list of strings, one per tag element or an empty string if url is None or on failure.
    """
    
    # Check if URL is None or not a string
    if not isinstance(url, str) or not url:
        return ""
    
    response = simple_get(url)
    if response is None:
        return ""
    
    html = BeautifulSoup(response, 'html.parser')
    res = []
    
    if tag:    
        for li in html.select(tag):
            for name in li.text.split('\n'):
                if name.strip():
                    res.append(name.strip())
                    
    if search:
        soup = html
        r = ''
        
        if 'find' in search.keys():
            d = search['find']
            kval = d.pop('key', '')
            if 'name' in d.keys():
                arg = d.pop('name')
                soup = soup.find(arg, d)
            else:
                soup = soup.find(**d)
            r = soup
                
        if 'find_all' in search.keys():
            d = search['find_all']
            kval = d.pop('key', '')
            if 'name' in d.keys():
                arg = d.pop('name')
                r = soup.find_all(arg, d)
            else:
                r = soup.find_all(**d)
                
        if r:
            if kval:
                if 'find_all' in search.keys():
                    res = [x[kval] for x in r]
                else:
                    res = r[kval]
            else:
                for x in list(r):
                    if x:
                        res.extend(x)
                        
    return res if res else "" 


def log_error(e):
    """
    It is always a good idea to log errors. 
    This function just prints them, but you can
    make it do anything.
    """
    print(e)

def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.text  # Using resp.text to get Unicode string content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None



def get_elements_from_html(html_content, search={}):
    """
    Parses HTML content and returns a list of attributes based on the provided search criteria.
    
    Parameters:
    - html_content: HTML content as a string.
    - search: A dictionary with 'find' or 'find_all' keys to specify BeautifulSoup find/find_all search.
    
    Returns:
    A list of attributes (e.g., href values for <a> tags) extracted based on the search criteria, 
    or an empty list if no matches are found.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    res = []

    if search:
        elements = []
        if 'find' in search:
            d = search['find']
            elements = [soup.find(**d)]
        elif 'find_all' in search:
            d = search['find_all']
            key = d.pop('key', None)
            elements = soup.find_all(**d)
        
        if key:
            # Extracting a specific attribute (e.g., 'href') from each element
            res = [element.get(key, '') for element in elements if element and element.has_attr(key)]

    return res    