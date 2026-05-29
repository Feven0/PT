"""Utility functions for prompt management."""
from typing import Dict, Any, Optional, List
from pathlib import Path

def format_template(template: str, **kwargs: Any) -> str:
    """Format a prompt template with variables."""
    try:
        return template.format(**kwargs)
    except KeyError as e:
        raise ValueError(f"Missing required variable {e} in template")
    except Exception as e:
        raise ValueError(f"Error formatting template: {e}")

def load_prompt_file(path: Path) -> Dict[str, Any]:
    """Load prompts from a file."""
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
        
    with path.open() as f:
        content = f.read()
        
    # Parse sections
    sections = {}
    current_section = None
    current_content = []
    
    for line in content.split('\n'):
        if line.startswith('# '):
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = line[2:].lower()
            current_content = []
        else:
            current_content.append(line)
            
    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()
        
    return sections

def validate_prompt_variables(template: str, variables: Dict[str, Any]) -> List[str]:
    """Validate that all required variables are present."""
    required = []
    
    # Extract required variables from template
    start = 0
    while True:
        start = template.find('{', start)
        if start == -1:
            break
            
        end = template.find('}', start)
        if end == -1:
            break
            
        var = template[start+1:end].split(':')[0]
        if var not in variables:
            required.append(var)
            
        start = end + 1
        
    return required

def merge_prompt_sections(*sections: Dict[str, Any]) -> Dict[str, Any]:
    """Merge multiple prompt section dictionaries."""
    merged = {}
    
    for section in sections:
        for key, value in section.items():
            if key in merged:
                if isinstance(merged[key], dict) and isinstance(value, dict):
                    merged[key].update(value)
                elif isinstance(merged[key], list) and isinstance(value, list):
                    merged[key].extend(value)
                else:
                    merged[key] = value
            else:
                merged[key] = value
                
    return merged 