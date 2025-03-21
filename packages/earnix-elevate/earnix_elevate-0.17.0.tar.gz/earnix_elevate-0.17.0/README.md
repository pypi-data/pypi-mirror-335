## Earnix Elevate SDK

[![ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://github.com/python/mypy)
[![bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

**Earnix is a global provider of Intelligent Insurance and Banking Operations through agile, composable and real-time solutions.**

This is a Software Development Kit for interactions with the Earnix Elevate line of products, providing HTTP clients and models covering 100% of the backend's capabilities, wrapped in an easy-to-use package. As of now, we only offer 1:1 interactions with the backend APIs, but we plan to introduce custom flows that call multiple APIs in the future.

With this package, you don't need to be learning the APIs, implementing the HTTP protocol or managing JSONs. For the best experience, we recommend using it with a modern Python LSP/IDE. We try to use type hinting whenever possible. The full developer experience includes automatic OOP model hierarchies, code completion, field validations and more.

## Requirements

- Python >= 3.9.
- An Earnix Elevate account.
- Valid `client_id` and `secret_key`, linked to that account or to a user within that account.

## Installation

- Using `pip` (maybe inside a `venv`):

  ```shell
  pip install --upgrade earnix-elevate
  ```

- Using a specific Python:

  ```shell
  python3.10 -m pip install --upgrade earnix-elevate
  ```

- Using another tool (such as `pdm` or `poetry`):

  ```shell
  pdm add earnix-elevate
  ```

## Example usage

- Print your Connections:

  ```python
  from earnix_elevate.core import ConnectionService

  connection_service = ConnectionService(
    server="eu",
    client_id="...",
    secret_key="...",
  )

  connections = connection_service.list_connections()
  print(connections)
  ```
