"""Schema definitions for tool functions and XML patterns."""
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from pydantic import BaseModel, Field
from datetime import datetime
import json
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape, unescape
import os

from ..tools.search.tools import CodebaseSearch, GrepSearch, FileSearch
from ..tools.file.tools import ReadFile, DeleteFile
from ..tools.edit.tools import EditFile, ReapplyEdit, ParallelApply
from ..tools.terminal.tools import CommandRunner
from ..tools.base import ToolContext
from ..metrics import MetricsCollector

@dataclass
class FunctionCall:
    """Represents a function call from the LLM."""
    name: str
    parameters: Dict[str, Any]
    explanation: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "name": self.name,
            "parameters": self.parameters,
            "explanation": self.explanation,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FunctionCall":
        """Create from dictionary format."""
        return cls(
            name=data["name"],
            parameters=data["parameters"],
            explanation=data.get("explanation"),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]) 
            if "created_at" in data else datetime.now()
        )
    
    @classmethod
    def from_xml(cls, xml_str: str) -> "FunctionCall":
        """Parse function call from XML string."""
        try:
            root = ET.fromstring(xml_str)
            if root.tag != "antml:function_calls":
                raise ValueError("Invalid XML: missing antml:function_calls root")
            
            invoke = root.find("antml:invoke")
            if invoke is None:
                raise ValueError("Invalid XML: missing antml:invoke element")
            
            name = invoke.get("name")
            if not name:
                raise ValueError("Invalid XML: missing name attribute")
            
            parameters = {}
            for param in invoke.findall("antml:parameter"):
                param_name = param.get("name")
                if not param_name:
                    continue
                    
                value = param.text or ""
                try:
                    parameters[param_name] = json.loads(value)
                except json.JSONDecodeError:
                    parameters[param_name] = value
            
            return cls(name=name, parameters=parameters)
            
        except ET.ParseError as e:
            raise ValueError(f"Invalid XML format: {e}")
        except Exception as e:
            raise ValueError(f"Error parsing function call: {e}")
            
    def to_xml(self) -> str:
        """Convert to XML format for LLM prompts."""
        root = ET.Element("antml:function_calls")
        invoke = ET.SubElement(root, "antml:invoke")
        invoke.set("name", self.name)
        
        for key, value in self.parameters.items():
            param = ET.SubElement(invoke, "antml:parameter")
            param.set("name", key)
            if isinstance(value, (dict, list)):
                param.text = json.dumps(value)
            else:
                param.text = str(value)
                
        return ET.tostring(root, encoding="unicode", method="xml") 
    
# Core function schemas
FUNCTION_SCHEMAS = {
    "codebase_search": {
        "name": "codebase_search",
        "description": "Find snippets of code from the codebase most relevant to the search query.\nThis is a semantic search tool, so the query should ask for something semantically matching what is needed.\nIf it makes sense to only search in particular directories, please specify them in the target_directories field.\nUnless there is a clear reason to use your own search query, please just reuse the user's exact query with their wording.\nTheir exact wording/phrasing can often be helpful for the semantic search query. Keeping the same exact question format can also be helpful.",
        "parameters": {
            "properties": {
                "query": {
                    "description": "The search query to find relevant code. You should reuse the user's exact query/most recent message with their wording unless there is a clear reason not to.",
                    "type": "string"
                },
                "target_directories": {
                    "description": "Glob patterns for directories to search over",
                    "items": {"type": "string"},
                    "type": "array"
                },
                "explanation": {
                    "description": "One sentence explanation as to why this tool is being used, and how it contributes to the goal.",
                    "type": "string"
                }
            },
            "required": ["query"],
            "type": "object"
        }
    },
    "read_file": {
        "name": "read_file", 
        "description": "Read the contents of a file. The output will be the 1-indexed file contents from start_line_one_indexed to end_line_one_indexed_inclusive, together with a summary of the lines outside that range.\nCan view at most 250 lines at a time.\nEnsure you have COMPLETE context by:\n1) Assess if contents viewed are sufficient\n2) Note lines not shown\n3) Call again to view more lines if needed\n4) When in doubt, gather more information\nReading entire files should be done sparingly.",
        "parameters": {
            "properties": {
                "relative_workspace_path": {
                    "description": "Path of file to read, relative to workspace root",
                    "type": "string"
                },
                "start_line_one_indexed": {
                    "description": "One-indexed line number to start reading from",
                    "type": "integer"
                },
                "end_line_one_indexed_inclusive": {
                    "description": "One-indexed line number to end reading at (inclusive)", 
                    "type": "integer"
                },
                "should_read_entire_file": {
                    "description": "Whether to read entire file. Use sparingly.",
                    "type": "boolean"
                },
                "explanation": {
                    "description": "Why this read is needed",
                    "type": "string"
                }
            },
            "required": ["relative_workspace_path", "should_read_entire_file", "start_line_one_indexed", "end_line_one_indexed_inclusive"],
            "type": "object"
        }
    },
    "edit_file": {
        "name": "edit_file",
        "description": "Edit an existing file or create a new one. Use '// ... existing code ...' to represent unchanged code between edits. Include sufficient context around edits. Never omit code without the comment.",
        "parameters": {
            "properties": {
                "target_file": {
                    "description": "Path to file to edit, relative to workspace",
                    "type": "string"
                },
                "instructions": {
                    "description": "Clear instruction of what edit will do",
                    "type": "string" 
                },
                "code_edit": {
                    "description": "The edit to apply, using // ... existing code ... for unchanged parts",
                    "type": "string"
                },
                "blocking": {
                    "description": "Whether to block further edits until this completes",
                    "type": "boolean"
                }
            },
            "required": ["target_file", "instructions", "code_edit", "blocking"],
            "type": "object"
        }
    },
    "run_terminal_cmd": {
        "name": "run_terminal_cmd",
        "description": "Run a command in the terminal. Commands need user approval. Add | cat for pager commands. Use is_background for long-running commands.",
        "parameters": {
            "properties": {
                "command": {
                    "description": "Command to execute", 
                    "type": "string"
                },
                "is_background": {
                    "description": "Whether to run in background",
                    "type": "boolean"
                },
                "require_user_approval": {
                    "description": "Whether user must approve first",
                    "type": "boolean"
                },
                "explanation": {
                    "description": "Why this command is needed",
                    "type": "string"
                }
            },
            "required": ["command", "is_background", "require_user_approval"],
            "type": "object"
        }
    },
    "list_dir": {
        "name": "list_dir",
        "description": "List the contents of a directory. The quick tool to use for discovery, before using more targeted tools like semantic search or file reading. Useful to try to understand the file structure before diving deeper into specific files. Can be used to explore the codebase.",
        "parameters": {
            "properties": {
                "relative_workspace_path": {
                    "description": "Path to list contents of, relative to the workspace root.",
                    "type": "string"
                },
                "explanation": {
                    "description": "One sentence explanation as to why this tool is being used, and how it contributes to the goal.",
                    "type": "string"
                }
            },
            "required": ["relative_workspace_path"],
            "type": "object"
        }
    },
    "grep_search": {
        "name": "grep_search",
        "description": "Fast text-based regex search that finds exact pattern matches within files or directories, utilizing the ripgrep command for efficient searching.\nResults will be formatted in the style of ripgrep and can be configured to include line numbers and content.\nTo avoid overwhelming output, the results are capped at 50 matches.\nUse the include or exclude patterns to filter the search scope by file type or specific paths.\n\nThis is best for finding exact text matches or regex patterns.\nMore precise than semantic search for finding specific strings or patterns.\nThis is preferred over semantic search when we know the exact symbol/function name/etc. to search in some set of directories/file types.",
        "parameters": {
            "properties": {
                "query": {
                    "description": "The regex pattern to search for",
                    "type": "string"
                },
                "case_sensitive": {
                    "description": "Whether the search should be case sensitive",
                    "type": "boolean"
                },
                "include_pattern": {
                    "description": "Glob pattern for files to include (e.g. '*.ts' for TypeScript files)",
                    "type": "string"
                },
                "exclude_pattern": {
                    "description": "Glob pattern for files to exclude",
                    "type": "string"
                },
                "explanation": {
                    "description": "One sentence explanation as to why this tool is being used, and how it contributes to the goal.",
                    "type": "string"
                }
            },
            "required": ["query"],
            "type": "object"
        }
    },
    "file_search": {
        "name": "file_search",
        "description": "Fast file search based on fuzzy matching against file path. Use if you know part of the file path but don't know where it's located exactly. Response will be capped to 10 results. Make your query more specific if need to filter results further.",
        "parameters": {
            "properties": {
                "query": {
                    "description": "Fuzzy filename to search for",
                    "type": "string"
                },
                "explanation": {
                    "description": "One sentence explanation as to why this tool is being used, and how it contributes to the goal.",
                    "type": "string"
                }
            },
            "required": ["query", "explanation"],
            "type": "object"
        }
    },
    "delete_file": {
        "name": "delete_file",
        "description": "Deletes a file at the specified path. The operation will fail gracefully if:\n    - The file doesn't exist\n    - The operation is rejected for security reasons\n    - The file cannot be deleted",
        "parameters": {
            "properties": {
                "target_file": {
                    "description": "The path of the file to delete, relative to the workspace root.",
                    "type": "string"
                },
                "explanation": {
                    "description": "One sentence explanation as to why this tool is being used, and how it contributes to the goal.",
                    "type": "string"
                }
            },
            "required": ["target_file"],
            "type": "object"
        }
    },
    "reapply": {
        "name": "reapply",
        "description": "Calls a smarter model to apply the last edit to the specified file.\nUse this tool immediately after the result of an edit_file tool call ONLY IF the diff is not what you expected, indicating the model applying the changes was not smart enough to follow your instructions.",
        "parameters": {
            "properties": {
                "target_file": {
                    "description": "The relative path to the file to reapply the last edit to.",
                    "type": "string"
                }
            },
            "required": ["target_file"],
            "type": "object"
        }
    },
    "parallel_apply": {
        "name": "parallel_apply",
        "description": "When there are multiple locations that can be edited in parallel, with a similar type of edit, use this tool to sketch out a plan for the edits.\nYou should start with the edit_plan which describes what the edits will be.\nThen, write out the files that will be edited with the edit_files argument.\nYou shouldn't edit more than 50 files at a time.",
        "parameters": {
            "properties": {
                "edit_plan": {
                    "description": "A detailed description of the parallel edits to be applied.\nThey should be specified in a way where a model just seeing one of the files and this plan would be able to apply the edits to any of the files.\nIt should be in the first person, describing what you will do on another iteration, after seeing the file.",
                    "type": "string"
                },
                "edit_regions": {
                    "description": "The region of the file that should be edited. It should include the minimum contents needed to read in addition to the edit_plan to be able to apply the edits. You should add a lot of cushion to make sure the model definitely has the context it needs to edit the file.",
                    "items": {
                        "type": "object",
                        "properties": {
                            "relative_workspace_path": {
                                "description": "The path to the file to edit.",
                                "type": "string"
                            },
                            "start_line": {
                                "description": "The start line of the region to edit. 1-indexed and inclusive.",
                                "type": "integer"
                            },
                            "end_line": {
                                "description": "The end line of the region to edit. 1-indexed and inclusive.",
                                "type": "integer"
                            }
                        },
                        "required": ["relative_workspace_path"]
                    },
                    "type": "array"
                }
            },
            "required": ["edit_plan", "edit_regions"],
            "type": "object"
        }
    }
}

# XML patterns for function calls
XML_PATTERNS = {
    "function_call_start": "<function_calls>",
    "function_call_end": "</function_calls>",
    "invoke_start": "<invoke name=\"{name}\">",
    "invoke_end": "</invoke>",
    "parameter": "<parameter name=\"{name}\">{value}</parameter>"
}

# XML templates for responses
XML_TEMPLATES = {
    "function_result": """
    <function_result>
        <name>{name}</name>
        <success>{success}</success>
        <result>{result}</result>
        {error_block}
    </function_result>
    """,
    
    "error_block": """
    <error>
        <message>{message}</message>
        <details>{details}</details>
    </error>
    """
}

# Function call template
FUNCTION_CALL_TEMPLATE = """
<function_calls>
<invoke name="{name}">
{parameters}
</invoke>
</function_calls>
"""

# Parameter template
PARAMETER_TEMPLATE = "<parameter name=\"{name}\">{value}</parameter>"

def get_default_context() -> ToolContext:
    """Get default tool context."""
    return ToolContext(
        workspace_path=os.getcwd(),  # Default to current directory
        user_id=None,
        session_id=None,
        metrics=MetricsCollector()  # Add default metrics collector
    )

# Map schema names to tool implementations
FUNCTION_IMPLEMENTATIONS = {
    "codebase_search": CodebaseSearch(get_default_context()).execute,
    "grep_search": GrepSearch(get_default_context()).execute,
    "file_search": FileSearch(get_default_context()).execute,
    "read_file": ReadFile(get_default_context()).execute,
    "delete_file": DeleteFile(get_default_context()).execute,
    "edit_file": EditFile(get_default_context()).execute,
    "reapply": ReapplyEdit(get_default_context()).execute,
    "parallel_apply": ParallelApply(get_default_context()).execute,
    "run_terminal_cmd": CommandRunner(context=get_default_context()).execute
}
