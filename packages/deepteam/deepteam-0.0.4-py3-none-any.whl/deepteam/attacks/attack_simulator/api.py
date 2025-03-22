from typing import List
from pydantic import BaseModel


class ApiGenerateBaselineAttack(BaseModel):
    purpose: str
    vulnerability: str
    num_attacks: int


class GenerateBaselineAttackResponseData(BaseModel):
    baseline_attacks: List[str]
