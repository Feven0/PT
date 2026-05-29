"""Unified middleware component."""
import gzip
import json
from typing import Optional, Dict, Any, List
from starlette.types import ASGIApp, Receive, Scope, Send
from starlette.datastructures import Headers, MutableHeaders
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from core.telemetry.metrics import MetricsManager
from core.logging import BackendLogger
from core.types.metrics import MetricType

from .base import MiddlewareComponent


class UnifiedMiddleware(MiddlewareComponent):
    """Middleware combining security, compression, and caching."""
    
    def __init__(
        self,
        app: ASGIApp,
        metrics: Optional[MetricsManager] = None,
        logger: Optional[BackendLogger] = None,
        security_headers: Optional[Dict[str, str]] = None,
        compression_min_size: int = 1024,
        cache_ttl: int = 3600,
        exclude_paths: Optional[List[str]] = None,
        **kwargs
    ):
        super().__init__(
            app=app,
            name="unified_middleware",
            metrics=metrics,
            logger=logger,
            order=2,  # Run after request processing
            **kwargs
        )
        self.security_headers = security_headers or {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }
        self.compression_min_size = compression_min_size
        self.cache_ttl = cache_ttl
        self.exclude_paths = exclude_paths or []
        
    async def _process_request(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Process the request with security, compression, and caching."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
            
        path = scope.get("path", "")
        if path in self.exclude_paths:
            await self.app(scope, receive, send)
            return
            
        # Get request headers
        headers = Headers(scope=scope)
        
        # Check cache
        cache_key = self._get_cache_key(scope)
        cached_response = await self._get_cached_response(cache_key)
        if cached_response:
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_cache_hits",
                    1,
                    labels={"path": scope.get("path", ""), "method": scope.get("method", "")}
                )
            await self._send_response(send, cached_response)
            return
        
        # Create response interceptor
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                # Add security headers
                headers = MutableHeaders(scope=message)
                self._add_security_headers(headers)
                
                # Add caching headers
                self._add_cache_headers(scope, headers)
                
            elif message["type"] == "http.response.body":
                # Compress response if needed
                body = message.get("body", b"")
                if self._should_compress(scope, len(body)):
                    body = self._compress_body(body)
                    message["body"] = body
                    
                    # Update compression metrics
                    self._update_compression_metrics(scope, len(message.get("body", b"")), len(body))
                
                # Cache response if needed
                if self._should_cache(scope):
                    await self._cache_response(cache_key, message)
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)
    
    def _add_security_headers(self, headers: MutableHeaders) -> None:
        """Add security headers to response."""
        for name, value in self.security_headers.items():
            headers.append(name, value)
    
    def _add_cache_headers(self, scope: Scope, headers: MutableHeaders) -> None:
        """Add caching headers to response."""
        if self._should_cache(scope):
            headers.append("Cache-Control", f"public, max-age={self.cache_ttl}")
        else:
            headers.append("Cache-Control", "no-store, must-revalidate")
            headers.append("Pragma", "no-cache")
            headers.append("Expires", "0")
    
    def _should_compress(self, scope: Scope, body_size: int) -> bool:
        """Check if response should be compressed."""
        if body_size < self.compression_min_size:
            return False
            
        headers = Headers(scope=scope)
        if "gzip" not in headers.get("accept-encoding", ""):
            return False
            
        return True
    
    def _compress_body(self, body: bytes) -> bytes:
        """Compress response body."""
        return gzip.compress(body)
    
    def _should_cache(self, scope: Scope) -> bool:
        """Check if response should be cached."""
        headers = Headers(scope=scope)
        if "authorization" in headers:
            return False
            
        if scope["method"] not in ["GET", "HEAD"]:
            return False
            
        path = scope.get("path", "")
        if any(path.startswith(prefix) for prefix in ["/static/", "/media/"]):
            return True
            
        return False
    
    def _get_cache_key(self, scope: Scope) -> str:
        """Generate cache key for request."""
        return f"{scope['method']}:{scope['path']}"
    
    async def _get_cached_response(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached response."""
        # TODO: Implement caching
        return None
    
    async def _cache_response(self, key: str, response: Dict[str, Any]) -> None:
        """Cache response."""
        # TODO: Implement caching
        pass
    
    def _update_compression_metrics(
        self,
        scope: Scope,
        original_size: int,
        compressed_size: int,
        content_type: str = ""
    ) -> None:
        """Update compression metrics."""
        if original_size > 0:
            ratio = compressed_size / original_size
            if self.metrics:
                self.metrics.record(
                    f"{self.name}_compression_ratio",
                    ratio,
                    labels={
                        "method": scope.get("method", ""),
                        "path": scope.get("path", ""),
                        "content_type": content_type
                    }
                )
    
    async def _initialize_impl(self) -> None:
        """Initialize middleware."""
        await super()._initialize_impl()
        # TODO: Initialize cache if needed
    
    async def _stop_impl(self) -> None:
        """Stop middleware."""
        await super()._stop_impl()
        # TODO: Cleanup cache if needed
    
    def update_security_headers(self, headers: Dict[str, str]) -> None:
        """Update security headers configuration."""
        self.security_headers.update(headers)
    
    def update_compression_config(self, min_size: int) -> None:
        """Update compression configuration."""
        self.compression_min_size = min_size
    
    def update_cache_config(self, ttl: int) -> None:
        """Update cache configuration."""
        self.cache_ttl = ttl
    
    def update_exclude_paths(self, paths: List[str]) -> None:
        """Update excluded paths."""
        self.exclude_paths = paths 
    
    def _register_request_metrics_impl(self) -> None:
        """Register unified middleware specific metrics."""
        if not self.metrics:
            return
            
        # Cache hits
        self.metrics.register_metric(
            name=f"{self.name}_cache_hits",
            type=MetricType.COUNTER,
            description=f"Number of cache hits in {self.name}",
            component=self.name,
            labels={"method": "", "path": "", "status": ""}
        )
        
        # Cache misses
        self.metrics.register_metric(
            name=f"{self.name}_cache_misses",
            type=MetricType.COUNTER,
            description=f"Number of cache misses in {self.name}",
            component=self.name,
            labels={"method": "", "path": "", "status": ""}
        )
        
        # Compression ratio
        self.metrics.register_metric(
            name=f"{self.name}_compression_ratio",
            type=MetricType.HISTOGRAM,
            description=f"Response compression ratio in {self.name}",
            component=self.name,
            labels={"method": "", "path": "", "content_type": ""}
        )
        
        # Security header additions
        self.metrics.register_metric(
            name=f"{self.name}_security_headers_added",
            type=MetricType.COUNTER,
            description=f"Number of security headers added in {self.name}",
            component=self.name,
            labels={"method": "", "path": "", "header": ""}
        ) 
    