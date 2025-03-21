from pydantic import BaseModel, Field
from enum import StrEnum
from typing import Optional



class CentralNotificationStatus(StrEnum):
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"
    INFO_HIGHLIGHTED = "info_highlighted"

# Soolo se generan DESDE LA BASE DE DATOS

class ChattyContentCentral(BaseModel):
    body: str
    status: Optional[CentralNotificationStatus] = Field(default=CentralNotificationStatus.INFO)
    CTA : Optional[str] = None

    def model_dump(self, *args, **kwargs):
        kwargs['exclude_unset'] = True
        return super().model_dump(*args, **kwargs)