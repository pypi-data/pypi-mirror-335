import os
import json
import asyncio
import time
from typing import Dict, List, Optional, Union, Any, AsyncGenerator, Callable
from urllib.parse import urljoin

import httpx

from tiptree.exceptions import ActxAPIError
from tiptree.interface_models import (
    Agent,
    AgentCreate,
    AgentUpdate,
    AgentSession,
    AgentSessionCreate,
    AgentSessionUpdate,
    AgentSessionWake,
    Message,
    MessageCreate,
    MessagePayload,
    UserKeyRead,
    APIResponse,
    MessageUpdate,
    OTPSignupRequest,
    TokenResponse,
    ApiKeyResponse,
    ApiSession,
    OTPVerifyRequest,
)


class TiptreeClient:
    """
    Client for interacting with the Tiptree Platform API v2.

    This client provides methods for all v2 API endpoints, organized into
    sections for agents, agent sessions, messages, and simple API interactions.

    All methods are available in both synchronous and asynchronous versions.
    Async methods are prefixed with 'async_'.
    """

    _instance: "TiptreeClient" = None

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 60.0,
    ):
        """
        Initialize the Tiptree client.

        Args:
            base_url: Base URL of the Tiptree Platform API
            api_key: API key for authentication (optional)
            timeout: Request timeout in seconds
        """
        if base_url:
            self.base_url = base_url.rstrip("/")
        else:
            self.base_url = os.environ.get(
                "TIPTREE_API_BASE", "https://api.tiptreesystems.com/platform"
            )
        self.api_key = api_key or os.environ.get("TIPTREE_API_KEY")

        # Check for API key in ~/.tiptreerc/credentials if not found elsewhere
        if not self.api_key:
            credentials_file = os.path.expanduser("~/.tiptreerc/credentials")
            if os.path.exists(credentials_file):
                with open(credentials_file, "r") as f:
                    for line in f:
                        if line.startswith("TIPTREE_API_KEY="):
                            self.api_key = line.strip().split("=", 1)[1]
                            break

        self.timeout = timeout
        self.async_client = httpx.AsyncClient(timeout=timeout)
        self.sync_client = httpx.Client(timeout=timeout)
        # Set the instance to the current instance
        self.__class__.set_instance(self)

    @classmethod
    def get_instance(cls, create_if_missing: bool = True) -> "TiptreeClient":
        if cls._instance is None and create_if_missing:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def set_instance(cls, instance, overwrite: bool = False):
        if cls._instance is None:
            cls._instance = instance
        elif overwrite:
            cls._instance = instance

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.async_close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    async def async_close(self):
        """Close the underlying async HTTP client."""
        await self.async_client.aclose()

    def close(self):
        """Close the underlying sync HTTP client."""
        self.sync_client.close()

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests, including authentication if available."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _get_url(self, path: str) -> str:
        """Construct a full URL from the base URL and path."""
        return urljoin(f"{self.base_url}/", path.lstrip("/"))

    async def _async_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """
        Make an async HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API endpoint path
            params: Query parameters
            json_data: JSON request body
            headers: Additional headers

        Returns:
            Response object

        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        url = self._get_url(path)
        headers = {**self._get_headers(), **(headers or {})}

        response = await self.async_client.request(
            method=method,
            url=url,
            params=params,
            json=json_data,
            headers=headers,
        )

        # Raise exception for error status codes
        response.raise_for_status()

        return response

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """
        Make a synchronous HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            path: API endpoint path
            params: Query parameters
            json_data: JSON request body
            headers: Additional headers

        Returns:
            Response object

        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        url = self._get_url(path)
        headers = {**self._get_headers(), **(headers or {})}

        response = self.sync_client.request(
            method=method,
            url=url,
            params=params,
            json=json_data,
            headers=headers,
        )

        # Raise exception for error status codes
        response.raise_for_status()

        return response

    # *******************
    # *** ACTX Routes ***
    # *******************

    # Agent methods

    def list_agents(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        most_recent_first: Optional[bool] = None,
    ) -> List[Agent]:
        """
        List all agents with optional pagination and sorting (synchronous).

        Args:
            offset: Number of items to skip
            limit: Maximum number of items to return
            most_recent_first: Sort by creation time in descending order

        Returns:
            List of Agent objects
        """
        params = {
            "offset": offset,
            "limit": limit,
            "most_recent_first": most_recent_first,
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        response = self._request("GET", "/api/v2/actx/agents", params=params)
        return [
            Agent.model_validate(agent).bind_client(self) for agent in response.json()
        ]

    async def async_list_agents(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        most_recent_first: Optional[bool] = None,
    ) -> List[Agent]:
        """
        List all agents with optional pagination and sorting (asynchronous).

        Args:
            offset: Number of items to skip
            limit: Maximum number of items to return
            most_recent_first: Sort by creation time in descending order

        Returns:
            List of Agent objects
        """
        params = {
            "offset": offset,
            "limit": limit,
            "most_recent_first": most_recent_first,
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        response = await self._async_request(
            "GET", "/api/v2/actx/agents", params=params
        )
        return [
            Agent.model_validate(agent).bind_client(self) for agent in response.json()
        ]

    def create_agent(self, agent_create: Optional[AgentCreate] = None) -> Agent:
        """
        Create a new agent (synchronous).

        Args:
            agent_create: Agent creation parameters

        Returns:
            Created Agent object
        """
        data = agent_create.model_dump() if agent_create else {}
        response = self._request("POST", "/api/v2/actx/agents", json_data=data)
        return Agent.model_validate(response.json()).bind_client(self)

    async def async_create_agent(
        self, agent_create: Optional[AgentCreate] = None
    ) -> Agent:
        """
        Create a new agent (asynchronous).

        Args:
            agent_create: Agent creation parameters

        Returns:
            Created Agent object
        """
        data = agent_create.model_dump() if agent_create else {}
        response = await self._async_request(
            "POST", "/api/v2/actx/agents", json_data=data
        )
        return Agent.model_validate(response.json()).bind_client(self)

    def get_agent(self, agent_id: str) -> Agent:
        """
        Get an agent by ID (synchronous).

        Args:
            agent_id: ID of the agent to retrieve

        Returns:
            Agent object
        """
        response = self._request("GET", f"/api/v2/actx/agents/{agent_id}")
        return Agent.model_validate(response.json()).bind_client(self)

    async def async_get_agent(self, agent_id: str) -> Agent:
        """
        Get an agent by ID (asynchronous).

        Args:
            agent_id: ID of the agent to retrieve

        Returns:
            Agent object
        """
        response = await self._async_request("GET", f"/api/v2/actx/agents/{agent_id}")
        return Agent.model_validate(response.json()).bind_client(self)

    def update_agent(self, agent_id: str, agent_update: AgentUpdate) -> Agent:
        """
        Update an existing agent (synchronous).

        Args:
            agent_id: ID of the agent to update
            agent_update: Agent update parameters

        Returns:
            Updated Agent object
        """
        response = self._request(
            "PATCH",
            f"/api/v2/actx/agents/{agent_id}",
            json_data=agent_update.model_dump(exclude_unset=True),
        )
        return Agent.model_validate(response.json()).bind_client(self)

    async def async_update_agent(
        self, agent_id: str, agent_update: AgentUpdate
    ) -> Agent:
        """
        Update an existing agent (asynchronous).

        Args:
            agent_id: ID of the agent to update
            agent_update: Agent update parameters

        Returns:
            Updated Agent object
        """
        response = await self._async_request(
            "PATCH",
            f"/api/v2/actx/agents/{agent_id}",
            json_data=agent_update.model_dump(exclude_unset=True),
        )
        return Agent.model_validate(response.json()).bind_client(self)

    # Agent Session methods

    def list_agent_sessions(
        self,
        agent_id: str,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        most_recent_first: Optional[bool] = None,
    ) -> List[AgentSession]:
        """
        List all sessions for an agent with optional pagination and sorting (synchronous).

        Args:
            agent_id: ID of the agent
            offset: Number of items to skip
            limit: Maximum number of items to return
            most_recent_first: Sort by creation time in descending order

        Returns:
            List of AgentSession objects
        """
        params = {
            "offset": offset,
            "limit": limit,
            "most_recent_first": most_recent_first,
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        response = self._request(
            "GET", f"/api/v2/actx/agents/{agent_id}/agent-sessions", params=params
        )
        return [
            AgentSession.model_validate(session).bind_client(self)
            for session in response.json()
        ]

    async def async_list_agent_sessions(
        self,
        agent_id: str,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        most_recent_first: Optional[bool] = None,
    ) -> List[AgentSession]:
        """
        List all sessions for an agent with optional pagination and sorting (asynchronous).

        Args:
            agent_id: ID of the agent
            offset: Number of items to skip
            limit: Maximum number of items to return
            most_recent_first: Sort by creation time in descending order

        Returns:
            List of AgentSession objects
        """
        params = {
            "offset": offset,
            "limit": limit,
            "most_recent_first": most_recent_first,
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        response = await self._async_request(
            "GET", f"/api/v2/actx/agents/{agent_id}/agent-sessions", params=params
        )
        return [
            AgentSession.model_validate(session).bind_client(self)
            for session in response.json()
        ]

    def create_agent_session(
        self, agent_id: str, agent_session_create: Optional[AgentSessionCreate] = None
    ) -> AgentSession:
        """
        Create a new agent session (synchronous).

        Args:
            agent_id: ID of the agent
            agent_session_create: Session creation parameters

        Returns:
            Created AgentSession object
        """
        data = agent_session_create.model_dump() if agent_session_create else {}
        response = self._request(
            "POST", f"/api/v2/actx/agents/{agent_id}/agent-sessions", json_data=data
        )
        return AgentSession.model_validate(response.json()).bind_client(self)

    async def async_create_agent_session(
        self, agent_id: str, agent_session_create: Optional[AgentSessionCreate] = None
    ) -> AgentSession:
        """
        Create a new agent session (asynchronous).

        Args:
            agent_id: ID of the agent
            agent_session_create: Session creation parameters

        Returns:
            Created AgentSession object
        """
        data = agent_session_create.model_dump() if agent_session_create else {}
        response = await self._async_request(
            "POST", f"/api/v2/actx/agents/{agent_id}/agent-sessions", json_data=data
        )
        return AgentSession.model_validate(response.json()).bind_client(self)

    def get_agent_session(self, agent_session_id: str) -> AgentSession:
        """
        Get an agent session by ID (synchronous).

        Args:
            agent_session_id: ID of the session to retrieve

        Returns:
            AgentSession object
        """
        response = self._request(
            "GET", f"/api/v2/actx/agent-sessions/{agent_session_id}"
        )
        return AgentSession.model_validate(response.json()).bind_client(self)

    async def async_get_agent_session(self, agent_session_id: str) -> AgentSession:
        """
        Get an agent session by ID (asynchronous).

        Args:
            agent_session_id: ID of the session to retrieve

        Returns:
            AgentSession object
        """
        response = await self._async_request(
            "GET", f"/api/v2/actx/agent-sessions/{agent_session_id}"
        )
        return AgentSession.model_validate(response.json()).bind_client(self)

    def update_agent_session(
        self, agent_session_id: str, agent_session_update: AgentSessionUpdate
    ) -> AgentSession:
        """
        Update an existing agent session (synchronous).

        Args:
            agent_session_id: ID of the session to update
            agent_session_update: Session update parameters

        Returns:
            Updated AgentSession object
        """
        response = self._request(
            "PATCH",
            f"/api/v2/actx/agent-sessions/{agent_session_id}",
            json_data=agent_session_update.model_dump(exclude_unset=True),
        )
        return AgentSession.model_validate(response.json()).bind_client(self)

    async def async_update_agent_session(
        self, agent_session_id: str, agent_session_update: AgentSessionUpdate
    ) -> AgentSession:
        """
        Update an existing agent session (asynchronous).

        Args:
            agent_session_id: ID of the session to update
            agent_session_update: Session update parameters

        Returns:
            Updated AgentSession object
        """
        response = await self._async_request(
            "PATCH",
            f"/api/v2/actx/agent-sessions/{agent_session_id}",
            json_data=agent_session_update.model_dump(exclude_unset=True),
        )
        return AgentSession.model_validate(response.json()).bind_client(self)

    def wake_agent_session(self, agent_session_id: str) -> AgentSessionWake:
        """
        Wake an agent session (synchronous).

        Args:
            agent_session_id: ID of the session to wake

        Returns:
            AgentSessionWake response
        """
        response = self._request(
            "POST", f"/api/v2/actx/agent-sessions/{agent_session_id}/wake"
        )
        return AgentSessionWake.model_validate(response.json())

    async def async_wake_agent_session(self, agent_session_id: str) -> AgentSessionWake:
        """
        Wake an agent session (asynchronous).

        Args:
            agent_session_id: ID of the session to wake

        Returns:
            AgentSessionWake response
        """
        response = await self._async_request(
            "POST", f"/api/v2/actx/agent-sessions/{agent_session_id}/wake"
        )
        return AgentSessionWake.model_validate(response.json())

    # Message methods

    def list_messages(
        self,
        agent_session_id: str,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        read: Optional[bool] = None,
        sender: Optional[str] = None,
        created_after: Optional[float] = None,
        created_before: Optional[float] = None,
    ) -> List[Message]:
        """
        List all messages for an agent session with optional pagination and filtering (synchronous).

        Args:
            agent_session_id: ID of the session
            offset: Number of items to skip
            limit: Maximum number of items to return
            read: Filter by read status
            sender: Filter by message sender
            created_after: Filter messages created after this timestamp
            created_before: Filter messages created before this timestamp

        Returns:
            List of Message objects
        """
        params = {
            "offset": offset,
            "limit": limit,
            "read": read,
            "sender": sender,
            "created_after": created_after,
            "created_before": created_before,
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        response = self._request(
            "GET",
            f"/api/v2/actx/agent-sessions/{agent_session_id}/messages",
            params=params,
        )
        return [
            Message.model_validate(message).bind_client(self)
            for message in response.json()
        ]

    async def async_list_messages(
        self,
        agent_session_id: str,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        read: Optional[bool] = None,
        sender: Optional[str] = None,
        created_after: Optional[float] = None,
        created_before: Optional[float] = None,
    ) -> List[Message]:
        """
        List all messages for an agent session with optional pagination and filtering (asynchronous).

        Args:
            agent_session_id: ID of the session
            offset: Number of items to skip
            limit: Maximum number of items to return
            read: Filter by read status
            sender: Filter by message sender
            created_after: Filter messages created after this timestamp
            created_before: Filter messages created before this timestamp

        Returns:
            List of Message objects
        """
        params = {
            "offset": offset,
            "limit": limit,
            "read": read,
            "sender": sender,
            "created_after": created_after,
            "created_before": created_before,
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        response = await self._async_request(
            "GET",
            f"/api/v2/actx/agent-sessions/{agent_session_id}/messages",
            params=params,
        )
        return [
            Message.model_validate(message).bind_client(self)
            for message in response.json()
        ]

    def send_message(
        self, agent_session_id: str, message: Union[MessageCreate, MessagePayload, str]
    ) -> Message:
        """
        Send a message to an agent session (synchronous).

        Args:
            agent_session_id: ID of the session
            message: Message to send (can be a MessageCreate, MessagePayload, or string)

        Returns:
            Created Message object
        """
        # Handle different message input types
        if isinstance(message, str):
            message_data = MessagePayload(content=message, sender="user")
        elif isinstance(message, MessageCreate):
            message_data = message.payload
        else:  # MessagePayload
            message_data = message

        response = self._request(
            "POST",
            f"/api/v2/actx/agent-sessions/{agent_session_id}/messages",
            json_data=message_data.model_dump(),
        )
        return Message.model_validate(response.json()).bind_client(self)

    async def async_send_message(
        self, session_id: str, message: Union[MessageCreate, MessagePayload, str]
    ) -> Message:
        """
        Send a message to an agent session (asynchronous).

        Args:
            session_id: ID of the session
            message: Message to send (can be a MessageCreate, MessagePayload, or string)

        Returns:
            Created Message object
        """
        # Handle different message input types
        if isinstance(message, str):
            message_data = MessagePayload(content=message)
        elif isinstance(message, MessageCreate):
            message_data = message.payload
        else:  # MessagePayload
            message_data = message

        response = await self._async_request(
            "POST",
            f"/api/v2/actx/agent-sessions/{session_id}/messages",
            json_data=message_data.model_dump(),
        )
        return Message.model_validate(response.json()).bind_client(self)

    def get_message(self, message_id: str) -> Message:
        """
        Get a message by ID (synchronous).

        Args:
            message_id: ID of the message to retrieve

        Returns:
            Message object
        """
        response = self._request("GET", f"/api/v2/actx/messages/{message_id}")
        return Message.model_validate(response.json()).bind_client(self)

    async def async_get_message(self, message_id: str) -> Message:
        """
        Get a message by ID (asynchronous).

        Args:
            message_id: ID of the message to retrieve

        Returns:
            Message object
        """
        response = await self._async_request(
            "GET", f"/api/v2/actx/messages/{message_id}"
        )
        return Message.model_validate(response.json()).bind_client(self)

    def update_message(self, message_id: str, message_update: MessageUpdate) -> Message:
        """
        Update a message by ID (synchronous).

        Currently supports marking messages as read.

        Args:
            message_id: ID of the message to update
            message_update: Update parameters (e.g., read status)

        Returns:
            Updated Message object
        """
        response = self._request(
            "PATCH",
            f"/api/v2/actx/messages/{message_id}",
            json_data=message_update.model_dump(exclude_unset=True),
        )
        return Message.model_validate(response.json()).bind_client(self)

    async def async_update_message(
        self, message_id: str, message_update: MessageUpdate
    ) -> Message:
        """
        Update a message by ID (asynchronous).

        Currently supports marking messages as read.

        Args:
            message_id: ID of the message to update
            message_update: Update parameters (e.g., read status)

        Returns:
            Updated Message object
        """
        response = await self._async_request(
            "PATCH",
            f"/api/v2/actx/messages/{message_id}",
            json_data=message_update.model_dump(exclude_unset=True),
        )
        return Message.model_validate(response.json()).bind_client(self)

    # *********************
    # *** Simple Routes ***
    # *********************

    def send_simple_message(
        self,
        user_key: str,
        message: Union[MessagePayload, str],
        wake_agent: bool = True,
    ) -> Message:
        """
        Send a message using the simple API (synchronous).

        Args:
            user_key: User key for identification
            message: Message to send (can be a MessagePayload or string)
            wake_agent: Whether to wake the agent

        Returns:
            Created Message object
        """
        # Handle different message input types
        if isinstance(message, str):
            message_data = MessagePayload(content=message)
        else:  # MessagePayload
            message_data = message

        params = {"wake_agent": wake_agent}

        response = self._request(
            "POST",
            f"/api/v2/simple/user-keys/{user_key}/message",
            params=params,
            json_data=message_data.model_dump(),
        )
        return Message.model_validate(response.json()).bind_client(self)

    async def async_send_simple_message(
        self,
        user_key: str,
        message: Union[MessagePayload, str],
        wake_agent: bool = True,
    ) -> Message:
        """
        Send a message using the simple API (asynchronous).

        Args:
            user_key: User key for identification
            message: Message to send (can be a MessagePayload or string)
            wake_agent: Whether to wake the agent

        Returns:
            Created Message object
        """
        # Handle different message input types
        if isinstance(message, str):
            message_data = MessagePayload(content=message)
        else:  # MessagePayload
            message_data = message

        params = {"wake_agent": wake_agent}

        response = await self._async_request(
            "POST",
            f"/api/v2/simple/user-keys/{user_key}/message",
            params=params,
            json_data=message_data.model_dump(),
        )
        return Message.model_validate(response.json()).bind_client(self)

    def get_simple_messages(
        self,
        user_key: str,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        most_recent_first: Optional[bool] = None,
    ) -> List[Message]:
        """
        Get messages using the simple API (synchronous).

        Args:
            user_key: User key for identification
            offset: Number of items to skip
            limit: Maximum number of items to return
            most_recent_first: Sort by creation time in descending order

        Returns:
            List of Message objects
        """
        params = {
            "offset": offset,
            "limit": limit,
            "most_recent_first": most_recent_first,
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        response = self._request(
            "GET", f"/api/v2/simple/user-keys/{user_key}/messages", params=params
        )
        return [
            Message.model_validate(message).bind_client(self)
            for message in response.json()
        ]

    async def async_get_simple_messages(
        self,
        user_key: str,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        most_recent_first: Optional[bool] = None,
    ) -> List[Message]:
        """
        Get messages using the simple API (asynchronous).

        Args:
            user_key: User key for identification
            offset: Number of items to skip
            limit: Maximum number of items to return
            most_recent_first: Sort by creation time in descending order

        Returns:
            List of Message objects
        """
        params = {
            "offset": offset,
            "limit": limit,
            "most_recent_first": most_recent_first,
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        response = await self._async_request(
            "GET", f"/api/v2/simple/user-keys/{user_key}/messages", params=params
        )
        return [
            Message.model_validate(message).bind_client(self)
            for message in response.json()
        ]

    def get_user_key(self, user_key: str) -> UserKeyRead:
        """
        Get user key information (synchronous).

        Args:
            user_key: User key to retrieve

        Returns:
            UserKeyRead object
        """
        response = self._request("GET", f"/api/v2/simple/user-keys/{user_key}")
        return UserKeyRead.model_validate(response.json())

    async def async_get_user_key(self, user_key: str) -> UserKeyRead:
        """
        Get user key information (asynchronous).

        Args:
            user_key: User key to retrieve

        Returns:
            UserKeyRead object
        """
        response = await self._async_request(
            "GET", f"/api/v2/simple/user-keys/{user_key}"
        )
        return UserKeyRead.model_validate(response.json())

    # ****************
    # *** Auth API ***
    # ****************

    def signup_with_otp(self, signup_request: OTPSignupRequest) -> APIResponse:
        """
        Start the OTP signup process (synchronous).

        Args:
            signup_request: OTP signup request containing email and first_name

        Returns:
            APIResponse with token for OTP verification
        """
        response = self._request(
            "POST", "/api/v2/auth/otp/signup", json_data=signup_request.model_dump()
        )
        return APIResponse.model_validate(response.json())

    async def async_signup_with_otp(
        self, signup_request: OTPSignupRequest
    ) -> APIResponse:
        """
        Start the OTP signup process (asynchronous).

        Args:
            signup_request: OTP signup request containing email and first_name

        Returns:
            APIResponse with token for OTP verification
        """
        response = await self._async_request(
            "POST", "/api/v2/auth/otp/signup", json_data=signup_request.model_dump()
        )
        return APIResponse.model_validate(response.json())

    def verify_signup_otp(self, token: str, otp: str) -> TokenResponse:
        """
        Verify OTP for signup (synchronous).

        Args:
            token: Token received from signup_with_otp
            otp: One-time password received via email

        Returns:
            TokenResponse with authentication tokens
        """
        response = self._request(
            "POST",
            "/api/v2/auth/otp/signup/verify",
            json_data=OTPVerifyRequest.model_validate(
                {"token": token, "otp": otp}
            ).model_dump(),
        )
        return TokenResponse.model_validate(response.json())

    async def async_verify_signup_otp(self, token: str, otp: str) -> TokenResponse:
        """
        Verify OTP for signup (asynchronous).

        Args:
            token: Token received from signup_with_otp
            otp: One-time password received via email

        Returns:
            TokenResponse with authentication tokens
        """
        response = await self._async_request(
            "POST",
            "/api/v2/auth/otp/signup/verify",
            json_data={"token": token, "otp": otp},
        )
        return TokenResponse.model_validate(response.json())

    def signin_with_otp(self, email: str) -> APIResponse:
        """
        Start the OTP signin process (synchronous).

        Args:
            email: Email address for signin

        Returns:
            APIResponse with token for OTP verification
        """
        response = self._request(
            "POST", "/api/v2/auth/otp/signin", json_data={"email": email}
        )
        return APIResponse.model_validate(response.json())

    async def async_signin_with_otp(self, email: str) -> APIResponse:
        """
        Start the OTP signin process (asynchronous).

        Args:
            email: Email address for signin

        Returns:
            APIResponse with token for OTP verification
        """
        response = await self._async_request(
            "POST", "/api/v2/auth/otp/signin", json_data={"email": email}
        )
        return APIResponse.model_validate(response.json())

    def verify_signin_otp(self, token: str, otp: str) -> TokenResponse:
        """
        Verify OTP for signin (synchronous).

        Args:
            token: Token received from signin_with_otp
            otp: One-time password received via email

        Returns:
            TokenResponse with authentication tokens
        """
        response = self._request(
            "POST",
            "/api/v2/auth/otp/signin/verify",
            json_data=OTPVerifyRequest.model_validate(
                {"token": token, "otp": otp}
            ).model_dump(),
        )
        return TokenResponse.model_validate(response.json())

    async def async_verify_signin_otp(self, token: str, otp: str) -> TokenResponse:
        """
        Verify OTP for signin (asynchronous).

        Args:
            token: Token received from signin_with_otp
            otp: One-time password received via email

        Returns:
            TokenResponse with authentication tokens
        """
        response = await self._async_request(
            "POST",
            "/api/v2/auth/otp/signin/verify",
            json_data={"token": token, "otp": otp},
        )
        return TokenResponse.model_validate(response.json())

    def create_api_key(self, authorization: str | None = None) -> ApiKeyResponse:
        """
        Create a new API key (synchronous).

        Returns:
            ApiKeyResponse containing the new API key
        """
        if authorization is not None:
            headers = {"Authorization": f"Bearer {authorization}"}
        else:
            headers = None
        response = self._request("POST", "/api/v2/auth/api-keys", headers=headers)
        return ApiKeyResponse.model_validate(response.json())

    async def async_create_api_key(
        self, authorization: str | None = None
    ) -> ApiKeyResponse:
        """
        Create a new API key (asynchronous).

        Returns:
            ApiKeyResponse containing the new API key
        """
        if authorization is not None:
            headers = {"Authorization": f"Bearer {authorization}"}
        else:
            headers = None
        response = await self._async_request(
            "POST", "/api/v2/auth/api-keys", headers=headers
        )
        return ApiKeyResponse.model_validate(response.json())

    def revoke_api_key(self, api_session_id: str) -> APIResponse:
        """
        Revoke an API key (synchronous).

        Args:
            api_session_id: ID of the API session to revoke

        Returns:
            APIResponse indicating success
        """
        response = self._request(
            "POST", f"/api/v2/auth/api-keys/{api_session_id}/revoke"
        )
        return APIResponse.model_validate(response.json())

    async def async_revoke_api_key(self, api_session_id: str) -> APIResponse:
        """
        Revoke an API key (asynchronous).

        Args:
            api_session_id: ID of the API session to revoke

        Returns:
            APIResponse indicating success
        """
        response = await self._async_request(
            "POST", f"/api/v2/auth/api-keys/{api_session_id}/revoke"
        )
        return APIResponse.model_validate(response.json())

    def list_api_keys(self) -> List[ApiSession]:
        """
        List all API keys (synchronous).

        Returns:
            List of ApiSession objects
        """
        response = self._request("GET", "/api/v2/auth/api-keys")
        return [ApiSession.model_validate(session) for session in response.json()]

    async def async_list_api_keys(self) -> List[ApiSession]:
        """
        List all API keys (asynchronous).

        Returns:
            List of ApiSession objects
        """
        response = await self._async_request("GET", "/api/v2/auth/api-keys")
        return [ApiSession.model_validate(session) for session in response.json()]
