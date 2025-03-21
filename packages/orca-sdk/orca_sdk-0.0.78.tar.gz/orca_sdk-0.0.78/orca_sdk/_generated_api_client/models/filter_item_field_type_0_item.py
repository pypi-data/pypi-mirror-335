from enum import Enum


class FilterItemFieldType0Item(str, Enum):
    CREATED_AT = "created_at"
    LABEL = "label"
    METADATA = "metadata"
    METRICS = "metrics"
    SCORE = "score"
    SOURCE_ID = "source_id"
    UPDATED_AT = "updated_at"
    VALUE = "value"

    def __str__(self) -> str:
        return str(self.value)
