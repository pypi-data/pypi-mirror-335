from pymilvus import MilvusClient, DataType

from src.vector_stores.store_interface import VectorStoreInterface

class MilvusVectorStore(VectorStoreInterface):
    def __init__(self, uri="milvus-lite-local.db", db_name="default", **kwargs) -> None:
        self._client = MilvusClient(uri=uri, db_name=db_name, **kwargs)

    @property
    def name(self):
        """Returns name of the vector store"""
        return "Milvus"
    
    def get_client(self):
        return self._client
    
    def drop_collection(self, collection_name):
        if self._client.has_collection(collection_name):
            self._client.drop_collection(collection_name)
        return self
    
    def collection_exists(self, collection_name):
        if self._client.has_collection(collection_name):
            return True
        return False

    def create_collection(self,
                          collection_name,
                          dim,
                          vector_field_name="vec_emb",
                          primary_field_name="id",
                          id_type=DataType.VARCHAR,
                          metric_type="COSINE",
                          auto_id=False,
                          max_length=36,
                          **kwargs):
        assert isinstance(collection_name, str)
        assert isinstance(vector_field_name, str)
        assert isinstance(dim, int)
        _ = self._client.create_collection(
            collection_name,
            dim,
            primary_field_name=primary_field_name,
            id_type=id_type,
            vector_field_name=vector_field_name,
            metric_type=metric_type,
            auto_id=auto_id,
            max_length=max_length,
            **kwargs
        )
        return self
    
    def upsert(self, collection_name, data, **kwargs):
        """Insert/update data into the vector store"""
        _ = self._client.upsert(
            collection_name=collection_name,
            data=data
        )
        return self
    
    def insert(self, collection_name, data, **kwargs):
        """Insert data into the vector store"""
        _ = self._client.insert(
            collection_name=collection_name,
            data=data
        )
        return self
    
    def retrieve(self, **kwargs):
        """Retrieve data from the vector store"""
        raise NotImplementedError
    
    def delete(self, collection_name, ids, **kwargs):
        """Delete data from the vector store. ids is a list of ids"""
        _ = self._client.delete(
            collection_name=collection_name,
            ids=ids
        )
        return self

    def ann_search(self, collection_name: str,
                            vec_emb,
                            k: int=10,
                            output_fields=[],
                            search_params=None,
                            filters="",
                            **kwargs):
        """Search k approximate nearest neighbors """
        if not search_params:
            search_criterion  = {"metric_type": "COSINE", "params": {"nprobe": 10}}
        retrieved_results = self._client.search(
            collection_name=collection_name,
            data=vec_emb, 
            search_params=search_criterion, 
            limit=k, 
            consistency_level="Strong",
            output_fields=output_fields,
            filter=filters,
            **kwargs
        )
        return retrieved_results

    def query(self, collection_name: str,
                            filters="",
                            output_fields=[],
                            **kwargs):
        """Search vector store directly based on some filter without embeddings"""
        retrieved_results = self._client.query(
            collection_name=collection_name,
            output_fields=output_fields,
            filter=filters,
            **kwargs
        )
        return retrieved_results


if __name__=="__main__":
    milvus_uri = "http://milvus-dev.esolutions.de:19530"
    milvus = MilvusVectorStore(uri=milvus_uri, db_name="ama_db")
    milvus.create_collection("confluence_chunks", 1024)