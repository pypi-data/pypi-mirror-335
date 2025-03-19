"""Tiptree client library for interacting with the Tiptree API.

This library provides a client for the Tiptree Platform API, with both
synchronous and asynchronous methods for all endpoints.
"""

__version__ = "0.1.0"

# Main client
from tiptree.client import TiptreeClient

# Exceptions
from tiptree.exceptions import ActxAPIError

# Models
from tiptree.interface_models import (
    # General
    APIResponse,
    APIResponseStatus,

    # Auth models
    OTPSignupRequest,
    TokenResponse,
    ApiKeyResponse,
    ApiSession,
    
    # Agent models
    Agent,
    AgentCreate,
    AgentUpdate,
    AgentConfig,
    
    # Agent session models
    AgentSession,
    AgentSessionCreate,
    AgentSessionUpdate,
    AgentSessionConfig,
    AgentSessionWake,
    
    # Message models
    Message,
    MessageCreate,
    MessageUpdate,
    MessagePayload,
    Attachment,
    
    # User models
    UserKeyRead,
)

__all__ = [
    # Version
    "__version__",
    
    # Client
    "TiptreeClient",
    
    # Exceptions
    "ActxAPIError",
    
    # API response models
    "APIResponse",
    "APIResponseStatus",

    # Auth models
    "OTPSignupRequest",
    "TokenResponse",
    "ApiKeyResponse",
    "ApiSession",
    
    # Agent models
    "Agent",
    "AgentCreate",
    "AgentUpdate",
    "AgentConfig",
    
    # Agent session models
    "AgentSession",
    "AgentSessionCreate",
    "AgentSessionUpdate",
    "AgentSessionConfig",
    "AgentSessionWake",
    
    # Message models
    "Message",
    "MessageCreate",
    "MessageUpdate",
    "MessagePayload",
    "Attachment",
    
    # User models
    "UserKeyRead",
]
