# Agentic

A simple framework for creating AI agents and agent managers with LLM backends.

## Installation

```bash
pip install agentrix
```

## Usage

```python
from agentrix import Tool, Agent, ManagerAgent
import openai

# Initialize OpenAI client
client = AzureOpenAI(
    api_key=os.getenv('AZURE_OPENAI_API_KEY'),
    api_version="2024-02-15-preview",
    azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT')
)

# Create a simple tool
calculator_tool = Tool(
    name="calculator",
    description="Calculate a mathematical expression",
    function=lambda expression: eval(expression),
    inputs={"expression": ["string", "The math expression to evaluate"]}
)

# Create an agent with the tool
math_agent = Agent(
    name="MathAgent",
    system_prompt="You are a helpful mathematical assistant.",
    llm=client,
    tools=[calculator_tool],
    verbose=True
)

# Use the agent
result = math_agent.go("What is 25 squared plus 13?")
print(result)
```

## Creating a Manager Agent

```python
# Create specialized agents
researcher = Agent("Researcher", "You research facts thoroughly.", client)
analyst = Agent("Analyst", "You analyze data and provide insights.", client)

# Create a manager agent
manager = ManagerAgent(
    name="Manager",
    system_prompt="You coordinate multiple agents to solve complex problems.",
    llm=client,
    agents=[(researcher, "Use for researching facts"), (analyst, "Use for data analysis")],
    parallel=True,
    verbose=True
)

# Use the manager agent
result = manager.go("Research the population of France and analyze its growth trend.")
print(result)
```