"""Agent prompts for task execution and action selection."""

# Agent behavior prompts

task_analysis_prompt = """
Analyze the following task and determine the best approach:
Task: {task}
Workspace: {workspace}

Consider:
1. What information do you need to gather?
2. What tools might be needed?
3. Are there potential risks or dependencies?
4. What validation is needed?

Provide your analysis and planned approach. If the user just is greeting you, complete the conversation by telling them who you are and what you are able to do. Be creative to tell them a random but thoughtful quote of the day. May be sometime choose to output a diagram of the codebase for questions and tasks that are not specific.
"""

action_selection_prompt = """
Based on the current context and task state, select the most appropriate action:

Available Actions:
1. Information Gathering ("GATHER_INFO")
   - Search codebase for relevant files
   - Read file contents
   - List directory contents
   - Check for specific patterns

2. Code Modification ("MODIFY_CODE")
   - Edit existing files
   - Create new files
   - Delete files
   - Apply parallel changes

3. Tool Execution ("EXECUTE_TOOL")
   - Run terminal commands
   - Execute external tools
   - Process tool results

4. Validation ("VALIDATE")
   - Check syntax
   - Verify imports
   - Test functionality
   - Validate changes

5. Error Recovery ("RECOVER")
   - Analyze error
   - Plan recovery
   - Execute recovery

6. Code Review ("CODE_REVIEW")
   - Review code changes
   - Check for potential issues
   - Suggest improvements

7. Code Suggestion ("CODE_SUGGESTION")
   - Suggest improvements
   - Suggest code refactoring

8. Cleanup After Task ("CLEANUP_AFTER_TASK")
   - Cleanup temporary files
   - Revert test changes
   - Update status

9. Terminate ("TERMINATE")
   - If the task is complete
   - If the task is not clear from the context
   - If the task is not in the list

10. Unknown ("UNKNOWN")
   - If the action is not in the list
   - If the action is not clear from the context

Current Task: {task}
Current State: {state}
Last Action Result: {last_result}

Select the next action and explain your reasoning.
"""

tool_selection_prompt = """
Given the current action, select the appropriate tool:

Action Type: {action_type}
Context: {context}
Available Tools: {tools}

Consider:
1. Tool capabilities and limitations
2. Required parameters
3. Expected outputs
4. Error handling needs

Explain your tool selection and parameter choices.
""" 

error_recovery_prompt = """
An error occurred during task execution:
Error: {error}
Context: {context}
Previous Actions: {actions}

Determine:
1. Root cause analysis
2. Recovery options
3. Prevention strategies
4. Next steps

Provide your recovery plan and preventive measures.
"""

task_completion_prompt = """
Review the task execution results:
Task: {task}
Actions Taken: {actions}
Results: {results}
Errors: {errors}

Evaluate:
1. Were all requirements met?
2. Are there any remaining issues?
3. Is additional validation needed?
4. What documentation or explanation is needed?

Provide your completion assessment and recommendations.
"""

code_review_prompt = """
Review code changes:
1. Are changes correct?
2. Follow best practices?
3. Any potential issues?
"""

code_suggestion_prompt = """
Suggest improvements:
1. Code quality
2. Performance
3. Security
"""

cleanup_after_task_prompt = """
Cleanup after task:
1. Remove temporary files
2. Revert test changes
3. Update status
"""

report_completion_prompt = """
Report the completion of the task:
Task: {task}
Actions Taken: {actions}
Results: {results}
Errors: {errors}

Consider:
1. Summarize changes
2. Note any issues
3. Suggest next steps
"""

AGENT_PROMPTS = {
    "task_analysis": task_analysis_prompt,
    "action_selection": action_selection_prompt,
    "tool_selection": tool_selection_prompt,
    "error_recovery": error_recovery_prompt,
    "task_completion": task_completion_prompt,
    "code_review": code_review_prompt,
    "code_suggestion": code_suggestion_prompt,
    "cleanup_after_task": cleanup_after_task_prompt,
    "report_completion": report_completion_prompt
}

# Action type definitions
ACTION_TYPES = {
    "GATHER_INFO": {"prompt":"task_analysis", 
                    "description": "Information gathering actions"},
    "SELECT_ACTION": {"prompt":"action_selection", 
                    "description": "Code modification actions"},
    "EXECUTE_TOOL": {"prompt":"tool_selection", 
                     "description": "Tool execution actions"},
    "VALIDATE": {"prompt":"task_completion", 
                 "description": "Validation actions"},
    "RECOVER": {"prompt":"error_recovery", 
                "description": "Error recovery actions"},
    "CODE_REVIEW": {"prompt":"code_review", 
                    "description": "Code review actions"},
    "CODE_SUGGESTION": {"prompt":"code_suggestion", 
                        "description": "Code suggestion actions"},
    "CLEANUP_AFTER_TASK": {"prompt":"cleanup_after_task", 
                           "description": "Cleanup after task actions"},
    "REPORT_COMPLETION": {"prompt":"report_completion", 
                          "description": "Report completion actions"},
    "TERMINATE": {"prompt":"task_completion", 
                  "description": "Termination actions"},
    "UNKNOWN": {"prompt":"task_completion", 
                "description": "Unknown actions"}
}


# Export prompts and types
__all__ = ['AGENT_PROMPTS', 'ACTION_TYPES'] 