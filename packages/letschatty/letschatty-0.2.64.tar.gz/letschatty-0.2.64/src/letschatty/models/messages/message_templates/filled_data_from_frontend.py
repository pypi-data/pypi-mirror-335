from __future__ import annotations
from typing import List, TYPE_CHECKING
from pydantic import BaseModel, Field, model_validator
from ...utils.definitions import Area
from ...utils.types.identifier import StrObjectId
from enum import StrEnum
import logging

if TYPE_CHECKING:
    from .required_for_frontend_templates import RequiredTemplateParameter

logger = logging.getLogger("RecipientOfTemplateCampaign")

class TemplateOrigin(StrEnum):
    FROM_CHAT = "from_chat"
    FROM_CAMPAIGN = "from_campaign"
    FROM_WORKFLOW = "from_workflow"
    FROM_CONTINUOUS_CONVERSATION = "from_continuous_conversation"
    FROM_TEMPLATES_MANAGER = "from_templates_manager"


class FilledRecipientParameter(BaseModel):
    id: str
    text: str

    @classmethod
    def from_required_template_parameters_and_recipient_dict(cls, required_template_parameters: List[RequiredTemplateParameter], recipient_dict: dict) -> List[FilledRecipientParameter]:
        logger.debug(f"Required template parameters: {required_template_parameters}")
        logger.debug(f"Recipient dict: {recipient_dict}")
        try:
            return [FilledRecipientParameter(id=parameter.id, text=recipient_dict[parameter.id]) for parameter in required_template_parameters]
        except KeyError as e:
            logger.error(f"Error in campaign creation: Missing parameter: {e} in recipient with phone number: {recipient_dict['phone_number']}")
            raise ValueError(f"Error in campaign creation: Missing parameter: {e} in recipient with phone number: {recipient_dict['phone_number']}")


class FilledTemplateData(BaseModel):
    template_name: str
    area: Area
    agent_email: str
    assign_to_agent: str | None = None
    phone_number: str | None = None
    new_contact_name: str | None = None
    parameters: List[FilledRecipientParameter] = Field(default_factory=list)
    tags: List[StrObjectId] = Field(default_factory=list)
    products: List[StrObjectId] = Field(default_factory=list)
    flow: List[StrObjectId] = Field(default_factory=list)
    description: str | None = None
    forced_send: bool = False
    lenguage: str | None = None
    campaign_name: str | None = None
    campaign_id: StrObjectId | None = None
    body: str | None = None
    origin : TemplateOrigin


    @model_validator(mode='after')
    def validate_template_data(self) -> dict:

        if self.area == Area.WITH_AGENT and not self.assign_to_agent:
            # TEMPORARY FIX FOR AGENT ASSIGNMENT: IF IT'S NOT SPECIFIED, ASSIGN TO THE AGENT EMAIL
            raise ValueError("Agent assignment must be specified for WITH AGENT area")

        if not self.phone_number:
            logger.warning("Phone number must be specified for single recipient")
            raise ValueError("Phone number must be specified for single recipient")

        self.phone_number = str(self.phone_number)

        if not self.new_contact_name:
            self.new_contact_name = self.phone_number

        return self