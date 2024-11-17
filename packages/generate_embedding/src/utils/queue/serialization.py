from datetime import datetime
from typing import Any
import json
from .errors import QueueSerializationError
from .message import JsonValue


def json_serializer_default(obj: Any) -> JsonValue:
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    try:
        # Try to convert to dict for dataclasses or objects with __dict__
        return obj.__dict__
    except AttributeError:
        pass
    try:
        # Try to convert to list for iterables
        return list(obj)
    except TypeError:
        pass
    raise QueueSerializationError(
        f"Object of type {type(obj)} is not JSON-serializable"
    )


def json_deserializer_object_hook(obj: dict) -> Any:
    for key, value in obj.items():
        if isinstance(value, str):
            try:
                # Try to parse as ISO date
                obj[key] = datetime.fromisoformat(value)
            except ValueError:
                pass
    return obj


def serialize_json(obj: Any) -> str:
    """Serialize object to JSON string with custom encoding"""
    try:
        return json.dumps(obj, default=json_serializer_default)
    except TypeError as e:
        raise QueueSerializationError(f"Failed to serialize object: {str(e)}")


def deserialize_json(json_str: str) -> Any:
    """Deserialize JSON string with custom decoding"""
    try:
        return json.loads(json_str, object_hook=json_deserializer_object_hook)
    except json.JSONDecodeError as e:
        raise QueueSerializationError(f"Failed to deserialize JSON: {str(e)}")
