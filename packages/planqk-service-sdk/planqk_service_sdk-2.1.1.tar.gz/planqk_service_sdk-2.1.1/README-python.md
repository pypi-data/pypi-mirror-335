# PLANQK Service SDK

## Installation

The package is published on PyPI and can be installed via `pip`:

```bash
pip install --upgrade planqk-service-sdk
```

## Usage

```python
import os
from planqk.service.client import PlanqkServiceClient

consumer_key = "..."
consumer_secret = "..."
service_endpoint = "..."

# Create a client
client = PlanqkServiceClient(service_endpoint, consumer_key, consumer_secret)

# Prepare your input data and parameters
data = {"input": {"a": 1, "b": 2}}
params = {"param1": "value1", "param2": "value2"}

# Start a service execution
service_execution = client.run(request={"data": data, "params": params})

# Wait for the service execution to finish (blocking)
service_execution.wait_for_final_state()

status = service_execution.status
ended_at = service_execution.ended_at
print(f"Service execution finished at '{ended_at}' with status '{status}'")

# Use the client to retrieve a service execution by its id
service_execution = client.get_service_execution("0030737b-35cb-46a8-88c2-f59d4885484d")

# Retrieve the result
result = service_execution.result()

# Retrieve service execution logs
logs = service_execution.logs()

# List the result files
files = service_execution.result_files()

# Download a result file
service_execution.download_result_file(files[0], os.getcwd())
```
