import os
import json
import time
import streamlit as st # type: ignore
import numpy as np # type: ignore
import pandas as pd


from pathfig import *
from api import config


from tenx_job_recommender.tenx_ipersona.api.llm.llm_models import ChatGPT, Gemini, TogetherAI
from tenx_job_recommender.tenx_ipersona.api.utils.document_utils import get_url_content, extract_text, extract_text_from_pdf
from zlm.utils.latex_ops import latex_to_pdf
from tenx_job_recommender.tenx_ipersona.api.utils.utils import (
    get_default_download_folder,
    key_value_chunking,
    measure_execution_time,
    read_json,
    write_file,
    write_json,
    job_doc_name,
    text_to_pdf,
    get_prompt,
)
from api.modules.trainee_information import TraineeInformation

openai_api_key = config.openai.api_key

download_path = f"{cpath}/zlm/data/user_data"
if not os.path.exists(download_path):
    os.makedirs(download_path)
    

module_dir = f"{cpath}/zlm"
demo_data_path = os.path.join(module_dir,"demo_data", "user_resume.pdf")
prompt_path = os.path.join(module_dir, "prompts")

class DataExtractor:

    def __init__(
        self, provider: str ):
        
        if provider is None or provider.strip() == "":
            self.provider = "openai"
        else:
            self.provider = provider

    def resume_to_json(self, pdf_path):
        """
        Converts a resume in PDF format to JSON format.

        Args:
            pdf_path (str): The path to the PDF file.

        Returns:
            dict: The resume data in JSON format.
        """
        system_prompt = get_prompt(
            os.path.join(prompt_path, "resume-extractor.txt")
        )
        llm = self.get_llm_instance(system_prompt)
        resume_text = extract_text_from_pdf(pdf_path)
        with open("resume_text.txt", "w") as file:
            file.write(resume_text)
        resume_json = llm.get_response(resume_text, need_json_output=True)
        return resume_json
    
    def get_llm_instance(self, system_prompt):
        if self.provider == "openai":
            return ChatGPT(api_key=openai_api_key, system_prompt=system_prompt)
        elif self.provider == "together":
            return TogetherAI(api_key=openai_api_key, system_prompt=system_prompt)
        elif self.provider == "gemini":
            return Gemini(api_key=openai_api_key, system_prompt=system_prompt)
        else:
            raise Exception("Invalid LLM Provider")

    def single_user_data_extraction(self, user_data_path= None,is_st=False):
        print("\nFetching user data...")

        if user_data_path is None:
            user_data_path = demo_data_path
            
        download_dir = os.path.join(download_path, "user_data.json")
        # Read user data
        if os.path.splitext(user_data_path)[1] == ".pdf":
            user_data = self.resume_to_json(user_data_path)
            write_json(download_dir, user_data)
            return user_data
            
            
    def extract_cv_content(self, is_st=False):
        """
        Process files in a folder.
        """
        ti = TraineeInformation()
        trainee_cv, trainee_profile =  ti.fetch_cv_and_profile(cvforce=True)
        
        folder_path = f"{cpath}/data/trainees_cv"
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            
            if file_name.endswith(".pdf"):
                try:
                    # Extract text from the PDF
                    user_data = self.resume_to_json(file_path)
                    if user_data:
                        json_file_path = os.path.join(download_path, os.path.splitext(file_name)[0] + ".json")
                        with open(json_file_path, 'w') as json_file:
                            json.dump({"text": user_data}, json_file, indent=4)
                        print(f"Text extracted from '{file_name}'")

                        
                    else:
                        print(f"File '{file_name}' is empty.")
                except Exception as e:
                    print(f"Error processing file '{file_name}': {e}")
            else:
                print(f"Skipping non-PDF file '{file_name}'.")
    

if __name__ == "__main__":
    de = DataExtractor(provider = 'openai')
    result = de.extract_cv_content()

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # #### evidence: 
    # where = ['Grade', 'Application', 'Interview']
    # who = ['Tutor', 'PA']
    # confidence_degree = ['High', 'Medium', 'Low']
    # sentment = ['Positive', 'Negative', 'Neutral']
    # Verb = ['Observed', 'Inferred', 'Guessed']
    # remark = ['any text']