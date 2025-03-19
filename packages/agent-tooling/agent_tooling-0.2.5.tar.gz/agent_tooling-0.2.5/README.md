# Agent Tooling

A lightweight Python package for registering and managing function metadata and references.

## Installation

```bash
pip install agent_tooling
```

## Usage

```python
from agent_tooling import tool, get_tool_schemas, get_tool_function

@tool
def add_numbers(a: int, b: int) -> int:
    """Simple function to add two numbers."""
    return a + b

# Get registered tool metadata
tool_schemas = get_tool_schemas()
print(tool_schemas)

# Get function reference by name
func = get_tool_function('add_numbers')
result = func(5, 3)  # Returns 8
```

## Example Output

```python
[{
    'name': 'add_numbers',
    'description': 'Simple function to add two numbers.',
    'parameters': {
        'type': 'object',
        'properties': {
            'a': {'type': 'integer'},
            'b': {'type': 'integer'}
        },
        'required': ['a', 'b']
    },
    'return_type': 'integer'
}]
```

## Features

- Easy function metadata registration
- Automatic introspection of function signatures
- Singleton tool registry
- JSON-schema compatible parameter definitions
- Function reference storage and retrieval
- Compatible with AI tools frameworks

## API Reference

### `@tool`
Decorator to register a function as a tool, capturing its metadata and storing its reference.

### `get_tool_schemas()`
Returns a list of metadata schemas for all registered tools.

### `get_tool_function(name)`
Returns the function reference for a registered tool by name.

### `get_registered_tools()` (Legacy)
Alias for `get_tool_schemas()` maintained for backward compatibility.

## Example with AI Tool Integration

```python
from agent_tooling import tool, get_tool_schemas, get_tool_function
from openai import OpenAI
import json

@tool
def get_weather(location: str, unit: str = "celsius") -> str:
    """Get the current weather for a location."""
    # Implementation omitted
    return f"The weather in {location} is sunny and 25°{unit[0].upper()}"

# Get tool schemas for AI model
tools = get_tool_schemas()

# Create AI client
client = OpenAI()

# Send request to AI with tools
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": "What's the weather in Paris?"}],
    tools=tools,
    tool_choice="auto",
)

# Process tool calls
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        
        # Get and call the function
        function_to_call = get_tool_function(name)
        result = function_to_call(**args)
        print(result)  # "The weather in Paris is sunny and 25°C"
```