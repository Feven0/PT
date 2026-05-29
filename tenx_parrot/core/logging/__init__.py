"""Core logging module with enhanced formatting and structured logging support."""
import os, sys
import json
from pprint import pprint
import logging
import logging.config
from enum import Enum
from typing import Any, Dict, Optional, Union
from datetime import datetime
import functools
from pathlib import Path
from wasabi import Printer, color, wrap, table
from typing import List, Dict, Any



ROOT_DIR = Path(__file__).parent.parent.parent

class LogFormat(str, Enum):
    """Log format types."""
    TEXT = "text"
    TABLE = "table"
    JSON = "json"


class LogLevel(str, Enum):
    """Log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"



# ANSI color codes
COLORS_DICT: Dict[str, str] = {
    'debug': '\033[36m',     # Cyan
    'info': '\033[94m',      # BBlue
    'warning': '\033[33m',   # Yellow
    'error': '\033[31m',     # Red
    'critical': '\033[35m',  # Magenta
    'reset': '\033[0m',       # Reset

    # Basic colors
    'black': '\033[30m',
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'magenta': '\033[35m',
    'cyan': '\033[36m',
    'white': '\033[37m',
    'pink': '\033[95m',
    
    # Bright colors
    'bright_black': '\033[90m',
    'bright_red': '\033[91m',
    'bright_green': '\033[92m',
    'bright_yellow': '\033[93m',
    'bright_blue': '\033[94m',
    'bright_magenta': '\033[95m',
    'bright_cyan': '\033[96m',
    'bright_white': '\033[97m',
    
    # Background colors
    'bg_black': '\033[40m',
    'bg_red': '\033[41m',
    'bg_green': '\033[42m',
    'bg_yellow': '\033[43m',
    'bg_blue': '\033[44m',
    'bg_magenta': '\033[45m',
    'bg_cyan': '\033[46m',
    'bg_white': '\033[47m',
    
    # Styles
    'bold': '\033[1m',
    'dim': '\033[2m',
    'italic': '\033[3m',
    'underline': '\033[4m',
    'blink': '\033[5m',
    'reverse': '\033[7m',
    'hidden': '\033[8m',
    'strike': '\033[9m',
    
    # Reset
    'reset': '\033[0m'
}

def get_color_code(color_name: str) -> str:
    """Get ANSI color code for a given color name.
    
    Args:
        color_name: Name of the color
        
    Returns:
        ANSI color code
    """
    return COLORS_DICT.get(color_name.lower(), COLORS_DICT['reset'])

def colorize(text: str, 
             color: Optional[str] = None, 
             style: Optional[str] = None,
             iscode: bool = True) -> str:
    """Colorize text with ANSI color codes.
    
    Args:
        text: Text to colorize
        color: Color name
        style: Style name (bold, italic, etc.)
        iscode: Whether to text is an ANSI color code or a color name
    Returns:
        Colorized text
    """
    result = ""

    
    if color:
        if iscode:
            result += get_color_code(color)
        else:
            result += color

    if style:
        result += get_color_code(style)        
        
    result += text
    result += COLORS_DICT['reset']
    
    return result

class LogFormatter(logging.Formatter):
    """Custom log formatter with color support."""

    
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
        fg = getattr(record, 'fg', '')
        if not fg:
            fg = getattr(record, 'color', '')

        style = getattr(record, 'style', '')
        if not style:
            bold = getattr(record, 'bold', '')
            if bold:
                style = 'bold'

        if context.upper() != record.levelname.upper():
            context_str = f"[{context}] " if context else ""
        else:
            context_str = ""
                
        if record.levelname in ['ERROR', 'CRITICAL']:
            
            # Format extra data
            extra_data = {}
            for key, value in record.__dict__.items():
                if key not in logging.LogRecord.__dict__ and key not in ['context', 'msg', 'args'] and key in ["exc_info", "stack_info", "stacklevel", "extra", 'key', 'error', 'thread', 'threadName', 'process', 'processName', 'task']:
                    extra_data[key] = value
            extra_str = f" {json.dumps(extra_data)}" if extra_data else ""
            
            # Build message
            message = f"{timestamp} {record.levelname:8} {context_str}{record.getMessage()}{extra_str}"
        else:
            extra_data = record.__dict__.get('extra', {})
            extra_str = f" {json.dumps(extra_data)}" if extra_data else ""
            message = f"{timestamp} {record.levelname:8} {context_str}{record.getMessage()}{extra_str}"
        
        # Add color if enabled
        if self.use_colors:
            if fg:
                color_name = fg
            else:
                color_name = record.levelname.strip()
            
            message = colorize(message, color=color_name, style=style)
        
        return message


def setup_logging(
    name: str,
    level: str = "INFO",
    log_file: Optional[str] = None,
    use_colors: bool = True
) -> logging.Logger:
    """Set up logger with custom configuration.
    
    Args:
        name: Logger name
        level: Log level
        log_file: Optional log file path
        use_colors: Whether to use colors in output
        
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers.clear()
    

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(LogFormatter(use_colors=use_colors))
    logger.addHandler(console_handler)
    
    # Add file handler if specified
    if log_file:
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
            
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(LogFormatter(use_colors=False))
        logger.addHandler(file_handler)
    
    return logger


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
        """Initialize the logger.
        
        Args:
            name: Logger name
            format: Default format (text, table, json)
            colors: Color mapping for contexts
            timestamp: Whether to include timestamp
            level: Log level
            log_file: Optional log file path
            use_colors: Whether to use colors in output
        """
        self.name = name
        self.format = format
        self.colors = colors or {}
        self.printer = Printer(
            timestamp=timestamp,
            colors=colors
        )
        
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
    
    def get_logger(self):
        """Get the logger instance."""
        return self
    

    def _format(self, 
                level: str,
                message: str, 
                context: str = None, 
                use_colors: bool = False,
                **kwargs) -> str:
        
        """Format log record with optional color."""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        fg = kwargs.get('fg', '')
        if not fg:
            fg = kwargs.get('color', '')

        style = kwargs.get('style', '')
        if not style:
            bold = kwargs.get('bold', '')
            if bold:
                style = 'bold'

        # Format context
        context_str = f"[{context}] " if context else ""

                
        if level in ['ERROR', 'CRITICAL', 'FAIL', 'BAD']:
            # Format extra data
            extra_data = {}
            for key, value in kwargs.items():
                if key not in logging.LogRecord.__dict__ and key not in ['context', 'msg', 'args', 'fg', 'bg', 'bold'] and key in ["exc_info", "stack_info", "stacklevel", "extra", 'key', 'error', 'thread', 'threadName', 'process', 'processName', 'task']:
                    extra_data[key] = value
            extra_str = f" {json.dumps(extra_data)}" if extra_data else ""
            
            # Build message
            message = f"{timestamp} {level:8} {context_str}{message}{extra_str}"
        else:
            extra_data = kwargs.get('extra', {})
            extra_str = f" {json.dumps(extra_data)}" if extra_data else ""
            message = f"{timestamp} {level:8} {context_str}{message}{extra_str}"
        
        # Add color if enabled
        if use_colors:
            if fg:
                color_name = fg            
                message = colorize(message, 
                                   color=color_name, 
                                   style=style,
                                   iscode=True)        
        
        return message

    def _print(self, 
               level: str, 
               message: str, 
               extra: Optional[Dict[str, Any]] = None,
               **kwargs
               ) -> None:
        

        if level.upper() in ['GOOD', 'BAD', 'FAIL', 'SUCCESS']:
            text = self._format(level.upper(), 
                                message, 
                                **extra, 
                                **kwargs)
            
            # Get color
            fg = extra.get('fg', '')
            if not fg:
                fg = extra.get('color', 'reset')            
                
            # Get color code
            fgc = COLORS_DICT['reset']
            if fg:
                print('fg',fg)
                fgc = COLORS_DICT.get(fg, fgc)

            fgc = fgc.lstrip('\033[').rstrip('m')
            
            
            # Print text
            Printer().text(text, color=fgc)
        else:
            self.logger.log(
                getattr(logging, level.upper()),
                message, 
                extra=extra,
                **kwargs
                )
    
    def _log(self, 
             level: str, 
             message: str, 
             format: Optional[str] = None, 
             context: Optional[str] = None, 
             **kwargs):
        """Core logging function.

        Args:
            level: Log level
            message: Log message
            format: Log format
            context: Log context
            **kwargs: Additional keyword arguments

        There are four keyword arguments in kwargs to logger which are inspected: exc_info, stack_info, stacklevel and extra.

        If exc_info does not evaluate as false, it causes exception information to be added to the logging message. If an exception tuple (in the format returned by sys.exc_info()) or an exception instance is provided, it is used; otherwise, sys.exc_info() is called to get the exception information. 
        https://docs.python.org/3/library/logging.html            
        """

        exckw = {}

        # Handle exc_info
        if 'exc_info' in kwargs:
            exckw['exc_info'] = kwargs.pop('exc_info')

        # Handle stack_info
        if 'stack_info' in kwargs:
            exckw['stack_info'] = kwargs.pop('stack_info')

        # Handle stacklevel    
        if 'stacklevel' in kwargs:
            exckw['stacklevel'] = kwargs.pop('stacklevel')

        if context is None:
            context = level

        show_caller = kwargs.pop('show_caller', False)

        # Process kwargs
        fg = kwargs.pop('fg', kwargs.pop('color', None))
        bg = kwargs.pop('bg', None)
        bold = kwargs.pop('bold', False)

        # Get caller information
        caller_info = []
        for i in [3, 2]:
            try:
                ith_stack = sys._getframe(i)
            except Exception as e:
                continue

            caller_line_number = ith_stack.f_lineno        
            caller_filename = ith_stack.f_code.co_filename
            caller_filename = caller_filename #.split(ROOT_DIR.name)[-1].strip('/') if '/' in caller_filename else caller_filename      
            caller_func_name = ith_stack.f_code.co_name

            prefix = f"{caller_filename}:{caller_func_name}:{caller_line_number}"
            caller_info.append(prefix)

        #
        if caller_info:

            if level in ['WARNING', 'ERROR', 'CRITICAL']:
                if caller_info[0] == caller_info[-1]:
                    message = f"{caller_info[0]} {message}"
                else:
                    message = f"{'->'.join(caller_info)} {message}"
            elif show_caller:
                message = f"{caller_info[-1]} {message}"
            else:
                message = f"{message}"


        message = compose_log_message(message, **kwargs)
        extra = {'context': context, 'fg': fg, 'bg': bg, 'bold': bold}

        # Determine format based on data type        
        if format is None:
            if 'table_data' in kwargs:
                format = LogFormat.TABLE
            elif 'json_data' in kwargs and not kwargs.get('print_json', False):
                format = LogFormat.TABLE
                kwargs['table_data'] = kwargs.pop('json_data')
            else:
                format = LogFormat.TEXT

        
        # Format message based on type
        if format == LogFormat.TABLE and 'table_data' in kwargs:
            ptkw = {'level': level}
            for k in ['title', 'widths', 'aligns', 'colors', 'fg', 'bg', 'bold']:
                if kwargs.get(k):
                    ptkw[k] = kwargs.pop(k)
                else:
                    _ = kwargs.pop(k, None)

            self._print(
                level,
                message,
                extra=extra,
                **exckw
            )

            # Print table
            print_colored_table(
                data=kwargs['table_data'],
                **ptkw
            )

        elif format == LogFormat.JSON and 'json_data' in kwargs:
            json_str = json.dumps(kwargs['json_data'])

            self._print(
                level,
                message,
                extra=extra,
                **exckw
            )

            # Print json
            self._print(
                level,
                json_str,
                extra=extra,
                **exckw
            )
        else:
            self._print(
                level,
                message,
                extra=extra,
                **exckw
            )
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""        
        self._log('DEBUG', message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        self._log('INFO', message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        self._log('WARNING', message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        self._log('ERROR', message, **kwargs)
    
    def success(self, message: str, **kwargs):
        """Log success message."""
        kwargs['fg'] = kwargs.get('fg', 'green')
        self._log('SUCCESS', message, **kwargs)

    def good(self, message: str, **kwargs):
        """Log good message."""
        kwargs['fg'] = kwargs.get('fg', 'pink')
        self._log('GOOD', message, **kwargs)

    def bad(self, message: str, **kwargs):
        """Log bad message."""
        kwargs['fg'] = kwargs.get('fg', 'red')
        self._log('BAD', message, **kwargs)

    def fail(self, message: str, **kwargs):
        """Log fail message."""
        kwargs['fg'] = kwargs.get('fg', 'red')
        self._log('FAIL', message, **kwargs)


def compose_log_message(*args, **kwargs) -> str:
    """Compose a log message with special formatting."""
    achar = kwargs.pop('achar', '-')
    message = ''
    
    # Handle arrow formatting
    if kwargs.get('arrow', ""):
        message = f"{achar*5}{kwargs.pop('arrow')}{achar*5}> "
    elif kwargs.get('smallarrow', ""):
        message = f"{achar*2}{kwargs.pop('smallarrow')}{achar*2}> "
    elif kwargs.get('bigarrow', ""):
        message = f"{achar*8}{kwargs.pop('bigarrow')}{achar*8}> "
    
    # Process args
    if args:
        message += ', '.join([f"{x}" for x in args if isinstance(x, (str, list, dict, tuple, float, int))])
    
    
    # Remove special keys
    for k in ['arrow', 'smallarrow', 'bigarrow', 'achar', 'color', 'fg', 'bg', 'bold']:
        if k in kwargs:
            _ = kwargs.pop(k, None)
    
    # Add remaining kwargs
    if kwargs:
        message += ', '
        message += ', '.join([f"{k}={v}" for k, v in kwargs.items() if isinstance(v, str)])

    
    return message 

def flatten_nested_json(data: Dict[str, Dict], 
                        vertical: bool = False,
                        prefix: str = "",
                        rows: List = []) -> List[Dict[str, Any]]:
    """Convert nested JSON to flat table format.
    
    Args:
        data: Nested JSON dictionary
        vertical: Whether to print the table vertically
    Returns:
        List of flattened dictionaries for table display
    """
    
    
    if prefix:
        prefix = f"Table: {prefix.upper()}"

    # Get all unique inner keys
    if vertical:
        for k, v in data.items():
            if isinstance(v, dict):
                rows.append({"Key": f"{prefix}{k}".upper(), "Value": ""})
                flatten_nested_json(v, 
                                    vertical=vertical,
                                    rows=rows
                                    )
            else:
                rows.append({"Key": str(k), "Value": str(v)})
    else:
        all_inner_keys = set()
        for outer_key, inner_dict in data.items():
            if isinstance(inner_dict, dict):
                all_inner_keys.update(inner_dict.keys())
        
        # Create rows
        for outer_key, inner_dict in data.items():
            row = {"Category": str(outer_key)}  
            if isinstance(inner_dict, dict):
                for inner_key in all_inner_keys:
                    row[str(inner_key)] = str(inner_dict.get(inner_key, ""))
            else:
                # Handle non-dict values
                row["Value"] = str(inner_dict)

            rows.append(row)
    
    return rows

def print_colored_table(
    data: Union[List[Dict[str, Any]], Dict[str, Any]],  # Updated type hint
    title: str = "",
    headers: List[str] = [],
    level: str = 'INFO',
    colors: Dict[str, str] = {},
    fg: str = None,
    bg: str = None,
    bold: bool = False,
    vertical: bool = False,
    **kwargs
) -> None:
    """Print a colored table using wasabi.
    
    Args:
        data: List of dictionaries or nested dictionary containing the data
        title: Table title
        headers: Column headers (defaults to dict keys)
        widths: Column widths
        aligns: Column alignments ('l', 'r', 'c')
        colors: Dictionary mapping values to colors
        **kwargs: Additional keyword arguments
    """
    # if not fg:
    #     fg = COLORS_DICT[level.lower()]
    if not fg:
        fg = level.lower()

    fgc = COLORS_DICT[fg].lstrip('\033[').rstrip('m')

    if not colors:
        colors={fg: fgc}

    printer = Printer(pretty=True, no_print=False, colors=colors, line_max=40)
    

    f1 = lambda x, y: printer.text(x.strip(), color=y, no_print=True)
    f2 = lambda x, y: colorize(x.strip(), color=y, iscode=False)
    f3 = lambda x, y: color(x.strip(), y)
    f4 = lambda x, y: x.strip()

    func = f4

 

    if not data:
        printer.warn("No data to display")
        return


    # Validate inner keys share the same set of keys    
    if isinstance(data, dict) and any(isinstance(v, dict) for v in data.values()):
        flatten = False
        all_inner_keys = set()
        for row in data.values():
            if len(all_inner_keys) > len(row.keys()):
                all_inner_keys = set(row.keys())

        for row in data.values():
            if not set(row.keys()).issubset(all_inner_keys):
                flatten = True
                break
            
        if not flatten:
            table_data =  []
            for k, row in data.items():
                table_data.append({"Category": k, **row})
            headers = ["Category"] + list(all_inner_keys)
            data = table_data
    elif isinstance(data, list) and any(isinstance(v, dict) for v in data):
        flatten = False
    else:
        flatten = True

    if flatten or vertical:
        data = flatten_nested_json(data, vertical=vertical or flatten)

    # Use first row keys as headers if not provided
    if not headers:
        headers = list(data[0].keys())


    # Prepare rows for the table
    rows = []
    for item in data:
        row = []
        for header in headers:
            value = item.get(header, "")
            # Apply color if value matches a color key
            if fg:
                value = func(value, fgc)
            row.append(value)
        rows.append(row)

    # Add color to headers if specified    
    headers = [func(h, colors.get("header", fgc)) for h in headers]

    # Print title if provided
    if title:
        title = func(title.strip(), colors.get("title", fgc))
        print(f"\n{title}\n")

    
    # Generate and print the table
    printer.divider()
    printer.table(
        data=rows,
        header=headers,
        divider=True,
        widths=kwargs.get('widths', [15] * len(headers)),
        aligns=kwargs.get('aligns', ['l'] * len(headers) ),
        fg_colors=[int(fgc)] * len(headers)
    )
    printer.divider()

# Example usage
if __name__ == "__main__":
    # Sample data
    alerts_data = [
        {
            "ID": "ALT001",
            "Severity": "CRITICAL",
            "Status": "ERROR",
            "Message": "Database connection failed"
        },
        {
            "ID": "ALT002",
            "Severity": "WARNING",
            "Status": "WARNING",
            "Message": "High CPU usage detected"
        },
        {
            "ID": "ALT003",
            "Severity": "INFO",
            "Status": "SUCCESS",
            "Message": "Backup completed"
        }
    ]

    # Color mapping
    colors = {
        "CRITICAL": "red",
        "WARNING": "yellow",
        "INFO": "green",
        "ERROR": "red",
        "SUCCESS": "green",
        "header": "bold",
        "title": "bold"
    }

    # Print table
    print_colored_table(
        data=alerts_data,
        title="System Alerts",
        headers=["ID", "Severity", "Status", "Message"],
        widths=[10, 12, 10, 30],
        aligns=["l", "c", "c", "l"],
        colors=colors
    )