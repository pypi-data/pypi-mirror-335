from __future__ import annotations
from typing import Dict, Type, TYPE_CHECKING
import logging

from .....models.analytics.sources import WhatsAppDefaultSource, TopicDefaultSource, PureAd, Source
from .....models.utils.types.source_types import SourceType
from .helpers import SourceFactoryHelpers

from bson import ObjectId

if TYPE_CHECKING:
    from .....models.messages import ChattyMessage
    from .....models.analytics.smart_messages.topic import Topic

logger = logging.getLogger(__name__)

class SourceFactory:

    @staticmethod
    def instantiate_source(source_data: dict) -> Source:
        """Instantiate a source from a dictionary.
        1) from mongo
        2) from a request (if its new, it creates the id for posterior mongo insertion)
        """
        source_type = source_data.get("type")
        source_class : Source = SourceFactoryHelpers.source_type_to_class(source_type)
        try:
            return source_class(**source_data)
        except Exception as e:
            logger.error(f"Error creating source of type {source_type}: {str(e)} {source_data}")
            raise e

    @staticmethod
    def create_whatsapp_default_source() -> WhatsAppDefaultSource:
        return WhatsAppDefaultSource()

    @staticmethod
    def create_topic_default_source(topic: Topic) -> TopicDefaultSource:
        return TopicDefaultSource(topic_id=topic.id, name = f"{topic.name} Topic Default Source", _id = topic.default_source_id, description= "Message matched the Topic but there was no direct source to attribute it to.", created_at=topic.created_at, updated_at=topic.updated_at)

    @staticmethod
    def create_new_pure_ad_not_loaded(message: ChattyMessage, default_flow: str = None) -> PureAd:
        body = message.referral.body
        headline = message.referral.headline
        source_url = message.referral.source_url
        ad_id = message.referral.source_id
        name_for_ad = f"Nuevo Anuncio de Meta {ad_id} {headline}"
        description = f"Se creó el anuncio ya que no estaba cargado como fuente de origen. \n Info: {source_url} - {body}"

        source_data = {
            "agent_email": "source_checker@letschatty.com",
            "name": name_for_ad,
            "type": SourceType.PURE_AD,
            "ad_id": ad_id,
            "flow": default_flow,
            "description": description,
            "trackeable": True,
            "meta_ad_url": message.referral.source_url,
            "meta_source_type": message.referral.source_type,
            "meta_body": message.referral.body,
            "meta_headline": message.referral.headline,
            "meta_media_type": message.referral.media_type,
            "meta_thumbnail_url": message.referral.thumbnail_url,
            "meta_image_url": message.referral.image_url,
            "meta_video_url": message.referral.video_url
            }

        return SourceFactory.instantiate_source(source_data)

    @staticmethod
    def create_new_impure_ad(message: ChattyMessage, default_flow: str = None) -> PureAd:
        source_data = {
            "agent_email": "source_checker@letschatty.com",
            "name": f"Anuncio Meta Impuro - {message.referral.source_url}",
            "type": SourceType.PURE_AD,
            "ad_id": "provisional_ad_id" + str(ObjectId()),
            "description": f"El anuncio es impuro porque sólo contiene la url del anuncio (falta el ad_id): {message.referral.source_url}",
            "trackeable": True,
            "meta_ad_url":message.referral.source_url.strip(),
            "flow": default_flow
        }
        return SourceFactory.instantiate_source(source_data)
