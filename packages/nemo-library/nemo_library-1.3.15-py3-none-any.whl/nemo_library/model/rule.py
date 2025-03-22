from dataclasses import dataclass, asdict, field
from typing import Dict
from nemo_library.utils.utils import get_internal_name


@dataclass
class Rule:
    """
    Represents a rule  with various properties and settings.
    """

    active: bool = True
    description: str = ""
    descriptionTranslations: Dict[str, str] = field(default_factory=dict)
    displayName: str = None
    displayNameTranslations: Dict[str, str] = field(default_factory=dict)
    internalName: str = None
    ruleGroup: str = ""
    ruleGroupTranslations: Dict[str, str] = field(default_factory=dict)
    ruleSourceInternalName: str = ""
    id: str = ""
    projectId: str = ""
    tenant: str = ""

    def to_dict(self):
        """
        Converts the RuleGroup instance to a dictionary.

        Returns:
            dict: A dictionary representation of the RuleGroup instance.
        """
        return asdict(self)

    def __post_init__(self):
        """
        Post-initialization processing to set the internal name if it is not provided.
        """
        if self.internalName is None:
            self.internalName = get_internal_name(self.displayName)
