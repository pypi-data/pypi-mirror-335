"""Error handling for CodeDoc MCP Server."""

# Import built-in modules
from enum import Enum, auto


class ErrorCode(Enum):
    """Error codes for CodeDoc MCP Server."""
    
    # General errors
    UNKNOWN_ERROR = auto()
    VALIDATION_ERROR = auto()
    CONFIGURATION_ERROR = auto()
    
    # Network related errors
    NETWORK_ERROR = auto()
    API_FAILURE = auto()
    TIMEOUT_ERROR = auto()
    
    # File system errors
    FILE_NOT_FOUND = auto()
    PERMISSION_ERROR = auto()
    
    # Code analysis errors
    PARSING_ERROR = auto()
    ANALYSIS_ERROR = auto()


class CodeDocError(Exception):
    """Base exception class for CodeDoc MCP Server."""
    
    def __init__(self, message: str, code: ErrorCode = ErrorCode.UNKNOWN_ERROR):
        """Initialize CodeDocError.
        
        Args:
            message: Error message
            code: Error code
        """
        self.message = message
        self.code = code
        super().__init__(self.message)
        
    def __str__(self) -> str:
        """Return string representation of error.
        
        Returns:
            str: Error message with code
        """
        return f"{self.code.name}: {self.message}"
