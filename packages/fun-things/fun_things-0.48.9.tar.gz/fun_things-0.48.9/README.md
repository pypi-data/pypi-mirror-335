# Fun-Things

A Python utility package containing a collection of helpful functions and tools for everyday development tasks.

## Installation

```bash
# Using pip
pip install fun-things
```

## Features

Fun-Things provides a variety of utility modules:

- **Asynchronous Tools**: Convert between sync/async functions and generators
- **Retry Mechanisms**: Simple retry patterns for functions and API calls
- **Middleware**: A middleware implementation for Python applications
- **Lazy Loading**: Utilities for lazy evaluation of objects
- **Network Tools**: Functions for network operations like ping
- **Type Utilities**: Helper functions for working with Python types
- **Categorizer**: Tools for categorizing data
- **CLI Tools**: Command-line utilities for package management
- **AdBlocker Filter Parser**: Parse and work with ad blocker filter rules
- **Singleton Factory**: Implementation of the singleton pattern
- **URL Utilities**: Tools for working with URLs
- **Environment Tools**: Environment variable handling
- **And more!**

## Usage

Import specific utilities

```python
from fun_things import lazy, undefined, merge_dict
from fun_things.retry import Retry, AsyncRetry
from fun_things.asynchronous import as_async, as_sync
```

Use the CLI

```sh
# After installation, the 'fun' command is available
$ fun freeze  # Freezes your dependencies
$ fun install  # Installation helper
```

## Requirements

- Python 3.8 or higher

## Documentation

For more detailed usage information, see the docstrings in each module.
