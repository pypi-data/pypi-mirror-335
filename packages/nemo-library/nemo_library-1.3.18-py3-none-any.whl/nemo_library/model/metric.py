from dataclasses import dataclass, asdict, field
from typing import Optional, Dict, Any, List

from nemo_library.utils.utils import get_internal_name


@dataclass
class Metric:
    """
    A class to represent a Metric.

    Attributes:
    -----------
    aggregateBy : str
        The column to aggregate by.
    aggregateFunction : str
        The function to use for aggregation.
    dateColumn : Optional[str]
        The column representing the date.
    description : str
        The description of the metric.
    descriptionTranslations : Dict[str, str]
        Translations for the description.
    displayName : str
        The display name of the metric.
    displayNameTranslations : Dict[str, str]
        Translations for the display name.
    groupByAggregations : Dict[str, str]
        Aggregations to group by.
    groupByColumn : str
        The column to group by.
    isCrawlable : bool
        Indicates if the metric is crawlable.
    optimizationOrientation : str
        The orientation for optimization.
    optimizationTarget : bool
        Indicates if the metric is an optimization target.
    scopeId : Optional[str]
        The ID of the scope.
    scopeName : Optional[str]
        The name of the scope.
    unit : str
        The unit of the metric.
    defaultScopeRestrictions : List[Any]
        Default restrictions for the scope.
    focusOrder : str
        The order of focus.
    internalName : str
        The internal name of the metric.
    parentAttributeGroupInternalName : str
        The internal name of the parent attribute group.
    id : str
        The ID of the metric.
    projectId : str
        The ID of the project.
    tenant : str
        The tenant of the metric.
    """

    aggregateBy: str = ""
    aggregateFunction: str = ""
    dateColumn: Optional[str] = ""
    description: str = ""
    descriptionTranslations: Dict[str, str] = field(default_factory=dict)
    displayName: str = ""
    displayNameTranslations: Dict[str, str] = field(default_factory=dict)
    groupByAggregations: Dict[str, str] = field(default_factory=dict)
    groupByColumn: str = ""
    isCrawlable: bool = True
    optimizationOrientation: str = ""
    optimizationTarget: bool = False
    scopeId: Optional[str] = ""
    scopeName: Optional[str] = ""
    unit: str = ""
    defaultScopeRestrictions: List[Any] = field(default_factory=list)
    focusOrder: str = ""
    internalName: str = ""
    parentAttributeGroupInternalName: str = ""
    id: str = ""
    projectId: str = ""
    tenant: str = ""

    def to_dict(self):
        """
        Convert the Metric instance to a dictionary.

        Returns:
        --------
        dict
            A dictionary representation of the Metric instance.
        """
        return asdict(self)

    def __post_init__(self):
        """
        Post-initialization processing to set the internal name if not provided.
        """
        if self.internalName is None:
            self.internalName = get_internal_name(self.displayName)
