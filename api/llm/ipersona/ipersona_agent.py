import autogen
#
from api.services.secret import get_auth

OPENAI_API_KEY  = get_auth(ssmkey='OPENAI_PARROT_API_KEY')


class agents:
    _instance = None
    def __init__(self):
        """
        Initialize the AgentManager with necessary configurations and agents.
        Args:
            persona (str): Persona for the agent.
        """
        
        self.default_llm_config = {
            "temperature": 0,
            "timeout": 600,
            "cache_seed": None,
            "config_list": [{"model": "gpt-4o-mini", "api_key": OPENAI_API_KEY}]
        }

  
        self.assistant = autogen.AssistantAgent(  
            name="assistant",
            llm_config= self.default_llm_config
        )

        self.interviewer_proxy = autogen.UserProxyAgent(
            name="interviewer_proxy",            
            is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
            human_input_mode="NEVER",
            max_consecutive_auto_reply=10,
        )
        
        self.interviewer_proxy.register_function(
            function_map={
                "real_time_response_evaluation": self.evaluate_candidate_response,
                "overall_interview_evaluation": self.evaluate_overall_interview,
                "overall_interview_metrics": self.overall_interview_metrics,
                "interview_question_clarification": self.interview_question_clarification
            }
        )       
        
    async def generate_question(self, message: str) -> None:
        try:
            await self.interviewer_proxy.a_initiate_chat(
                recipient=self.assistant,
                clear_history=False,
                message=message,
                max_turns=10
            )
            response = [messages for agent, messages in self.interviewer_proxy.chat_messages.items()][0][-1]["content"].replace("TERMINATE", "")
            return response
        except Exception as e:
            return f'Error: {str(e)}'
        

    async def evaluate_candidate_response(self, evaluation_prompt: str) -> None:
        try:
            llm_config = {
                "functions": [
                    {
                        "name": "real_time_response_evaluation",
                        "description": "Your response should be in a single json format as specfied",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                 "evaluation_prompt": {
                                    "type": "string",
                                    "description": "evaluation_prompt"
                                },
                            },
                            "required": ["evaluation_prompt"]
                        }
                    },
                ],
                "timeout": 120,
                "config_list": [{"model": "gpt-4o-mini", "api_key": OPENAI_API_KEY }]
            }
            self.assistant.llm_config = llm_config

            self.interviewer_proxy.initiate_chat(
                self.assistant,   
                message={
                    "function_call": {
                        "name": "real_time_response_evaluation",
                        "arguments": evaluation_prompt
                    }
                },
            )
            response = [messages for agent, messages in self.interviewer_proxy.chat_messages.items()][0][-1]["content"].replace("TERMINATE", "")
            return response
        
        except Exception as e:
            return f'Error: {str(e)}'


    async def evaluate_overall_interview(self, overall_evaluation_prompt):
        try:
            llm_config = {
                "functions": [
                    {
                        "name": "overall_interview_evaluation",
                        "description": "Your response should be in a single json format as specfied",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "overall_interview_evaluation": {
                                    "type": "string",                                   
                                    "description": "These data contains the whole back and forth conversation held by you and the candidate, your job is evaluate and provide an overall assessment summary on the candidate's performance of the interview."
                                }
                            },
                            "required": ["overall_interview_evaluation"]
                        }
                    }
                ],
                "timeout": 120,
                "config_list": [{"model": "gpt-4o-mini", "api_key": OPENAI_API_KEY }]
            }
            
            self.assistant.llm_config = llm_config

            self.interviewer_proxy.initiate_chat(
                self.assistant, 
                message={
                    "function_call": {
                        "name": "overall_interview_evaluation",
                        "arguments": overall_evaluation_prompt 
                    }
                }
            )
            response = [messages for agent, messages in self.interviewer_proxy.chat_messages.items()][0][-1]["content"].replace("TERMINATE", "")
            return response 
        
        except Exception as e:
            return f'Error: {str(e)}'
        
        
    async def overall_interview_metrics(self, overall_interview_metrics):
        try:
            llm_config = {
                "functions": [
                    {
                        "name": "overall_interview_metrics",
                        "description": "Your response should be in a single json format as specfied",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "overall_interview_metrics": {
                                    "type": "string",                                   
                                    "description": "overall_interview_metrics"
                                } 
                            },
                            "required": ["overall_interview_metrics"]
                        }
                    }
                ],
                "timeout": 120,
                "config_list": [{"model": "gpt-4o-mini", "api_key": OPENAI_API_KEY }]
            }
            
            self.assistant.llm_config = llm_config

            self.interviewer_proxy.initiate_chat(
                self.assistant, 
                message={
                    "function_call": {
                        "name": "overall_interview_metrics",
                        "arguments": overall_interview_metrics 
                    }
                }
            )
            response = [messages for agent, messages in self.interviewer_proxy.chat_messages.items()][0][-1]["content"].replace("TERMINATE", "")
            return response 
        
        except Exception as e:
            return f'Error: {str(e)}'


    async def interview_question_clarification(self, interview_question_clarification):
        try:
            llm_config = {
                "functions": [
                    {
                        "name": "interview_question_clarification",
                        "description": "Your response should be in a single json format as specfied",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "interview_question_clarification": {
                                    "type": "string",                                   
                                    "description": "interview_question_clarification"
                                } 
                            },
                            "required": ["interview_question_clarification"]
                        }
                    }
                ],
                "timeout": 120,
                "config_list": [{"model": "gpt-4o-mini", "api_key": OPENAI_API_KEY }]
            }
            
            self.assistant.llm_config = llm_config

            self.interviewer_proxy.initiate_chat(
                self.assistant, 
                message={
                    "function_call": {
                        "name": "interview_question_clarification",
                        "arguments": interview_question_clarification 
                    }
                }
            )
            response = [messages for agent, messages in self.interviewer_proxy.chat_messages.items()][0][-1]["content"].replace("TERMINATE", "")
            return response 
        
        except Exception as e:
            return f'Error: {str(e)}'


 