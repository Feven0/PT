# Logging System

## Overview

The application uses Python's built-in logging module with enhanced formatting and structured logging support. The logging system provides consistent, informative, and configurable logging across all components.

## Features

1. **Structured Logging**
   - JSON format support
   - Context propagation
   - Metadata enrichment
   - Correlation IDs

2. **Color Support**
   - Level-based colors
   - Context-based colors
   - Custom color schemes
   - Terminal detection

3. **Multiple Outputs**
   - Console output
   - File output
   - JSON format
   - Custom formatters

4. **Log Levels**
   - DEBUG
   - INFO
   - WARNING
   - ERROR
   - CRITICAL

## Implementation

### LogFormatter

Custom formatter with color support:

```python
class LogFormatter(logging.Formatter):
    """Custom log formatter with color support."""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def __init__(self, use_colors: bool = True):
        """Initialize formatter."""
        super().__init__()
        self.use_colors = use_colors
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with optional color."""
        # Add timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
        
        # Format context
        context = getattr(record, 'context', '')
        context_str = f"[{context}] " if context else ""
        
        # Format extra data
        extra_data = {}
        for key, value in record.__dict__.items():
            if key not in logging.LogRecord.__dict__ and key not in ['context', 'msg', 'args']:
                extra_data[key] = value
        extra_str = f" {json.dumps(extra_data)}" if extra_data else ""
        
        # Build message
        message = f"{timestamp} {record.levelname:8} {context_str}{record.getMessage()}{extra_str}"
        
        # Add color if enabled
        if self.use_colors:
            color_code = self.COLORS.get(record.levelname, '')
            reset_code = self.COLORS['RESET']
            message = f"{color_code}{message}{reset_code}"
        
        return message
```

### BackendLogger

Enhanced logger with structured logging:

```python
class BackendLogger:
    """Enhanced logger with structured logging and color support."""
    
    def __init__(
        self,
        name: str,
        format: str = "text",
        colors: Optional[Dict[str, str]] = None,
        timestamp: bool = True,
        level: str = "INFO",
        log_file: Optional[str] = None,
        use_colors: bool = True
    ):
        """Initialize the logger."""
        self.name = name
        self.format = format
        self.colors = colors or {}
        
        # Default colors for contexts
        self.default_colors = {
            "success": "bright_green",
            "error": "bright_red",
            "warning": "bright_yellow",
            "info": "bright_blue",
            "debug": "bright_cyan"
        }
        self.colors.update(self.default_colors)
        
        # Set up logging
        self.logger = setup_logging(
            name=name,
            level=level,
            log_file=log_file,
            use_colors=use_colors
        )
    
    def _log(self, 
             level: str, 
             message: str, 
             format: Optional[str] = None, 
             context: Optional[str] = None, 
             **kwargs):
        """Core logging function."""
        if context is None:
            context = level
            
        # Log message with context and metadata
        self.logger.log(
            getattr(logging, level.upper()),
            message,
            extra={'context': context, **kwargs}
        )
```

## Usage Examples

### Basic Logging

```python
logger = BackendLogger("app")

# Simple logging
logger.info("Application started")

# With context
logger.info("User logged in", context="auth", user_id="123")

# With metadata
logger.error(
    "Database connection failed",
    context="db",
    host="localhost",
    port=5432,
    error="Connection refused"
)
```

### Structured Logging

```python
logger = BackendLogger("app", format="json")

# Log structured data
logger.info(
    "Request processed",
    context="http",
    method="GET",
    path="/api/v1/resource",
    duration=0.123,
    status=200
)
```

### File Logging

```python
logger = BackendLogger(
    "app",
    log_file="app.log",
    use_colors=False
)

# Logs will be written to both console and file
logger.info("Application event")
```

### Custom Colors

```python
logger = BackendLogger(
    "app",
    colors={
        "http": "bright_blue",
        "db": "bright_magenta",
        "cache": "bright_cyan"
    }
)

# Each context will use its own color
logger.info("Cache hit", context="cache")
logger.info("Query executed", context="db")
logger.info("Request received", context="http")
```

## Best Practices

1. **Use Appropriate Levels**
   - DEBUG: Detailed information for debugging
   - INFO: General operational events
   - WARNING: Potential issues that don't affect operation
   - ERROR: Error events that might still allow operation
   - CRITICAL: Critical events that prevent operation

2. **Include Context**
   - Always set a meaningful context
   - Use consistent context names
   - Group related logs under same context
   - Add relevant metadata

3. **Structured Data**
   - Use JSON format for machine processing
   - Include all relevant fields
   - Use consistent field names
   - Avoid nested structures when possible

4. **Performance**
   - Use lazy evaluation for expensive operations
   - Avoid logging sensitive data
   - Clean up old log files
   - Monitor log volume

5. **Error Logging**
   - Include stack traces
   - Add error context
   - Log recovery actions
   - Track error frequency