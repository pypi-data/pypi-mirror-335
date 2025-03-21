from __future__ import annotations
from typing import TypeVar, Generic, Type, Callable, TYPE_CHECKING
from .base_container_with_collection import ChattyAssetCollectionInterface, ChattyAssetContainerWithCollection
from ...models.base_models import ChattyAssetModel
from ...models.data_base.mongo_connection import MongoConnection
    
T = TypeVar('T', bound=ChattyAssetModel)

class AssetCollection(Generic[T], ChattyAssetCollectionInterface[T]):
    def __init__(self, 
                 database: str, 
                 collection: str, 
                 asset_type: Type[T],
                 connection: MongoConnection,
                 create_instance_method: Callable[[dict], T]):
        super().__init__(
            database=database,
            collection=collection,
            connection=connection,
            type=asset_type
        )
        self._create_instance_method = create_instance_method

    def create_instance(self, data: dict) -> T:
        if not isinstance(data, dict):
            raise ValueError(f"Data must be a dictionary, got {type(data)}: {data}")
        return self._create_instance_method(data)

class AssetService(Generic[T], ChattyAssetContainerWithCollection[T]):
    """Generic service for handling CRUD operations for any Chatty asset"""
    
    def __init__(self, 
                 database_name: str,
                 collection_name: str,
                 asset_type: Type[T],
                 connection: MongoConnection,
                 create_instance_method: Callable[[dict], T]):
        asset_collection = AssetCollection(
            database=database_name,
            collection=collection_name,
            asset_type=asset_type,
            connection=connection,
            create_instance_method=create_instance_method
        )
        super().__init__(
            item_type=asset_type,
            collection=asset_collection
        )
