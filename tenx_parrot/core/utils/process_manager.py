"""Process management for tool execution."""
from typing import Dict, Optional, Any, List
import asyncio
import logging
import signal
import psutil
from datetime import datetime
from dataclasses import dataclass, field

from core.base.manager import BaseManager

logger = logging.getLogger(__name__)

@dataclass
class ProcessInfo:
    """Information about a running process."""
    process_id: str
    command: str
    start_time: datetime
    end_time: Optional[datetime] = None
    exit_code: Optional[int] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class ProcessManager(BaseManager):
    """Manages tool process execution."""
    
    def __init__(self, max_processes: int = 10):
        """Initialize process manager."""
        super().__init__()
        self.max_processes = max_processes
        self.processes: Dict[str, ProcessInfo] = {}
        self.active_processes: Dict[str, asyncio.subprocess.Process] = {}
        self.semaphore = asyncio.Semaphore(max_processes)
        
    async def initialize(self) -> None:
        """Initialize the process manager."""
        self.initialized = True
        logger.info(
            f"Process manager initialized (max processes: {self.max_processes})"
        )
        
    async def cleanup(self) -> None:
        """Clean up process manager."""
        # Terminate all running processes
        for process_id in list(self.active_processes.keys()):
            await self.terminate_process(process_id)
            
        self.processes.clear()
        self.active_processes.clear()
        self.initialized = False
        logger.info("Process manager cleaned up")
        
    async def run_process(
        self,
        command: str,
        process_id: Optional[str] = None,
        shell: bool = True,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None
    ) -> ProcessInfo:
        """Run a process."""
        if not process_id:
            process_id = f"proc_{len(self.processes)}"
            
        async with self.semaphore:
            try:
                process = await asyncio.create_subprocess_shell(
                    command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    shell=shell,
                    cwd=cwd,
                    env=env
                )
                
                info = ProcessInfo(
                    process_id=process_id,
                    command=command,
                    start_time=datetime.now()
                )
                self.processes[process_id] = info
                self.active_processes[process_id] = process
                
                try:
                    stdout, stderr = await asyncio.wait_for(
                        process.communicate(),
                        timeout=timeout
                    )
                    
                    info.end_time = datetime.now()
                    info.exit_code = process.returncode
                    info.metadata.update({
                        "stdout": stdout.decode() if stdout else "",
                        "stderr": stderr.decode() if stderr else ""
                    })
                    
                except asyncio.TimeoutError:
                    await self.terminate_process(process_id)
                    info.error = f"Process timed out after {timeout}s"
                    
                except Exception as e:
                    info.error = str(e)
                    
                finally:
                    self.active_processes.pop(process_id, None)
                    
                return info
                
            except Exception as e:
                logger.error(f"Failed to start process: {e}")
                info = ProcessInfo(
                    process_id=process_id,
                    command=command,
                    start_time=datetime.now(),
                    end_time=datetime.now(),
                    error=str(e)
                )
                self.processes[process_id] = info
                return info
                
    async def terminate_process(
        self,
        process_id: str,
        force: bool = False
    ) -> None:
        """Terminate a running process."""
        process = self.active_processes.get(process_id)
        if not process:
            return
            
        info = self.processes.get(process_id)
        if info:
            info.end_time = datetime.now()
            
        try:
            if force:
                process.kill()
            else:
                process.terminate()
                
            try:
                await asyncio.wait_for(process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                process.kill()
                
        except ProcessLookupError:
            pass
        except Exception as e:
            logger.error(f"Error terminating process {process_id}: {e}")
            
        self.active_processes.pop(process_id, None)
        
    def get_process_info(self, process_id: str) -> Optional[ProcessInfo]:
        """Get information about a process."""
        return self.processes.get(process_id)
        
    def list_active_processes(self) -> List[ProcessInfo]:
        """List all active processes."""
        return [
            info for info in self.processes.values()
            if info.process_id in self.active_processes
        ]
        
    def get_process_stats(self, process_id: str) -> Optional[Dict[str, Any]]:
        """Get process statistics."""
        process = self.active_processes.get(process_id)
        if not process or process.returncode is not None:
            return None
            
        try:
            proc = psutil.Process(process.pid)
            with proc.oneshot():
                return {
                    "cpu_percent": proc.cpu_percent(),
                    "memory_percent": proc.memory_percent(),
                    "memory_info": proc.memory_info()._asdict(),
                    "num_threads": proc.num_threads(),
                    "status": proc.status()
                }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None
            
    async def wait_for_process(
        self,
        process_id: str,
        timeout: Optional[float] = None
    ) -> Optional[ProcessInfo]:
        """Wait for a process to complete."""
        process = self.active_processes.get(process_id)
        if not process:
            return self.processes.get(process_id)
            
        try:
            await asyncio.wait_for(process.wait(), timeout=timeout)
        except asyncio.TimeoutError:
            return None
            
        return self.processes.get(process_id) 