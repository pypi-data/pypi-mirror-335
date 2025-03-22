from __future__ import annotations

import logging
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    Literal,
    Optional,
    Tuple,
    TypeVar,
    Union,
    cast,
)

import numpy as np
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import VectorStore

from pylevers import *
from pylevers.core.types import *

from langchain_levers.utils.constant import *

logger = logging.getLogger(__name__)

DEFAULT_LEVERS_CONNECTION = {
    "host": "localhost",
    "port": 8099,
}

Matrix = Union[List[List[float]], List[np.ndarray], np.ndarray]


def cosine_similarity(X: Matrix, Y: Matrix) -> np.ndarray:
    """Row-wise cosine similarity between two equal-width matrices."""
    if len(X) == 0 or len(Y) == 0:
        return np.array([])

    X = np.array(X)
    Y = np.array(Y)
    if X.shape[1] != Y.shape[1]:
        raise ValueError(
            f"Number of columns in X and Y must be the same. X has shape {X.shape} "
            f"and Y has shape {Y.shape}."
        )
    try:
        import simsimd as simd

        X = np.array(X, dtype=np.float32)
        Y = np.array(Y, dtype=np.float32)
        Z = 1 - np.array(simd.cdist(X, Y, metric="cosine"))
        return Z
    except ImportError:
        logger.debug(
            "Unable to import simsimd, defaulting to NumPy implementation. If you want "
            "to use simsimd please install with `pip install simsimd`."
        )
        X_norm = np.linalg.norm(X, axis=1)
        Y_norm = np.linalg.norm(Y, axis=1)
        # Ignore divide by zero errors run time warnings as those are handled below.
        with np.errstate(divide="ignore", invalid="ignore"):
            similarity = np.dot(X, Y.T) / np.outer(X_norm, Y_norm)
        similarity[np.isnan(similarity) | np.isinf(similarity)] = 0.0
        return similarity


def maximal_marginal_relevance(
    query_embedding: np.ndarray,
    embedding_list: list,
    lambda_mult: float = 0.5,
    k: int = 4,
) -> List[int]:
    """Calculate maximal marginal relevance.

    Args:
        query_embedding: The query embedding.
        embedding_list: The list of embeddings.
        lambda_mult: The lambda multiplier. Defaults to 0.5.
        k: The number of results to return. Defaults to 4.

    Returns:
        List[int]: The list of indices.
    """
    if min(k, len(embedding_list)) <= 0:
        return []
    if query_embedding.ndim == 1:
        query_embedding = np.expand_dims(query_embedding, axis=0)
    similarity_to_query = cosine_similarity(query_embedding, embedding_list)[0]
    most_similar = int(np.argmax(similarity_to_query))
    idxs = [most_similar]
    selected = np.array([embedding_list[most_similar]])
    while len(idxs) < min(k, len(embedding_list)):
        best_score = -np.inf
        idx_to_add = -1
        similarity_to_selected = cosine_similarity(embedding_list, selected)
        for i, query_score in enumerate(similarity_to_query):
            if i in idxs:
                continue
            redundant_score = max(similarity_to_selected[i])
            equation_score = (
                lambda_mult * query_score - (1 - lambda_mult) * redundant_score
            )
            if equation_score > best_score:
                best_score = equation_score
                idx_to_add = i
        idxs.append(idx_to_add)
        selected = np.append(selected, [embedding_list[idx_to_add]], axis=0)
    return idxs


EmbeddingType = Union[Embeddings]
T = TypeVar("T")


class Levers(VectorStore):
    """Milvus vector store integration.

    Setup:
        Install ``langchain_milvus`` package:

        .. code-block:: bash

            pip install -qU  langchain_milvus

    Key init args — indexing params:
        collection_name: str
            Name of the collection.
        collection_description: str
            Description of the collection.
        embedding_function: Union[Embeddings, BaseSparseEmbedding]
            Embedding function to use.

    Key init args — client params:
        connection_args: Optional[dict]
            Connection arguments.

    Instantiate:
        .. code-block:: python

            from langchain_milvus import Milvus
            from langchain_openai import OpenAIEmbeddings

            URI = "./milvus_example.db"

            vector_store = Milvus(
                embedding_function=OpenAIEmbeddings(),
                connection_args={"uri": URI},
            )

    Add Documents:
        .. code-block:: python

            from langchain_core.documents import Document

            document_1 = Document(page_content="foo", metadata={"baz": "bar"})
            document_2 = Document(page_content="thud", metadata={"baz": "baz"})
            document_3 = Document(page_content="i will be deleted :(", metadata={"baz": "qux"})

            documents = [document_1, document_2, document_3]
            ids = ["1", "2", "3"]
            vector_store.add_documents(documents=documents, ids=ids)

    Delete Documents:
        .. code-block:: python

            vector_store.delete(ids=["3"])

    Search:
        .. code-block:: python

            results = vector_store.similarity_search(query="thud",k=1)
            for doc in results:
                print(f"* {doc.page_content} [{doc.metadata}]")

        .. code-block:: python

            * thud [{'baz': 'baz', 'pk': '2'}]

    Search with filter:
        .. code-block:: python

            results = vector_store.similarity_search(query="thud",k=1,filter={"bar": "baz"})
            for doc in results:
                print(f"* {doc.page_content} [{doc.metadata}]")

        .. code-block:: python

            * thud [{'baz': 'baz', 'pk': '2'}]

    Search with score:
        .. code-block:: python

            results = vector_store.similarity_search_with_score(query="qux",k=1)
            for doc, score in results:
                print(f"* [SIM={score:3f}] {doc.page_content} [{doc.metadata}]")

        .. code-block:: python

            * [SIM=0.335463] foo [{'baz': 'bar', 'pk': '1'}]

    Async:
        .. code-block:: python

            # add documents
            # await vector_store.aadd_documents(documents=documents, ids=ids)

            # delete documents
            # await vector_store.adelete(ids=["3"])

            # search
            # results = vector_store.asimilarity_search(query="thud",k=1)

            # search with score
            results = await vector_store.asimilarity_search_with_score(query="qux",k=1)
            for doc,score in results:
                print(f"* [SIM={score:3f}] {doc.page_content} [{doc.metadata}]")

        .. code-block:: python

            * [SIM=0.335463] foo [{'baz': 'bar', 'pk': '1'}]

    Use as Retriever:
        .. code-block:: python

            retriever = vector_store.as_retriever(
                search_type="mmr",
                search_kwargs={"k": 1, "fetch_k": 2, "lambda_mult": 0.5},
            )
            retriever.invoke("thud")

        .. code-block:: python

            [Document(metadata={'baz': 'baz', 'pk': '2'}, page_content='thud')]

    """  # noqa: E501

    def __init__(
        self,
        embedding_function: Optional[Union[EmbeddingType, List[EmbeddingType]]],
        collection_name: str = DEFAULT_COLL_NAME,
        collection_description: str = "",
        collection_properties: Optional[dict[str, Any]] = None,
        connection_args: Optional[dict[str, Any]] = None,
        index_params: Optional[Union[dict, List[dict]]] = None,
        search_params: Optional[Union[dict, List[dict]]] = None,
        drop_old: Optional[bool] = False,
        *,
        primary_field: str = PRIMARY_FIELD,
        text_field: str = TEXT_FIELD,
        vector_field: str = VECTOR_FIELD,
        timeout: Optional[float] = None,
        num_shards: Optional[int] = None,
    ):
        """Initialize the Levers vector store."""
        self.default_search_params = {
            "SPANN": {"metric_type": "L2", "params": {}},
            "HNSW": {"metric_type": "L2", "params": {"ef": 10}},
        }

        if not embedding_function:
            raise ValueError("No embedding function provided.")

        _embedding_function = self._as_list(embedding_function)
        if len(_embedding_function) > 1:
            raise ValueError("Only one embedding function is supported.")

        self.embedding_func: Optional[
            Union[EmbeddingType, List[EmbeddingType]]
        ] = self._from_list(embedding_function)

        self.collection_description = collection_description
        self.collection_properties = collection_properties
        self.index_params = index_params
        self.search_params = search_params

        self._primary_field = primary_field
        self._text_field = text_field
        self._vector_field = vector_field
        self._metadata_field : Optional[dict[str, DataType]] = {}
        self._timeout = timeout
        self._num_shards = num_shards

        self.cli : Client = None

        if not connection_args:
            connection_args = DEFAULT_LEVERS_CONNECTION
        else:
            if not connection_args.get("host"):
                connection_args["host"] = DEFAULT_LEVERS_CONNECTION["host"]
            if not connection_args.get("port"):
                connection_args["port"] = DEFAULT_LEVERS_CONNECTION["port"]

        self.user = connection_args.get("user", "")
        self.password = connection_args.get("password", "")
        self.db_name = connection_args.get("db_name", DEFAULT_DB_NAME)
        self.collection_name = collection_name

        self._connection_args = connection_args

        self._create_connection()

        self._collection_schema = self._get_collection_schema()
        # print(f"collection_schema: {self._collection_schema}")
        # print(f"drop_old: {drop_old}")
        if drop_old and self._collection_schema:
            self.cli.drop_collection(self.collection_name)
            self._collection_schema = None
        if self._collection_schema:
            logger.info(f"Collection {self.collection_name} already exists.")
            for field in self._collection_schema.fields:
                # print(f"field: {field.name} {field.data_type}")
                not_metadata_field = [self._text_field, self._vector_field]
                if field.name in not_metadata_field:
                    continue
                self._metadata_field[field.name] = field.data_type
            # print(f"Metadata fields: {self._metadata_field}")
            logger.info(f"Metadata fields: {self._metadata_field}")

    def _create_connection(self):
        """Create a connection to Levers."""
        self.cli = Client(
            self._connection_args["host"],
            self._connection_args["port"])
        self.cli.connect(
            user=self.user,
            password=self.password,
            db_name=self.db_name,
        )

    def _create_collection(
        self, embeddings: List[list], metadatas: Optional[list[dict]] = None
    ) -> None:
        """Create a collection in Levers."""
        fields = []

        # text field
        fields.append(
            FieldSchema(name=self._text_field,
                        data_type=DataType.STRING,
                        indexed_segment_schema=None))

        # metadata fields
        if metadatas:
            for k,v in metadatas[0].items():
                dt = None
                if isinstance(v, int) or isinstance(v, np.int64):
                    dt = DataType.INT64
                elif isinstance(v, np.int32):
                    dt = DataType.INT32
                elif isinstance(v, float) or isinstance(v, np.float32) or isinstance(v, np.float64):
                    dt = DataType.FLOAT
                elif isinstance(v, bool) or isinstance(v, np.bool_):
                    dt = DataType.BOOL
                elif isinstance(v, str):
                    dt = DataType.STRING
                else:
                    logger.warning(f"Metadata field {k} has unsupported type {type(v)}, defaulting to string.")
                    dt = DataType.NONE
                self._metadata_field[k] = dt
                dt = DataType.STRING if dt == DataType.NONE else dt
                fields.append(
                    FieldSchema(name=k,
                                data_type=dt,
                                indexed_segment_schema=None))

        # print("embeddings: type", type(embeddings))
        # print(f"embeddings: {len(embeddings[0][0])}")
        # vector fields
        for i, _ in enumerate(self._as_list(self.embedding_func)):
            dim = len(embeddings[0][0])
            fields.append(
                FieldSchema(name=self._vector_field if len(self._as_list(self.embedding_func)) == 1 else f"{self._vector_field}_{i}",
                            data_type=DataType.FLOAT_VECTOR,
                            indexed_segment_schema=None,
                            dimension=dim)
            )

        collection_schema = CollectionSchema(
                name=self.collection_name,
                description=self.collection_description,
                fields=fields,
                extra_params=self.collection_properties if self.collection_properties else {},
        )
        status = self.cli.create_collection(collection_schema)
        logger.info(f"Collection {self.collection_name} created with status {status}")
        # set collection schema
        self._collection_schema = collection_schema

    def _get_collection_schema(self) -> CollectionSchema:
        """Check if the collection exists."""
        status, schema = self.cli.describe_collection(self.collection_name)
        logger.debug(f"_collection_schema_status: {status.code}, _collection_schema_stats: {schema}")
        # print(f"_collection_schema_status: {status.code}")
        # print(f"_collection_schema_stats: {schema}")
        if status.code == 0 and isinstance(schema, CollectionSchema) and schema.name == f"{self.db_name}_{self.collection_name}":
            return schema
        else:
            return None

    def add_documents(self, documents: List[Document], **kwargs: Any) -> List[str]:
        """Run more documents through the embeddings and add to the vectorstore.

        Args:
            documents: Documents to add to the vectorstore.

        Returns:
            List of IDs of the added texts.
        """
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        return self.add_texts(texts, metadatas, **kwargs)

    def add_texts(
        self,
        texts: Iterable[str],
        metadatas: Optional[List[dict]] = None,
        timeout: Optional[float] = None,
        batch_size: int = 1000,
        *,
        ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> List[str]:
        """Insert text data into Levers.

        Inserting data when the collection has not be made yet will result
        in creating a new Collection. The data of the first entity decides
        the schema of the new collection, the dim is extracted from the first
        embedding and the columns are decided by the first metadata dict.
        Metadata keys will need to be present for all inserted values. At
        the moment there is no None equivalent in Levers.

        Args:
            texts (Iterable[str]): The texts to embed, it is assumed
                that they all fit in memory.
            metadatas (Optional[List[dict]]): Metadata dicts attached to each of
                the texts. Defaults to None.
            should be less than 65535 bytes. Required and work when auto_id is False.
            timeout (Optional[float]): Timeout for each batch insert. Defaults
                to None.
            batch_size (int, optional): Batch size to use for insertion.
                Defaults to 1000.
            ids (Optional[List[str]]): List of text ids. The length of each item

        Raises:
            Exception: Failure to add texts

        Returns:
            List[str]: The resulting keys for each inserted element.
        """

        entity_metas = []

        # embeddings
        embeddings: List = []
        for _embedding_func in self._as_list(self.embedding_func):
            try:
                embeddings.append(_embedding_func.embed_documents(texts))
            except NotImplementedError:
                embeddings.append([_embedding_func.embed_query(x) for x in texts])
        # print(f"Embeddings: {embeddings}")

        # init collection
        if self._collection_schema is None:
            # print("Creating collection")
            self._create_collection(
                embeddings=embeddings,
                metadatas=metadatas,
            )

        # text field
        entity_metas.append(EntityMeta(self._text_field, DataType.STRING))
        # metadata fields
        if self._metadata_field:
            for k,v in self._metadata_field.items():
                dt = DataType.STRING if v == DataType.NONE else v
                entity_metas.append(EntityMeta(k, dt))
        # vector fields
        for i, _ in enumerate(self._as_list(self.embedding_func)):
            entity_metas.append(EntityMeta(
                self._vector_field if len(self._as_list(self.embedding_func)) == 1 else f"{self._vector_field}_{i}",
                DataType.FLOAT_VECTOR))

        ids_len = len(ids) if ids else 0
        entities = []
        inserted_ids = []
        if not self._metadata_field:
            metadatas = [{} for _ in range(len(texts))]
        for index, (text, metadata) in enumerate(zip(texts, metadatas)):
            # print(f"Index: {index}, Text: {text}, Metadata: {metadata}")
            field_values = []
            # text value
            field_values.append(text)
            # metadata values
            if self._metadata_field:
                if not metadata or len(metadata) != len(self._metadata_field):
                    raise ValueError(
                        f"Metadata must be a list of dicts with keys matching the metadata fields."
                    )
                for k,v in self._metadata_field.items():
                    _mtd_value = metadata.get(k, None)
                    if _mtd_value is None:
                        raise ValueError(f"Metadata field {k} is missing in metadata.")
                    _mtd_value = str(_mtd_value) if v == DataType.NONE else _mtd_value
                    field_values.append(_mtd_value)

            # vector values
            for i, embedding in enumerate(embeddings):
                # print(f"i: {i} index: {index}", embedding[index])
                emb = np.array(embedding[index], dtype=np.float32)
                field_values.append(emb.tobytes())

            # primary key
            _pk = None
            if ids and ids_len > index and isinstance(ids[index], int):
                _pk = ids[index]
                # TODO: ids contains int and str, need to handle this
            else:
                _pk = 0

            entity = EntityData(pk = _pk, field_values = field_values)
            entities.append(entity)

            if len(entities) == batch_size:
                status,result = self.cli.insert(self.collection_name, entity_metas, entities)
                if status.code == 0:
                    inserted_ids.extend(result.succ_index)
                logger.info(f"Inserted {len(entities)} entities with status {status}")
                entities = []

        if entities:
            status,result = self.cli.insert(self.collection_name, entity_metas, entities)
            # print(f"Inserted {len(entities)} entities with status {status}")
            # print(f"Inserted entities: {result.succ_index}")
            if status.code == 0:
                inserted_ids.extend(result.succ_index)
            logger.info(f"Inserted {len(entities)} entities with status {status}")

        return inserted_ids

    def _collection_search(
        self,
        embedding: List[float],
        k: int = 4,
        param: Optional[dict] = None,
        expr: Optional[str] = None,
        timeout: Optional[float] = None,
        output_vector: bool = False,
        **kwargs: Any,
    ):
        if self.cli is None:
            logger.debug("No existing collection to search.")
            return None

        array = np.array(embedding, dtype=np.float32)
        batch_count = 1

        knn_params = KnnParam(
            field_name=self._vector_field,
            vectors=array.tobytes(),
            # vectors=struct.pack('8f', *vec),
            batch_count=batch_count,
            is_bruteforce = False
        )
        output_fields = []
        if output_vector:
            output_fields = ["*"]
        else:
            output_fields = [self._text_field]
            for mtd_k,_ in self._metadata_field.items():
                output_fields.append(mtd_k)
        # print(f"output_fields: {output_fields}")
        status, results = self.cli.search(
            self.collection_name,
            knn_param=knn_params,
            topk=k,
            filter=expr,
            output_fields=output_fields,
            extra_params=param if param else {},
        )
        logger.debug(f"status: {status}, results: {results}")
        # print(f"status: {status}")
        # print(f"results: {results}")
        return results

    def _parse_vector(self, data: dict) -> List[float]:
        vector_fields: List[str] = self._as_list(self._vector_field)
        for vector_field in vector_fields:
            if vector_field in data:
                return data.pop(vector_field)
        return []

    def _parse_document(self, data: dict) -> Document:
        # vector_fields: List[str] = self._as_list(self._vector_field)
        # for vector_field in vector_fields:
        #     if vector_field in data:
        #         data.pop(vector_field)
        # print(f"Data: {data}")
        _metadata = {}
        for k,_ in self._metadata_field.items():
            _metadata[k] = data.pop(k)
            # v = data.pop(k, None)
            # if v is not None:
            #     _metadata[k] = v
        return Document(
            page_content=data.pop(self._text_field),
            metadata=_metadata if _metadata else {},
        )

    def _parse_documents_from_search_results(
        self,
        col_search_res: SearchResult,
    ) -> List[Tuple[Document, float]]:
        if not col_search_res:
            return []
        ret = []
        for entity in col_search_res[0].entity_results:
            # print("entity: ", entity)
            data = {x.name : x.value for x in entity.field_datas}
            doc = self._parse_document(data)
            pair = (doc, entity.scores)
            # print(f"pair: {pair}")
            logger.debug(f"pair: {pair}")
            ret.append(pair)
        return ret

    def similarity_search(
        self,
        query: str,
        k: int = 4,
        param: Optional[dict | list[dict]] = None,
        expr: Optional[str] = None,
        timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> List[Document]:
        """Perform a similarity search against the query string.

        Args:
            query (str): The text to search.
            k (int, optional): How many results to return. Defaults to 4.
            param (dict | list[dict], optional): The search params for the index type.
                Defaults to None.
            expr (str, optional): Filtering expression. Defaults to None.
            timeout (int, optional): How long to wait before timeout error.
                Defaults to None.
            kwargs: Collection.search() keyword arguments.

        Returns:
            List[Document]: Document results for search.
        """
        if self.cli is None:
            logger.debug("No existing collection to search.")
            return []
        timeout = self._timeout or timeout
        res = self.similarity_search_with_score(
            query=query, k=k, param=param, expr=expr, timeout=timeout, **kwargs
        )
        # print(f"res: {res}")
        return [doc for doc, _ in res]

    def similarity_search_by_vector(
        self,
        embedding: List[float],
        k: int = 4,
        param: Optional[dict] = None,
        expr: Optional[str] = None,
        timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> List[Document]:
        """Perform a similarity search against the query string.

        Args:
            embedding (List[float]): The embedding vector to search.
            k (int, optional): How many results to return. Defaults to 4.
            param (dict, optional): The search params for the index type.
                Defaults to None.
            expr (str, optional): Filtering expression. Defaults to None.
            timeout (int, optional): How long to wait before timeout error.
                Defaults to None.
            kwargs: Collection.search() keyword arguments.

        Returns:
            List[Document]: Document results for search.
        """
        if self.cli is None:
            logger.debug("No existing collection to search.")
            return []
        timeout = self._timeout or timeout
        res = self.similarity_search_with_score_by_vector(
            embedding=embedding, k=k, param=param, expr=expr, timeout=timeout, **kwargs
        )
        # print(f"res: {res}")
        return [doc for doc, _ in res]

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        param: Optional[dict | list[dict]] = None,
        expr: Optional[str] = None,
        timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> List[Tuple[Document, float]]:
        """Perform a search on a query string and return results with score.

        Args:
            query (str): The text being searched.
            k (int, optional): The amount of results to return. Defaults to 4.
            param (dict | list[dict], optional): The search params for the specified
            index. Defaults to None.
            expr (str, optional): Filtering expression. Defaults to None.
            timeout (float, optional): How long to wait before timeout error.
                Defaults to None.
            kwargs: Collection.search() or hybrid_search() keyword arguments.

        Returns:
            List[Tuple[Document, float]]: List of result doc and score.
        """
        if self.cli is None:
            logger.debug("No existing collection to search.")
            return []

        embedding = self._as_list(self.embedding_func)[0].embed_query(query)

        # print(f"embedding: {embedding}")

        results = self._collection_search(
            embedding=embedding,
            k=k,
            param=param,
            expr=expr,
            timeout=timeout,
            **kwargs,
        )

        # print(f"results: {results}")

        return self._parse_documents_from_search_results(results)

    def similarity_search_with_score_by_vector(
        self,
        embedding: List[float] | Dict[int, float],
        k: int = 4,
        param: Optional[dict] = None,
        expr: Optional[str] = None,
        timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> List[Tuple[Document, float]]:
        """Perform a search on an embedding and return results with score.

        Args:
            embedding (List[float] | Dict[int, float]): The embedding vector being
                searched.
            k (int, optional): The amount of results to return. Defaults to 4.
            param (dict): The search params for the specified index.
                Defaults to None.
            expr (str, optional): Filtering expression. Defaults to None.
            timeout (float, optional): How long to wait before timeout error.
                Defaults to None.
            kwargs: Collection.search() keyword arguments.

        Returns:
            List[Tuple[Document, float]]: Result doc and score.
        """
        col_search_res = self._collection_search(
            embedding=embedding,
            k=k,
            param=param,
            expr=expr,
            timeout=timeout,
            **kwargs,
        )
        return self._parse_documents_from_search_results(col_search_res)

    def max_marginal_relevance_search(
        self,
        query: str,
        k: int = 4,
        fetch_k: int = 20,
        lambda_mult: float = 0.5,
        param: Optional[dict] = None,
        expr: Optional[str] = None,
        timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> List[Document]:
        """Perform a search and return results that are reordered by MMR.

        Args:
            query (str): The text being searched.
            k (int, optional): How many results to give. Defaults to 4.
            fetch_k (int, optional): Total results to select k from.
                Defaults to 20.
            lambda_mult: Number between 0 and 1 that determines the degree
                        of diversity among the results with 0 corresponding
                        to maximum diversity and 1 to minimum diversity.
                        Defaults to 0.5
            param (dict, optional): The search params for the specified index.
                Defaults to None.
            expr (str, optional): Filtering expression. Defaults to None.
            timeout (float, optional): How long to wait before timeout error.
                Defaults to None.
            kwargs: Collection.search() keyword arguments.


        Returns:
            List[Document]: Document results for search.
        """
        if self.cli is None:
            logger.debug("No existing collection to search.")
            return None

        assert (
            len(self._as_list(self.embedding_func)) == 1  # type: ignore[arg-type]
        ), "You must set only one embedding function for MMR search."

        embedding = self._as_list(self.embedding_func)[0].embed_query(query)  # type: ignore
        timeout = self._timeout or timeout
        return self.max_marginal_relevance_search_by_vector(
            embedding=embedding,
            k=k,
            fetch_k=fetch_k,
            lambda_mult=lambda_mult,
            param=param,
            expr=expr,
            timeout=timeout,
            **kwargs,
        )

    def max_marginal_relevance_search_by_vector(
        self,
        embedding: list[float] | dict[int, float],
        k: int = 4,
        fetch_k: int = 20,
        lambda_mult: float = 0.5,
        param: Optional[dict] = None,
        expr: Optional[str] = None,
        timeout: Optional[float] = None,
        **kwargs: Any,
    ) -> List[Document]:
        """Perform a search and return results that are reordered by MMR.

        Args:
            embedding (list[float] | dict[int, float]): The embedding vector being
                searched.
            k (int, optional): How many results to give. Defaults to 4.
            fetch_k (int, optional): Total results to select k from.
                Defaults to 20.
            lambda_mult: Number between 0 and 1 that determines the degree
                        of diversity among the results with 0 corresponding
                        to maximum diversity and 1 to minimum diversity.
                        Defaults to 0.5
            param (dict, optional): The search params for the specified index.
                Defaults to None.
            expr (str, optional): Filtering expression. Defaults to None.
            timeout (float, optional): How long to wait before timeout error.
                Defaults to None.
            kwargs: Collection.search() keyword arguments.

        Returns:
            List[Document]: Document results for search.
        """
        results = self._collection_search(
            embedding=embedding,
            k=fetch_k,
            param=param,
            expr=expr,
            timeout=timeout,
            output_vector=True,
            **kwargs,
        )

        if not results:
            return []

        embedding_list = []
        docs = []
        scores = []
        for entity in results[0].entity_results:
            data = {x.name : x.value for x in entity.field_datas}
            _vec = self._parse_vector(data)
            if _vec:
                embedding_list.append(_vec)
            doc = self._parse_document(data)
            docs.append(doc)
            scores.append(entity.scores)

        new_ordering = maximal_marginal_relevance(
            np.array(embedding), embedding_list, k=k, lambda_mult=lambda_mult
        )

        logger.debug(f"New ordering: {new_ordering}")

        # Reorder the values and return.
        ret = []
        for x in new_ordering:
            # print(f"New ordering: {x}")
            # Function can return -1 index
            if x == -1:
                break
            else:
                ret.append(docs[x])
        return ret

    def _select_relevance_score_fn(self) -> Callable[[float], float]:
        """
        The 'correct' relevance function
        may differ depending on a few things, including:
        - the distance / similarity metric used by the VectorStore
        - the scale of your embeddings (OpenAI's are unit normed. Many others are not!)
        - embedding dimensionality
        - etc.

        """
        if not self.cli:
            raise ValueError("No existing collection to search.")

        def _map_l2_to_similarity(l2_distance: float) -> float:
            """Return a similarity score on a scale [0, 1].
            It is recommended that the original vector is normalized,
            Levers only calculates the value after applying square root.
            l2_distance range: (0 is most similar, 2 most dissimilar)
            See
            https://milvus.io/docs/metric.md?tab=floating#Euclidean-distance-L2
            """
            return 1 - l2_distance / 2.0

        # cosine: distance = 1 - [-1,1] = [0,2]
        def _map_cosine_to_similarity(cosine_score: float) -> float:
            """Return a similarity score on a scale [0, 1].
            It is recommended that the original vector is normalized,
            cosine_score range: (0 is most similar, 2 most dissimilar)
            See
            https://milvus.io/docs/metric.md?tab=floating#Inner-product-IP
            https://milvus.io/docs/metric.md?tab=floating#Cosine-Similarity
            """
            return 1 - cosine_score / 2.0

        # IP: distance = [0,2] - 1 = 1 - [-1,1] - 1 = -[-1,1] = [-1,1]
        def _map_ip_to_similarity(ip_score: float) -> float:
            """Return a similarity score on a scale [0, 1].
            It is recommended that the original vector is normalized,
            ip_score range: (-1 is most similar, 1 most dissimilar)
            See
            https://milvus.io/docs/metric.md?tab=floating#Inner-product-IP
            https://milvus.io/docs/metric.md?tab=floating#Cosine-Similarity
            """
            return 1 - (ip_score + 1) / 2.0

        if not self.index_params:
            logger.warning(
                "No index params provided. Could not determine relevance function. "
                "Use L2 distance as default."
            )
            return _map_l2_to_similarity
        indexes_params = self._as_list(self.index_params)
        if len(indexes_params) > 1:
            raise ValueError(
                "No supported normalization function for multi vectors. "
                "Could not determine relevance function."
            )
        # In the left case, the len of indexes_params is 1.
        metric_type = indexes_params[0]["metric_type"]
        if metric_type == "L2":
            return _map_l2_to_similarity
        elif metric_type == "COSINE":
            return _map_cosine_to_similarity
        elif metric_type == "IP":
            return _map_ip_to_similarity
        else:
            raise ValueError(
                "No supported normalization function"
                f" for metric type: {metric_type}."
            )

    def delete(
        self, ids: Optional[List[str]] = None, expr: Optional[str] = None, **kwargs: str
    ):
        """Delete by vector ID or boolean expression.
        Refer to [Milvus documentation](https://milvus.io/docs/delete_data.md)
        for notes and examples of expressions.

        Args:
            ids: List of ids to delete.
            expr: Boolean expression that specifies the entities to delete.
            kwargs: Other parameters in Milvus delete api.
        """
        # if not ids:
        #     raise ValueError("No ids provided to delete.")
        # del_ids = []
        # for _id in ids:
        #     if _id is not None and isinstance(_id, int):
        #         del_ids.append(_id)
        #     else:
        #         raise ValueError("Primary key must be an integer.")
        if isinstance(ids, list) and len(ids) > 0:
            if expr is not None:
                logger.warning(
                    "Both ids and expr are provided. " "Ignore expr and delete by ids."
                )
            expr = f"{self._primary_field} in {ids}"
        else:
            assert isinstance(
                expr, str
            ), "Either ids list or expr string must be provided."
        status, results = self.cli.delete(self.collection_name, expr=expr)
        # print(f"Deleted {len(del_ids)} entities with status {status}")
        # print(f"Deleted entities: {results}")
        logger.info(f"deleted expressions: {expr} with status {status}")
        logger.debug(f"Deleted entities: {results}")
        return results

    @classmethod
    def from_texts(
        cls,
        texts: List[str],
        embedding: Optional[Union[EmbeddingType, List[EmbeddingType]]],
        metadatas: Optional[List[dict]] = None,
        collection_name: str = "LangChainCollection",
        connection_args: Optional[Dict[str, Any]] = None,
        index_params: Optional[Union[dict, List[dict]]] = None,
        search_params: Optional[Union[dict, List[dict]]] = None,
        *,
        ids: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Levers:
        """Create a Levers collection, indexes it with SPANN, and insert data.

        Args:
            texts (List[str]): Text data.
            embedding (Optional[Union[Embeddings, BaseSparseEmbedding]]): Embedding
                function.
            metadatas (Optional[List[dict]]): Metadata for each text if it exists.
                Defaults to None.
            collection_name (str, optional): Collection name to use. Defaults to
                "LangChainCollection".
            connection_args (dict[str, Any], optional): Connection args to use. Defaults
                to DEFAULT_LEVERS_CONNECTION.
            index_params (Optional[dict], optional): Which index_params to use. Defaults
                to None.
            search_params (Optional[dict], optional): Which search params to use.
                Defaults to None.
            ids (Optional[List[str]]): List of text ids. Defaults to None.
            **kwargs: Other parameters in Milvus Collection.
        Returns:
            Milvus: Milvus Vector Store
        """
        vector_db = cls(
            embedding_function=embedding,
            collection_name=collection_name,
            connection_args=connection_args,
            index_params=index_params,
            search_params=search_params,
            **kwargs,
        )
        vector_db.add_texts(texts=texts, metadatas=metadatas, ids=ids)
        return vector_db

    @staticmethod
    def _as_list(value: Optional[Union[T, List[T]]]) -> List[T]:
        """Try to cast a value to a list"""
        if not value:
            return []
        return [value] if not isinstance(value, list) else value

    @staticmethod
    def _from_list(value: Optional[Union[T, List[T]]]) -> Optional[Union[T, List[T]]]:
        """Try to cast a list to a single value"""
        if isinstance(value, list) and len(value) == 1:
            return value[0]
        return value
