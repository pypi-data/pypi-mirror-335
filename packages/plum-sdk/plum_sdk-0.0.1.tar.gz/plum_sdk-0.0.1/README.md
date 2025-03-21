# Plum SDK

Python SDK for uploading data to the Plum DB.

## Installation

```bash
pip install plum_sdk
```

## Usage

```python
from plum_sdk import PlumSDK

api_key = "YOUR_API_KEY"
data = [
    {"input": "example_input1", "output": "example_output1"},
    {"input": "example_input2", "output": "example_output2"}
]
system_prompt = "Your system prompt"

sdk = PlumSDK(api_key)
response = sdk.upload_data(data, system_prompt)

print(response)
```