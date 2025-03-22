from dataclasses import dataclass, asdict, field
from typing import Dict, Optional

from nemo_library.utils.utils import get_import_name, get_internal_name


@dataclass
class ImportedColumn:
    """
    Represents an imported column with various attributes related to its metadata.
    """

    categorialType: bool = False
    columnType: str = "ExportedColumn"
    containsSensitiveData: bool = False
    dataType: str = "string"
    description: str = ""
    descriptionTranslations: Dict[str, str] = field(default_factory=dict)
    displayName: str = None
    displayNameTranslations: Dict[str, str] = field(default_factory=dict)
    formula: str = ""
    groupByColumnInternalName: Optional[str] = field(default_factory=str)
    importName: str = None
    stringSize: int = 0
    unit: str = ""
    focusOrder: str = ""
    internalName: str = None
    parentAttributeGroupInternalName: str = None
    id: str = ""
    projectId: str = ""
    tenant: str = ""

    def to_dict(self):
        """
        Converts the ImportedColumn instance to a dictionary.

        Returns:
            dict: A dictionary representation of the ImportedColumn instance.
        """
        return asdict(self)

    def __post_init__(self):
        """
        Post-initialization processing to set default values for importName and internalName
        if they are not provided.
        """
        if self.importName is None:
            self.importName = get_import_name(self.displayName)

        if self.internalName is None:
            self.internalName = get_internal_name(self.displayName)
