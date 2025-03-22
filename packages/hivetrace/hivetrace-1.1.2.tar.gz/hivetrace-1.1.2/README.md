# Hivetrace SDK

## Description
Hivetrace SDK is designed for integration with the Hivetrace service, providing monitoring of user prompts and LLM responses.

## Installation

Install the SDK via pip:

```sh
pip install hivetrace
```

## Usage

```python
from hivetrace.hivetrace import HivetraceSDK
```

# Initialize the SDK
```python
hivetrace = HivetraceSDK()
```

# Send a user prompt
```python
response = hivetrace.input(
    application_id="your-application-id", # get after registering the application in the UI
    message="User prompt here"
)
```

# Send a response from your LLM
```python
response = hivetrace.output(
    application_id="your-application-id", # get after registering the application in the UI
    message="LLM response here"
)
```

### Example with additional parameters
```python
response = hivetrace.input(
    application_id="your-application-id",
    message="User prompt here",
    additional_parameters={
        "session_id": "your-session-id",
        "user_id": "your-user-id",
        "agents": {
            "agent-1-id": {"name": "Agent 1", "description": "Agent description"},
            "agent-2-id": {"name": "Agent 2"},
            "agent-3-id": {}
        }
    }
)
```

## API

### `input(application_id: str, message: str, additional_parameters: dict = None) -> dict`
Sends a user prompt to Hivetrace.

- `application_id` - Application identifier (must be a valid UUID, created in the UI)
- `message` - User prompt
- `additional_parameters` - Dictionary of additional parameters (optional)

#### Response Example for `input()`
```json
{
    "status": "processed",
    "monitoring_result": {
        "is_toxic": false,
        "type_of_violation": "benign",
        "token_count": 9,
        "token_usage_warning": false,
        "token_usage_unbounded": false
    }
}
```

### `output(application_id: str, message: str, additional_parameters: dict = None) -> dict`
Sends an LLM response to Hivetrace.

- `application_id` - Application identifier (must be a valid UUID, created in the UI)
- `message` - LLM response
- `additional_parameters` - Dictionary of additional parameters (optional)

#### Response Example for `output()`
```json
{
    "status": "processed",
    "monitoring_result": {
        "is_toxic": false,
        "type_of_violation": "safe",
        "token_count": 21,
        "token_usage_warning": false,
        "token_usage_unbounded": false
    }
}
```

## Additional Parameters
The `additional_parameters` argument is an optional dictionary that allows passing extra metadata along with requests.
It may include:

- `user_id` (str, optional) – Unique user identifier (must be a valid UUID).
- `session_id` (str, optional) – UUID representing a session.
- `agents` (dict, optional) – Dictionary where keys are agent IDs (must be valid UUIDs) and values contain agent metadata:
  - `name` (str, optional) – Agent's name. If not provided, it will be automatically generated based on parts of its ID.
  - `description` (str, optional) – Description of the agent.

If `user_id` is not found in the system, it will be automatically created. Agents provided in the request will also be automatically registered in the system and can be viewed in the UI.

## Configuration
The SDK loads configuration from environment variables. The allowed domain (`HIVETRACE_URL`) and access token (`HIVETRACE_ACCESS_TOKEN`) is automatically retrieved from the environment.

### Configuration Sources
Hivetrace SDK can retrieve the configuration from the following sources:

1. **.env File**: Place a `.env` file in your project directory containing:
   ```ini
   HIVETRACE_URL=https://your-hivetrace-instance.com
   HIVETRACE_ACCESS_TOKEN=your-access-token
   ```
   The SDK will automatically load this.

## License

This project is licensed under the [Apache License 2.0](http://www.apache.org/licenses/LICENSE-2.0).

