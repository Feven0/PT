"""Chain-related prompts and templates."""
from typing import Dict, Any

CHAIN_PROMPTS = {
    "chat_response": """You are a helpful AI assistant. Review the conversation history and latest message, then provide a clear and helpful response.

Conversation History:
{history}

Latest Message:
{message}

Consider:
1. Context from previous messages
2. User's intent and needs
3. Relevant information to include
4. Clear and concise response format""",

    "code_response": """Analyze the following code and provide a detailed response:

Code:
{message}

Context:
{context}

Consider:
1. Context from previous messages
2. User's intent and needs
3. Relevant information to include
4. Code semantic and syntax
5. Code quality and performance
6. Code complexity and readability
7. Code best practices and patterns
8. Code security and compliance
""",

    "chain_init": """Initialize a new processing chain:
Task: {task}
Context: {context}
Tools: {tools}

Consider:
1. Required steps
2. Dependencies
3. State tracking needs
4. Error handling""",

    "chain_step": """Process the current chain step:
Step: {step}
State: {state}
Previous Results: {results}

Determine:
1. Step requirements
2. Input validation
3. Output handling
4. State updates""",

    "chain_state": """Track chain execution state:
Chain ID: {chain_id}
Current Step: {step}
Completed Steps: {completed}
Pending Steps: {pending}
Results: {results}
Errors: {errors}

Evaluate:
1. Progress status
2. State consistency
3. Error conditions
4. Recovery needs""",

    "chain_result": """Analyze chain execution results:
Chain: {chain_id}
Steps Completed: {steps}
Final Results: {results}
Duration: {duration}
Issues: {issues}

Review:
1. Success criteria
2. Result quality
3. Performance metrics
4. Improvement areas""",

    "message_classification": """Classify the following message type and return a tuple of (type, confidence) where type is either 'code' or 'chat'.

Message:
{message}""",  

    "message_classification_result": """Type: {type}
Confidence: {confidence}"""
}

CHAIN_TEMPLATES = {
    "step_result": """Step Execution:
- Step: {step}
- Status: {status}
- Duration: {duration}
- Results: {results}
- Next Step: {next_step}""",

    "state_update": """State Update:
- Chain: {chain_id}
- Previous: {previous_state}
- Current: {current_state}
- Changes: {changes}
- Timestamp: {timestamp}""",

    "error_state": """Error State:
- Step: {step}
- Error: {error}
- Context: {context}
- Recovery: {recovery}
- Status: {status}"""
}

# Export prompts and templates
__all__ = ['CHAIN_PROMPTS', 'CHAIN_TEMPLATES'] 