from typing import Union

from deepteam.vulnerabilities.intellectual_property import (
    IntellectualPropertyType,
)
from deepteam.vulnerabilities.unauthorized_access import UnauthorizedAccessType
from deepteam.vulnerabilities.illegal_activity import IllegalActivityType
from deepteam.vulnerabilities.excessive_agency import ExcessiveAgencyType
from deepteam.vulnerabilities.personal_safety import PersonalSafetyType
from deepteam.vulnerabilities.graphic_content import GraphicContentType
from deepteam.vulnerabilities.misinformation import MisinformationType
from deepteam.vulnerabilities.prompt_leakage import PromptLeakageType
from deepteam.vulnerabilities.competition import CompetitionType
from deepteam.vulnerabilities.pii_leakage import PIILeakageType
from deepteam.vulnerabilities.robustness import RobustnessType
from deepteam.vulnerabilities.toxicity import ToxicityType
from deepteam.vulnerabilities.bias import BiasType

VulnerabilityType = Union[
    UnauthorizedAccessType,
    IllegalActivityType,
    ExcessiveAgencyType,
    PersonalSafetyType,
    GraphicContentType,
    MisinformationType,
    PromptLeakageType,
    PromptLeakageType,
    CompetitionType,
    PIILeakageType,
    RobustnessType,
    ToxicityType,
    BiasType,
    IntellectualPropertyType,
    IntellectualPropertyType,
    IntellectualPropertyType,
]
