from . import TimestampValidationMixin, UpdateableMixin
from pydantic import BaseModel, Field, ConfigDict
from typing import Any, ClassVar
from bson import ObjectId
from ...models.utils.types import StrObjectId
from ...models.utils.types.serializer_type import SerializerType
import logging
import json
# Create and configure logger
logger = logging.getLogger("chatty_asset_model")

class ChattyAssetModel(TimestampValidationMixin, UpdateableMixin, BaseModel):
    id: StrObjectId = Field(alias="_id", default_factory=lambda: str(ObjectId()), frozen=True)
    exclude_fields: ClassVar[dict[SerializerType, set[str]]] = {}
    model_config = ConfigDict(
        populate_by_alias=True)

    def model_dump(
        self,
        *args,
        serializer: SerializerType = SerializerType.API,
        **kwargs
    ) -> dict[str, Any]:
        # Get fields to exclude for this serializer type
        exclude = self.exclude_fields.get(serializer, set())

        # Add exclude to kwargs if not present, or update existing exclude
        if 'exclude' in kwargs:
            if isinstance(kwargs['exclude'], set):
                kwargs['exclude'].update(exclude)
            else:
                kwargs['exclude'] = exclude
        else:
            kwargs['exclude'] = exclude

        kwargs["by_alias"] = True
        data = super().model_dump(*args, **kwargs)
        ordered_data = {}

        # Handle id/_id field based on serializer type
        id_value = data.pop('_id')
        if serializer == SerializerType.FRONTEND_ASSET_PREVIEW or serializer == SerializerType.FRONTEND:
            ordered_data['id'] = id_value
        elif serializer == SerializerType.DATABASE:
            ordered_data['_id'] = ObjectId(id_value) if isinstance(id_value, str) else id_value
        else:  # API and other cases
            ordered_data['_id'] = id_value

        # Handle name field if present
        if 'name' in data:
            ordered_data['name'] = data.pop('name')

        # Add remaining fields
        ordered_data.update(data)
        return ordered_data

    def model_dump_json(
        self,
        *args,
        serializer: SerializerType = SerializerType.API,  # Default to API for JSON
        **kwargs
    ) -> str:
        # Just add serializer to kwargs and let parent handle the JSON conversion
        dumped_json = super().model_dump_json(*args, exclude=self.exclude_fields.get(serializer, set()), **kwargs)
        if serializer == SerializerType.DATABASE:
            dumped_json = json.loads(dumped_json)
            id = dumped_json.pop("_id", None)
            if not id:
                id = dumped_json.pop("id", None)
            dumped_json["_id"] = ObjectId(id)
        return dumped_json
