"""Default prompt templates."""
from typing import Dict, Any

from core.types.prompt import PromptSet, InterviewFlow, ModelConfig

DEFAULT_CHAT_PROMPT = PromptSet(
    id="default_chat",
    name="Default Chat Prompt",
    description="Default prompt set for general chat interactions",
    system_prompt="""You are a helpful AI assistant. You aim to be:
    1. Helpful and informative
    2. Direct and concise
    3. Friendly but professional
    4. Honest about your capabilities and limitations""",
    user_prompts=[
        {
            "role": "user",
            "content": "{user_input}"
        }
    ],
    model_config=ModelConfig(
        model_name="gpt-4",
        provider="openai",
        temperature=0.7,
        max_tokens=500
    ),
    metadata={
        "type": "chat",
        "version": "1.0",
        "is_default": True
    }
)

DEFAULT_INTERVIEW_PROMPT = PromptSet(
    id="default_interview",
    name="Default Interview Prompt",
    description="Default prompt set for technical interviews",
    system_prompt="""You are an expert technical interviewer. Your role is to:
    1. Ask clear, relevant technical questions
    2. Evaluate responses objectively
    3. Provide constructive feedback
    4. Maintain a professional and encouraging tone""",
    user_prompts=[
        {
            "role": "user",
            "content": "Please evaluate my answer to the following question: {question}\n\nMy answer: {answer}"
        }
    ],
    interview_flow=InterviewFlow(
        name="Standard Technical Interview",
        description="Basic technical interview flow",
        steps=[
            {
                "id": "intro",
                "type": "introduction",
                "question": "Please introduce yourself and your background.",
                "duration": 300
            },
            {
                "id": "technical",
                "type": "technical",
                "question": "Let's discuss your experience with {technology}.",
                "duration": 600
            },
            {
                "id": "coding",
                "type": "coding",
                "question": "Please solve this coding problem: {problem}",
                "duration": 1200
            }
        ]
    ),
    model_config=ModelConfig(
        model_name="gpt-4",
        provider="openai",
        temperature=0.3,
        max_tokens=1000
    ),
    metadata={
        "type": "interview",
        "version": "1.0",
        "is_default": True
    }
)

DEFAULT_ANALYSIS_PROMPT = PromptSet(
    id="default_analysis",
    name="Default Analysis Prompt",
    description="Default prompt set for session analysis",
    system_prompt="""You are an expert conversation analyzer. Your task is to:
    1. Identify key topics and themes
    2. Analyze sentiment and engagement
    3. Extract actionable insights
    4. Provide clear recommendations""",
    user_prompts=[
        {
            "role": "user",
            "content": "Please analyze the following conversation:\n\n{conversation}"
        }
    ],
    model_config=ModelConfig(
        model_name="gpt-4",
        provider="openai",
        temperature=0.2,
        max_tokens=2000
    ),
    metadata={
        "type": "analysis",
        "version": "1.0",
        "is_default": True
    }
)

DEFAULT_AUDIO_PROMPT = PromptSet(
    id="default_audio",
    name="Default Audio Prompt",
    description="Default prompt set for audio interactions",
    system_prompt="""You are a voice interaction specialist. Your role is to:
    1. Process and understand spoken input clearly
    2. Provide concise, clear responses suitable for speech
    3. Maintain context in audio conversations
    4. Handle speech recognition uncertainties gracefully""",
    user_prompts=[
        {
            "role": "user",
            "content": "{transcribed_audio}"
        }
    ],
    model_config=ModelConfig(
        model_name="gpt-4",
        provider="openai",
        temperature=0.5,
        max_tokens=300
    ),
    metadata={
        "type": "audio",
        "version": "1.0",
        "is_default": True
    }
)

# Map of default prompts by type
DEFAULT_PROMPTS: Dict[str, PromptSet] = {
    "chat": DEFAULT_CHAT_PROMPT,
    "interview": DEFAULT_INTERVIEW_PROMPT,
    "analysis": DEFAULT_ANALYSIS_PROMPT,
    "audio": DEFAULT_AUDIO_PROMPT
}

def get_default_prompt(prompt_type: str) -> PromptSet:
    """Get default prompt set for a given type."""
    return DEFAULT_PROMPTS.get(prompt_type, DEFAULT_CHAT_PROMPT) 