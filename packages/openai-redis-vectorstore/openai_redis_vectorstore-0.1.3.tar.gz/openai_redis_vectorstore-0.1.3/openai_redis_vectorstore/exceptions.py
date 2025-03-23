__all__ = [
    "MissingConfigError",
    "MissingIndexName",
    "MissingEmbeddingsModel",
    "MissingRedisStackUrl",
    "MissingRedisInstance",
    "MissingLLM",
]


class MissingConfigError(RuntimeError):
    def __init__(self, *args, **kwargs):
        args = args or ["缺少必须字段。"]
        super().__init__(*args, **kwargs)


class MissingIndexName(MissingConfigError):
    """缺少index_name（索引名称）参数或配置项。"""

    def __init__(self, *args, **kwargs):
        args = args or ["缺少index_name（索引名称）参数或配置项。"]
        super().__init__(*args, **kwargs)


class MissingEmbeddingsModel(MissingConfigError):
    """缺少embeddings_model（向量化模型名称）参数或配置项。"""

    def __init__(self, *args, **kwargs):
        args = args or ["缺少embeddings_model（向量化模型名称）参数或配置项。"]
        super().__init__(*args, **kwargs)


class MissingRedisStackUrl(MissingConfigError):
    """缺少redis_stack_url（向量数据库连接地址）参数或配置项。"""

    def __init__(self, *args, **kwargs):
        args = args or ["缺少redis_stack_url（向量数据库连接地址）参数或配置项。"]
        super().__init__(*args, **kwargs)


class MissingRedisInstance(MissingConfigError):
    """缺少redis_instance（向量数据库实例）参数或配置项。"""

    def __init__(self, *args, **kwargs):
        args = args or ["缺少redis_instance（向量数据库实例）参数或配置项。"]
        super().__init__(*args, **kwargs)


class MissingLLM(MissingConfigError):
    """缺少llm（OPENAI兼容API服务）参数或配置项。"""

    def __init__(self, *args, **kwargs):
        args = args or ["缺少llm（OPENAI兼容API服务）参数或配置项。"]
        super().__init__(*args, **kwargs)
