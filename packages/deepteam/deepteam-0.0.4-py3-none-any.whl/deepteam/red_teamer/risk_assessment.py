from pydantic import BaseModel, Field
from typing import Optional, List
import datetime
import os
import json
from enum import Enum

from deepteam.vulnerabilities.types import VulnerabilityType


class VulnerabilityTypeResult(BaseModel):
    vulnerability: str
    vulnerability_type: VulnerabilityType
    pass_rate: float
    passing: int
    failing: int
    errored: int


class RedTeamingTestCase(BaseModel):
    vulnerability: str
    vulnerability_type: VulnerabilityType
    risk_category: str = Field(alias="riskCategory")
    attack_method: Optional[str] = Field(None, alias="attackMethod")
    input: Optional[str] = None
    actual_output: Optional[str] = Field(
        None, serialization_alias="actualOutput"
    )
    score: Optional[float] = None
    reason: Optional[str] = None
    error: Optional[str] = None


class TestCasesList(list):
    def to_df(self):
        import pandas as pd

        data = []
        for case in self:
            data.append(
                {
                    "Vulnerability": case.vulnerability,
                    "Vulnerability Type": str(case.vulnerability_type.value),
                    "Risk Category": case.risk_category,
                    "Attack Enhancement": case.attack_method,
                    "Input": case.input,
                    "Actual Output": case.actual_output,
                    "Score": case.score,
                    "Reason": case.reason,
                    "Error": case.error,
                    "Status": (
                        "Passed"
                        if case.score and case.score > 0
                        else "Errored" if case.error else "Failed"
                    ),
                }
            )
        return pd.DataFrame(data)


class RedTeamingOverview(BaseModel):
    vulnerability_type_results: List[VulnerabilityTypeResult]

    def to_df(self):
        import pandas as pd

        data = []
        for result in self.vulnerability_type_results:
            data.append(
                {
                    "Vulnerability": result.vulnerability,
                    "Vulnerability Type": str(result.vulnerability_type.value),
                    "Total": result.passing + result.failing + result.errored,
                    "Pass Rate": result.pass_rate,
                    "Passing": result.passing,
                    "Failing": result.failing,
                    "Errored": result.errored,
                }
            )
        return pd.DataFrame(data)


class EnumEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        return super().default(obj)


class RiskAssessment(BaseModel):
    overview: RedTeamingOverview
    test_cases: List[RedTeamingTestCase]

    def __init__(self, **data):
        super().__init__(**data)
        self.test_cases = TestCasesList[RedTeamingTestCase](self.test_cases)

    def save(self, to: str) -> str:
        try:
            new_filename = (
                datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".json"
            )

            if not os.path.exists(to):
                try:
                    os.makedirs(to)
                except OSError as e:
                    raise OSError(f"Cannot create directory '{to}': {e}")

            full_file_path = os.path.join(to, new_filename)

            # Convert model to a dictionary
            data = self.model_dump(by_alias=True)

            # Write to JSON file
            with open(full_file_path, "w") as f:
                json.dump(data, f, indent=2, cls=EnumEncoder)

            print(
                f"🎉 Success! 🎉 Your risk assessment file has been saved to:\n📁 {full_file_path} ✅"
            )

        except OSError as e:
            raise OSError(f"Failed to save file to '{to}': {e}") from e


def construct_risk_assessment_overview(
    test_cases: List[RedTeamingTestCase],
) -> RedTeamingOverview:
    # Group test cases by vulnerability type
    vulnerability_type_to_cases = {}
    for test_case in test_cases:
        if test_case.vulnerability_type not in vulnerability_type_to_cases:
            vulnerability_type_to_cases[test_case.vulnerability_type] = []
        vulnerability_type_to_cases[test_case.vulnerability_type].append(
            test_case
        )

    # Calculate statistics for each vulnerability type
    vulnerability_type_results = []

    for vuln_type, test_cases in vulnerability_type_to_cases.items():
        # Count passing, failing, and errored cases
        passing = sum(
            1
            for test_case in test_cases
            if test_case.score is not None and test_case.score > 0
        )
        errored = sum(
            1 for test_case in test_cases if test_case.error is not None
        )
        failing = len(test_cases) - passing - errored

        # Calculate pass rate (excluding errored cases from the denominator)
        valid_test_cases = len(test_cases) - errored
        pass_rate = (
            (passing / valid_test_cases) if valid_test_cases > 0 else 0.0
        )

        # Use the vulnerability name from the first case in this group
        vulnerability_name = test_cases[0].vulnerability if test_cases else ""

        # Create the result object
        result = VulnerabilityTypeResult(
            vulnerability=vulnerability_name,
            vulnerability_type=vuln_type,
            pass_rate=pass_rate,
            passing=passing,
            failing=failing,
            errored=errored,
        )

        vulnerability_type_results.append(result)

    # Create and return the final assessment
    return RedTeamingOverview(
        vulnerability_type_results=vulnerability_type_results
    )
