from __future__ import annotations
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import model_validator, Field, field_validator
from zoneinfo import ZoneInfo
from enum import StrEnum
from ..messages.chatty_messages.base.message_draft import MessageDraft, SendMessagesFromAgentToChat
from ..base_models.chatty_asset_model import ChattyAssetModel
from ..utils.types.message_types import MessageSubtype
from ..messages.chatty_messages.schema import ChattyContext
from ...models.utils.types.message_types import MessageType


class ContinuousConversationStatus(StrEnum):
    APPROVED = "approved" # User accepted the CC request
    REJECTED = "rejected" # User rejected the CC request
    CANCELLED = "cancelled" # Agent canceled the CC request
    EXPIRED = "expired" # CC request expired without response
    OTHER_ANSWER = "other_answer" # User sent non-standard response
    FAILED = "failed" # CC request failed because template couldn't be send
    CREATED = "created" # CC request created
    SENT = "sent" # CC request sent to the user

class ContinuousConversation(ChattyAssetModel):
    template_message_waid: Optional[str] = None
    status: Optional[ContinuousConversationStatus] = Field(default=ContinuousConversationStatus.CREATED)
    active: bool = Field(default=True)
    expires_at: datetime = Field(default=datetime.now(ZoneInfo("UTC")) + timedelta(days=10))
    messages: List[MessageDraft]
    agent_email: str

    @property
    def is_expired(self) -> bool:
        return self.expires_at < datetime.now(ZoneInfo("UTC"))

    @field_validator("messages")
    @classmethod
    def first_message_is_text(cls, v: List[MessageDraft]):
        """First message must be a text message"""
        if not v:
            raise ValueError("Messages are required")
        first_message = v[0]
        if first_message.type != MessageType.TEXT:
            raise ValueError("First message must be a text message")
        return v

    @model_validator(mode='after')
    def set_context_and_subtype_on_messages(self):
        for message in self.messages:
            message.context = ChattyContext(continuous_conversation_id=self.id)
            message.subtype = MessageSubtype.CONTINUOUS_CONVERSATION
        return self

    def append_messages(self, messages: List[MessageDraft]):
        for message in messages:
            message.context = ChattyContext(continuous_conversation_id=self.id)
            message.subtype = MessageSubtype.CONTINUOUS_CONVERSATION
            self.messages.append(message)
        return self


    def set_status(self, status: ContinuousConversationStatus):
        self.status = status
        self.active = False
        return None