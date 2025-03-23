from pydantic import BaseModel, ConfigDict
from datetime import datetime
from enum import Enum

class BaseSchema(BaseModel):
    """Base schema class with config for handling datetime and enum serialization"""
    model_config = ConfigDict(
        from_attributes=True
    )

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        
        def _process(data):
            """Recursively process data to convert datetime and enum objects"""
            if isinstance(data, dict):
                return {key: _process(value) for key, value in data.items()}
            elif isinstance(data, list):
                return [_process(item) for item in data]
            elif isinstance(data, datetime):
                return data.isoformat()
            elif isinstance(data, Enum):
                return data.value
            else:
                return data

        return _process(data)

    @classmethod
    def model_json_schema(cls, *args, **kwargs):
        schema = super().model_json_schema(*args, **kwargs)
        # Update schema to handle datetime serialization
        for prop in schema.get("properties", {}).values():
            if prop.get("type") == "string" and prop.get("format") == "date-time":
                prop["format"] = "date-time"
        return schema