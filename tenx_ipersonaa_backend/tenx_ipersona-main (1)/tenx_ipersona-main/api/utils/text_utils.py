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

def find_first_numeric_value(text, default=0):
    if not isinstance(text, (str, int, float)):
        return default
    
    match = re.search(r"\d+", str(text))
    if match:
        return int(match.group())
    else:
        return default
    
def clean_string(text: str):
    text = text.title().replace(" ", "").strip()
    text = re.sub(r"[^a-zA-Z0-9]+", "", text)
    return text

    
def normalize_text(text: str) -> list:
    """Normalize the input text.

    This function tokenizes the text, removes stopwords and punctuations, 
    and applies stemming.

    Args:
        text (str): The text to normalize.

    Returns:
        list: The list of normalized words.
    """    
    
    def callback(str):
        return str.replace(".", " ")

    text = re.sub(r"(?:[A-Z]\.)+", lambda m: callback(m.group()), text)
    text = re.sub("\n", " ", text)
    words = text.split(' ')

    return words
    

def remove_urls(list_of_strings):
    """Removes strings containing URLs from a list using regular expressions."""
    filtered_list = [string for string in list_of_strings if not re.search(r"https?://\S+", string)]
    return filtered_list

def short_url(url, **kwargs): 
    if not (config.shorturl.SHORTEN_URL and config.shorturl.API_KEY):
        return url
    else:
        import pyshorteners 
        if not url.startswith('http'):
            return url
        else:
            s = pyshorteners.Shortener()
            return s.tinyurl.short(url)