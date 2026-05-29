"""Code agent for executing coding tasks."""
from typing import Dict, Any, Optional, List, AsyncIterator
import asyncio
from datetime import datetime
import uuid

from core.llm.client import LLMClient
from core.llm.chain.chain import Chain as LLMChain
from core.llm.models import (
    Message,
    ModelResponse,
    ChainStep,
    ChainStepStatus
)
from .schemas import (
    FunctionCall,
    FUNCTION_SCHEMAS,
    FUNCTION_IMPLEMENTATIONS,
    XML_TEMPLATES
)
from core.logging import BackendLogger
from .tool_manager import ToolManager
from core.config.base import AppConfig
from core.prompt.templates.system_prompts import (
    SYSTEM_PROMPT,
    COMMUNICATION_RULES,
    TOOL_CALLING_RULES,
    SEARCH_AND_READING_RULES,
    CODE_CHANGE_RULES,
    DEBUGGING_RULES,
    API_RULES
)
from core.prompt.templates.agent_prompts import AGENT_PROMPTS, ACTION_TYPES
from ..errors import AgentError, handle_agent_error

from .state import AgentState
from .context import TaskContext
from .. import models  # Import our pydantic models

logger = BackendLogger(__name__).get_logger()

class CodeAgent:
    """Agent for executing coding tasks."""
    
    def __init__(
        self,
        config: AppConfig,
        llm_client: LLMClient,
        tool_manager: ToolManager,
        chain_manager: LLMChain,
        task_storage: Optional['TaskStorage'] = None
    ):
        """Initialize the agent."""
        self.config = config
        self.llm_client = llm_client
        self.tool_manager = tool_manager
        self.chain_manager = chain_manager
        self.task_storage = task_storage
        self.state = AgentState.IDLE
        self.current_task: Optional[TaskContext] = None
        
    
    async def _save_task_state(self) -> None:
        """Save current task state to storage."""
        if not self.current_task:
            return
            
        await self.task_storage.update_task(
            self.current_task.task_id,
            {
                "state": self.state.value,
                "metadata": self.current_task.metadata,
                "tool_calls": self.current_task.tool_calls,
                "errors": self.current_task.errors
            }
        )    
        
    async def _execute_function_call_with_retry(
        self,
        function_call: FunctionCall,
        max_retries: int = 3,
        base_delay: float = 1.0
    ) -> Dict[str, Any]:
        """Execute a function call with retry mechanism."""
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                result = await self._execute_function_call(function_call)
                await self._save_task_state()
                return result
                
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    # Calculate delay with exponential backoff
                    delay = base_delay * (2 ** attempt)
                    
                    # Update task context with retry information
                    if self.current_task:
                        self.current_task.add_error({
                            "error": str(e),
                            "attempt": attempt + 1,
                            "max_retries": max_retries,
                            "next_retry_delay": delay
                        })
                        await self._save_task_state()
                    
                    # Log retry attempt
                    logger.warning(
                        f"Function call {function_call.name} failed (attempt {attempt + 1}/{max_retries}). "
                        f"Retrying in {delay} seconds. Error: {str(e)}"
                    )
                    
                    await asyncio.sleep(delay)
                    continue
                    
                # If we've exhausted retries, raise the last error
                raise handle_agent_error(last_error, {
                    "function": function_call.name,
                    "attempts": attempt + 1,
                    "max_retries": max_retries
        })
        
    async def _execute_function_call(
        self,
        function_call: FunctionCall
    ) -> Dict[str, Any]:
        """Execute a function call."""
        if not self.current_task:
            raise ValueError("No active task")
            
        # Update agent state
        self.state = AgentState.EXECUTING
        await self._save_task_state()
        
        try:
            # Validate function exists
            if function_call.name not in FUNCTION_IMPLEMENTATIONS:
                raise ValueError(f"Unknown function: {function_call.name}")
                
            # Get implementation
            tool_class = FUNCTION_IMPLEMENTATIONS[function_call.name]
            if not tool_class:
                raise ValueError(f"No implementation for: {function_call.name}")
                
            # Get tool instance
            tool = self.tool_manager.get_tool(function_call.name)
            if not tool:
                tool = tool_class()
                
            # Create chain step for tracking
            step = ChainStep(
                name=function_call.name,
                description=f"Executing tool {function_call.name} with parameters: {function_call.parameters}",
                status=ChainStepStatus.RUNNING,
                started_at=datetime.now(),
                metadata={
                    "tool": function_call.name,
                    "parameters": function_call.parameters
                }
            )
            
            # Execute tool
            result = await tool.execute(**function_call.parameters)
            
            # Update step status
            step.status = ChainStepStatus.COMPLETED
            step.completed_at = datetime.now()
            step.result = result
            
            # Update task context
            if self.current_task:
                self.current_task.add_tool_call({
                    "name": function_call.name,
                    "parameters": function_call.parameters,
                    "result": result,
                    "step": step.to_dict()
                })
                await self._save_task_state()
            
            return result
            
        except Exception as e:
            error = handle_agent_error(e, {
                "function": function_call.name,
                "parameters": function_call.parameters
            })
            
            # Update step status
            if step:
                step.status = ChainStepStatus.ERROR
                step.error = error.to_dict()
                
            # Update task context
            if self.current_task:
                self.current_task.add_error(error.to_dict())
                await self._save_task_state()
            
            raise error
            
    async def execute_task(
        self,
        task_description: str,
        context: Optional[TaskContext] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a coding task."""
        try:
            # Initialize task context
            self.current_task = context or TaskContext(
                description=task_description,
                metadata=metadata
            )
            
            # Create task in storage
            task = await self.task_storage.create_task(
                description=task_description,
                metadata=metadata
            )
            self.current_task.task_id = task.id
            
            # Update state
            self.state = AgentState.GATHERING_CONTEXT
            self.current_task.update_state(
                self.state.value,
                {"description": task_description}
            )
            await self._save_task_state()
            
            # Compose system prompt
            system_message = Message(
                role="system",
                content=self._compose_system_prompt(),
                metadata={"type": "system"}
            )
            
            # Create chain
            chain = self.chain_manager.create_chain(
                name=f"task_{self.current_task.task_id}",
                messages=[system_message],
                metadata={
                    "task_id": self.current_task.task_id,
                    "description": task_description
                }
            )
            
            # Add initial user message
            chain.add_message(Message(
                role="user",
                content=task_description,
                metadata={"type": "task_description"}
            ))
            
            # Update state
            self.state = AgentState.EXECUTING
            self.current_task.update_state(
                self.state.value,
                {"chain_id": chain.chain_id}
            )
            await self._save_task_state()
            
            # Execute initial chain
            result = await chain.execute()
            step_count = 1
            max_steps = 5
            
            # Loop to determine next actions and add new steps
            while step_count < max_steps:
                action = await self._select_action(self.current_task)
                new_prompt = action.get("prompt", "What should I do next?")

                # If the action is to terminate or unknown, break   
                if action.get("type", "") in ["TERMINATE", "UNKNOWN"]:
                    break

                # Select the tool to execute  
                if action.get("type", "").lower() == "execute_tool":
                    tool_selection = await self._select_tool(action, 
                                                         self.current_task)
                else:
                    tool_selection = None

                chain.add_step(
                    name=f"step_{step_count}",
                    prompt=new_prompt,
                    metadata={"action": action, 
                              "tool_selection": tool_selection}
                )
                result = await chain.execute()
                step_count += 1

            # Update state after executing all steps
            self.state = AgentState.VERIFYING
            self.current_task.update_state(self.state.value, {"result": result, "steps_executed": step_count})
            await self._save_task_state()

            # Complete task
            self.current_task.complete()
            await self.task_storage.complete_task(self.current_task.task_id)

            return {
                "task_id": self.current_task.task_id,
                "status": "completed",
                "result": result,
                "context": self.current_task.to_dict()
            }
            
        except Exception as e:
            error = handle_agent_error(e, {
                "task_id": self.current_task.task_id if self.current_task else None,
                "description": task_description,
                "state": self.state.value
            })
            
            # Update task state
            if self.current_task:
                self.state = AgentState.ERROR
                self.current_task.update_state(
                    self.state.value,
                    {"error": error.to_dict()}
                )

                await self._save_task_state()
                
                # Mark task as failed
                await self.task_storage.complete_task(
                    self.current_task.task_id,
                    state="failed"
                )      
                          
                self.current_task.add_error({
                    "type": "task_error",
                    "message": str(e)
                })
            
            return {
                "task_id": self.current_task.task_id if self.current_task else None,
                "status": "failed",
                "error": str(e),
                "context": self.current_task.to_dict() if self.current_task else None
            }
            
        finally:
            self.state = AgentState.IDLE
            
    async def stream_task(self, 
                          context: TaskContext) -> AsyncIterator[models.AgentStreamResponse]:
        """Stream task execution updates."""
        try:
            self.state = AgentState.EXECUTING
            self.current_task = context

            # Initialize with system prompt
            system_message = Message(
                role="system",
                content=self._compose_system_prompt(),
                metadata={"type": "system"}
            )

            # Create streaming chain
            chain = self.chain_manager.create_chain(
                name="task_streaming",
                messages=[system_message],
                metadata={
                    "task_id": context.task_id,
                    "workspace": context.workspace_path,
                    "streaming": True
                }
            )

            # Add task step
            chain.add_step(
                name="task_analysis",
                prompt=AGENT_PROMPTS["task_analysis"].format(
                    task=context.description,
                    workspace=context.workspace_path
                ),
                metadata={"type": "analysis"}
            )

            accumulated_content = ""

        except Exception as e:
            logger.error(f"Preparing task streaming error: {e}")
            raise e

        try:
            # Execute streaming for initial chain steps
            async for chain_response in chain.stream():
                #print('chain_response',chain_response)

                if isinstance(chain_response, dict):
                    logger.debug(f"Streaming agent message update: {chain_response}")
                    # Convert dict response to ModelResponse if needed
                    if "content" in chain_response:
                        response = ModelResponse(
                            content=chain_response["content"],
                            metadata=chain_response.get("metadata", {}),
                            function_call=chain_response.get("function_call")
                        )
                    else:
                        continue
                elif not isinstance(chain_response, ModelResponse):
                    logger.error(f"Unexpected chain response type: {type(chain_response)}")
                    raise ValueError(f"Unexpected chain response type: {type(chain_response)}")
                else:
                    response = chain_response

                # Ensure metadata exists
                if not hasattr(response, "metadata"):
                    response.metadata = {}

                self.current_task.last_update = response.metadata.get("timestamp", datetime.now())

                if response.metadata.get("is_chunk", False):
                    accumulated_content += response.content
                    yield models.ContentUpdate(
                        type="content",
                        data=models.ContentData(
                            content=response.content,
                            metadata=response.metadata
                        )
                    )
                else:
                    accumulated_content += response.content
                    yield models.MessageUpdate(
                        type="message",
                        data=models.MessageData(
                            content=response.content,
                            metadata=response.metadata
                        )
                    )
                    
                # Process any function calls in the current response chunk
                if call:=response.function_call:
                    try:
                        yield models.ToolCallUpdate(
                            type="tool_call",
                            data=models.ToolCallData(
                                tool=call.name,
                                input=call.parameters,
                                call_id=call.call_id,
                                timestamp=datetime.now()
                            )
                        )
                        result = await self._execute_function_call_with_retry(call)
                        yield models.ToolResultUpdate(
                            type="tool_result",
                            data=models.ToolResultData(
                                call_id=call.call_id,
                                tool=call.name,
                                input=call.parameters,
                                result=result,
                                status="completed",
                                timestamp=datetime.now()
                            )
                        )
                    except Exception as e:
                        yield models.ToolResultUpdate(
                            type="tool_result",
                            data=models.ToolResultData(
                                call_id=call.call_id,
                                tool=call.name,
                                input=call.parameters,
                                result=str(e),
                                status="failed",
                                timestamp=datetime.now()
                            )
                        )

        except Exception as e:
            logger.error(f"First Steps Task streaming error: {e}")
            raise e

        try:
            # After initial streaming, attempt to add additional steps
            step_count = 1
            max_steps = 5
            while step_count < max_steps:
                action = await self._select_action(self.current_task, 
                                                   accumulated_content)
                new_prompt = action.get("prompt", "")

                if action.get("type", "") in ["TERMINATE", "UNKNOWN"]:
                    break

                if action.get("type", "").lower() == "execute_tool":
                    tool_selection = await self._select_tool(action, 
                                                         self.current_task)
                else:
                    tool_selection = None

                chain.add_step(
                    name=f"step_{step_count}",
                    prompt=new_prompt.format(
                        task=self.current_task.description,
                        state=self.current_task.state,
                        last_result=accumulated_content
                    ),
                    metadata={"action": action, 
                              "tool_selection": tool_selection}
                )

                # Iterate over the chain steps and yield the response
                async for chain_response in chain.stream():

                    if isinstance(chain_response, dict):
                        logger.debug(f"Streaming agent message update: {chain_response}")
                        # Convert dict response to ModelResponse if needed
                        if "content" in chain_response:
                            response = ModelResponse(
                                content=chain_response["content"],
                                metadata=chain_response.get("metadata", {}),
                                function_call=chain_response.get("function_call")
                            )
                        else:
                            continue
                    elif not isinstance(chain_response, ModelResponse):
                        logger.error(f"Unexpected chain response type: {type(chain_response)}")
                        #raise ValueError(f"Unexpected chain response type: {type(chain_response)}")
                        continue
                    else:
                        response = chain_response


                    if response.metadata.get("is_chunk", False):
                        accumulated_content += response.content
                        yield models.ContentUpdate(
                            type="content",
                            data=models.ContentData(
                                content=response.content,
                                metadata=response.metadata
                            )
                        )
                    else:
                        accumulated_content += response.content
                        yield models.MessageUpdate(
                            type="message",
                            data=models.MessageData(
                                content=response.content,
                                metadata=response.metadata
                            )
                        )

                 
                    # If there is a function call, yield the tool call and result
                    if call:=response.function_call:
                        try:
                            yield models.ToolCallUpdate(
                                type="tool_call",
                                data=models.ToolCallData(
                                    tool=call.name,
                                    input=call.parameters,
                                    call_id=call.call_id,
                                    timestamp=datetime.now()
                                )
                            )
                            result = await self._execute_function_call_with_retry(call)
                            if result:
                                accumulated_content += str(result)
                                yield models.ToolResultUpdate(
                                    type="tool_result",
                                    data=models.ToolResultData(
                                    call_id=call.call_id,
                                    tool=call.name,
                                    input=call.parameters,
                                    result=result,
                                    status="completed",
                                    timestamp=datetime.now()
                                )
                            )
                        except Exception as e:
                            yield models.ToolResultUpdate(
                                type="tool_result",
                                data=models.ToolResultData(
                                    call_id=call.call_id,
                                    tool=call.name,
                                    input=call.parameters,
                                    result=str(e),
                                    status="failed",
                                    timestamp=datetime.now()
                                )
                            )
                    step_count += 1

        except Exception as e:
            logger.error(f"Final Steps Task streaming error: {e}")

            if self.current_task:
                self.current_task.state = "failed"
                self.current_task.errors.append({
                    "type": "stream_error",
                    "message": str(e),
                    "timestamp": datetime.now().isoformat()
                })

            yield models.ErrorUpdate(
                type="error",
                data=models.ErrorData(
                    error=str(e),
                    task_id=context.task_id
                )
            )
        finally:
            self.state = AgentState.IDLE

            # Final complete event
            yield models.CompleteUpdate(
                type="complete",
                data=models.CompleteData(
                    task_id=context.task_id,
                    content=accumulated_content,
                    status="completed"
                )
            )


    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a task."""
        if not self.current_task or self.current_task.task_id != task_id:
            return {
                "task_id": task_id,
                "status": "not_found"
            }
            
        return {
            "task_id": task_id,
            "status": self.current_task.state,
            "tool_calls": len(self.current_task.tool_calls),
            "errors": len(self.current_task.errors)
        }
        
    def cancel_task(self, task_id: str) -> Dict[str, Any]:
        """Cancel a running task."""
        if not self.current_task or self.current_task.task_id != task_id:
            return {
                "task_id": task_id,
                "status": "not_found"
            }
            
        self.current_task.state = "cancelled"
        self.state = AgentState.IDLE
        
        return {
            "task_id": task_id,
            "status": "cancelled"
        } 

    def _parse_action_type(self, content: str) -> str:
        """Parse action type from response content."""
        if any([x.lower() in content.lower() for x in ["search", 
                                                       "find", 
                                                       "read", 
                                                       "gather", 
                                                       "Information Gathering"]]):
            return "GATHER_INFO"
        elif any([x.lower() in content.lower() for x in ["edit", 
                                                        "modify", 
                                                        "update", 
                                                        "change",
                                                        "Code Modification"]]):
            return "MODIFY_CODE"
        elif any([x.lower() in content.lower() for x in ["execute", 
                                                        "run", 
                                                        "execute_tool",
                                                        "Tool Execution"]]):
            return "EXECUTE_TOOL"
        elif any([x.lower() in content.lower() for x in ["validate", 
                                                        "verify",
                                                        "Validation"]]):
            return "VALIDATE"
        elif any([x.lower() in content.lower() for x in ["recover", 
                                                        "error", 
                                                        "Error Recovery"]]):
            return "RECOVER"
        elif any([x.lower() in content.lower() for x in ["review", 
                                                        "Code Review"]]):
            return "CODE_REVIEW"
        elif any([x.lower() in content.lower() for x in ["suggest", 
                                                        "Code Suggestion"]]):
            return "CODE_SUGGESTION"
        elif any([x.lower() in content.lower() for x in ["cleanup", 
                                                        "Cleanup After Task"]]):
            return "CLEANUP_AFTER_TASK"
        elif any([x.lower() in content.lower() for x in ["report", 
                                                        "Report Completion"]]):
            return "REPORT_COMPLETION"
        else:
            return "TERMINATE"

    async def _select_action(self, context: TaskContext, last_result: str="") -> Dict[str, Any]:
        """Select next action based on context and last result."""
        try:

           # Create action selection message
            messages = [
                Message(
                    role="user",
                    content=AGENT_PROMPTS["action_selection"].format(
                        task=context.description,
                        state=context.state,
                        last_result=last_result
                    ),
                    metadata={"type": "action_selection"}
                )
            ]
            
            # Get action selection response
            try:
                response = await self.llm_client.generate(
                    messages=messages,
                    temperature=0.7,
                    metadata={"type": "action_selection"}
                )
            except Exception as e:
                logger.error(f"Error in action selection LLM generation: {e}")
                response = None

            # Ensure we have content in the response
            if not response or not hasattr(response, 'content'):
                logger.error("Invalid response format from LLM")
                action_type = "UNKNOWN"    
            else:
                # Parse the action type from content
                action_type = self._parse_action_type(response.content)

            if action_type not in ACTION_TYPES:
                action_type = "UNKNOWN"
            
            # Get prompt and description for the action type
            prompt = ACTION_TYPES[action_type]["prompt"].format(
                        task=context.description,
                        state=context.state,
                        last_result=last_result,
                        context="",
                        tools=list(FUNCTION_SCHEMAS.keys()),
                        error=context.errors,
                        action_type=action_type,
                        actions=context.actions
                    )
            description = ACTION_TYPES[action_type]["description"]

            # Parse selected action
            action = {
                "type": action_type,                
                "description": description,
                "timestamp": datetime.now().isoformat()
            }

            logger.good(f"Selected action: {action}")
            
            # Update context
            context.actions.append(action)

            # add the prompt to the action
            action["prompt"] = prompt

            return action        

        except Exception as e:
            logger.error(f"Error in action selection: {e}")
            # Parse selected action
            action = {
                "type": 'UNKNOWN',
                "prompt": '',
                "description": '',
                "timestamp": datetime.now().isoformat()
            }
            return action

    async def _select_tool(self, action: Dict[str, Any], context: TaskContext) -> Optional[Dict[str, Any]]:
        """Select appropriate tool based on action."""
        try:
            # Create tool selection message
            message = Message(
                role="user",
                content=AGENT_PROMPTS["tool_selection"].format(
                    action_type=action["type"],
                    context=context.to_dict(),
                    tools=list(FUNCTION_SCHEMAS.keys())
                ),
                metadata={"type": "tool_selection"}
            )
            
            # Get tool selection response
            response = await self.llm_client.generate(
                messages=[message],
                functions=list(FUNCTION_SCHEMAS.values()),
                temperature=0.1,  # Very low temperature for consistent selection
                metadata={"type": "tool_selection"}
            )
            # Ensure we have content and proper response structure
            if not response or not hasattr(response, 'content'):
                logger.error("Invalid tool selection response format")
                return None

            # Parse tool selection from content
            content = response.content
            metadata = response.metadata if hasattr(response, 'metadata') else {}

            # Parse function call if present
            if response.function_call:
                return {
                    "name": response.function_call.name,
                    "parameters": response.function_call.parameters,
                    "content": content,
                    "timestamp": datetime.now().isoformat(),
                    "metadata": metadata
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error in tool selection: {e}")
            return None

    async def get_task_progress(self, task_id: str) -> Dict[str, Any]:
        """Get detailed task progress."""
        if not self.current_task or self.current_task.task_id != task_id:
            raise ValueError("Task not found")
            
        total_steps = len(self.current_task.tool_calls) + len(self.current_task.messages)
        completed_steps = sum(1 for call in self.current_task.tool_calls if call.get("completed_at"))
        
        return {
            "task_id": task_id,
            "progress": completed_steps / total_steps if total_steps > 0 else 0,
            "current_step": self.state.value,
            "completed_steps": completed_steps,
            "total_steps": total_steps,
            "started_at": self.current_task.created_at,
            "updated_at": datetime.now(),
            "estimated_completion": self._estimate_completion_time(),
            "performance_metrics": self._get_performance_metrics()
        }

    def _estimate_completion_time(self) -> Optional[datetime]:
        """Estimate task completion time based on progress."""
        if not self.current_task:
            return None
            
        elapsed = datetime.now() - self.current_task.created_at
        completed_steps = sum(1 for call in self.current_task.tool_calls if call.get("completed_at"))
        total_steps = len(self.current_task.tool_calls) + len(self.current_task.messages)
        
        if completed_steps == 0 or total_steps == 0:
            return None
            
        avg_step_time = elapsed / completed_steps
        remaining_steps = total_steps - completed_steps
        estimated_remaining = avg_step_time * remaining_steps
        
        return datetime.now() + estimated_remaining

    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        if not self.current_task:
            return {}
            
        return {
            "avg_step_time": self._calculate_avg_step_time(),
            "error_rate": self._calculate_error_rate(),
            "memory_usage": self._get_memory_usage(),
            "token_usage": self._get_token_usage()
        }

    async def get_chain_state(self, task_id: str) -> Dict[str, Any]:
        """Get chain execution state."""
        chain = self.chain_manager.get_chain(task_id)
        if not chain:
            raise ValueError("Chain not found")
            
        return {
            "chain_id": chain.chain_id,
            "status": chain.status,
            "current_step": chain.current_step.name if chain.current_step else None,
            "steps": [step.to_dict() for step in chain.steps],
            "messages": [msg.dict() for msg in chain.messages],
            "execution_graph": chain.get_execution_graph(),
            "dependencies": chain.get_dependencies()
        }

    async def get_tool_history(self, task_id: str) -> Dict[str, Any]:
        """Get tool execution history."""
        if not self.current_task or self.current_task.task_id != task_id:
            raise ValueError("Task not found")
            
        return {
            "task_id": task_id,
            "tools": self.current_task.tool_calls,
            "stats": self._calculate_tool_stats(),
            "performance": self._get_tool_performance(),
            "resource_usage": self._get_resource_usage()
        }

    def _calculate_tool_stats(self) -> Dict[str, Any]:
        """Calculate tool usage statistics."""
        if not self.current_task:
            return {}
            
        stats = {}
        for call in self.current_task.tool_calls:
            tool_name = call.get("name")
            if tool_name not in stats:
                stats[tool_name] = {
                    "count": 0,
                    "success": 0,
                    "failure": 0,
                    "avg_duration": 0
                }
            
            stats[tool_name]["count"] += 1
            if call.get("error"):
                stats[tool_name]["failure"] += 1
            else:
                stats[tool_name]["success"] += 1
                
            if call.get("completed_at") and call.get("started_at"):
                duration = (call["completed_at"] - call["started_at"]).total_seconds()
                stats[tool_name]["avg_duration"] = (
                    (stats[tool_name]["avg_duration"] * (stats[tool_name]["count"] - 1) + duration)
                    / stats[tool_name]["count"]
                )
                
        return stats

    async def get_task_metrics(self, task_id: str) -> Dict[str, Any]:
        """Get task performance metrics."""
        if not self.current_task or self.current_task.task_id != task_id:
            raise ValueError("Task not found")
            
        return {
            "task_id": task_id,
            "execution_time": self._get_execution_time(),
            "memory_usage": self._get_memory_usage(),
            "token_usage": self._get_token_usage(),
            "tool_stats": self._calculate_tool_stats(),
            "error_rates": self._calculate_error_rates()
        }

    async def retry_task(self, task_id: str) -> Dict[str, Any]:
        """Retry a failed task."""
        if not self.current_task or self.current_task.task_id != task_id:
            raise ValueError("Task not found")
            
        if self.state != AgentState.ERROR:
            raise ValueError("Task is not in error state")
            
        # Reset state
        self.state = AgentState.IDLE
        self.current_task.errors = []
        
        # Re-execute task
        return await self.execute_task(
            task_description=self.current_task.description,
            context=self.current_task
        )

    async def list_active_tasks(self) -> List[Dict[str, Any]]:
        """List all active tasks."""
        active_tasks = []
        
        if self.current_task and self.state != AgentState.IDLE:
            active_tasks.append({
                "task_id": self.current_task.task_id,
                "state": self.state.value,
                "description": self.current_task.description,
                "started_at": self.current_task.created_at.isoformat()
            })
            
        return active_tasks

    async def stream_updates(self, task_id: str) -> AsyncIterator[Dict[str, Any]]:
        """Stream task execution updates."""
        if not self.current_task or self.current_task.task_id != task_id:
            raise ValueError("Task not found")
            
        while self.state != AgentState.IDLE:
            # Yield progress update
            yield {
                "type": "progress",
                "data": await self.get_task_progress(task_id),
                "timestamp": datetime.now()
            }
            
            # Yield tool execution updates
            if self.current_task.tool_calls:
                latest_tool = self.current_task.tool_calls[-1]
                yield {
                    "type": "tool",
                    "data": latest_tool,
                    "timestamp": datetime.now()
                }
                
            # Yield chain state updates
            try:
                chain_state = await self.get_chain_state(task_id)
                yield {
                    "type": "chain",
                    "data": chain_state,
                    "timestamp": datetime.now()
                }
            except ValueError:
                pass
                
            await asyncio.sleep(0.1)

    def _calculate_avg_step_time(self) -> float:
        """Calculate average step execution time."""
        if not self.current_task or not self.current_task.tool_calls:
            return 0.0
            
        total_time = 0.0
        count = 0
        
        for call in self.current_task.tool_calls:
            if call.get("completed_at") and call.get("started_at"):
                total_time += (call["completed_at"] - call["started_at"]).total_seconds()
                count += 1
                
        return total_time / count if count > 0 else 0.0

    def _calculate_error_rate(self) -> float:
        """Calculate error rate for tool executions."""
        if not self.current_task or not self.current_task.tool_calls:
            return 0.0
            
        total_calls = len(self.current_task.tool_calls)
        error_count = sum(1 for call in self.current_task.tool_calls if call.get("error"))
        
        return error_count / total_calls if total_calls > 0 else 0.0

    def _get_memory_usage(self) -> Dict[str, float]:
        """Get memory usage metrics."""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                "rss": memory_info.rss / 1024 / 1024,  # MB
                "vms": memory_info.vms / 1024 / 1024,  # MB
                "percent": process.memory_percent()
            }
        except ImportError:
            return {"error": "psutil not available"}

    def _get_token_usage(self) -> Dict[str, int]:
        """Get token usage metrics."""
        if not self.current_task:
            return {"total": 0, "prompt": 0, "completion": 0}
            
        total_tokens = 0
        prompt_tokens = 0
        completion_tokens = 0
        
        for msg in self.current_task.messages:
            if msg.metadata.get("token_usage"):
                usage = msg.metadata["token_usage"]
                total_tokens += usage.get("total_tokens", 0)
                prompt_tokens += usage.get("prompt_tokens", 0)
                completion_tokens += usage.get("completion_tokens", 0)
                
        return {
            "total": total_tokens,
            "prompt": prompt_tokens,
            "completion": completion_tokens
        }

    def _get_execution_time(self) -> float:
        """Get total execution time in seconds."""
        if not self.current_task:
            return 0.0
        
        if self.current_task.completed_at:
            return (self.current_task.completed_at - self.current_task.created_at).total_seconds()
        else:
            return (datetime.now() - self.current_task.created_at).total_seconds()

    def _calculate_error_rates(self) -> Dict[str, float]:
        """Calculate detailed error rates."""
        if not self.current_task:
            return {}
            
        total_operations = len(self.current_task.tool_calls) + len(self.current_task.messages)
        if total_operations == 0:
            return {
                "overall": 0.0,
                "tool_calls": 0.0,
                "messages": 0.0
            }
            
        tool_errors = sum(1 for call in self.current_task.tool_calls if call.get("error"))
        message_errors = sum(1 for msg in self.current_task.messages if msg.metadata.get("error"))
        
        return {
            "overall": (tool_errors + message_errors) / total_operations,
            "tool_calls": tool_errors / len(self.current_task.tool_calls) if self.current_task.tool_calls else 0.0,
            "messages": message_errors / len(self.current_task.messages) if self.current_task.messages else 0.0
        }

    def _get_tool_performance(self) -> Dict[str, float]:
        """Get tool performance metrics."""
        if not self.current_task:
            return {}
            
        return {
            "avg_execution_time": self._calculate_avg_step_time(),
            "success_rate": 1.0 - self._calculate_error_rate(),
            "throughput": len(self.current_task.tool_calls) / self._get_execution_time() if self._get_execution_time() > 0 else 0.0
        }
        
    def _get_resource_usage(self) -> Dict[str, Any]:
        """Get resource usage metrics."""
        return {
            "memory": self._get_memory_usage(),
            "tokens": self._get_token_usage(),
            "execution_time": self._get_execution_time()
        }

    async def _create_chain_step(
        self,
        name: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChainStep:
        """Create a new chain step."""
        return ChainStep(
            name=name,
            description=description,
            status=ChainStepStatus.PENDING,
            metadata=metadata or {}
        ) 
    
    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task by ID."""
        task = await self.task_storage.get_task(task_id)
        return task.to_dict() if task else None
        
    async def list_tasks(
        self,
        limit: int = 100,
        offset: int = 0,
        state: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List tasks."""
        tasks = await self.task_storage.list_tasks(limit, offset, state)
        return [task.to_dict() for task in tasks] 

    def _compose_system_prompt(self) -> str:
        """Compose the system prompt for the agent."""
        return "\n\n".join([
            SYSTEM_PROMPT,
            COMMUNICATION_RULES,
            TOOL_CALLING_RULES,
            SEARCH_AND_READING_RULES,
            CODE_CHANGE_RULES,
            DEBUGGING_RULES,
            API_RULES
        ]) 