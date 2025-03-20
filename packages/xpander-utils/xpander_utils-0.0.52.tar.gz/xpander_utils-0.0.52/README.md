# xpander_utils Package Development Guide
## Local Development
To set up the project locally, follow these steps:

### Local Build and Link
Install the package in editable mode:
```bash
pip install -e .
```

## Usage

To use the `xpander-utils` package, install it via pip:
```bash
pip install xpander-utils
```

### Example Code

Below is an example of how to use the `SmolAgentsAdapter` for bridging xpander.ai and smolagents:

```python
from smolagents import OpenAIServerModel, ToolCallingAgent, ActionStep, MultiStepAgent
from xpander_utils.sdk.adapters import SmolAgentsAdapter


llm_api_key = "{YOUR_LLM_KEY}"

# get xpander agent
xpander = SmolAgentsAdapter(agent_id="{YOUR_AGENT_ID}", api_key="{YOUR_API_KEY}")

# declare model
model = OpenAIServerModel(
    model_id="gpt-4o",
    api_key=llm_api_key
)

# init xpander task
prompt = "get the longest tag"
xpander.add_task(input=prompt)

# convert xpander tools to smolagents

# create the agent
agent = ToolCallingAgent(step_callbacks=[xpander.step_callback()],tools=xpander.get_tools(),model=model,prompt_templates={"system_prompt": xpander.get_system_prompt()})

# init memory from xpander
xpander.init_memory(agent=agent)

result = agent.run(task=prompt, reset=False)
```

## Package Information

- **Package Name:** `xpander_utils`
- **Version:** `0.0.1`
- **Author:** `xpanderAI`
- **Email:** `dev@xpander.ai`
- **Description:** A Python utilities SDK for xpander.ai services.
- **URL:** [xpander.ai](https://www.xpander.ai)

## Dependencies
The package requires the following dependencies:

- `pydantic`
- `loguru`
- `smolagents`
- `xpander-sdk`

## Supported Python Versions
This package requires Python `>=3.12.17`.

## License
This project is licensed under the MIT License.

