# civitai_api

![Coverage](https://img.shields.io/badge/coverage-87%25-brightgreen)

This project provide a easy way to communicating with Civitai-API.

It supports both Sync and Async request implementation, and both Async implementation (AsyncIO and Trio) by using Anyio.

**See usage example in : [/tests/test_v1.py](./tests/test_v1.py).**

You may need to register your own CivitAI api key, see [here](https://github.com/civitai/civitai/wiki/REST-API-Reference#authorization).

## Exception handling

There are 3 types of Exception you should care of

1. QueryParamsError
    - only for the endpoints which could return multiple results.
2. FileNotFoundError
    - only for the endpoints which could return single results.
3. ConnectionAbortedError
    - every endpoint could trigger this Exception when the number of requests reach Civitai server's limitation.

```python

```

## Attention

1. you could only get model's availability from endpoint models or modelId endpoints!
    - some of the models have an EarlyAccess duration at the first time they get published.
2. Trainned Prompts could only get from VersionId or Hash endpoints!

