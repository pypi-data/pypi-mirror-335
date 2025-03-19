from enum import Enum

from pydantic import BaseModel, Field
from typing import Dict, List, Optional

from tiptree.mixins.agent import AgentMixin
from tiptree.mixins.agent_session import AgentSessionMixin
from tiptree.mixins.message import MessageMixin


# ***************
# *** General ***
# ***************


class APIResponseStatus(str, Enum):
    """Status codes for API responses."""

    OK = "ok"
    ERROR = "error"
    FAIL = "fail"


class APIResponse(BaseModel):
    """Standard API response format."""

    status: APIResponseStatus = Field(..., description="Status of the API response")
    message: str | None = Field(
        None, description="Optional message providing additional information"
    )
    payload: dict | None = Field(None, description="Optional payload data")
    status_code: int | None = Field(None, description="HTTP status code")

    @classmethod
    def success(
        cls,
        message: str | None = None,
        payload: dict | None = None,
        status_code: int = 200,
    ):
        return cls(
            status=APIResponseStatus.OK,
            message=message,
            payload=payload,
            status_code=status_code,
        )

    @classmethod
    def error(
        cls,
        message: str | None = None,
        payload: dict | None = None,
        status_code: int = 400,
    ):
        return cls(
            status=APIResponseStatus.ERROR,
            message=message,
            payload=payload,
            status_code=status_code,
        )

    @classmethod
    def fail(
        cls,
        message: str | None = None,
        payload: dict | None = None,
        status_code: int = 500,
    ):
        return cls(
            status=APIResponseStatus.FAIL,
            message=message,
            payload=payload,
            status_code=status_code,
        )


# ************
# *** Auth ***
# ************


class OTPSignupRequest(BaseModel):
    email: str
    first_name: str | None = None
    last_name: str | None = None


class OTPVerifyRequest(BaseModel):
    otp: str
    token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"
    expires_in: float
    refresh_token: str | None = None
    scope: str | None = None


class ApiKeyResponse(BaseModel):
    id: str
    api_key: str
    created_at: float
    expires_at: float
    revoked_at: float | None = None


class ApiSession(BaseModel):
    id: str
    created_at: float
    expires_at: float
    revoked_at: float | None = None
    info: dict | None = None


# **************
# *** Agents ***
# **************


class AgentConfig(BaseModel):
    """
    Configuration for an AI agent.

    This defines the basic properties and behavior of an agent.
    """

    # Metadata
    name: str = Field(..., description="The name of the agent")
    description: Optional[str] = Field(
        None, description="Optional description of the agent's purpose and capabilities"
    )
    # Tasks
    task_whitelist: Optional[List[str]] = Field(
        None,
        description=(
            "List of allowed task names for the agent. "
            "If None, all tasks are allowed."
        ),
    )
    task_blacklist: Optional[List[str]] = Field(
        None,
        description=(
            "List of disallowed task names for the agent. "
            "If None, no tasks are disallowed."
        ),
    )
    # Memory
    enable_memory: bool = Field(
        True, description="Whether the agent should use cross-session memory."
    )
    enable_remembrance: bool = Field(
        True, description="Whether the agent should use associative recall."
    )


class AgentBase(BaseModel):
    """
    Base model for Agent operations.

    Contains the common fields used across agent-related models.
    """

    info: Optional[Dict] = Field(
        None, description="Additional metadata about the agent"
    )
    config: Optional[AgentConfig] = Field(
        None, description="Configuration settings for the agent"
    )


class AgentCreate(AgentBase):
    """
    Model for creating a new agent.

    Used when sending a request to create an agent.
    """

    pass


class Agent(AgentBase, AgentMixin):
    """
    Model representing an agent.

    Contains all agent data including system-generated fields.
    """

    id: str = Field(..., description="Unique identifier for the agent")
    created_at: float = Field(..., description="Timestamp when the agent was created")


class AgentUpdate(AgentBase):
    """
    Model for updating an existing agent.

    Used when sending a request to update an agent's properties.
    """

    pass


# *********************
# *** Agent Session ***
# *********************


class AgentSessionConfig(BaseModel):
    """
    Configuration for an agent session.

    Defines how a particular session with an agent should behave.
    """

    initial_prompt: Optional[str] = Field(
        None, description="Initial prompt / instructions for the agent session."
    )
    metadata: Optional[Dict] = Field(
        None, description="Additional configuration metadata for the agent session"
    )


class AgentSessionBase(BaseModel):
    """
    Base model for Agent Session operations.

    Contains the common fields used across session-related models.
    """

    info: Optional[Dict] = Field(
        None, description="Additional metadata about the agent session"
    )
    config: Optional[AgentSessionConfig] = Field(
        None, description="Configuration settings for the agent session"
    )


class AgentSessionCreate(AgentSessionBase):
    """
    Model for creating a new agent session.

    Used when sending a request to create a session with an agent.
    """

    pass


class AgentSession(AgentSessionBase, AgentSessionMixin):
    """
    Model representing an agent session.

    Contains all session data including system-generated fields.
    """

    id: str = Field(..., description="Unique identifier for the agent session")
    agent_id: str = Field(
        ..., description="ID of the agent this agent session belongs to"
    )
    created_at: float = Field(
        ..., description="Timestamp when the agent session was created"
    )


class AgentSessionUpdate(AgentSessionBase):
    """
    Model for updating an existing agent session.

    Used when sending a request to update a session's properties.
    """

    pass


class AgentSessionWake(BaseModel):
    """
    Response model for waking an agent session.

    Contains information about the wake operation result.
    """

    agent_session_id: str = Field(
        ..., description="ID of the agent session that was woken"
    )
    woken_at: float = Field(
        ..., description="Timestamp when the agent session was woken"
    )
    success: bool = Field(..., description="Whether the wake operation was successful")


# ***************
# *** Message ***
# ***************


class Attachment(BaseModel):
    """
    Attachment for a message.

    Represents a file or other content attached to a message.
    """

    name: str = Field(..., description="Name of the attachment")
    url: str = Field(..., description="URL where the attachment can be accessed")
    description: str | None = Field(
        None, description="Optional description of the attachment"
    )
    type: str | None = Field(None, description="MIME type identifier")
    size: int | None = Field(None, description="Size of the attachment in bytes")


class MessagePayload(BaseModel):
    """
    Content of a message.

    Contains the actual content and metadata for a message.
    """

    content: str = Field(..., description="The text content of the message")
    sender: Optional[str] = Field(
        None,
        description=(
            "Who sent the message (e.g. user, assistant, etc.). "
            "Default value set automatically if not provided."
        ),
    )
    attachments: List[Attachment] = Field(
        [], description="List of attachments included with the message"
    )


class MessageBase(BaseModel):
    """
    Base model for Message operations.

    Contains the common fields used across message-related models.
    """

    payload: MessagePayload = Field(
        ..., description="The content and metadata of the message"
    )


class MessageCreate(MessageBase):
    """
    Model for creating a new message.

    Used when sending a request to create a message.
    """

    pass


class Message(MessageBase, MessageMixin):
    """
    Model representing a message.

    Contains all message data including system-generated fields.
    """

    id: str = Field(..., description="Unique identifier for the message")
    agent_session_id: str = Field(
        ..., description="ID of the agent session this message belongs to"
    )
    created_at: float = Field(..., description="Timestamp when the message was created")
    read: bool = Field(False, description="Whether the message has been marked as read")


class MessageUpdate(BaseModel):
    """
    Model for updating an existing message.

    Currently only supports marking messages as read.
    """

    read: bool | None = Field(
        None, description="Set to true to mark the message as read"
    )


# ******************
# *** User Keys ***
# ******************


class UserKeyRead(BaseModel):
    """
    Model representing a user key mapping.

    Contains information about a user key and its associated resources.
    """

    user_key: str = Field(..., description="The unique user key")
    agent_id: Optional[str] = Field(
        None, description="ID of the agent associated with this key, if any"
    )
    agent_session_id: Optional[str] = Field(
        None, description="ID of the session associated with this key, if any"
    )
    created_at: float = Field(..., description="Timestamp when the key was created")
