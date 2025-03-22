from enum import Enum
from typing import Literal


class ExcessiveAgencyType(Enum):
    FUNCTIONALITY = "excessive functionality"
    PERMISSIONS = "excessive permissions"
    AUTONOMY = "excessive autonomy"


ExcessiveAgencyTypes = Literal[
    ExcessiveAgencyType.FUNCTIONALITY.value,
    ExcessiveAgencyType.PERMISSIONS.value,
    ExcessiveAgencyType.AUTONOMY.value,
]
