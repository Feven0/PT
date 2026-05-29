"""Application main entry point."""

import os
import asyncio
import signal
import sys, traceback
import json
from typing import Set, Any, Dict, Optional, Union
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio

from core.logging import BackendLogger
from core.config import AppConfig, load_env_file
from core.di import Container, container_context
from core.middleware import ErrorHandlingMiddleware
from core.middleware import ContextMiddleware
from core.middleware import RequestProcessingMiddleware
from core.middleware import UnifiedMiddleware
from core.middleware import HealthCheckMiddleware
from tests.mock_config import create_mock_config
from api.v2 import router as v2_router
from core.websocket.socketio_manager import SocketIOManager

logger = BackendLogger(name="main")


class Application:
    """Application class."""

    def __init__(self, config: AppConfig):
        """Initialize application.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.container = Container(config)
        self._shutdown_event = asyncio.Event()
        self._shutdown_timeout = timedelta(seconds=config.server.graceful_timeout)
        self._active_connections: Dict[str, asyncio.Task] = {}
        self._shutdown_signals: Set[signal.Signals] = {
            signal.SIGINT,
            signal.SIGTERM
        }  # Reduce to essential shutdown signals
        self.app = self._create_app()

    def _track_connection(self, conn_id: str, task: asyncio.Task) -> None:
        """Track active connection.
        
        Args:
            conn_id: Connection identifier
            task: Connection task
        """
        self._active_connections[conn_id] = task
        task.add_done_callback(
            lambda _: self._active_connections.pop(conn_id, None)
        )

    async def _close_connections(self) -> None:
        """Close active connections gracefully."""
        if not self._active_connections:
            return

        logger.info(
            "closing_active_connections",
            context="main",
            connection_count=len(self._active_connections)
        )

        # Cancel all active connections
        for conn_id, task in self._active_connections.items():
            task.cancel()

        # Wait for connections to close
        if self._active_connections:
            try:
                await asyncio.wait(
                    list(self._active_connections.values()),
                    timeout=self._shutdown_timeout.total_seconds()
                )
            except asyncio.TimeoutError:
                logger.warning(
                    "connection_close_timeout",
                    context="main",
                    remaining_connections=len(self._active_connections)
                )

    async def _shutdown(self) -> None:
        """Shutdown application with timeout."""
        if hasattr(self, '_shutting_down') and self._shutting_down:
            return
            
        self._shutting_down = True
        
        timeout = self._shutdown_timeout.total_seconds()
        logger.info(
            "starting_shutdown_sequence",
            context="main"
        )
        
        try:
            # 1. Stop accepting new requests in middleware
            logger.info("stopping_middleware", context="main")
            for middleware in self.app.user_middleware:
                if hasattr(middleware, 'cleanup'):
                    try:
                        await asyncio.wait_for(
                            middleware.cleanup(),
                            timeout=5.0
                        )
                    except Exception as e:
                        logger.error(f"middleware_cleanup_error: {str(e)}")

            # 2. Close active connections
            logger.info("closing_connections", context="main")
            try:
                await asyncio.wait_for(
                    self._close_connections(),
                    timeout=5.0
                )
            except asyncio.TimeoutError:
                logger.error("connections_close_timeout", context="main")
            except Exception as e:
                logger.error(f"connections_close_error: {str(e)}", context="main")

            # 3. Stop container components
            logger.info("stopping_container", context="main")
            try:
                await asyncio.wait_for(
                    self.container.stop(),
                    timeout=10.0
                )
            except asyncio.TimeoutError:
                logger.error("container_stop_timeout", context="main")
            except Exception as e:
                logger.error(f"container_stop_error: {str(e)}", context="main")

            # 4. Final cleanup
            logger.info("cleaning_up", context="main")
            try:
                await asyncio.wait_for(
                    self.container.cleanup(),
                    timeout=10.0
                )
            except asyncio.TimeoutError:
                logger.error("cleanup_timeout", context="main")
            except Exception as e:
                logger.error(f"cleanup_error: {str(e)}", context="main")

            logger.info("shutdown_complete", context="main")

        except Exception as e:
            logger.error(
                "shutdown_failed",
                context="main",
                error=str(e)
            )
        finally:
            # Force exit after a final timeout
            def force_exit():
                logger.warning("forcing_exit", context="main")
                os._exit(0)
                
            loop = asyncio.get_event_loop()
            loop.call_later(5.0, force_exit)

    def _handle_signal(self, signum: int, frame: Any) -> None:
        """Handle shutdown signal."""
        if hasattr(self, '_shutting_down') and self._shutting_down:
            # If already shutting down and get another signal, force exit
            logger.warning("forced_shutdown_requested", context="main")
            os._exit(0)
            
        logger.info(
            "shutdown_signal_received",
            context="main",
            signal=signal.Signals(signum).name
        )
        
        # Set shutdown event
        self._shutdown_event.set()

    @asynccontextmanager
    async def _lifespan(self, app: FastAPI):
        """Application lifespan manager."""
        logger.info(
            "starting application",
            context="lifespan"
        )
        
        # Set container context
        with container_context(self.container):
            try:
                # Add debug logging
                logger.info(
                    "initializing container components",
                    context="lifespan",
                    components=list(self.container._components.keys())
                )
                
                # Initialize and start container                
                await self.container.initialize()
                await self.container.start()             
                
                # Verify initialization
                if not self.container.socketio_manager._initialized:
                    raise RuntimeError("SocketIOManager failed to initialize")


                app = self.container.socketio_manager.create_asgi_app(app)   

                logger.info(
                    "application_started",
                    context="lifespan"
                )
                
                yield
                
                # Initiate shutdown sequence
                logger.info("lifespan_context_exit", context="lifespan")
                await self._shutdown()
                
            except Exception as e:
                logger.error(
                    "lifespan_startup_failed",
                    context="lifespan",
                    error=str(e)
                )
                raise
            finally:
                # Ensure shutdown happens even on errors
                if not hasattr(self, '_shutting_down'):
                    await self._shutdown()

    def _setup_middleware(self, app: FastAPI) -> None:
        """Setup middleware stack in correct order.
        
        Args:
            app: FastAPI application instance
        """
        logger.info("setting up middleware", context="middleware")

        # 1. CORS middleware (must be first to handle preflight)
        if self.config.cors.enabled:
            cors_config = self.config.cors.to_dict(core=False)        
            app.add_middleware(
                CORSMiddleware,
                **cors_config
            )
        else:
            logger.info('CORS is disabled')
        
        # 2. Error handling (catch all errors)
        app.add_middleware(
            ErrorHandlingMiddleware,
            metrics=self.container.metrics_manager
        )
        
        # 3. Context middleware (establish request context)
        app.add_middleware(
            ContextMiddleware,
            metrics=self.container.metrics_manager
        )
        
        # 4. Request processing (rate limiting, timeouts)
        app.add_middleware(
            RequestProcessingMiddleware,
            metrics=self.container.metrics_manager
        )
        
        # 5. Health checks
        app.add_middleware(
            HealthCheckMiddleware,
            metrics=self.container.metrics_manager
        )
        
        # 6. Unified middleware (compression, caching)
        app.add_middleware(
            UnifiedMiddleware,
            metrics=self.container.metrics_manager
        )

        logger.info("middleware setup complete", 
                    middleware_count=len(app.user_middleware),
                    middleware_names=list([type(middleware).__name__ for middleware in app.user_middleware]),
                    context="middleware")


    
    def _create_app(self) -> Union[FastAPI, socketio.ASGIApp]:
        """Create FastAPI application.
        
        Returns:
            FastAPI application instance
        """
        app = FastAPI(
            title=self.config.server.name,
            description=self.config.server.description,
            version=self.config.server.version,
            lifespan=self._lifespan
        )
        
        # Setup middleware
        #self._setup_middleware(app)
        
        # Include API routers
        #app.include_router(v1_router)
        app.include_router(v2_router)
        
        return app

    def run(self) -> None:
        """Run application."""
        import uvicorn
        
        # Run server with proper shutdown timeout
        uvicorn.run(
            app=self.app,
            host=self.config.server.host,
            port=self.config.server.port,
            reload=self.config.server.reload,
            workers=self.config.server.workers,
            timeout_keep_alive=self.config.server.keep_alive_timeout,
            timeout_graceful_shutdown=15,  # 15 seconds max for graceful shutdown
            log_level="info",
            access_log=True,
            use_colors=True,
            loop="auto"
        )


def main(run=False) -> None:
    """Application entry point."""
    try:
        # Load environment variables
        load_env_file()
        
        # Add debug logging
        logger.debug(
            "loading_configuration",
            context="main"
        )
        
        if os.getenv("USE_MOCK_CONFIG", "false").lower() == "true":
            # Load mock configuration
            config = create_mock_config()
        else:
            # Load configuration
            config = AppConfig.from_env()
        
        logger.debug(
            "configuration_loaded",
            context="main",
            config_sections=list(config.model_dump().keys())
        )
        
        # Create and start application
        application = Application(config)

        if run:
            application.run()
        else:
            return application.app  # Return the FastAPI instance instead of Application instance
        
    except Exception as e:
        print("*** print_exception:")
        traceback.print_exception(e, limit=2, file=sys.stdout)
        logger.error(
            "application_failed",
            context="main",
            error=json.dumps({'error': str(e), 'error_type': type(e).__name__, 'error_traceback': str(e.__traceback__.tb_frame)}),
        )
        sys.exit(1)
        
app = main(run=False)  # This will now be the FastAPI instance

if __name__ == "__main__":
    main(run=True) 