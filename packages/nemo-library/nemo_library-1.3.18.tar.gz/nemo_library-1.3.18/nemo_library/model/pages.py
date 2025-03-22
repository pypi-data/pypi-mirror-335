from dataclasses import dataclass, asdict
from typing import Dict, List


@dataclass
class Visual:
    """
    Represents a visual element on a page.

    Attributes:
        column (int): The column position of the visual.
        columnSpan (int): The number of columns the visual spans.
        content (str): The content of the visual.
        contentTranslations (Dict[str, str]): Translations of the content.
        id (str): The unique identifier of the visual.
        row (int): The row position of the visual.
        rowSpan (int): The number of rows the visual spans.
        type (str): The type of the visual.
    """

    column: int
    columnSpan: int
    content: str
    contentTranslations: Dict[str, str]
    id: str
    row: int
    rowSpan: int
    type: str


@dataclass
class Page:
    """
    Represents a page containing multiple visuals.

    Attributes:
        description (str): The description of the page.
        descriptionTranslations (Dict[str, str]): Translations of the description.
        displayName (str): The display name of the page.
        displayNameTranslations (Dict[str, str]): Translations of the display name.
        hideIfColumns (List[str]): Columns that hide the page if present.
        internalName (str): The internal name of the page.
        numberOfColumns (int): The number of columns on the page.
        numberOfRows (int): The number of rows on the page.
        showIfColumns (List[str]): Columns that show the page if present.
        visuals (List[Visual]): The visuals contained in the page.
        id (str): The unique identifier of the page.
        projectId (str): The project identifier the page belongs to.
        tenant (str): The tenant identifier the page belongs to.
    """

    description: str
    descriptionTranslations: Dict[str, str]
    displayName: str
    displayNameTranslations: Dict[str, str]
    hideIfColumns: List[str]
    internalName: str
    numberOfColumns: int
    numberOfRows: int
    showIfColumns: List[str]
    visuals: List[Visual]
    id: str
    projectId: str
    tenant: str

    def to_dict(self):
        """
        Converts the Page instance to a dictionary.

        Returns:
            dict: A dictionary representation of the Page instance.
        """
        return asdict(self)
