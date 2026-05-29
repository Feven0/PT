"""Storage type definitions."""
from typing import Any, Dict, Optional, Protocol, runtime_checkable, Union, BinaryIO, List
from pathlib import Path

from core.types.protocols import InfrastructureProviderProtocol

StoragePath = Union[str, Path]


class StorageProviderProtocol(InfrastructureProviderProtocol, Protocol):
    """Protocol for storage providers."""
    
    async def upload_file(
        self,
        path: StoragePath,
        data: Union[bytes, BinaryIO],
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Upload file to storage."""
        ...
    
    async def download_file(
        self,
        path: StoragePath,
        destination: Optional[StoragePath] = None
    ) -> Union[bytes, None]:
        """Download file from storage."""
        ...
    
    async def delete_file(self, path: StoragePath) -> bool:
        """Delete file from storage."""
        ...
    
    async def exists(self, path: StoragePath) -> bool:
        """Check if file exists in storage."""
        ...
    
    async def list_files(
        self,
        prefix: str = "",
        recursive: bool = True
    ) -> List[str]:
        """List files in storage with optional prefix."""
        ...
    
    async def get_metadata(
        self,
        path: StoragePath
    ) -> Dict[str, Any]:
        """Get file metadata from storage."""
        ...
    
    async def update_metadata(
        self,
        path: StoragePath,
        metadata: Dict[str, Any]
    ) -> None:
        """Update file metadata in storage."""
        ...
    
    async def copy_file(
        self,
        src_path: StoragePath,
        dst_path: StoragePath
    ) -> None:
        """Copy file within storage."""
        ...
    
    async def move_file(
        self,
        src_path: StoragePath,
        dst_path: StoragePath
    ) -> None:
        """Move file within storage."""
        ... 