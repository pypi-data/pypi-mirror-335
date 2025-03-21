# Fabrica principal de mensajes, que convierte mensajes de meta, frontend o BD a mensajes de Chatty
from __future__ import annotations
from bson import ObjectId
from datetime import datetime
from zoneinfo import ZoneInfo
from ....models.messages import CentralNotification
from ....models.messages.chatty_messages.schema import ChattyContentCentral
from ....models.utils import MessageType, Status, MessageSubtype
from ....models.chat.continuous_conversation import ContinuousConversation
from ....models.messages.chatty_messages.schema import ChattyContext

class CentralNotificationFactory:

    @staticmethod
    def from_notification_body(notification_body: str) -> CentralNotification:
        return CentralNotification(
        created_at=datetime.now(tz=ZoneInfo("UTC")),
        updated_at=datetime.now(tz=ZoneInfo("UTC")),
        type=MessageType.CENTRAL,
        content=ChattyContentCentral(body=notification_body),
        status=Status.DELIVERED,
        is_incoming_message=False,
        id=str(ObjectId()),
        sent_by="notifications@letschatty.com",
        starred=False)

    @staticmethod
    def continuous_conversation_status(cc: ContinuousConversation, content:ChattyContentCentral) -> CentralNotification:

        return CentralNotification(
        created_at=datetime.now(tz=ZoneInfo("UTC")),
        updated_at=datetime.now(tz=ZoneInfo("UTC")),
        type=MessageType.CENTRAL,
        content=content,
        status=Status.DELIVERED,
        is_incoming_message=False,
        id=str(ObjectId()),
        sent_by="notifications@letschatty.com",
        starred=False,
        context = ChattyContext(continuous_conversation_id=cc.id),
        subtype=MessageSubtype.CONTINUOUS_CONVERSATION
        )
