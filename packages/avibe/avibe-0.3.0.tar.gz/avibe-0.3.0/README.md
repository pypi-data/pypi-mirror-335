# avibe
Utility for executing python async functions everywhere the same way - scripts, notebooks, etc.

Stupidly simple, surprisingly useful.

## Installation
```shell
pip install avibe
```

## Usage
`run_async_function` allows you to execute asynchronous functions the same way in both scripts and Jupyter notebooks...like a normal sync function.

```python
from avibe import run_async_function
import asyncio


# Sample async function
async def sample_async_function(x, y):
    await asyncio.sleep(1)  # Simulate async work
    return x + y


# Run the async function
result = run_async_function(sample_async_function, 5, 7)
print(result)  # Output: 12
```



