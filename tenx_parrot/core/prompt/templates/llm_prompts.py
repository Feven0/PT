"""LLM-specific prompts and templates."""
from typing import Dict, Any

# LLM operation prompts
LLM_PROMPTS: Dict[str, Any] = {
    'code_generation': {
        'analyze': """Analyze requirements:
1. What functionality is needed?
2. What are the inputs/outputs?
3. What constraints exist?""",
        
        'design': """Design implementation:
1. Choose architecture
2. Plan components
3. Consider patterns""",
        
        'implement': """Implement solution:
1. Write clean code
2. Add documentation
3. Include tests"""
    },
    
    'code_analysis': {
        'understand': """Understand the code:
1. What does it do?
2. How does it work?
3. What are key components?""",
        
        'evaluate': """Evaluate the code:
1. Check correctness
2. Look for issues
3. Assess quality""",
        
        'suggest': """Make suggestions:
1. Identify improvements
2. Note concerns
3. Propose changes"""
    },
    
    'error_handling': {
        'analyze': """Analyze the error:
1. What is the error?
2. Where did it occur?
3. What caused it?""",
        
        'fix': """Fix the error:
1. Determine solution
2. Make changes
3. Add safeguards""",
        
        'prevent': """Prevent recurrence:
1. Add validation
2. Improve error handling
3. Update documentation"""
    },
    
    'code_review': {
        'check': """Check implementation:
1. Verify correctness
2. Review style
3. Look for bugs""",
        
        'feedback': """Provide feedback:
1. Note issues
2. Suggest fixes
3. Highlight good parts""",
        
        'approve': """Approve changes:
1. Confirm requirements
2. Verify tests
3. Check documentation"""
    }
} 