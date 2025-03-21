from pydantic import Field
from datetime import datetime, timedelta
from typing import Optional
from ..base_models import ChattyAssetModel
from ..utils.types.identifier import StrObjectId
from .sources import Source
from .sources.utms.referer_info import RefererInfo
from ..utils.types.source_types import SourceCheckerType

class ContactPoint(ChattyAssetModel):
    source_checker_method : SourceCheckerType
    source_id: Optional[StrObjectId] = Field(default=None)
    source: Optional[Source] = Field(default=None, exclude=True) #This is only used inside the API as a shortcut, so it's not stored in the DB
    match_timestamp: Optional[datetime] = Field(default=None)
    referer_info: Optional[RefererInfo] = Field(default=None)
    time_from_request_to_match : Optional[timedelta] = Field(default=None)
    topic_id : Optional[StrObjectId] = Field(default=None)
    chat_id : Optional[StrObjectId] = Field(default=None)
    message_id : Optional[str] = Field(default=None)
    
