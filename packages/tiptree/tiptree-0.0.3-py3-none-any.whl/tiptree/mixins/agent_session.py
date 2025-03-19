import time
from typing import (
    TYPE_CHECKING,
    Dict,
    List,
    Optional,
    Union,
    AsyncGenerator,
    Callable,
    Any,
    Generator,
)
import asyncio

from tiptree.utils import ClientBind

if TYPE_CHECKING:
    from tiptree.interface_models import (
        AgentSession,
        AgentSessionWake,
        Message,
        MessageCreate,
        MessagePayload,
        AgentSessionUpdate,
        AgentSessionConfig,
    )


class AgentSessionMixin(ClientBind):
    id: str
    config: Optional["AgentSessionConfig"]
    info: dict | None

    def _create_agent_session_update_params(
        self,
        agent_session_update: Optional["AgentSessionUpdate"],
        initial_prompt: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> "AgentSessionUpdate":
        """Create AgentSessionUpdate from parameters if needed."""
        if agent_session_update is None and (
            initial_prompt is not None or metadata is not None
        ):
            from tiptree.interface_models import AgentSessionUpdate, AgentSessionConfig

            # Start with current values if available
            current_config = self.config

            # Create new config if needed
            if current_config:
                # Update existing config with new values
                config_dict = current_config.model_dump()
                if initial_prompt is not None:
                    config_dict["initial_prompt"] = initial_prompt
                if metadata is not None:
                    config_dict["metadata"] = metadata
                config = AgentSessionConfig(**config_dict)
            else:
                # Create new config with provided values
                config = AgentSessionConfig(
                    initial_prompt=initial_prompt, metadata=metadata
                )

            return AgentSessionUpdate(config=config)
        return agent_session_update

    @property
    def title(self) -> str | None:
        if self.info is None:
            return None
        return self.info.get("title")

    def wake(self) -> "AgentSessionWake":
        """
        Wake this agent session (synchronous).

        Returns:
            AgentSessionWake response
        """
        self.ensure_client_bound()
        return self.client.wake_agent_session(self.id)

    async def async_wake(self) -> "AgentSessionWake":
        """
        Wake this agent session (asynchronous).

        Returns:
            AgentSessionWake response
        """
        self.ensure_client_bound()
        return await self.client.async_wake_agent_session(self.id)

    def get_messages(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        read: Optional[bool] = None,
        sender: Optional[str] = None,
        created_after: Optional[float] = None,
        created_before: Optional[float] = None,
    ) -> List["Message"]:
        """
        Get messages for this agent session with optional filtering (synchronous).

        Args:
            offset: Number of items to skip
            limit: Maximum number of items to return
            read: Filter by read status
            sender: Filter by message sender
            created_after: Filter messages created after this timestamp
            created_before: Filter messages created before this timestamp

        Returns:
            List of Message objects
        """
        self.ensure_client_bound()
        return self.client.list_messages(
            self.id,
            offset=offset,
            limit=limit,
            read=read,
            sender=sender,
            created_after=created_after,
            created_before=created_before,
        )

    async def async_get_messages(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        read: Optional[bool] = None,
        sender: Optional[str] = None,
        created_after: Optional[float] = None,
        created_before: Optional[float] = None,
    ) -> List["Message"]:
        """
        Get messages for this agent session with optional filtering (asynchronous).

        Args:
            offset: Number of items to skip
            limit: Maximum number of items to return
            read: Filter by read status
            sender: Filter by message sender
            created_after: Filter messages created after this timestamp
            created_before: Filter messages created before this timestamp

        Returns:
            List of Message objects
        """
        self.ensure_client_bound()
        return await self.client.async_list_messages(
            self.id,
            offset=offset,
            limit=limit,
            read=read,
            sender=sender,
            created_after=created_after,
            created_before=created_before,
        )

    def send_message(
        self, message: Union["MessageCreate", "MessagePayload", str], wake: bool = True
    ) -> "Message":
        """
        Send a message to this agent session (synchronous).

        Args:
            message: Message to send (can be a MessageCreate, MessagePayload, or string)
            wake: Whether to wake the agent session after sending the message

        Returns:
            Created Message object
        """
        self.ensure_client_bound()
        result = self.client.send_message(self.id, message)
        if wake:
            self.wake()
        return result

    async def async_send_message(
        self, message: Union["MessageCreate", "MessagePayload", str], wake: bool = True
    ) -> "Message":
        """
        Send a message to this agent session (asynchronous).

        Args:
            message: Message to send (can be a MessageCreate, MessagePayload, or string)
            wake: Whether to wake the agent session after sending the message

        Returns:
            Created Message object
        """
        self.ensure_client_bound()
        result = await self.client.async_send_message(self.id, message)
        if wake:
            await self.async_wake()
        return result

    def update(
        self,
        initial_prompt: Optional[str] = None,
        metadata: Optional[Dict] = None,
        agent_session_update: Optional["AgentSessionUpdate"] = None,
    ) -> "AgentSession":
        """
        Update this agent session (synchronous).

        Args:
            initial_prompt: Optional new initial prompt for the session
            metadata: Optional new metadata for the session
            agent_session_update: Optional session update parameters

        Returns:
            Updated AgentSession object
        """
        self.ensure_client_bound()
        agent_session_update = self._create_agent_session_update_params(
            agent_session_update, initial_prompt, metadata
        )
        return self.client.update_agent_session(self.id, agent_session_update)

    async def async_update(
        self,
        initial_prompt: Optional[str] = None,
        metadata: Optional[Dict] = None,
        agent_session_update: Optional["AgentSessionUpdate"] = None,
    ) -> "AgentSession":
        """
        Update this agent session (asynchronous).

        Args:
            initial_prompt: Optional new initial prompt for the session
            metadata: Optional new metadata for the session
            agent_session_update: Optional session update parameters

        Returns:
            Updated AgentSession object
        """
        self.ensure_client_bound()
        agent_session_update = self._create_agent_session_update_params(
            agent_session_update, initial_prompt, metadata
        )
        return await self.client.async_update_agent_session(
            self.id, agent_session_update
        )

    async def async_listen(
        self,
        start_time: Optional[float] = None,
        poll_interval: float = 20.0,
        listen_for: float | None = None,
        break_after_message: bool = False,
        auto_mark_as_read: bool = True,
    ) -> AsyncGenerator["Message", None]:
        """
        Poll for new messages at regular intervals (asynchronous).

        This method yields new messages as they arrive.

        Args:
            start_time: Only return messages created after this timestamp (default: current time)
            poll_interval: Time between polls in seconds (default: 60.0)
            listen_for: Maximum time to listen in seconds (default: None, listen indefinitely)
            break_after_message: If True, stop listening after receiving first message (default: False)
            auto_mark_as_read: If True, automatically mark each message as read (default: True)

        Yields:
            New Message objects one at a time

        Example:
            ```python
            async for message in session.async_listen(poll_interval=2.0, listen_for=60.0):
                print(f"{message.payload.sender}: {message.payload.content}")
                # Process each message as it arrives
            ```
        """
        self.ensure_client_bound()

        if start_time is None:
            start_time = time.time()

        start_listen_time = time.time()

        while True:
            messages = self.client.list_messages(
                agent_session_id=self.id, created_after=start_time, read=False
            )

            for message in messages:
                if auto_mark_as_read:
                    await message.async_mark_as_read()
                yield message
                if break_after_message:
                    return

            await asyncio.sleep(poll_interval)

            # Break if listen_for seconds has passed
            if listen_for is not None and (
                time.time() - start_listen_time > listen_for
            ):
                break

    def listen(
        self,
        start_time: Optional[float] = None,
        poll_interval: float = 20.0,
        listen_for: float | None = None,
        break_after_message: bool = False,
        auto_mark_as_read: bool = True,
    ) -> Generator["Message", None, None]:
        """
        Poll for new messages at regular intervals (synchronous).

        This method yields new messages as they arrive.

        Args:
            start_time: Only return messages created after this timestamp (default: current time)
            poll_interval: Time between polls in seconds (default: 60.0)
            listen_for: Maximum time to listen in seconds (default: None, listen indefinitely)
            break_after_message: If True, stop listening after receiving first message (default: False)
            auto_mark_as_read: If True, automatically mark each message as read (default: True)

        Yields:
            New Message objects one at a time

        Example:
            ```python
            for message in session.listen(poll_interval=2.0, listen_for=60.0):
                print(f"{message.payload.sender}: {message.payload.content}")
                # Process each message as it arrives
            ```
        """
        self.ensure_client_bound()

        if start_time is None:
            start_time = time.time()

        start_listen_time = time.time()

        while True:
            messages = self.client.list_messages(
                agent_session_id=self.id, created_after=start_time, read=False
            )

            for message in messages:
                if auto_mark_as_read:
                    message.mark_as_read()
                yield message
                if break_after_message:
                    return

            time.sleep(poll_interval)

            # Break if listen_for seconds has passed
            if listen_for is not None and (
                time.time() - start_listen_time > listen_for
            ):
                break

    def wait_for_next_message(
        self,
        start_time: Optional[float] = None,
        poll_interval: float = 20.0,
        auto_mark_as_read: bool = True,
    ) -> "Message":
        """
        Wait for and return the next message in this agent session (synchronous).

        Args:
            start_time: Only return messages created after this timestamp (default: current time)
            poll_interval: Time between polls in seconds (default: 20.0)
            auto_mark_as_read: If True, automatically mark the message as read (default: True)

        Returns:
            The next Message object received
        """
        for message in self.listen(
            start_time=start_time,
            poll_interval=poll_interval,
            break_after_message=True,
            auto_mark_as_read=auto_mark_as_read,
        ):
            return message

    async def async_wait_for_next_message(
        self,
        start_time: Optional[float] = None,
        poll_interval: float = 20.0,
        auto_mark_as_read: bool = True,
    ) -> "Message":
        """
        Wait for and return the next message in this agent session (asynchronous).

        Args:
            start_time: Only return messages created after this timestamp (default: current time)
            poll_interval: Time between polls in seconds (default: 20.0)
            auto_mark_as_read: If True, automatically mark the message as read (default: True)

        Returns:
            The next Message object received
        """
        async for message in self.async_listen(
            start_time=start_time,
            poll_interval=poll_interval,
            break_after_message=True,
            auto_mark_as_read=auto_mark_as_read,
        ):
            return message
