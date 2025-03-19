from typing import TYPE_CHECKING, Dict, List, Optional

from tiptree.utils import ClientBind

if TYPE_CHECKING:
    from tiptree.interface_models import (
        Agent,
        AgentSession,
        AgentSessionCreate,
        AgentSessionConfig,
        AgentUpdate,
        AgentConfig,
        AgentCreate,
    )
    from tiptree.client import TiptreeClient


class AgentMixin(ClientBind):
    id: str
    config: Optional["AgentConfig"]
    info: Optional[Dict]

    def _create_agent_session_params(
        self,
        agent_session_create: Optional["AgentSessionCreate"],
        initial_prompt: Optional[str],
        metadata: Optional[Dict],
    ) -> "AgentSessionCreate":
        """Create AgentSessionCreate from parameters if needed."""
        if agent_session_create is not None:
            return agent_session_create

        from tiptree.interface_models import AgentSessionCreate, AgentSessionConfig

        config = {}
        if initial_prompt is not None:
            config["initial_prompt"] = initial_prompt
        if metadata is not None:
            config["metadata"] = metadata

        config = AgentSessionConfig(**config)
        return AgentSessionCreate(config=config)

    def _create_agent_update_params(
        self,
        agent_update: Optional["AgentUpdate"],
        name: Optional[str] = None,
        description: Optional[str] = None,
        info: Optional[Dict] = None,
        task_whitelist: Optional[List[str]] = None,
        task_blacklist: Optional[List[str]] = None,
        enable_memory: Optional[bool] = None,
        enable_remembrance: Optional[bool] = None,
    ) -> "AgentUpdate":
        """Create AgentUpdate from parameters if needed."""
        if agent_update is not None:
            return agent_update

        from tiptree.interface_models import AgentUpdate, AgentConfig

        # Start with current values if available
        current_config = self.config
        current_info = self.info

        # Create config with current values or new values
        config_kwargs = {}
        if name is not None:
            config_kwargs["name"] = name
        if description is not None:
            config_kwargs["description"] = description
        if task_whitelist is not None:
            if len(task_whitelist) == 1 and task_whitelist[0] == "*/*/*":
                # This is a special case to allow all tasks
                task_whitelist = None
            config_kwargs["task_whitelist"] = task_whitelist
        if task_blacklist is not None:
            config_kwargs["task_blacklist"] = task_blacklist
        if enable_memory is not None:
            config_kwargs["enable_memory"] = enable_memory
        if enable_remembrance is not None:
            config_kwargs["enable_remembrance"] = enable_remembrance

        if current_config and not config_kwargs:
            # No changes to config
            config = current_config
        elif current_config:
            # Update existing config with new values
            config_dict = current_config.model_dump()
            config_dict.update(config_kwargs)
            config = AgentConfig(**config_dict)
        else:
            # Create new config with provided values or defaults
            if "name" not in config_kwargs:
                config_kwargs["name"] = "Unnamed Agent"
            config = AgentConfig(**config_kwargs)

        # Use provided info or current info
        final_info = info if info is not None else current_info

        return AgentUpdate(config=config, info=final_info)

    @classmethod
    def _create_agent_create_params(
        cls,
        agent_create: Optional["AgentCreate"],
        name: Optional[str] = None,
        description: Optional[str] = None,
        info: Optional[Dict] = None,
        task_whitelist: Optional[List[str]] = None,
        task_blacklist: Optional[List[str]] = None,
        enable_memory: Optional[bool] = None,
        enable_remembrance: Optional[bool] = None,
    ) -> "AgentCreate":
        """Create AgentCreate from parameters if needed."""
        if agent_create is not None:
            return agent_create

        from tiptree.interface_models import AgentCreate, AgentConfig

        # Only include non-None values to let AgentConfig defaults take precedence
        config_kwargs = {"name": name or "Unnamed Agent"}
        if description is not None:
            config_kwargs["description"] = description
        if task_whitelist is not None:
            config_kwargs["task_whitelist"] = task_whitelist
        if task_blacklist is not None:
            config_kwargs["task_blacklist"] = task_blacklist
        if enable_memory is not None:
            config_kwargs["enable_memory"] = enable_memory
        if enable_remembrance is not None:
            config_kwargs["enable_remembrance"] = enable_remembrance

        config = AgentConfig(**config_kwargs)
        return AgentCreate(config=config, info=info)

    @classmethod
    def create(
        cls,
        name: Optional[str] = None,
        description: Optional[str] = None,
        info: Optional[Dict] = None,
        task_whitelist: Optional[List[str]] = None,
        task_blacklist: Optional[List[str]] = None,
        enable_memory: Optional[bool] = None,
        enable_remembrance: Optional[bool] = None,
        agent_create: Optional["AgentCreate"] = None,
        client: Optional["TiptreeClient"] = None,
    ) -> "Agent":
        """
        Create a new agent (synchronous).

        Args:
            name: Optional name for the agent
            description: Optional description for the agent
            info: Optional info dictionary for the agent
            task_whitelist: Optional list of allowed task names
            task_blacklist: Optional list of disallowed task names
            enable_memory: Whether to enable cross-session memory
            enable_remembrance: Whether to enable associative recall
            agent_create: Optional agent creation parameters
            client: TiptreeClient instance, or None to use the default client

        Returns:
            Created Agent object
        """
        from tiptree.client import TiptreeClient

        client = client or TiptreeClient.get_instance()

        agent_create = cls._create_agent_create_params(
            agent_create,
            name,
            description,
            info,
            task_whitelist,
            task_blacklist,
            enable_memory,
            enable_remembrance,
        )
        return client.create_agent(agent_create)

    @classmethod
    async def async_create(
        cls,
        name: Optional[str] = None,
        description: Optional[str] = None,
        info: Optional[Dict] = None,
        task_whitelist: Optional[List[str]] = None,
        task_blacklist: Optional[List[str]] = None,
        enable_memory: Optional[bool] = None,
        enable_remembrance: Optional[bool] = None,
        agent_create: Optional["AgentCreate"] = None,
        client: Optional["TiptreeClient"] = None,
    ) -> "Agent":
        """
        Create a new agent (asynchronous).

        Args:
            name: Optional name for the agent
            description: Optional description for the agent
            info: Optional info dictionary for the agent
            task_whitelist: Optional list of allowed task names
            task_blacklist: Optional list of disallowed task names
            enable_memory: Whether to enable cross-session memory
            enable_remembrance: Whether to enable associative recall
            agent_create: Optional agent creation parameters
            client: TiptreeClient instance, or None to use the default client

        Returns:
            Created Agent object
        """
        from tiptree.client import TiptreeClient

        client = client or TiptreeClient.get_instance()

        agent_create = cls._create_agent_create_params(
            agent_create,
            name,
            description,
            info,
            task_whitelist,
            task_blacklist,
            enable_memory,
            enable_remembrance,
        )
        return await client.async_create_agent(agent_create)

    @classmethod
    def list(
        cls,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        most_recent_first: Optional[bool] = None,
        client: Optional["TiptreeClient"] = None,
    ) -> List["Agent"]:
        """
        List all agents with optional pagination and sorting (synchronous).

        Args:
            offset: Number of items to skip
            limit: Maximum number of items to return
            most_recent_first: Sort by creation time in descending order
            client: TiptreeClient instance, or None to use the default client

        Returns:
            List of Agent objects
        """
        from tiptree.client import TiptreeClient

        client = client or TiptreeClient.get_instance()
        return client.list_agents(
            offset=offset, limit=limit, most_recent_first=most_recent_first
        )

    @classmethod
    async def async_list(
        cls,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        most_recent_first: Optional[bool] = None,
        client: Optional["TiptreeClient"] = None,
    ) -> List["Agent"]:
        """
        List all agents with optional pagination and sorting (asynchronous).

        Args:
            offset: Number of items to skip
            limit: Maximum number of items to return
            most_recent_first: Sort by creation time in descending order
            client: TiptreeClient instance, or None to use the default client

        Returns:
            List of Agent objects
        """
        from tiptree.client import TiptreeClient

        client = client or TiptreeClient.get_instance()
        return await client.async_list_agents(
            offset=offset, limit=limit, most_recent_first=most_recent_first
        )

    @classmethod
    def get_or_create(
        cls,
        name: Optional[str] = None,
        description: Optional[str] = None,
        info: Optional[Dict] = None,
        agent_create: Optional["AgentCreate"] = None,
        client: Optional["TiptreeClient"] = None,
    ) -> "Agent":
        """
        Get an existing agent by name or create a new one if it doesn't exist (synchronous).

        Args:
            name: Name to search for or use in creation (defaults to "Unnamed Agent")
            description: Optional description for the agent if created
            info: Optional info dictionary for the agent if created
            agent_create: Optional agent creation parameters
            client: TiptreeClient instance, or None to use the default client

        Returns:
            Existing or newly created Agent object
        """
        search_name = name or "Unnamed Agent"
        existing_agents = cls.list(client=client)

        # Search for agent with matching name
        for agent in existing_agents:
            if agent.config and agent.config.name == search_name:
                return agent

        # If not found, create new agent
        return cls.create(
            name=name,
            description=description,
            info=info,
            agent_create=agent_create,
            client=client,
        )

    @classmethod
    async def async_get_or_create(
        cls,
        name: Optional[str] = None,
        description: Optional[str] = None,
        info: Optional[Dict] = None,
        agent_create: Optional["AgentCreate"] = None,
        client: Optional["TiptreeClient"] = None,
    ) -> "Agent":
        """
        Get an existing agent by name or create a new one if it doesn't exist (asynchronous).

        Args:
            name: Name to search for or use in creation (defaults to "Unnamed Agent")
            description: Optional description for the agent if created
            info: Optional info dictionary for the agent if created
            agent_create: Optional agent creation parameters
            client: TiptreeClient instance, or None to use the default client

        Returns:
            Existing or newly created Agent object
        """
        search_name = name or "Unnamed Agent"
        existing_agents = await cls.async_list(client=client)

        # Search for agent with matching name
        for agent in existing_agents:
            if agent.config and agent.config.name == search_name:
                return agent

        # If not found, create new agent
        return await cls.async_create(
            name=name,
            description=description,
            info=info,
            agent_create=agent_create,
            client=client,
        )

    def create_agent_session(
        self,
        initial_prompt: Optional[str] = None,
        metadata: Optional[Dict] = None,
        agent_session_create: Optional["AgentSessionCreate"] = None,
    ) -> "AgentSession":
        """
        Create a new agent session for this agent (synchronous).

        Args:
            agent_session_create: Optional session creation parameters
            initial_prompt: Optional initial prompt for the session
            metadata: Optional metadata for the session

        Returns:
            Created AgentSession object
        """
        self.ensure_client_bound()
        agent_session_create = self._create_agent_session_params(
            agent_session_create, initial_prompt, metadata
        )
        return self.client.create_agent_session(self.id, agent_session_create)

    async def async_create_agent_session(
        self,
        initial_prompt: Optional[str] = None,
        metadata: Optional[Dict] = None,
        agent_session_create: Optional["AgentSessionCreate"] = None,
    ) -> "AgentSession":
        """
        Create a new agent session for this agent (asynchronous).

        Args:
            agent_session_create: Optional session creation parameters
            initial_prompt: Optional initial prompt for the session
            metadata: Optional metadata for the session

        Returns:
            Created AgentSession object
        """
        self.ensure_client_bound()
        agent_session_create = self._create_agent_session_params(
            agent_session_create, initial_prompt, metadata
        )
        return await self.client.async_create_agent_session(
            self.id, agent_session_create
        )

    def get_agent_session(self, agent_session_id: str) -> "AgentSession":
        """
        Get an agent session by ID (synchronous).

        Args:
            agent_session_id: ID of the session to retrieve

        Returns:
            AgentSession object
        """
        self.ensure_client_bound()
        return self.client.get_agent_session(agent_session_id)

    async def async_get_agent_session(self, agent_session_id: str) -> "AgentSession":
        """
        Get an agent session by ID (asynchronous).

        Args:
            agent_session_id: ID of the session to retrieve

        Returns:
            AgentSession object
        """
        self.ensure_client_bound()
        return await self.client.async_get_agent_session(agent_session_id)

    def list_agent_sessions(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        most_recent_first: Optional[bool] = None,
    ) -> List["AgentSession"]:
        """
        List all sessions for this agent with optional pagination and sorting (synchronous).

        Args:
            offset: Number of items to skip
            limit: Maximum number of items to return
            most_recent_first: Sort by creation time in descending order

        Returns:
            List of AgentSession objects
        """
        self.ensure_client_bound()
        return self.client.list_agent_sessions(
            self.id, offset=offset, limit=limit, most_recent_first=most_recent_first
        )

    async def async_list_agent_sessions(
        self,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
        most_recent_first: Optional[bool] = None,
    ) -> List["AgentSession"]:
        """
        List all sessions for this agent with optional pagination and sorting (asynchronous).

        Args:
            offset: Number of items to skip
            limit: Maximum number of items to return
            most_recent_first: Sort by creation time in descending order

        Returns:
            List of AgentSession objects
        """
        self.ensure_client_bound()
        return await self.client.async_list_agent_sessions(
            self.id, offset=offset, limit=limit, most_recent_first=most_recent_first
        )

    def update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        info: Optional[Dict] = None,
        task_whitelist: Optional[List[str]] = None,
        task_blacklist: Optional[List[str]] = None,
        enable_memory: Optional[bool] = None,
        enable_remembrance: Optional[bool] = None,
        agent_update: Optional["AgentUpdate"] = None,
    ) -> "Agent":
        """
        Update this agent (synchronous).

        Args:
            name: Optional new name for the agent
            description: Optional new description for the agent
            info: Optional new info dictionary for the agent
            task_whitelist: Optional list of allowed task names
            task_blacklist: Optional list of disallowed task names
            enable_memory: Whether to enable cross-session memory
            enable_remembrance: Whether to enable associative recall
            agent_update: Optional agent update parameters

        Returns:
            Updated Agent object
        """
        self.ensure_client_bound()
        agent_update = self._create_agent_update_params(
            agent_update,
            name,
            description,
            info,
            task_whitelist,
            task_blacklist,
            enable_memory,
            enable_remembrance,
        )
        return self.client.update_agent(self.id, agent_update)

    async def async_update(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        info: Optional[Dict] = None,
        task_whitelist: Optional[List[str]] = None,
        task_blacklist: Optional[List[str]] = None,
        enable_memory: Optional[bool] = None,
        enable_remembrance: Optional[bool] = None,
        agent_update: Optional["AgentUpdate"] = None,
    ) -> "Agent":
        """
        Update this agent (asynchronous).

        Args:
            name: Optional new name for the agent
            description: Optional new description for the agent
            info: Optional new info dictionary for the agent
            task_whitelist: Optional list of allowed task names
            task_blacklist: Optional list of disallowed task names
            enable_memory: Whether to enable cross-session memory
            enable_remembrance: Whether to enable associative recall
            agent_update: Optional agent update parameters

        Returns:
            Updated Agent object
        """
        self.ensure_client_bound()
        agent_update = self._create_agent_update_params(
            agent_update,
            name,
            description,
            info,
            task_whitelist,
            task_blacklist,
            enable_memory,
            enable_remembrance,
        )
        return await self.client.async_update_agent(self.id, agent_update)
