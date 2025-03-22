<p align="center">
    <img src="https://github.com/confident-ai/deepteam/blob/main/docs/static/img/deepteam.png" alt="DeepTeam Logo" width="100%">
</p>

<p align="center">
    <h1 align="center">The LLM Red Teaming Framework</h1>
</p>

<p align="center">
    <a href="https://discord.com/invite/a3K9c8GRGt">
        <img alt="discord-invite" src="https://dcbadge.vercel.app/api/server/a3K9c8GRGt?style=flat">
    </a>
</p>

<h4 align="center">
    <p>
        <a href="https://www.trydeepteam.com?utm_source=GitHub">Documentation</a> |
        <a href="#-vulnerabilities--attacks--and-features-">Vulnerabilities, Attacks, and Features</a> |
        <a href="#-quickstart">Getting Started</a> 
    <p>
</h4>

<p align="center">
    <a href="https://github.com/confident-ai/deepteam/releases">
        <img alt="GitHub release" src="https://img.shields.io/github/release/confident-ai/deepeval.svg?color=violet">
    </a>
    <a href="https://colab.research.google.com/drive/1PPxYEBa6eu__LquGoFFJZkhYgWVYE6kh?usp=sharing">
        <img alt="Try Quickstart in Colab" src="https://colab.research.google.com/assets/colab-badge.svg">
    </a>
    <a href="https://github.com/confident-ai/deepteam/blob/master/LICENSE.md">
        <img alt="License" src="https://img.shields.io/github/license/confident-ai/deepeval.svg?color=yellow">
    </a>
</p>

**DeepTeam** is a simple-to-use, open-source LLM red teaming framework, for safety testing large-language model systems. DeepTeam incorporates the latest research to simulate adversarial attacks using SOTA techniques such as jailbreaking and prompt injections, to catch vulnerabilities like bias and PII Leakage that you might not otherwise be aware of.

DeepTeam runs **locally on your machine**, and **uses LLMs** for both simulation and evaluation during red teaming. With DeepTeam, whether your LLM systems are RAG piplines, chatbots, AI agents, or just the LLM itself, you can be confident that safety risks and security vulnerabilities are caught before your users do.

> [!IMPORTANT]
> DeepTeam is powered by [DeepEval](https://github.com/confident-ai/deepeval), the open-source LLM evaluation framework.

> Want to talk LLM security, or just to say hi? [Come join our discord.](https://discord.com/invite/a3K9c8GRGt)

<br />

# 🚨⚠️ Vulnerabilities, 💥 Attacks, and Features 🔥

- 40+ [vulnerabilities](https://www.trydeepteam.com/docs/red-teaming-vulnerabilities) available out-of-the-box, including:
  - Bias
     - Gender
     - Race
     - Political
     - Religion
  - PII Leakage
    - Direct leakage
    - Session leakage
    - Database access
  - Misinformation
    - Factual error
    - Unsupported claims
  - Robustness
    - Input overreliance
    - Hijacking
  - etc.
- 10+ [adversarial attack](https://www.trydeepteam.com/docs/red-teaming-adversarial-attacks) methods, for both single-turn and multi-turn (conversational based red teaming):
  - Single-Turn
    - Prompt Injection
    - Leetspeak
    - ROT-13
    - Math Problem
  - Multi-Turn
    - Linear Jailbreaking
    - Tree Jailbreaking
    - Crescendo Jailbreaking
- Customize different vulnerabilities and attacks to your specific organization needs in 5 lines of code.
- Easily access red teaming risk assessments, display in dataframes, and **save locally on your machine in JSON format.**
- Out of the box support for standard guidelines such as OWASP Top 10 for LLMs, NIST AI RMF.

<br />

# 🚀 QuickStart

DeepTeam does not require you to define what LLM system you are red teaming because neither will malicious users/bad actors. All you need to do is to install `deepteam`, define a `model_callback`, and you're good to go.

## Installation

```
pip install -U deepteam
```

## Defining Your Target Model Callback

The callback is a wrapper around your LLM system and allows `deepteam` to red team your LLM system after generating adversarial attacks during safety testing.

First create a test file:

```bash
touch red_team_llm.py
```

Open `red_team_llm.py` and paste in the code:

```python
def model_callback(input: str) -> str:
    # Replace this with your LLM application
    return f"I'm sorry but I can't answer this: {input}"
```
You'll need to replace the implementation of this callback with your own LLM application.

## Detect Your First Vulnerability

Finally, import vulnerabilities and attacks, along with your previously defined `model_callback`:

```python
from deepteam import red_team
from deepteam.vulnerabilities import Bias
from deepteam.attacks.single_turn import PromptInjection

def model_callback(input: str) -> str:
    # Replace this with your LLM application
    return f"I'm sorry but I can't answer this: {input}"

bias = Bias(types=["race"])
prompt_injection = PromptInjection()

risk_assessment = red_team(model_callback=model_callback, vulnerabilities=[bias], attacks=[prompt_injection])
```
Don't forget to run the file:

```bash
python red_team_llm.py
```

**Congratulations! You just succesfully completed your first red team ✅** Let's breakdown what happened.

- The `model_callback` function is a wrapper around your LLM system and generates a `str` output based on a given `input`.
- At red teaming time, `deepteam` simulates an attack for [`Bias`](https://www.trydeepteam.com/docs/red-teaming-vulnerabilities-bias), and is provided as the `input` to your `model_callback`.
- The simulated attack is of the [`PromptInjection`](https://www.trydeepteam.com/docs/red-teaming-adversarial-attacks-prompt-injection) method.
- Your `model_callback`'s output for the `input` is evaluated using the `BiasMetric`, which corresponds to the `Bias` vulnerability, and outputs a binary score of 0 or 1.
- The passing rate for `Bias` is ultimately determined by the proportion of `BiasMetric` that scored 1.

Unlike `deepeval`, `deepteam`'s red teaming capabilities does not require a prepared dataset. This is because adversarial attacks to your LLM application is dynamically simulated at red teaming time based on the list of `vulnerabilities` you wish to red team for.

> [!NOTE]
> You'll need to set your `OPENAI_API_KEY` as an enviornment variable before running the `red_team()` function, since `deepteam` uses LLMs to both generate adversarial attacks and evaluate LLM outputs. To use **ANY** custom LLM of your choice, [check out this part of the docs](https://docs.confident-ai.com/guides/guides-using-custom-llms).

<br />


# Roadmap

- [ ] More vulnerabilities for everyone
- [ ] More attacks for everyone

<br />

# Authors

Built by the founders of Confident AI. Contact jeffreyip@confident-ai.com for all enquiries.

<br />

# License

DeepTeam is licensed under Apache 2.0 - see the [LICENSE.md](https://github.com/confident-ai/deepteam/blob/main/LICENSE.md) file for details.
