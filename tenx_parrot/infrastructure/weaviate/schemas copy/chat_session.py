"""Chat session schema for Weaviate."""
import os
import json
from typing import Dict, Any, List, Optional

import weaviate
import weaviate.classes.config as wc
from weaviate.classes.query import Filter

from core.logging import BackendLogger
logger = BackendLogger(os.path.basename(__file__))

class ChatSessionSchema:
    """Schema for chat sessions in Weaviate."""
    
    def __init__(self, collection_name="ChatSession", weaviate_client=None):
        self.collection_name = (collection_name
                              .title()
                              .replace('_','')
                              .replace(' ','')
                              .replace('-',''))
        self.weaviate = weaviate_client
        
    def create_collection(self,
                         collection_name="",
                         force: bool = False,
                         model: str = "text-embedding-3-small",
                         dim: int = 512):
        """Creates a new collection in Weaviate.
        
        Args:
            force (bool): Whether to force creation if exists
            model (str): OpenAI model to use
            dim (int): Vector dimensions
        """
        if not collection_name:
            collection_name = self.collection_name
            
        exists = self.check_collection_exists(collection_name)[0]
        
        if exists and not force:
            logger.error(f"Collection {collection_name} already exists")
            return
            
        if exists and force:
            logger.info(f"Deleting collection {collection_name} due to force flag")
            self.delete_collection(collection_name)
            
        self.weaviate.create_collection(
            collection_name=collection_name,
            description="Chat session data including messages, participants and context",
            vectorizer_config=wc.Configure.Vectorizer.text2vec_openai(
                model=model,
                dimensions=dim,
                vectorize_collection_name=False
            ),
            generative_config=wc.Configure.Generative.openai(),
            properties=[
                wc.Property(
                    name="session_id",
                    data_type=wc.DataType.TEXT,
                    description="Unique session identifier",
                    index_filterable=True,
                    index_searchable=True,
                    skip_vectorization=True,
                    tokenization=wc.Tokenization.FIELD
                ),
                wc.Property(
                    name="user_id",
                    data_type=wc.DataType.TEXT,
                    description="ID of the user",
                    index_filterable=True,
                    index_searchable=True,
                    skip_vectorization=True,
                    tokenization=wc.Tokenization.FIELD
                ),
                wc.Property(
                    name="messages",
                    data_type=wc.DataType.TEXT_ARRAY,
                    description="Array of chat messages",
                    index_filterable=True,
                    index_searchable=True,
                    skip_vectorization=False,
                    tokenization=wc.Tokenization.WORD
                ),
                wc.Property(
                    name="participants",
                    data_type=wc.DataType.TEXT_ARRAY,
                    description="List of session participants",
                    index_filterable=True,
                    index_searchable=True,
                    skip_vectorization=True,
                    tokenization=wc.Tokenization.WORD
                ),
                wc.Property(
                    name="start_time",
                    data_type=wc.DataType.TEXT,
                    description="Session start timestamp",
                    index_filterable=True,
                    index_searchable=True,
                    skip_vectorization=True,
                    tokenization=wc.Tokenization.FIELD
                ),
                wc.Property(
                    name="end_time",
                    data_type=wc.DataType.TEXT,
                    description="Session end timestamp",
                    index_filterable=True,
                    index_searchable=True,
                    skip_vectorization=True,
                    tokenization=wc.Tokenization.FIELD
                ),
                wc.Property(
                    name="context",
                    data_type=wc.DataType.TEXT,
                    description="Session context information",
                    index_filterable=True,
                    index_searchable=True,
                    skip_vectorization=False,
                    tokenization=wc.Tokenization.WORD
                ),
                wc.Property(
                    name="metadata",
                    data_type=wc.DataType.TEXT,
                    description="Additional session metadata",
                    index_filterable=True,
                    index_searchable=True,
                    skip_vectorization=True,
                    tokenization=wc.Tokenization.WORD
                ),
                wc.Property(
                    name="tags",
                    data_type=wc.DataType.TEXT,
                    description="Tags for categorizing the session",
                    index_filterable=True,
                    index_searchable=True,
                    skip_vectorization=True,
                    tokenization=wc.Tokenization.WORD
                ),
                wc.Property(
                    name="description",
                    data_type=wc.DataType.TEXT,
                    description="Additional description or notes",
                    index_filterable=False,
                    index_searchable=False,
                    skip_vectorization=True,
                    tokenization=wc.Tokenization.WORD
                )
            ]
        )
        
        logger.info(f"Collection {collection_name} created successfully")
        
    def check_collection_exists(self, collection_name=""):
        if not collection_name:
            collection_name = self.collection_name
        return self.weaviate.check_if_collection_exists(collection_name)
        
    def delete_collection(self, collection_name=""):
        if not collection_name:
            collection_name = self.collection_name
        exists = self.check_collection_exists(collection_name)[0]
        if not exists:
            logger.error(f"Collection {collection_name} doesn't exist")
            return
        self.weaviate.delete_collection(collection_name)
        
    def get_properties(self):
        """Get schema properties."""
        prop = ["session_id", "user_id", "messages", "participants", "start_time",
                "end_time", "context", "metadata", "tags", "description"]
        bm25prop = ["messages", "context", "metadata", "tags"]
        mandatory_prop = ["session_id", "user_id", "messages"]
        return prop, bm25prop, mandatory_prop
        
    def parse_response(self, res, include_vector=False):
        """Parse Weaviate response."""
        prop, _, _ = self.get_properties()
        if isinstance(res, dict):
            for p in prop:
                if res.get(p):
                    if isinstance(res[p], list):
                        res[p] = [str(item).replace("\n", " ") for item in res[p]]
                    else:
                        res[p] = str(res[p]).replace("\n", " ")
        elif isinstance(res, list):
            res = [self.parse_response(r) for r in res]
        elif isinstance(res, (weaviate.collections.classes.internal.Object,
                            weaviate.collections.classes.internal.ObjectSingleReturn)):
            uuid = str(res.uuid)
            wmetadata = res.metadata.__dict__
            vector = res.vector["default"] if include_vector else None
            res = self.parse_response(res.properties)
            if res:
                res['uuid'] = uuid
                res['weaviate_metadata'] = wmetadata
                res['vector'] = vector
        return res

    def add_object(self, data_object, include_vector=True, return_object=False, collection_name=""):
        """Add object to collection."""
        if not collection_name:
            collection_name = self.collection_name
            
        if not isinstance(data_object, dict):
            logger.error("Data object must be a dictionary")
            return

        # Check mandatory properties
        _, _, mandatory_prop = self.get_properties()
        for prop in mandatory_prop:
            if prop not in data_object:
                logger.error(f"Missing mandatory property: {prop}")
                return

        uuid = self.weaviate.add_object_to_collection(collection_name, data_object)
        if return_object and uuid:
            obj = self.weaviate.get_object_by_id(collection_name, uuid, include_vector=include_vector)
            res = self.parse_response(obj, include_vector=include_vector)
            return res
        return uuid

    def get_content(self, collection_name="", limit=1000, offset=0, include_vector=False):
        """Get objects from collection."""
        if not collection_name:
            collection_name = self.collection_name
        obj = self.weaviate.get_objects(
            collection_name,
            include_vector=include_vector,
            limit=limit,
            offset=offset
        )
        return self.parse_response(obj, include_vector=include_vector)

    def get_by_keyword(self, keyword, include_vector=False, collection_name=""):
        """Search objects by keyword."""
        if not collection_name:
            collection_name = self.collection_name
        obj = self.weaviate.keyword_search(collection_name, query_text=keyword)
        return self.parse_response(obj, include_vector=include_vector)

    def get_by_id(self, id, include_vector=False, collection_name=""):
        """Get object by ID."""
        if not collection_name:
            collection_name = self.collection_name
        obj = self.weaviate.get_object_by_id(collection_name, object_id=id)
        return self.parse_response(obj, include_vector=include_vector)