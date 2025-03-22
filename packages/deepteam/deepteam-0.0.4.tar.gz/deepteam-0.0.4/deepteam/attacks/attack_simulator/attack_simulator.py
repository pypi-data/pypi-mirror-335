import random
import asyncio
from tqdm import tqdm
from pydantic import BaseModel
from typing import List, Optional, Union


from deepeval.metrics.utils import initialize_model
from deepeval.models import DeepEvalBaseLLM
from deepeval.confident.api import Api, HttpMethods, Endpoints


from deepteam.attacks import BaseAttack
from deepteam.vulnerabilities import BaseVulnerability
from deepteam.vulnerabilities.types import VulnerabilityType
from deepteam.attacks.attack_simulator.utils import (
    generate_schema,
    a_generate_schema,
)
from deepteam.attacks.attack_simulator.api import (
    ApiGenerateBaselineAttack,
    GenerateBaselineAttackResponseData,
)


class SimulatedAttack(BaseModel):
    vulnerability: str
    vulnerability_type: VulnerabilityType
    # When there is an error, base input can fail to simulate
    # and subsequently enhancements are redundant
    input: Optional[str] = None
    attack_method: Optional[str] = None
    error: Optional[str] = None


BASE_URL = "https://deepeval.confident-ai.com"


class AttackSimulator:
    def __init__(
        self,
        purpose: str,
        max_concurrent: int,
        simulator_model: Optional[Union[str, DeepEvalBaseLLM]] = None,
    ):
        # Initialize models and async mode
        self.purpose = purpose
        self.simulator_model, self.using_native_model = initialize_model(
            simulator_model
        )

        # Define list of attacks and unaligned vulnerabilities
        self.simulated_attacks: List[SimulatedAttack] = []
        self.max_concurrent = max_concurrent

    ##################################################
    ### Generating Attacks ###########################
    ##################################################

    def simulate(
        self,
        attacks_per_vulnerability_type: int,
        vulnerabilities: List[BaseVulnerability],
        attacks: List[BaseAttack],
        ignore_errors: bool,
    ) -> List[SimulatedAttack]:
        # Simulate unenhanced attacks for each vulnerability
        baseline_attacks: List[SimulatedAttack] = []
        num_vulnerability_types = sum(
            len(v.get_types()) for v in vulnerabilities
        )
        pbar = tqdm(
            vulnerabilities,
            desc=f"💥 Generating {num_vulnerability_types * attacks_per_vulnerability_type} attacks (for {num_vulnerability_types} vulnerability types across {len(vulnerabilities)} vulnerability(s))",
        )
        for vulnerability in pbar:
            baseline_attacks.extend(
                self.simulate_baseline_attacks(
                    attacks_per_vulnerability_type=attacks_per_vulnerability_type,
                    vulnerability=vulnerability,
                    ignore_errors=ignore_errors,
                )
            )
        # Enhance attacks by sampling from the provided distribution
        simulated_attacks: List[SimulatedAttack] = []
        pbar = tqdm(
            baseline_attacks,
            desc=f"✨ Simulating {num_vulnerability_types * attacks_per_vulnerability_type} attacks (using {len(attacks)} method(s))",
        )
        attack_weights = [attack.weight for attack in attacks]

        for baseline_attack in pbar:
            # Randomly sample an enhancement based on the distribution
            sampled_attack = random.choices(
                attacks, weights=attack_weights, k=1
            )[0]
            enhanced_attack = self.enhance_attack(
                attack=sampled_attack,
                simulated_attack=baseline_attack,
                ignore_errors=ignore_errors,
            )
            simulated_attacks.append(enhanced_attack)

        self.simulated_attacks.extend(simulated_attacks)
        return simulated_attacks

    async def a_simulate(
        self,
        attacks_per_vulnerability_type: int,
        vulnerabilities: List[BaseVulnerability],
        attacks: List[BaseAttack],
        ignore_errors: bool,
    ) -> List[SimulatedAttack]:
        # Create a semaphore to control the number of concurrent tasks
        semaphore = asyncio.Semaphore(self.max_concurrent)

        # Simulate unenhanced attacks for each vulnerability
        baseline_attacks: List[SimulatedAttack] = []
        num_vulnerability_types = sum(
            len(v.get_types()) for v in vulnerabilities
        )
        pbar = tqdm(
            vulnerabilities,
            desc=f"💥 Generating {num_vulnerability_types * attacks_per_vulnerability_type} attacks (for {num_vulnerability_types} vulnerability types across {len(vulnerabilities)} vulnerability(s))",
        )

        async def throttled_simulate_baseline_attack(vulnerability):
            async with semaphore:  # Throttling applied here
                result = await self.a_simulate_baseline_attacks(
                    attacks_per_vulnerability_type=attacks_per_vulnerability_type,
                    vulnerability=vulnerability,
                    ignore_errors=ignore_errors,
                )
                pbar.update(1)
                return result

        simulate_tasks = [
            asyncio.create_task(
                throttled_simulate_baseline_attack(vulnerability)
            )
            for vulnerability in vulnerabilities
        ]

        attack_results = await asyncio.gather(*simulate_tasks)
        for result in attack_results:
            baseline_attacks.extend(result)
        pbar.close()

        # Enhance attacks by sampling from the provided distribution
        enhanced_attacks: List[SimulatedAttack] = []
        pbar = tqdm(
            total=len(baseline_attacks),
            desc=f"✨ Simulating {num_vulnerability_types * attacks_per_vulnerability_type} attacks (using {len(attacks)} method(s))",
        )

        async def throttled_attack_method(
            baseline_attack: SimulatedAttack,
        ):
            async with semaphore:  # Throttling applied here
                # Randomly sample an enhancement based on the distribution
                attack_weights = [attack.weight for attack in attacks]
                sampled_attack = random.choices(
                    attacks, weights=attack_weights, k=1
                )[0]

                result = await self.a_enhance_attack(
                    attack=sampled_attack,
                    simulated_attack=baseline_attack,
                    ignore_errors=ignore_errors,
                )
                pbar.update(1)
                return result

        enhanced_attacks.extend(
            await asyncio.gather(
                *[
                    asyncio.create_task(
                        throttled_attack_method(baseline_attack)
                    )
                    for baseline_attack in baseline_attacks
                ]
            )
        )
        pbar.close()

        # Store the simulated and enhanced attacks
        self.simulated_attacks.extend(enhanced_attacks)

        return enhanced_attacks

    ##################################################
    ### Simulating Base (Unenhanced) Attacks #########
    ##################################################

    def simulate_baseline_attacks(
        self,
        attacks_per_vulnerability_type: int,
        vulnerability: BaseVulnerability,
        ignore_errors: bool,
    ) -> List[SimulatedAttack]:
        baseline_attacks: List[SimulatedAttack] = []

        for vulnerability_type in vulnerability.get_types():
            try:
                remote_attacks = self.simulate_remote_attack(
                    self.purpose,
                    vulnerability_type,
                    attacks_per_vulnerability_type,
                )
                baseline_attacks.extend(
                    [
                        SimulatedAttack(
                            vulnerability=vulnerability.get_name(),
                            vulnerability_type=vulnerability_type,
                            input=remote_attack,
                        )
                        for remote_attack in remote_attacks
                    ]
                )
            except:
                if ignore_errors:
                    for _ in range(attacks_per_vulnerability_type):
                        baseline_attacks.append(
                            SimulatedAttack(
                                vulnerability=vulnerability.get_name(),
                                vulnerability_type=vulnerability_type,
                                error="Error simulating adversarial attacks.",
                            )
                        )
                else:
                    raise
        return baseline_attacks

    async def a_simulate_baseline_attacks(
        self,
        attacks_per_vulnerability_type: int,
        vulnerability: BaseVulnerability,
        ignore_errors: bool,
    ) -> List[SimulatedAttack]:
        baseline_attacks: List[SimulatedAttack] = []
        for vulnerability_type in vulnerability.get_types():
            try:
                remote_attacks = self.simulate_remote_attack(
                    self.purpose,
                    vulnerability_type,
                    attacks_per_vulnerability_type,
                )
                baseline_attacks.extend(
                    [
                        SimulatedAttack(
                            vulnerability=vulnerability.get_name(),
                            vulnerability_type=vulnerability_type,
                            input=remote_attack,
                        )
                        for remote_attack in remote_attacks
                    ]
                )
            except:
                if ignore_errors:
                    for _ in range(attacks_per_vulnerability_type):
                        baseline_attacks.append(
                            SimulatedAttack(
                                vulnerability=vulnerability.get_name(),
                                vulnerability_type=vulnerability_type,
                                error="Error simulating adversarial attacks.",
                            )
                        )
                else:
                    raise
        return baseline_attacks

    ##################################################
    ### Enhance attacks ##############################
    ##################################################

    def enhance_attack(
        self,
        attack: BaseAttack,
        simulated_attack: SimulatedAttack,
        ignore_errors: bool,
    ):
        attack_input = simulated_attack.input
        if attack_input is None:
            return simulated_attack

        simulated_attack.attack_method = attack.get_name()
        try:
            simulated_attack.input = attack.enhance(attack_input)
        except:
            if ignore_errors:
                simulated_attack.error = "Error enhancing attack"
                return simulated_attack
            else:
                raise

        return simulated_attack

    async def a_enhance_attack(
        self,
        attack: BaseAttack,
        simulated_attack: SimulatedAttack,
        ignore_errors: bool,
    ):
        attack_input = simulated_attack.input
        if attack_input is None:
            return simulated_attack

        simulated_attack.attack_method = attack.get_name()
        try:
            simulated_attack.input = await attack.a_enhance(attack_input)
        except:
            if ignore_errors:
                simulated_attack.error = "Error enhancing attack"
                return simulated_attack
            else:
                raise

        return simulated_attack

    ##################################################
    ### Utils ########################################
    ##################################################

    def _generate_schema(self, prompt: str, schema: BaseModel):
        return generate_schema(
            prompt, schema, self.using_native_model, self.simulator_model
        )

    async def _a_generate_schema(self, prompt: str, schema: BaseModel):
        return await a_generate_schema(
            prompt, schema, self.using_native_model, self.simulator_model
        )

    def simulate_remote_attack(
        self,
        purpose: str,
        vulnerability_type: VulnerabilityType,
        num_attacks: int,
    ) -> List[SimulatedAttack]:
        # Prepare parameters for API request
        generate_baseline_attack_request = ApiGenerateBaselineAttack(
            purpose=purpose,
            vulnerability=vulnerability_type.value,
            num_attacks=num_attacks,
        )
        body = generate_baseline_attack_request.model_dump(
            by_alias=True, exclude_none=True
        )
        api = Api(base_url=BASE_URL, api_key="NA")
        try:
            # API request
            response = api.send_request(
                method=HttpMethods.POST,
                endpoint=Endpoints.BASELINE_ATTACKS_ENDPOINT,
                body=body,
            )
        except Exception as e:
            print(e)

        return GenerateBaselineAttackResponseData(**response).baseline_attacks
