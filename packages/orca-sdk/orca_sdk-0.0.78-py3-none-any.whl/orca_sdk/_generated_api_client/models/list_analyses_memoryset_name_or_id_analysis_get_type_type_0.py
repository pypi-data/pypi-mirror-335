from enum import Enum


class ListAnalysesMemorysetNameOrIdAnalysisGetTypeType0(str, Enum):
    ANALYZE_DUPLICATE_MEMORIES = "ANALYZE_DUPLICATE_MEMORIES"
    ANALYZE_MEMORY_NEIGHBOR_LABELS = "ANALYZE_MEMORY_NEIGHBOR_LABELS"

    def __str__(self) -> str:
        return str(self.value)
