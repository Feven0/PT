import os
import json
from collections import OrderedDict
import copy
from typing import Optional, Dict, List, Iterable, Union, Tuple


from api import config

from api.llm.openai_wrapper import RunOnThread
import api.utils.s3_utils as s3utils
from api.llm.llm_models import ChatGPT, Gemini, TogetherAI, cv_agents
from api.llm.utils.llm_parse import extract_json
from api.utils.document_utils import pdf_to_text as extract_text

from api.modules import competency
from api.utils import (
    get_default_download_folder,
    get_default_output_folder, 
    delete_files_and_subdirectories,
    measure_execution_time,
    read_json,
    write_file,
    write_json,
    get_prompt,
    delete_file,
    delete_folder    
)

from api.utils.logger import LLPackerLogger
logger = LLPackerLogger(os.path.basename(__file__))

module_dir = os.path.dirname(__file__)
prompt_path = os.path.join(module_dir, "prompts")


class CVAnalysisModel:
    """
    A class that represents an Auto Apply Model for job applications.

    Args:
        api_key (str): The OpenAI API key.
        downloads_dir (str, optional): The directory to save downloaded files. Defaults to the default download folder.

    Attributes:
        api_key (str): The OpenAI API key.
        downloads_dir (str): The directory to save downloaded files.

    """

    def __init__(
        self, api_key: str = config.openai.api_key, 
        provider: str = "openai", 
        downloads_dir: str = get_default_download_folder(),
        output_dir: str = get_default_output_folder(),
        google_drive: bool = True,        
        s3bucket: str = config.s3.zlm_bucket,
    ):

        self.s3bucket = s3bucket
        
        
        #
        if provider is None or provider.strip() == "":
            self.provider = "openai"
        else:
            self.provider = provider

        if api_key is None or api_key.strip() == "os":
            if provider == "openai":
                self.api_key = os.environ.get("OPENAI_API_KEY")
            elif provider == "together":
                self.api_key = os.environ.get("TOGETHER_KEY")
            elif provider == "gemini":
                self.api_key = os.environ.get("GEMINI_API_KEY")
        else:
            self.api_key = api_key

        if downloads_dir is None or downloads_dir.strip() == "":
            self.downloads_dir = get_default_download_folder()
        else:
            self.downloads_dir = downloads_dir
            
        if output_dir is None or output_dir.strip() == "":
            self.output_dir = get_default_output_folder()
        else:
            self.output_dir = output_dir
            

    
    def get_llm_instance(self, system_prompt, easy=False, powerful=False, chat_model=None):
        if self.provider == "openai":
            if not chat_model:
                if easy:
                    chat_model = config.openai.cheap_model
                elif powerful:
                    chat_model = config.openai.powerful_model
                else:
                    chat_model = config.openai.model
                    
            return ChatGPT(api_key=self.api_key, system_prompt=system_prompt, chat_model=chat_model)
        elif self.provider == "together":
            return TogetherAI(api_key=self.api_key, system_prompt=system_prompt)
        elif self.provider == "gemini":
            return Gemini(api_key=self.api_key, system_prompt=system_prompt)
        else:
            raise Exception("Invalid LLM Provider")
            
    # Define a function to perform similarity search between user and job description
    def find_similar_points(self, user_embeddings, job_embeddings):
            try:
                relevant_points = set()
                for embedding in job_embeddings['embedding']:
                    dot_products = np.dot(np.stack(user_embeddings['embedding']), embedding)
                    idx = np.argmax(dot_products)
                    relevant_points.add(user_embeddings.iloc[idx]['chunk'])
                
                return relevant_points
            except Exception as e:      
                logger.error(f"Error: {e}")
                return None


    
    @measure_execution_time
    async def prepare_resume_sfia_analysis(self, pdf_path, overwrite=False):
 
        # Default Values to return
        is_resume_or_cv = False
        target_sfia = {}
        analysis = {}
        default_return = {'is_resume_or_cv': is_resume_or_cv,
                          'resume_text': '',
                          'resume_cache_id': '',
                          'status': 200,
                          'target_sfia': target_sfia,
                          'analysis': analysis,
                          'message': ''
                          }
        
        # Extract Text from Resume
        try:
            resume_text, first_page = extract_text(pdf_path, 
                                                   max_pages=3, 
                                                   return_first_page=True)                                                
        except Exception as e:
            print(e)
            logger.error(f"Error in extracting text from resume.")
            default_return['status'] = 400
            default_return['message'] = 'Error in extracting text from resume.'
            return default_return
        
        if resume_text:
            job_hash = config.shash(resume_text)
            default_return['resume_cache_path'] = f"cv_analysis/{job_hash}"
            default_return['resume_text'] = resume_text
            default_return['is_resume_or_cv'] = True
        else:
            logger.error(f"Resume text is empty.")
            default_return['is_resume_or_cv'] = False
            default_return['message'] = 'Resume text is empty.'
            return default_return

        if overwrite:
            logger.info(f"Overwrite is true: Not checking if result exists in S3.")        
                
        # Check if Agent Analysis JSON exists in S3        
        try:
            if not overwrite:                
                local_path = config.temp_path('agent_analysis.json')
                remote_path = f"cv_analysis/{job_hash}/agent_analysis.json"
                
                if s3utils.file_exists_in_s3(self.s3bucket, remote_path) and not overwrite:
                    logger.good(f"Agent Analysis JSON already exists in S3: {remote_path}")                
                    try:
                        analysis = s3utils.read_text_file_from_s3(self.s3bucket, remote_path)
                        if not isinstance(analysis, dict):
                            analysis = json.loads(analysis)
                            default_return['analysis'] = analysis                        
                            default_return['is_resume_or_cv'] = True
                    except Exception as e:
                        print(e)
                        logger.error(f"Error in loading Agent Analysis JSON.")
                        default_return['message'] = 'Error in loading Agent Analysis JSON'
        except Exception as e:
            print(e)
            logger.error(f"Error in checking if Agent Analysis JSON exists in S3.")
            
            
        # return if analysis is not empty
        if default_return['analysis']:
            return default_return
        
        
        # Check if Target SFIA JSON exists in S3
        try:       
            if not overwrite:             
                job_hash = config.shash(resume_text)
                local_path = config.temp_path('target_sfia.json')
                remote_path = f"cv_analysis/{job_hash}/target_sfia.json"
                
                
                if s3utils.file_exists_in_s3(self.s3bucket, remote_path) and not overwrite:
                    logger.good(f"Target SFIA JSON already exists in S3: {remote_path}")                
                    try:
                        target_sfia = s3utils.read_text_file_from_s3(self.s3bucket, remote_path)
                        target_sfia = extract_json(target_sfia)
                        default_return['target_sfia'] = target_sfia
                        default_return['is_resume_or_cv'] = True
                    except Exception as e:
                        print(e)
                        logger.error(f"Error in loading target SFIA JSON.")                                                                   
        except Exception as e:
            print(e)
            logger.error(f"Error in checking if Target SFIA JSON exists in S3.")
            
        # return
        if target_sfia:
            return default_return
        
        # Here means that the target_sfia is empty    
        try:
            # Get Target SFIA Values
            if not first_page:
                first_page = resume_text
                
            # determine if the text is a resume or cv like
            iscv_prompt = get_prompt(
                    os.path.join(prompt_path, 'hragent/iscv_prompt.txt')  
            ).replace("[Insert extracted text here]", first_page)
            llm = self.get_llm_instance(iscv_prompt, easy=True)
            output = llm.get_response(resume_text, need_json_output=True) 
            is_resume_or_cv = extract_json(output).get('is_resume_or_cv', True)
            default_return['is_resume_or_cv'] = is_resume_or_cv
            
            if not is_resume_or_cv:
                default_return['message'] = 'PDF IS NOT a resume or cv!'
                logger.warn(f"PDF is not a resume or cv.")                    
            else:
                default_return['message'] = 'PDF IS a resume or cv!'
                logger.good(f"PDF is a resume or cv!")    
                                        
        except Exception as e:
            print(e)
            logger.error(f"Error in determining if the text is a resume or cv.")
            default_return['message'] = "Error in determining if the text is a resume or cv."
            default_return['status'] = 400                             
            
        return default_return
                              
    @measure_execution_time
    async def resume_sfia_analysis(self, resume_text, target_sfia={}):
        """
        Converts a resume in PDF format to JSON format.

        Args:
            pdf_path (str): The path to the PDF file.

        Returns:
            dict: The resume data in JSON format.
        """
        
        
        the_cv_agent = cv_agents()
        analysis = {}
        
        # Get all values
        try:
            competency_holder, _, system_prompt = competency.sfia_values()
            # print('==========1. SFIA SKILL System Prompt==========')
            # print(system_prompt)
            # print('==========1. END==========')
        except Exception as e:
            print(e)
            logger.error(f"Error in getting competency holder and system prompt.")
            raise
         
        # Compute SFIA Values
        if not target_sfia:
            try:
                job_hash = config.shash(resume_text)
                local_path = config.temp_path('target_sfia.json')
                remote_path = f"cv_analysis/{job_hash}/target_sfia.json"
                        
                #                            
                # now get the target sfia values
                llm = self.get_llm_instance(system_prompt)            
                target_sfia = llm.get_response(resume_text, need_json_output=True)               
                    
                # Save to S3
                if target_sfia:
                    logger.info(f"Saving Target SFIA JSON to S3: {remote_path} ..")
                    write_json(local_path, target_sfia)                   
                    s3utils.upload_file_to_s3(local_path, remote_path, self.s3bucket, isfile=True) 
                    logger.good(f"Target SFIA JSON successfully saved to S3: {remote_path}")    
                                                            
            except Exception as e:
                print(e)
                logger.error(f"Error in getting target SFIA values from LLM.")

        # Exit if target_sfia is empty
        if not target_sfia:
            logger.error(f"Target SFIA values are empty.")            
            return analysis
        
        # Get Competency Values
        try:
            output = competency.get_competency(competency_holder, target_sfia)    
            target_competency, consensus_competency, difference_competency = output
        except Exception as e:
            print(e)
            logger.error(f"Error in getting competency values.")
            raise
            
                    
        # Get Competency Analysis
        try:
            job_hash = config.shash(resume_text)
            local_path = config.temp_path('agent_analysis.json')
            remote_path = f"cv_analysis/{job_hash}/agent_analysis.json"
                            
            message = get_prompt(
                    os.path.join(prompt_path, 'hragent/cv_alumni_analysis_msg.txt')  
            )   
                        
            user_message = (str(message)
                        .replace("{cv}", resume_text)
                        .replace("{target_competency}", str(target_competency))
                        .replace("{difference_competency}", str(difference_competency))
                        .replace("{consensus_competency}", str(consensus_competency))
            )

            agent_message = get_prompt(
                    os.path.join(prompt_path, 'hragent/cv_alumni_agent.txt')  
            ) 
        
            logger.good('Updating system message ...', fg='blue')
            the_cv_agent.assistant.update_system_message(agent_message)
            
            logger.good('Sending message to CV Analyser ...', fg='blue')
            response = await the_cv_agent.send_message_cvanalyser(user_message)        
        
            logger.good('Parsing response ...', fg='blue')
            try:
                response = extract_json(response)
            except Exception as e:
                print(response)
                logger.error(f"Error in parsing response: {e}")
                raise

            logger.good('Extracting track competency ...', fg='blue')
            analysis = competency.extract_track_competency(response, 
                                                            target_competency,
                                                            consensus_competency)
            logger.good('Agent completed Analysis!')
            #print(json.dumps(analysis, indent=4))
            
            # Save to S3
            logger.info(f"Saving Agent Analysis JSON to S3: {remote_path} ..")
            write_json(local_path, analysis)                   
            s3utils.upload_file_to_s3(local_path, remote_path, self.s3bucket, isfile=True) 
            logger.good(f"Agent Analysis JSON successfully saved to S3: {remote_path}")                                                                 
        except Exception as e:
            print(e)
            logger.error(f"Error in getting competency values.")
            raise
        
        return analysis    