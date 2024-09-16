import autogen
import openai, os

from dotenv import load_dotenv
load_dotenv(os.path.abspath("../../.env"))
# print("Not a thing")
# print(os.getenv('OPENAI_API_KEY'))

# openai.api_key = os.getenv('OPENAI_API_KEY')
OPENAI_API_KEY = "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"
# openai.api_key = os.environ.get('OPENAI_API_KEY')
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY )


class agents:
    _instance = None

    # def __new__(cls, *args, **kwargs):
    #     if cls._instance is None:
    #         cls._instance = super(agents, cls).__new__(cls)
    #     return cls._instance

    def __init__(self):
        """
        Initialize the AgentManager with necessary configurations and agents.
        Args:
            persona (str): Persona for the agent.
        """
  
        self.assistant = autogen.AssistantAgent(  
            name="assistant",
            code_execution_config=False,
            llm_config={
                "temperature": 0,
                "timeout": 600,
                "cache_seed": None,
                "config_list": [{"model": "gpt-4o-mini", "api_key": OPENAI_API_KEY }],
            },
        )

        self.analyser_proxy = autogen.UserProxyAgent(
            name="analyser_proxy",
            is_termination_msg=lambda x: isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper(),
            human_input_mode="NEVER",
            max_consecutive_auto_reply=3,
        )

        self.interviewer_proxy = autogen.UserProxyAgent(
            name="interviewer_proxy",
            is_termination_msg=lambda x: isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper(),
            human_input_mode="NEVER",
            max_consecutive_auto_reply=3,
        )

    async def send_message_analyser(self, message: str) -> None:
        try:
            await self.analyser_proxy.a_initiate_chat(
                recipient=self.assistant,
                clear_history=False,
                message=message,
                max_turns=10
            )
            response = [messages for agent, messages in self.analyser_proxy.chat_messages.items()][0][-1]["content"].replace("TERMINATE", "")
            return response
        except Exception as e:
            return f'Error: {str(e)}'
        
    async def send_message_interview(self, message: str) -> None:
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