from dataclasses import dataclass, asdict, field
from typing import Dict, List

from nemo_library.utils.utils import get_internal_name


@dataclass
class Forecast:
    """
    Represents a forecast configuration.

    Attributes:
        groupBy (str): The attribute to group by.
        metric (str): The metric to forecast.
    """

    groupBy: str
    metric: str


@dataclass
class PageReference:
    """
    Represents a reference to a page.

    Attributes:
        order (int): The order of the page.
        page (str): The page identifier.
    """

    order: int
    page: str


@dataclass
class Application:
    """
    Represents an application configuration.

    Attributes:
        active (bool): Indicates if the application is active.
        description (str): The description of the application.
        descriptionTranslations (Dict[str, str]): Translations for the description.
        displayName (str): The display name of the application.
        displayNameTranslations (Dict[str, str]): Translations for the display name.
        download (str): The download link for the application.
        forecasts (List[Forecast]): List of forecast configurations.
        formatCompact (bool): Indicates if the format is compact.
        internalName (str): The internal name of the application.
        links (List[str]): List of related links.
        models (List[str]): List of associated models.
        pages (List[PageReference]): List of page references.
        scopeName (str): The scope name of the application.
        id (str): The unique identifier of the application.
        projectId (str): The project identifier.
        tenant (str): The tenant identifier.
    """

    active: bool = True
    description: str = ""
    descriptionTranslations: Dict[str, str] = field(default_factory=dict)
    displayName: str = None
    displayNameTranslations: Dict[str, str] = field(default_factory=dict)
    download: str = ""
    forecasts: List[Forecast] = field(default_factory=list)
    formatCompact: bool = False
    internalName: str = None
    links: List[str] = field(default_factory=list)
    models: List[str] = field(default_factory=list)
    pages: List[PageReference] = field(default_factory=list)
    scopeName: str = ""
    id: str = ""
    projectId: str = ""
    tenant: str = ""

    def to_dict(self):
        """
        Converts the Application instance to a dictionary.

        Returns:
            dict: The dictionary representation of the Application instance.
        """
        return asdict(self)

    def __post_init__(self):
        """
        Post-initialization processing to set the internal name if not provided.
        """
        if self.internalName is None:
            self.internalName = get_internal_name(self.displayName)
