from math import e
import os, sys
import openai
import base64

import time
import copy
import json

from collections import deque

#
import api.config as config
from .pyprompts import system_messages_general as smg
import api.llm.utils.token_counter as tcount
from api.llm.utils.llm_parse import extract_json
from  api.services import redis_client as rc
from api.utils.logger import LLPackerLogger


logger = LLPackerLogger(os.path.basename(__file__))


def openai_summarise(text, **kwargs):
    temperature = kwargs.pop("temperature", 0)
    max_tokens = kwargs.pop("max_tokens", 1000)
    system_message = kwargs.pop("system_message", smg.get_summary_prompt_prefix(**kwargs))
    question = kwargs.pop("question", "Summary of the following document:")
    message = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"{question} \n {text}"}
            ]
    
    client = openai.OpenAI(api_key=config.openai.api_key)  
    response = client.chat.completions.create(
        model=config.openai.model,
        temperature=temperature,        
        messages=message,
        max_tokens=max_tokens,
        **kwargs
    )

    return response.choices[0].message.content

def summarise_long_text(text, 
                        model=config.openai.model, 
                        max_characters=0,
                        max_tokens=config.openai.max_tokens-1000):

    # requested summary based on character length
    if max_characters > 0:
        iloop = 1
        c2t = 5
        chunk_summary = text
        while len(chunk_summary) <= max_characters:
            chunk_summary = openai_summarise(text, 
                                             model=model, 
                                             max_tokens=max_characters//c2t)
            
            # break if we have looped more than 3 times
            if iloop > 3:
                break
            
            # increase character to token ratio
            c2t += iloop
            iloop += 1
                    
        return chunk_summary, len(chunk_summary)
        
    # requested summary based on token length
    chunk_summary = []
    chunk_summary_lens = [] 
    
    # split text into chunks of max_tokens
    chunks_list = list(tcount.chunked_tokens(text, chunk_length=max_tokens, model=model))
    
    # if text is less than max_tokens, then return text
    if len(chunks_list) < 2:
        return text, len(text)
    
    # summarise each chunk
    for chunk in chunks_list:
        chunk_summary = openai_summarise(chunk, model=model)
        chunk_summary.append(chunk_summary)
        chunk_summary_lens.append(len(chunk_summary))

    return ' \n '.join(chunk_summary), chunk_summary_lens

def get_openai_response(functions, messages, **kwargs):
    temperature = kwargs.pop("temperature", 0)    
    client = openai.OpenAI(api_key=config.openai.api_key)  
    return client.chat.completions.create(
        model=config.openai.model,
        tools=functions,
        tool_choice="auto",  # "auto" means the model can pick between generating a message or calling a function.
        temperature=temperature,        
        messages=messages,
        **kwargs
    )


class OpenAiBase:
    def __init__(self, **kwargs) -> None:   #this is a mixin class
        
        self.message = []

        api_key = kwargs.get('api_key', config.openai.api_key)
        
        #self.llm = LLMInteraction(api_key=config.openai.api_key)
        self.client = openai.OpenAI(api_key=config.openai.api_key)
        self.model = config.openai.model
        self.temperature = config.openai.temperature
        self.max_tokens = config.openai.max_tokens

        # Create a queue
        self.run_queue = deque()  #insert (thread, run) tuple
        self.fileid_queue = deque() #insert (file_ids, metadata) tuple
        self.vectorstoreid_queue = deque() # insert (vectorstore_ids, metadata) tuple
        self.associated_fileid_queue = deque()
        self.content_queue = deque() #insert (content, metadata) tuple
        self.message_queue = deque() #insert (prompt, metadata) tuple
        self.result_queue = deque() #insert (result, metadata) tuple

        
        # get the current directory
        self.curdir = os.path.dirname(os.path.realpath(__file__))
        self.cpath = os.path.dirname(self.curdir)

    def clear_all_queues(self):
        self.run_queue.clear()
        self.fileid_queue.clear()
        self.vectorstoreid_queue.clear()
        self.associated_fileid_queue.clear()
        self.content_queue.clear()
        self.message_queue.clear()
        self.result_queue.clear()

    def clear_input_data_queues(self):
        self.fileid_queue.clear()
        self.vectorstoreid_queue.clear()
        self.associated_fileid_queue.clear()
        self.content_queue.clear()
        self.message_queue.clear()

    def add_grade_result_to_queue(self, grade, feedback, metadata):
        self.result_queue.append((grade, feedback, metadata))

    def add_run_to_queue(self, thread, run, metadata, call_counter):
        self.run_queue.append((thread, run, metadata, call_counter))

    def add_fileid_to_queue(self, file_ids, metadata, associated=False):
        if associated:
            self.associated_fileid_queue.append((file_ids, metadata))
        else:
            self.fileid_queue.append((file_ids, metadata))
            
    def add_vectorstoreid_to_queue(self, vectorstore_ids, metadata, associated=False):
            self.vectorstoreid_queue.append((vectorstore_ids, metadata))

    def add_message_to_queue(self, messages, metadata):
        self.message_queue.append((messages, metadata))

    def add_content_to_queue(self, content, metadata):
        total_tokens = tcount.count_token(content, model=config.openai.model, count=True)
        self.content_queue.append((content, metadata, total_tokens))

            
    def get_openai_response_content(self, result):
        try:
            try: #if isinstance(result, openai.openai_object.OpenAIObject):
                result_str = result.choices[0].message.content
                return result_str
            except:
                return "Output type error"
            
        except openai.APIResponseError as e:
            logger.log_error(function_name= "check_for_result_type", 
                             returned_info=f" Error occurred: {str(e)}",
                             error_type="APIResponseError", 
                             action= "failed")
            return "Output type error"
                
    def get_image_summary(self, base64_images, text="", 
                          max_tokens=600, 
                          model=config.openai.vision_model):
        content = []
        if len(text) == 0:            
            text = '''
            You are a helpful AI assistant tasked with summarising figure, plot, diagram, etc. images. These images are extracted from a report, blog, presentation slide or other similar documents. You are asked to summarise the content of the images. Describe the type, intent, and relevant components of the images such that your summary sufficiently captures the KEY INFORMATION and IMPORTANT DETAILS of the images. Please Return the summary of the images as follows 

            Summary of image 1.:
            The image shows a plot of x and y. The x-axis shows the time in seconds and the y-axis shows the temperature in degree Celsius.
            
            Summary: Summary of image 2.:
            The image shows a work flow diagram. The details of the work flow are as follows.

            Please now summarise the following images following the above guideline and examples.:
            '''
        
        logger.info('adding text and image to message ...')
        message = self.add_message("user", 
                                   content, 
                                   text=text,
                                   image=base64_images)
        
        payload = {
                "model": model,
                "messages": message,   
                "max_tokens": max_tokens    
        }
        response = self.client.chat.completions.create(**payload)
        image_summary = self.get_openai_response_content(response)
        
        return image_summary  
        
    def create_message(self, role, content, **kwargs):

        self.message = [{
            "role": role,
            "content": content,
        }]

        return self.message

    def add_message(self, role: str, contentIn: [str, list], **kwargs):

        content = copy.deepcopy(contentIn)

        if self.message is None:
            self.message = []

        if isinstance(content, str):
            # convert string to list of dict
            content = self.add_text_to_content([], kwargs.get('text'))

        if 'text' in kwargs:
            # convert string to list of dict
            content = self.add_text_to_content(content, kwargs.get('text'))

        if 'image' in kwargs:
            image = kwargs.get('image')
            content = self.add_image_to_content(content, image)

        if 'file_ids' in kwargs:
            file_ids = kwargs.get('file_ids')
            self.message = self.add_file_and_content_to_message(content, file_ids)
        else:
            self.message.append({
                "role": role,
                "content": content,
            })

        return self.message

    def add_system_message(self, content, **kwargs):
        return self.add_message("system", content, **kwargs)
        
    def add_user_message(self, content, **kwargs):
        return self.add_message("user", content, **kwargs)     

    def add_assistant_message(self, content, **kwargs):
        return self.add_message("assistant", content, **kwargs)            
    
    def add_file_and_content_to_message(self, content, file_ids, **kwargs):
        self.message.append({
            "role": "user",
            "content": content,
            "file_ids": self.file_ids
        })

        return self.message
    
    def add_text_to_content(self, content, text, **kwargs):
        content.append({
                        "type": "text", 
                        "text": text
        })

        return content

    def add_image_to_content(self, content, images, detail='auto', **kwargs):
            
        if detail not in ['auto', 'low', 'medium', 'high']:
            detail = 'auto'

        if content is None:
            content = []

        if not isinstance(images, list):
            images = [images]
        
        for image in images:

            # Explicitly checking if 'image' is a string and starts with 'http'
            if isinstance(image, str) and image.startswith('http'):
                islink = True
            else:
                islink = False

            if not islink:
                # This block is for non-URLs which we assume to be base64 encoded images
                logger.info('add_image_to_content: adding base64 image to message ...')     
                content.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image}","detail": detail},
                })
            else:
                # This block is for URLs            
                content.append({
                    "type": "image_url",
                    "image_url": {"url": image, "detail": detail},
                })
        return content


    def add_text_image_to_content(self, content, text, images, detail='auto',**kwargs):
        if detail not in ['auto', 'low', 'medium', 'high']:
            detail = 'auto'

        if content is None:
            content = []

        # Add the text content first
        content.append({
            "type": "text",
            "text": text
        })

        if not isinstance(images, list):
            images = [images]
        
        for image in images:
            # Explicitly checking if 'image' is a string and starts with 'http'
            if isinstance(image, str) and image.startswith('http'):
                islink = True
            else:
                islink = False

            if islink:
                # This block is for URLs            
                content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": image,
                        "detail": detail
                    }
                })
            else:
                # This block is for base64 encoded images
                logger.info('add_image_to_content: uploading image to get file ID...')
                
                # Decode the base64 image to a binary format
                image_data = base64.b64decode(image)
                
                # Save the decoded image to a temporary file
                temp_image_path = "temp_image.jpg"
                with open(temp_image_path, "wb") as temp_file:
                    temp_file.write(image_data)
                
                # Upload the file to get the file ID
                file = self.client.files.create(
                    file=open(temp_image_path, "rb"),
                    purpose="vision"
                )
                
                # Remove the temporary file after uploading
                os.remove(temp_image_path)
                
                content.append({
                    "type": "image_file",
                    "image_file": {
                        "file_id": file.id
                    }
                })

        return content


    def create_prompt(self, content, 
                      template="<content>", 
                      var="<content>", 
                      **kwargs):
            
        prompt = template.replace(var, content)
        total_tokens = tcount.count_token(prompt, model=config.openai.model, count=True)
        below_max_tokens = total_tokens < config.openai.max_tokens-100

        return prompt, total_tokens, below_max_tokens        


class OpenAiAssistantApi(OpenAiBase):  #this is a mixin class no positional arguments in the constructor
    def __init__(self, 
                 assistant_name="", 
                 prompt_prefix="", 
                 system_message="",
                 tools=None,  #{"type": "code_interpreter"} {"type": "retrieval"}
                 **kwargs) -> None:
        '''
        Initialize the API response object

        Args:
            assistant_name (str): The name of the assistant.
            tools (list): The list of tools to enable for the assistant.
            kwargs:
                Could be for OpenAI RUN Request body
                    assistant_id
                    The ID of the assistant to use to execute this run.

                    [model]
                    The ID of the Model to be used to execute this run. If a value is provided here, it will override the model associated with the assistant. If not, the model associated with the assistant will be used.

                    [instructions]
                    Overrides the instructions of the assistant. This is useful for modifying the behavior on a per-run basis.

                    [additional_instructions]
                    Appends additional instructions at the end of the instructions for the run. This is useful for modifying the behavior on a per-run basis without overriding other instructions.

                    [tools]
                    Override the tools the assistant can use for this run. This is useful for modifying the behavior on a per-run basis.            
        

        '''

        super().__init__(**kwargs)


        self.prompt_prefix = prompt_prefix  # used to add prefix to the user questions (prompt)
        self.system_message = system_message # only useful to create new assistant
        
        
        # load or create OpenAI Assistant 
        self.assistant = self.get_assistant_by_name(assistant_name, tools=tools)  

        
        #_ = self.delete_assistant_files(nkeep=0)

    def get_assistant_by_id(self, assistant_id):
        return self.client.beta.assistants.retrieve(assistant_id)
    
    def get_assistant_by_name(self, assistant_name, tools=None):
        # # load or create the Assistant with the uploaded file.


        assistant = None
        try:       
            has_more = True
            while has_more:     
                my_assistants = self.client.beta.assistants.list(
                    order="desc",
                    limit="100",
                )  
                for a in my_assistants.data:
                    if a.name == assistant_name:
                        assistant = a
                        has_more = False
                        break
                    else:
                        has_more = my_assistants.has_more
                        continue
        except Exception as err:
            print(err)

        if assistant is None:        
            #sm = self.system_message                
            assistant = self.client.beta.assistants.create(
                    name=assistant_name,
                    description='provide a fair, helpful, and action oriented evaliation and feedback',
                    model=self.model,
                    tools=tools
                    )
            logger.good(f"Created new OpenAI Assistant API with name={assistant_name} ..")
        else:
            logger.good(f"Loaded existing OpenAI Assistant API with name={assistant_name} ..")

        return assistant


    def get_associated_file_ids(self, **kwargs):
        '''
        API Ref: 
        https://beta.openai.com/docs/api-reference/assistants/listFiles?lang=python
        '''
        try:
            assistant_files = self.client.beta.assistants.files.list(
                assistant_id=self.assistant.id,
                **kwargs
            )

            # sort by created_at
            res = sorted(assistant_files.data, 
                        key=lambda d: d.created_at, 
                        reverse=True)
                        
            return res
        except Exception as err:
            logger.warn(f"File retrieval from OpenAI Assistant API failed with error={err}")
            return None
        
    def check_file_uploaded(self, fname, **kwargs):    
        '''
        Call this function to check if the file already exists in the assistant
        '''    
        
        res = self.client.files.list()

        
        #check if file already exists
        for f in res.data:
            if f.filename == fname:
                return f.id

        return None
            
                        
    def delete_assistant_files(self, nkeep=18): 
        '''
        Delete older file_ids associated to to OpenAi assistant 
        
        Note: only max of 20 files can be associated to a single assistant
        '''
        
        try:
            # get thesorted list of files associated to the assistant
            assistant_files_data = self.get_associated_file_ids()

            if len(assistant_files_data) > nkeep:
                for f in assistant_files_data[nkeep:]:
                    self.client.beta.assistants.files.delete(assistant_id=self.assistant.id,
                                                            file_id=f.id
                                                            ) 
        except Exception as err:
            print(err)
            logger.warn(f"File deletion from OpenAI Assistant API failed with error={err}")


    def create_localfile_from_content(self, content, fname, isbyte=False):
        '''
        Supported formats:                         
            [\'c\', \'cpp\', \'csv\',                          
            \'docx\', \'html\',                                
            \'java\', \'json\', \'md\',                        
            \'pdf\', \'php\', \'pptx\',                        
            \'py\', \'rb\', \'tex\',                           
            \'txt\', \'css\', \'jpeg\',                        
            \'jpg\', \'js\', \'gif\',                          
            \'png\', \'tar\', \'ts\',                          
            \'xlsx\', \'xml\',                                 
            \'zip\']        
        '''

        
        if isbyte:
            with open(fname, "wb") as f:
                f.write(content.getvalue())
        else:
            with open(fname, "wt") as f:
                f.write(content)                    

        return fname
    
    def check_vectors_stored(self,file_path, **kwargs):

        res = self.client.beta.vector_stores.list()

        for f in res.data:
            if f.name == file_path:
                return f.id
        return None
    
    def upload_file_to_vector_store(self,file_path, **kwargs):
        try:
            vector_store_id = self.check_vectors_stored(file_path)
            if vector_store_id is None:
                vector_store = self.client.beta.vector_stores.create(name=file_path)   
                if isinstance(file_path, list):
                    file_streams = [open(path, "rb") for path in file_path]
                else:
                    file_streams = [open(file_path, "rb")]
            
                file_batch = self.client.beta.vector_stores.file_batches.upload_and_poll(
                vector_store_id=vector_store.id, files=file_streams
                )
            print(file_batch.status)
            print(file_batch.file_counts)
            return vector_store.id
        except Exception as err:
            logger.warn(f"File upload to OpenAI vecor store failed with error={err}")
            return None


    def upload_file_to_openai(self, file_path):
        '''
        Upload and Associate files to openai assistant
        '''
        try:
            file_id = self.check_file_uploaded(file_path)
            if file_id is None:
                with open(file_path, 'rb') as file:
                    # Upload a file to OpenAI files
                    logger.info(f"Uploading file={file_path} to OpenAI Assistant API ..")
                    uploaded_file = self.client.files.create(file=file, 
                                                            purpose='assistants')
                    file_id = uploaded_file.id
        
            return file_id
        
        except Exception as err:
            logger.warn(f"File upload to OpenAI Assistant API failed with error={err}")
            return None
        
    def upload_content_queue(self, mkey='id', ext='txt', **kwargs):
        '''
        Upload and Associate files to OpenAI assistant

        Args:
            self.content_queue: list of (filename/content, metadata) to upload

        Returns:
            file_ids: list of (file_id, metadata) associated to the assistant
        '''
        
        qsize = len(self.content_queue)
        logger.info(f"Uploading {qsize} content to message queue or OpenAI fileid queue...")

        iloop = 1
        while self.content_queue:
            # Process items in content queue
            content, metadata, ntoken = self.content_queue.popleft()            
            sid = metadata.get(mkey)
            payload = metadata.get('payload', {})
            document_format = payload.get('document_format', 
                                          metadata.get('document_format', 'text'))
            
            print("document_format",document_format)
            file_name = None
            file_id = None

            if document_format=='pdf':
                logger.error('pdf format not supported')
                raise Exception('pdf format not supported')
                
            
            try:
                file_name = config.random_file_name(ext=ext, prefix=sid, content=content)
            except Exception as err:
                print(f'Unknown document format: document_format={document_format}')
                print('Content:', content)
                logger.warn(f"File creation failed with error={err}")
                continue


            if file_name:
                file_id = self.upload_file_to_openai(file_name)
                if file_id is not None:
                    self.add_fileid_to_queue(file_id, metadata)
            
            iloop += 1

        logger.info(f"Upload content queue while loop ended! Remaining content queue: {len(self.content_queue)}")
        logger.good(f"Uploaded {len(self.fileid_queue)} files and created {len(self.message_queue)} messages!")

        return self.fileid_queue, self.message_queue



    def associate_fileid_queue(self, **kwargs):
        '''
        Associate files to openai assistant
        '''

        # no need to associate fileid to assistent as we need the file only for the current run 
        ## When a file is attached at the Message-level, it is only accessible within the specific Thread the Message is attached to.
        for file_id, metadata in self.fileid_queue:
             self.add_fileid_to_queue(file_id, metadata, associated=True)


        

        # fileid_queue = copy.deepcopy(self.fileid_queue)
        # # Associate files to openai assistant
        # while len(fileid_queue) > 0:
        #     logger.info(f"Associating {len(fileid_queue)} files to OpenAI Assistant API ..")
        #     file_id, metadata = fileid_queue.popleft()
        #     if file_id:
        #         try:                    
        #             _ = self.client.beta.assistants.files.create(
        #                                                     assistant_id=self.assistant_id, 
        #                                                     file_id=file_id
        #                                                     )
        #             self.add_fileid_to_queue(file_id, metadata, associated=True)
        #         except Exception as err:
        #             logger.warn(f"File upload to OpenAI Assistant API failed with error={err}")
        #     else:
        #         logger.warn(f"No file (content is empty) is uploaded to OpenAI Assistant API!")

        logger.good(f'Associated {len(self.associated_fileid_queue)} submissions to openai!') 

        return self.associated_fileid_queue
        
    def extract_run_metadata(self, metadata):
        return {k:metadata.get(k) for k in config.get_openai_run_metadata_keys() if k in metadata}

    def extract_run_kwargs(self, kwargs):
        res = {k:kwargs.get(k) for k in config.get_openai_run_keys() if k in kwargs}
        return res
                
    def run_assistant(self, thread, metadata={}, **kwargs):
        '''
        kwargs:
            Could be for OpenAI RUN Request body
                assistant_id
                The ID of the assistant to use to execute this run.

                [model]
                The ID of the Model to be used to execute this run. If a value is provided here, it will override the model associated with the assistant. If not, the model associated with the assistant will be used.

                [instructions]
                Overrides the instructions of the assistant. This is useful for modifying the behavior on a per-run basis.

                [additional_instructions]
                Appends additional instructions at the end of the instructions for the run. This is useful for modifying the behavior on a per-run basis without overriding other instructions.

                [tools]
                Override the tools the assistant can use for this run. This is useful for modifying the behavior on a per-run basis.    

                [metadata]
                Set of 16 key-value pairs that can be attached to an object. This can be useful for storing additional information about the object in a structured format. Keys can be a maximum of 64 characters long and values can be a maxium of 512 characters long.
        '''
        
        # Extract the run parameters
        run_kwargs = self.extract_run_kwargs(kwargs)
        if not metadata:
            metadata = self.extract_run_metadata(kwargs)

        # Run the Assistant
        run = self.client.beta.threads.runs.create(
                                                    thread_id=thread.id,
                                                    assistant_id=self.assistant.id,
                                                    metadata=metadata,
                                                    **run_kwargs 
                                                )
        return run   
         
    def run_assistant_and_wait(self, thread, **kwargs):
        '''
        API Ref:
        https://platform.openai.com/docs/api-reference/runs/object?lang=python
        
        The status of the run, which can be either queued, in_progress, requires_action, cancelling, cancelled, failed, completed, or expired.        
        '''
        run = self.run_assistant(thread, **kwargs)

        return self.wait_on_run(thread, run)
    
            
    def cancel_all_runs(self, thread_id):
        runs = self.client.beta.threads.runs.list(thread_id)
        for r in runs:
            r = self.client.beta.threads.runs.cancel(
                                                thread_id=thread_id,
                                                run_id=r.id
                                                ) 
                    
    def delete_thread(self, thread_id):
        _ = self.cancel_all_runs(thread_id)
        response = self.client.beta.threads.delete(thread_id)
        return response  
    
    def delete_vector_store(self,thread):
            vector_store_id = thread.tool_resources.file_search.vector_store_ids[0]
            deleted_vector_store = self.client.beta.vector_stores.delete(
            vector_store_id= vector_store_id
            )
            logger.good(f"VectorStoreDeleted(id='{vector_store_id}', deleted={deleted_vector_store})") #print(deleted_vector_store)
            return deleted_vector_store
        
    def wait_on_run(self, thread, run):
        while run.status == "queued" or run.status == "in_progress":
            run = self.client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id,
            )
            time.sleep(5)
        return run
            
    def wait_run_queue_without_tools(self, **kwargs):
                
        while len(self.run_queue) > 0:
            logger.info(f"Waiting {len(self.run_queue)} OpenAI threads and runs to finish  ..")

            (thread, run, metadata, call_counter) = self.run_queue.popleft()
            if isinstance(run, str):
                logger.info(f"Not waiting for run as it is a string: {run}", fg='pink')
            else:
                run = self.wait_on_run(thread, run)
            if isinstance(thread, str):
                logger.info(f"Get last message from already existing thread with thread_id={thread}", fg='pink')
                output = self.get_run_messages(thread, key='last')
            else:                
                output = self.get_run_messages(thread.id, key='last')
                
            if kwargs.get('json_response', False):
                try:
                    output = extract_json(output)
                except:
                    logger.warn(f"Failed to extract json from output for metadata: {metadata}")
                
            self.result_queue.append((output, metadata))
            
        if len(self.result_queue) == 0:
            logger.warn(f"No thread and run created on OpenAI Assistant API!")
          
        return self.result_queue

    def create_and_run_thread(self, messages, metadata={}, tools=None, **kwargs):
        '''
        kwargs is parameters for run
        Request body
            assistant_id
            The ID of the assistant to use to execute this run.

            [model]
            The ID of the Model to be used to execute this run. If a value is provided here, it will override the model associated with the assistant. If not, the model associated with the assistant will be used.

            [instructions]
            Overrides the instructions of the assistant. This is useful for modifying the behavior on a per-run basis.

            [additional_instructions]
            Appends additional instructions at the end of the instructions for the run. This is useful for modifying the behavior on a per-run basis without overriding other instructions.

            [tools]
            Override the tools the assistant can use for this run. This is useful for modifying the behavior on a per-run basis.
        '''
        # Create a Thread with an initial list of Messages 
        # https://beta.openai.com/docs/api-reference/threads/create
                
        
        thread = self.client.beta.threads.create(messages=messages, 
                                                 metadata=metadata)  
        
        # if there are any runs, cancel them 
        _ = self.cancel_all_runs(thread.id)

        # Run the Assistant
        run = self.run_assistant(thread, 
                                 tools=tools, 
                                 metadata=metadata, 
                                 **kwargs)          

        return thread, run                    

    def get_thread_run_ids_from_redis(self, redis_client, metadata):
        tid = ""
        rid = ""
        if redis_client:
            try:
                tid, rid = redis_client.get_openai_thread_run_ids(metadata)
            except:
                pass
        
            
        if tid and rid:
            r = rid
            t = tid
        else:
            t = None
            r = None
            
        return t, r
                        
    def ask_with_fileids(self, question, metadata={}, file_ids=[], tools=None, redis_client=None, **kwargs):

        if self.prompt_prefix:
            content = self.prompt_prefix + " \n " + question
        else:
            content = question

        if isinstance(file_ids, str):
            file_ids = [file_ids]
        
        if not isinstance(file_ids, list):            
            file_ids = []
            logger.error(f"File_ids must be a list of file_ids but got {file_ids} ..")
        if file_ids:
                attachement = []
                for file_id in file_ids:
                    v = {"file_id": file_id, 'tools':['file_search', 'code-interpreter']}
                    attachement.append(v)
        if tools is None:
            tools = [{"type": "file_search"}, {"type": "code_interpreter"}]
        else:
            for item in [{"type": "retrieval"}, {"type": "code_interpreter"}]:
                if item not in tools:
                    tools.append(item)

        messages=[
                {
                    "role": "user",
                    "content": content,
                    "attachments": attachement
                }               
            ]  
        t, r = self.create_and_run_thread(messages,  
                                          metadata=self.extract_run_metadata(metadata), 
                                          tools=tools, 
                                          **kwargs)
        self.add_run_to_queue(t, r, metadata, 1)

        return self.run_queue

    def ask_with_vectorstoreids(self, question, metadata={},tools=None, redis_client=None, **kwargs):

        if self.prompt_prefix:
            content = self.prompt_prefix + " \n " + question
        else:
            content = question

        for vectorstore_id, metadata in self.vectorstoreid_queue:
            if isinstance(vectorstore_id, list):
                vectorstore_id = vectorstore_id
            else:
                vectorstore_id = [vectorstore_id]

            messages=[
                {
                    "role": "user",
                    "content": content,
                }               
            ]        
            tool_resources={
                            "file_search": {
                            "vector_store_ids": vectorstore_id
                            }
                        }     
            
            
            t, r = None, None
            if redis_client:
                try:
                    t, r = self.get_thread_run_ids_from_redis(redis_client, metadata)
                except Exception as e:
                    logger.error(f"Failed to get thread and run ids from redis: {e}")
                
            if t is None or r is None:
                t, r = self.create_and_run_thread(messages, 
                                                metadata=self.extract_run_metadata(metadata), 
                                                tools=tools,
                                                tool_resources=tool_resources, 
                                                **kwargs)
                if redis_client:
                    try:
                        redis_client.set_openai_thread_run_ids(metadata, t.id, r.id)
                    except Exception as e:
                        logger.error(f"Failed to set thread and run ids in redis: {e}")
                     
                                 

            self.add_run_to_queue(t, r, metadata, 1)

        logger.good(f'Started {len(self.associated_fileid_queue)} runs using file in vectorstore!')
        return self.run_queue 

    def ask_per_associated_fileid_queue(self, question, tools=None, redis_client=None, **kwargs):
        if self.prompt_prefix:
            content_text = self.prompt_prefix + " \n " + question
        else:
            content_text = question

        for file_id, metadata in self.associated_fileid_queue:
            if 'image' in metadata:
                images = metadata['image']
                content = self.add_text_image_to_content([], content_text, images)
            else:
                content = [{"type": "text", "text": content_text}]

            if isinstance(file_id, list):
                file_ids = file_id
            else:
                file_ids = [file_id]

            attachments = []
            if file_ids:
                for fid in file_ids:
                    v = {"file_id": fid, 'tools': [{"type": "file_search"}, {"type": "code_interpreter"}]}
                    attachments.append(v)

            if tools is None:
                tools = [{"type": "file_search"}, {"type": "code_interpreter"}]
            else:
                for item in [{"type": "file_search"}, {"type": "code_interpreter"}]:
                    if item not in tools:
                        tools.append(item)
            
            messages = [
                {
                    "role": "user",
                    "content": content,
                    "attachments": attachments
                }
            ]

            # Printing the message content payload
            #print(f"Formatted payload for file ID: {file_id}")
            #print(messages)

            t, r = None, None
            if redis_client:
                try:
                    t, r = self.get_thread_run_ids_from_redis(redis_client, metadata)
                except Exception as e:
                    logger.error(f"Failed to get thread and run ids from redis: {e}")
                
            if t is None or r is None:
                t, r = self.create_and_run_thread(messages, 
                                                metadata=self.extract_run_metadata(metadata), 
                                                tools=tools, 
                                                **kwargs)
                if redis_client:
                    try:
                        redis_client.set_openai_thread_run_ids(metadata, t.id, r.id)
                    except Exception as e:
                        logger.error(f"Failed to set thread and run ids in redis: {e}")
                     
                        
                        

            self.add_run_to_queue(t, r, metadata, 1)

        logger.info(f'Started {len(self.associated_fileid_queue)} runs using files uploaded in OpenAI!')
        return self.run_queue

    def ask_per_message_queue(self, tools=None, redis_client=None, **kwargs):
        for prompt, metadata in self.message_queue:
            if 'images' in metadata:
                text = prompt if isinstance(prompt, str) else " ".join(msg["content"] for msg in prompt if msg["role"] == "user")
                images = metadata['images']
                content = self.add_text_image_to_content([], text, images)
                #print(f"Content: {content}")
                messages = [
                    {
                        "role": "user",
                        "content": content
                    }
                ]
            else:
                messages = [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
                #print(f"Prompt: {prompt}")
            # Printing the message content payload
            #print(f"Formatted payload for prompt: {prompt}")
            #print(messages)

            t, r = None, None
            if redis_client:
                try:
                    logger.info(f"Getting thread and run ids from redis for metadata: {metadata}")
                    t, r = self.get_thread_run_ids_from_redis(redis_client, metadata)
                    logger.info(f"Got thread_id={t} and run=id={r} from redis")
                except Exception as e:
                    logger.error(f"Failed to get thread and run ids from redis: {e}")
            else:
                logger.warn(f"Redis client not provided, skipping getting thread and run ids from redis")
                
            if t is None or r is None:
                t, r = self.create_and_run_thread(messages, 
                                                metadata=self.extract_run_metadata(metadata), 
                                                tools=tools, 
                                                **kwargs)
                if redis_client:
                    try:
                        logger.info(f"Setting thread and run ids in redis for metadata: {metadata}")
                        redis_client.set_openai_thread_run_ids(metadata, t.id, r.id)
                        logger.good(f"Successfuly registered thread_id={t.id} and run=id={r.id} in redis")
                    except Exception as e:
                        logger.error(f"Failed to set thread and run ids in redis: {e}")
                else:
                    logger.warn(f"Redis client not provided, skipping setting thread and run ids in redis")
                        
                
            self.add_run_to_queue(t, r, metadata, 1)

        logger.info(f'Started {len(self.message_queue)} runs from submission contents as prompts!')
        return self.run_queue


    def run_from_content_queue(self, question="", tools=None, redis_client=None, **kwargs):
        '''
        Run the assistant using the content uploaded to openai assistant
        '''

        # Step 1: Upload or prepare content to openai assistant
        mkey = kwargs.pop('mkey', 'id')
        ext = kwargs.pop('ext', 'txt')
        
        fidq = self.upload_content_queue(mkey=mkey, ext=ext, **kwargs)  
      
        # Step 2: Associate files to openai assistant
        afidq = self.associate_fileid_queue()           
            
        # Step 3: Run the assistant for large content that are uploaded as file to assistant
        runq = self.ask_per_associated_fileid_queue(question, 
                                                    tools=tools,  
                                                    redis_client=redis_client,
                                                    **kwargs)
        
        runq = self.ask_with_vectorstoreids(question,
                                                tools=tools,
                                                redis_client=redis_client,
                                                **kwargs)
        
        # Step 4: Run the assistant for small content
        runq = self.ask_per_message_queue(tools=tools, 
                                          redis_client=redis_client,
                                          **kwargs)
        
        logger.good(f'Started {len(runq)} runs in openai ...') 
               
        # now clear all queues except run queue 
        self.clear_input_data_queues()               

        return runq        


    def ask_question(self, thread, question, role='user', wait=True, **kwargs):
        # Create a message object
        '''
        API Ref: 
        https://platform.openai.com/docs/api-reference/messages/listMessages?lang=python
        '''
        message = self.client.beta.threads.messages.create(
            thread_id=thread.id,
            role=role,
            content=question
        )

        if wait:
            return self.wait_on_run(thread, message)
        else:            
            return self.run_assistant(thread, **kwargs)


    def get_run_messages(self, thread_id, key='last',role="role", **kwargs):
        '''
        API Ref:
        https://platform.openai.com/docs/api-reference/messages/listMessages?lang=python
        '''
        messages = self.client.beta.threads.messages.list(
            thread_id=thread_id,
            **kwargs
        )
        # print('-----------------messages-------------------')
        # print(messages.data)
        # print('------------------------------------')

        if key=='last':
            return messages.data[0].content[0].text.value
        elif key=='all':            
            return [x.content[0].text.value for x in messages.data]
        else:
            return messages.data

    def add_footnote(self, message_id, thread_id=None):
        # Retrieve the message object
        message = self.client.beta.threads.messages.retrieve(
                    thread_id=thread_id,
                    message_id=message_id
                )

        # Extract the message content
        message_content = message.content[0].text
        annotations = message_content.annotations
        citations = []

        # Iterate over the annotations and add footnotes
        for index, annotation in enumerate(annotations):
            # Replace the text with a footnote
            message_content.value = message_content.value.replace(annotation.text, f' [{index}]')

            # Gather citations based on annotation attributes
            if (file_citation := getattr(annotation, 'file_citation', None)):
                cited_file = self.client.files.retrieve(file_citation.file_id)
                citations.append(f'[{index}] {file_citation.quote} from {cited_file.filename}')
            elif (file_path := getattr(annotation, 'file_path', None)):
                cited_file = self.client.files.retrieve(file_path.file_id)
                citations.append(f'[{index}] Click <here> to download {cited_file.filename}')
                # Note: File download functionality not implemented above for brevity

        # Add footnotes to the end of the message before displaying to user
        message_content.value += '\n' + '\n'.join(citations)


class RunOnThread():
    '''
    This class is used to run multiple prompts in OpenAI Assistant API on a thread
    '''
    def __init__(self, stype='prompt', use_redis=True, metadata_id_col="", **kwargs):        
        '''
        This function initialises the OpenAi Assistant api.
        '''

        logger.good(f"Initialising OpenAi Assistant api with stype={stype} ...", fg='pink')
        
        #init assistant class
        assistant_name = kwargs.pop('assistant_name', 'tenx_agent')
                                     
        self.llm = OpenAiAssistantApi(assistant_name=assistant_name, **kwargs)

        self.stype = stype
        self.simple = kwargs.get('simple', True)
        self.max_calls = kwargs.get('max_calls', 1)
        
        self.system_message = kwargs.get('system_message', "")
        self.question = kwargs.get('question', "")
        
        
        # init ai function result store - holds the result of each ai function call
        self.require_all_success = kwargs.get('require_all_success', False)
        self.ai_function_result_store = {}
        self.functions_and_tools = []        
        self.tools = kwargs.get('tools', None)
        
        if use_redis and metadata_id_col:
            midcol = metadata_id_col            
            self.rclient = rc.RedisOpenAIAssistentClient(midcol=midcol)
            logger.good(f"Initialised RedisOpenAIAssistentClient with metadata_id_col={midcol}", fg='pink')
        else:
            self.rclient = None            
        
    def _fill_content_queue(self, listobj, listmetadata, **kwargs):       
        '''
        This function is used to fill the content queue for grading
        '''
            
        idvec = range(len(listobj))
        for icm, prompt, metadata in zip(idvec, listobj, listmetadata):   
            _ = self.llm.add_message_to_queue(prompt, metadata)
            #_ = self.llm.add_content_to_queue(prompt, metadata)

        logger.good(f'Added {len(self.llm.message_queue)} messages to content queue!')

        return self.llm.content_queue                     
                           
    def _fill_vectorstore_queue(self, listobj, listmetadata, **kwargs):       
        '''
        This function is used to fill the content queue for grading
        '''
            
        idvec = range(len(listobj))
        for icm, prompt, metadata in zip(idvec, listobj, listmetadata):   
            _ = self.llm.add_message_to_queue(prompt, metadata)
            #_ = self.llm.add_content_to_queue(prompt, metadata)

        logger.good(f'Added {len(self.llm.message_queue)} messages to content queue!')

        return self.llm.content_queue                            
    
    def run(self, objlist, **kwargs):
        '''
        This function is used to run the OpenAI assistant api
        '''
        
        # add the type of submission
        stype = kwargs.get('stype', self.stype)
        question = kwargs.get('question', self.question)
        system_message = kwargs.get('system_message', self.system_message)
  
        listobjs = []
        listmetadata = []
        for obj in objlist:
            if isinstance(obj, tuple):
                listobjs.append(obj[0])
                listmetadata.append(obj[1])
            elif isinstance(obj, dict):
                listobjs.append(obj.get('content')) 
                listmetadata.append(obj.get('metadata', {}))        
                            
        # Step 1: Fill the content queue
        cqueue = self._fill_content_queue(listobjs, listmetadata, **kwargs)

        #
        if cqueue is None:
            logger.warn(f"Failed to fill content queue. Returning None.")
            return None
                    
    
        # result_queue = self.llm.result_queue
            
        # Step 2: Run the assistant
        runq = self.llm.run_from_content_queue(question=question, 
                                               tools=self.functions_and_tools, 
                                               instructions=system_message,
                                               stype=stype,
                                               redis_client=self.rclient,
                                               **kwargs)
        
        # Step 3: Wait for the run queue to finish
        try:
            result_queue = self.llm.wait_run_queue_without_tools(**kwargs)
        except Exception as e:
            logger.warn(f"Failed to wait for run queue. Error={e}")
            return None
        
        
        # Step 5: save the results to tenx and return the results as list of tuples
        result_list = []
        for (result, metadata) in result_queue:
            result_list.append((result, metadata))
            
            # join metadata with result
            # if isinstance(metadata, dict) and isinstance(result, dict):
            #     for k, v in metadata.items():
            #         result[f"source_{k}"] = v
            #     result_list.append(result)
            # else:
            #     result_list.append((result, metadata))
            
        return result_list