import python_environment_settings


REDIS_STACK_URL = python_environment_settings.get(
    "REDIS_STACK_URL",
    "redis://localhost:6379/0",
    aliases=[
        "REDIS_URL",
        "REDIS",
    ],
)
