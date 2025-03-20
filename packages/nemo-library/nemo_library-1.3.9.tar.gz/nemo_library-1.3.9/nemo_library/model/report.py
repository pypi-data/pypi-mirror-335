from dataclasses import asdict, dataclass, field
from typing import List, Dict

from nemo_library.utils.utils import get_internal_name


@dataclass
class Report:
    """
    A class to represent a report.

    Attributes:
    columns (List[str]): A list of column names.
    description (str): A description of the report.
    descriptionTranslations (Dict[str, str]): Translations of the description.
    displayName (str): The display name of the report.
    displayNameTranslations (Dict[str, str]): Translations of the display name.
    internalName (str): The internal name of the report.
    querySyntax (str): The query syntax used in the report.
    reportCategories (List[str]): A list of report categories.
    id (str): The unique identifier of the report.
    projectId (str): The project ID associated with the report.
    tenant (str): The tenant associated with the report.
    """

    columns: List[str] = field(default_factory=list)
    description: str = ""
    descriptionTranslations: Dict[str, str] = field(default_factory=dict)
    displayName: str = None
    displayNameTranslations: Dict[str, str] = field(default_factory=dict)
    internalName: str = None
    querySyntax: str = None
    reportCategories: List[str] = field(default_factory=list)
    id: str = ""
    projectId: str = ""
    tenant: str = ""

    def to_dict(self):
        """
        Convert the Report instance to a dictionary.

        Returns:
        dict: A dictionary representation of the Report instance.
        """
        return asdict(self)

    def __post_init__(self):
        """
        Post-initialization processing to set the internal name and
        convert column names to uppercase.
        """
        if self.internalName is None:
            self.internalName = get_internal_name(self.displayName)

        self.columns = [col.upper() for col in self.columns]
