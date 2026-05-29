"""Tool-specific prompts and templates."""

# Tool operation prompts

TOOL_PROMPTS_V1 = {
    'search_tools': {
        'semantic': """Semantic code search:
1. What concepts to search for?
2. Which files to include?
3. How specific should results be?""",
        
        'pattern': """Pattern matching search:
1. What exact pattern to match?
2. Which file types to search?
3. Case sensitivity?""",
        
        'analyze': """Analyze search results:
1. Are results relevant?
2. Need more specific search?
3. Check other locations?"""
    },
    
    'file_tools': {
        'read': """Reading file contents:
1. Which sections to read?
2. Need full context?
3. Check related files?""",
        
        'write': """Writing to file:
1. Backup existing content?
2. Validate new content?
3. Update related files?""",
        
        'manage': """File management:
1. Clean up temporary files?
2. Update permissions?
3. Verify integrity?"""
    },
    
    'edit_tools': {
        'plan': """Plan edits:
1. What changes needed?
2. Impact on other code?
3. Required imports?""",
        
        'execute': """Execute edits:
1. Make changes safely
2. Preserve formatting
3. Update imports""",
        
        'verify': """Verify edits:
1. Changes applied correctly?
2. Syntax valid?
3. Tests passing?"""
    },
    
    'terminal_tools': {
        'execute': """Execute command:
1. Command safe to run?
2. Capture all output?
3. Handle errors?""",
        
        'monitor': """Monitor execution:
1. Track progress
2. Watch for errors
3. Check resource usage""",
        
        'cleanup': """Clean up after execution:
1. Remove temp files
2. Reset environment
3. Verify state"""
    }
} 

TOOL_PROMPTS = {
    "search": {
        "codebase_search": """Find relevant code using semantic search:
Query: {query}
Context: {context}
Consider file types and locations that are most likely to contain relevant code.""",
        
        "grep_search": """Search for exact text patterns:
Pattern: {pattern}
Context: {context}
Consider case sensitivity and file patterns to include/exclude.""",
        
        "file_search": """Find files by name pattern:
Pattern: {pattern}
Context: {context}
Consider directory structure and file extensions."""
    },
    
    "file": {
        "read_file": """Read file contents with proper context:
File: {file}
Lines: {lines}
Ensure you have sufficient context for understanding the code.""",
        
        "edit_file": """Make precise code changes:
File: {file}
Changes: {changes}
Ensure changes maintain code functionality and style.""",
        
        "delete_file": """Remove files safely:
File: {file}
Verify file is safe to delete and won't break dependencies."""
    },
    
    "terminal": {
        "run_command": """Execute terminal command:
Command: {command}
Context: {context}
Consider command safety and output handling."""
    }
}

TOOL_RESULT_TEMPLATES = {
    "search_result": """Search Results:
- Found {count} matches
- Most relevant: {highlights}
- Suggested next steps: {suggestions}""",
    
    "file_read": """File Contents:
- Path: {path}
- Lines: {line_range}
- Summary: {summary}
- Key elements: {elements}""",
    
    "edit_result": """Edit Results:
- File: {file}
- Changes made: {changes}
- Validation: {validation}
- Next steps: {next_steps}""",
    
    "command_result": """Command Execution:
- Command: {command}
- Status: {status}
- Output: {output}
- Errors: {errors}"""
}

# Export prompts and templates
__all__ = ['TOOL_PROMPTS', 'TOOL_RESULT_TEMPLATES'] 