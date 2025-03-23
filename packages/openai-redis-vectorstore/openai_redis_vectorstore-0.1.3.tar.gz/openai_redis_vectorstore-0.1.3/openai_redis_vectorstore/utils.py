import json
import yaml

__all__ = [
    "Serializer",
    "JsonSerializer",
    "YamlSerializer",
]


class Serializer:
    def dumps(self, value):
        raise NotImplementedError()

    def loads(self, data):
        raise NotImplementedError()


class JsonSerializer(Serializer):
    def dumps(self, value):
        return json.dumps(value)

    def loads(self, data):
        return json.loads(data)


class YamlSerializer(Serializer):
    def dumps(self, value):
        return yaml.safe_dump(value)

    def loads(self, data):
        return yaml.safe_load(data)
