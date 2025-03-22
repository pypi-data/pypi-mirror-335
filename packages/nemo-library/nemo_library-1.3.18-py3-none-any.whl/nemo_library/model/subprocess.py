from dataclasses import asdict, dataclass
from typing import List, Dict
from datetime import datetime
from uuid import UUID


@dataclass
class SubProcess:
    """
    Represents a subprocess with various attributes including names, descriptions,
    translations, aggregations, and identifiers.
    """

    columnInternalNames: List[str]
    description: str
    descriptionTranslations: Dict[str, str]
    displayName: str
    displayNameTranslations: Dict[str, str]
    groupByAggregations: Dict[str, str]
    groupByColumn: str
    internalName: str
    isAggregation: bool
    timeUnit: str
    id: str
    projectId: UUID
    tenant: str

    def to_dict(self):
        """
        Converts the SubProcess instance to a dictionary.

        Returns:
            dict: A dictionary representation of the SubProcess instance.
        """
        return asdict(self)
