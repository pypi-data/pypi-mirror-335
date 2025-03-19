from typing import TYPE_CHECKING

from tiptree.utils import ClientBind


if TYPE_CHECKING:
    from tiptree.interface_models import MessagePayload, MessageUpdate, Message


class MessageMixin(ClientBind):
    id: str
    payload: "MessagePayload"

    @property
    def content(self) -> str:
        return self.payload.content

    def update(self, message_update: "MessageUpdate") -> "Message":
        """
        Update this message (synchronous).

        Args:
            message_update: Update parameters for the message

        Returns:
            Updated Message object
        """
        self.ensure_client_bound()
        return self.client.update_message(self.id, message_update)

    async def async_update(self, message_update: "MessageUpdate") -> "Message":
        """
        Update this message (asynchronous).

        Args:
            message_update: Update parameters for the message

        Returns:
            Updated Message object
        """
        self.ensure_client_bound()
        return await self.client.async_update_message(self.id, message_update)

    def mark_as_read(self) -> "Message":
        """
        Mark this message as read (synchronous).

        Returns:
            Updated Message object
        """
        from tiptree.interface_models import MessageUpdate

        self.ensure_client_bound()
        return self.client.update_message(self.id, MessageUpdate(read=True))

    async def async_mark_as_read(self) -> "Message":
        """
        Mark this message as read (asynchronous).

        Returns:
            Updated Message object
        """
        from tiptree.interface_models import MessageUpdate

        self.ensure_client_bound()
        return await self.client.async_update_message(self.id, MessageUpdate(read=True))
