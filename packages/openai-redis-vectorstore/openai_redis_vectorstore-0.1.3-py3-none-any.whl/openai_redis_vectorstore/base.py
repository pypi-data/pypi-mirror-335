from typing import Optional
from typing import List
import logging

import redis
from redis.exceptions import ResponseError
from openai import OpenAI
from langchain_community.vectorstores.redis import Redis as LangchainRedisVectorStore
from openai_simple_embeddings.settings import OPENAI_API_KEY
from openai_simple_embeddings.settings import OPENAI_BASE_URL
from openai_simple_embeddings.settings import OPENAI_EMBEDDINGS_MODEL
from openai_simple_embeddings.settings import OPENAI_EMBEDDINGS_MAX_SIZE
from openai_simple_embeddings.langchain_embeddings import OpenAISimpleEmbeddings
from openai_simple_rerank.settings import OPENAI_RERANK_MODEL
from openai_simple_rerank.settings import OPENAI_RERANK_MAX_SIZE
from openai_simple_rerank.base import get_rerank_scores
from zenutils import strutils

from .utils import Serializer
from .utils import YamlSerializer
from .schemas import Document
from .settings import REDIS_STACK_URL
from .exceptions import MissingIndexName
from .exceptions import MissingEmbeddingsModel
from .exceptions import MissingRedisStackUrl
from .exceptions import MissingRedisInstance
from .exceptions import MissingLLM

_logger = logging.getLogger(__name__)


class RedisVectorStore(object):
    """基于redis-stack的向量数据库。"""

    def __init__(
        self,
        index_name: Optional[str] = None,
        redis_stack_url: Optional[str] = None,
        llm: Optional[OpenAI] = None,
        embeddings_model: Optional[str] = None,
        rerank_model: Optional[str] = None,
        embeddings_max_size: Optional[int] = None,
        rerank_max_size: Optional[int] = None,
        embeddings_score_threshold: Optional[float] = None,
        rerank_score_threshold: Optional[float] = None,
        meta_serializer: Optional[Serializer] = None,
    ):
        self.index_name = index_name
        self.embeddings_score_threshold = embeddings_score_threshold
        self.rerank_score_threshold = rerank_score_threshold
        self.redis_stack_url = redis_stack_url or REDIS_STACK_URL
        self.redis_instance = (
            self.redis_stack_url and redis.from_url(self.redis_stack_url) or None
        )
        self.llm = llm or OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
        self.embeddings_model = embeddings_model or OPENAI_EMBEDDINGS_MODEL
        self.embeddings_max_size = embeddings_max_size or OPENAI_EMBEDDINGS_MAX_SIZE
        self.rerank_model = rerank_model or OPENAI_RERANK_MODEL
        self.rerank_max_size = rerank_max_size or OPENAI_RERANK_MAX_SIZE
        self.meta_serializer = meta_serializer or YamlSerializer()
        self.vectorstores = {}

    def get_cached_vectorstore(
        self,
        index_name: Optional[str] = None,
        embeddings_model: Optional[str] = None,
        embeddings_max_size: Optional[int] = None,
        llm: Optional[OpenAI] = None,
    ) -> LangchainRedisVectorStore:
        # 参数处理，缺省参数取实例默认值
        index_name = index_name or self.index_name
        embeddings_model = embeddings_model or self.embeddings_model
        embeddings_max_size = embeddings_max_size or self.embeddings_max_size
        llm = llm or self.llm
        # 检查必要参数是否缺失
        if not self.redis_stack_url:
            raise MissingRedisStackUrl()
        if not index_name:
            raise MissingIndexName()
        if not embeddings_model:
            raise MissingEmbeddingsModel()
        if not llm:
            raise MissingLLM()
        # 计算缓存键
        cache_key = (
            f"{index_name}:{embeddings_model}:{llm.base_url}:{embeddings_max_size}"
        )
        # 如果已缓存，则取缓存实例
        if cache_key in self.vectorstores:
            return self.vectorstores[cache_key]
        # 创建新实例并缓存
        embeddings = OpenAISimpleEmbeddings(
            llm=llm,
            model=embeddings_model,
            max_size=embeddings_max_size,
        )
        self.vectorstores[cache_key] = LangchainRedisVectorStore(
            redis_url=self.redis_stack_url,
            index_name=index_name,
            key_prefix=index_name,
            embedding=embeddings,
        )
        # 返回新建实例
        return self.vectorstores[cache_key]

    def get_serialized_meta(self, meta):
        serialized_meta = {}
        for k, v in meta.items():
            serialized_meta[k] = self.meta_serializer.dumps(v)
        return serialized_meta

    def get_unserialized_meta(self, serialized_meta):
        meta = {}
        for k, v in serialized_meta.items():
            k = strutils.TEXT(k)
            # 矢量数据库插入text时会自动创建content字段
            # content字段值即插入的text
            # 转化时需要排除
            if k == "content":
                v = strutils.TEXT(v)
            else:
                try:
                    v = self.meta_serializer.loads(v)
                except Exception:
                    pass
            meta[k] = v
        return meta

    def get_item(self, uid):
        serialized_meta = self.redis_instance.hgetall(uid)
        meta = self.get_unserialized_meta(serialized_meta)
        return meta

    def insert(
        self,
        text: str,
        meta: Optional[dict[str, str]] = None,
        index_name: Optional[str] = None,
        llm: Optional[OpenAI] = None,
        embeddings_model: Optional[str] = None,
        embeddings_max_size: Optional[int] = None,
    ):
        vs = self.get_cached_vectorstore(
            index_name=index_name,
            embeddings_model=embeddings_model,
            embeddings_max_size=embeddings_max_size,
            llm=llm,
        )
        if meta:
            meta = self.get_serialized_meta(meta)
            uids = vs.add_texts([text], [meta])
        else:
            uids = vs.add_texts([text])
        return uids[0]

    def insert_many(
        self,
        texts: List[str],
        metas: Optional[List[dict[str, str]]] = None,
        index_name: Optional[str] = None,
        llm: Optional[OpenAI] = None,
        embeddings_model: Optional[str] = None,
        embeddings_max_size: Optional[int] = None,
    ):
        vs = self.get_cached_vectorstore(
            index_name=index_name,
            embeddings_model=embeddings_model,
            embeddings_max_size=embeddings_max_size,
            llm=llm,
        )
        if metas:
            serialized_metas = []
            for meta in metas:
                serialized_metas.append(self.get_serialized_meta(meta))
            uids = vs.add_texts(texts, serialized_metas)
        else:
            uids = vs.add_texts(texts)
        return uids

    def delete(self, uid):
        if not self.redis_instance:
            raise MissingRedisInstance()
        if uid:
            return self.redis_instance.delete(uid)
        else:
            return 0

    def delete_many(self, uids):
        if not self.redis_instance:
            raise MissingRedisInstance()
        if uids:
            return self.redis_instance.delete(*uids)
        else:
            return 0

    def similarity_search_with_relevance_scores(
        self,
        query,
        index_name: Optional[str] = None,
        document_schema: Document = Document,
        k=4,
        llm: Optional[OpenAI] = None,
        embeddings_model: Optional[str] = None,
        embeddings_max_size: Optional[int] = None,
        embeddings_score_threshold: Optional[float] = None,
        **kwargs,
    ):

        score_threshold = embeddings_score_threshold or self.embeddings_score_threshold
        kwargs = kwargs or {}
        if score_threshold:
            kwargs["score_threshold"] = score_threshold
        vs = self.get_cached_vectorstore(
            index_name=index_name,
            embeddings_model=embeddings_model,
            embeddings_max_size=embeddings_max_size,
            llm=llm,
        )
        docs: List[Document] = []
        try:
            search_result = vs.similarity_search_with_relevance_scores(
                query,
                k=k,
                **kwargs,
            )
        except ResponseError as error:
            # 如果搜索一个空知识库，则会执行一个`redis.exceptions.ResponseError: xxxx: no such index`异常
            # 这个实际上是一个正常的业务行为，只有返回结果为空即可
            # 其它异常，直接抛出即可
            if "no such index" in str(error):
                _logger.warning("search on unindexed vector store: %s", vs.index_name)
                search_result = []
            else:
                raise error
        for doc, vs_embeddings_score in search_result:
            item = {}
            if document_schema != Document:
                item = self.get_item(doc.metadata["id"])
            item["vs_uid"] = doc.metadata["id"]
            item["vs_page_content"] = self.meta_serializer.loads(doc.page_content)
            item["vs_embeddings_score"] = vs_embeddings_score
            item["vs_rerank_score"] = None
            item["vs_index_name"] = vs.index_name
            doc = document_schema.model_validate(item)
            docs.append(doc)
        if docs:
            docs.sort(key=lambda doc: -doc.vs_embeddings_score)
        return docs

    def rerank(
        self,
        query: str,
        docs: List[Document],
        k: int = 4,
        llm: Optional[OpenAI] = None,
        rerank_model: Optional[str] = None,
        rerank_max_size: Optional[int] = None,
        rerank_score_threshold: Optional[float] = None,
    ):
        rerank_score_threshold = rerank_score_threshold or self.rerank_score_threshold
        scores = get_rerank_scores(
            query=query,
            documents=[doc.vs_page_content for doc in docs],
            llm=llm,
            model=rerank_model,
            max_size=rerank_max_size,
        )
        for score, doc in zip(scores, docs):
            doc.vs_rerank_score = score
        if rerank_score_threshold:
            docs = [
                doc for doc in docs if doc.vs_rerank_score >= rerank_score_threshold
            ]
        docs.sort(key=lambda doc: -doc.vs_rerank_score)
        return docs[:k]

    def similarity_search_and_rerank(
        self,
        query,
        index_name: Optional[str] = None,
        index_names: Optional[List[str]] = None,
        k: int = 4,
        scale: int = 2,
        document_schema: Document = Document,
        llm: Optional[OpenAI] = None,
        embeddings_model: Optional[str] = None,
        embeddings_max_size: Optional[int] = None,
        embeddings_score_threshold: Optional[float] = None,
        rerank_model: Optional[str] = None,
        rerank_max_size: Optional[int] = None,
        rerank_score_threshold: Optional[float] = None,
        **kwargs,
    ):
        index_names = index_names or []
        if not index_names:
            docs = self.similarity_search_with_relevance_scores(
                query=query,
                k=k * scale,
                index_name=index_name,
                document_schema=document_schema,
                llm=llm,
                embeddings_model=embeddings_model,
                embeddings_max_size=embeddings_max_size,
                embeddings_score_threshold=embeddings_score_threshold,
                **kwargs,
            )
        else:
            docs = []
            if index_name:
                index_names.append(index_name)
            for index_name in index_names:
                try:
                    docs += self.similarity_search_with_relevance_scores(
                        query=query,
                        k=k * scale,
                        index_name=index_name,
                        document_schema=document_schema,
                        llm=llm,
                        embeddings_model=embeddings_model,
                        embeddings_max_size=embeddings_max_size,
                        embeddings_score_threshold=embeddings_score_threshold,
                        **kwargs,
                    )
                except Exception as error:
                    if "no such index" in str(error):
                        _logger.warning(
                            "RedisVectorStore:similarity_search_and_rerank no inde"
                        )
                        continue
        return self.rerank(
            query=query,
            docs=docs,
            k=k,
            llm=llm,
            rerank_model=rerank_model,
            rerank_max_size=rerank_max_size,
            rerank_score_threshold=rerank_score_threshold,
        )

    def flush(self, index_name: str = None):
        """清空指定索引。"""
        index_name = index_name or self.index_name

        if not index_name:
            raise MissingIndexName()
        if not self.redis_instance:
            raise MissingRedisInstance()

        # 删除所有索引项
        keys = self.redis_instance.keys(index_name + ":*")
        if keys:
            self.redis_instance.delete(*keys)
        # 删除索引
        indexes = self.redis_instance.execute_command("FT._LIST")
        if indexes:
            indexes = [x.decode("utf-8") for x in indexes]
        if self.index_name in indexes:
            self.redis_instance.execute_command(f"FT.DROPINDEX {self.index_name}")
        return True
