# Tiptree Client

A Python client library for interacting with the Tiptree's Agent Runtime Platform. This client provides both synchronous and asynchronous methods for all API endpoints.

## Installation

```bash
pip install tiptree
```

## Quick Start

Please make sure your API keys are either saved in `~/.tiptreerc/credentials` or passed as an environment variable:

```bash
export TIPTREE_API_KEY=<your-api-key>
```

Here's a simple example of how to use the client:

```python
from tiptree import Agent

# Create an agent
agent = Agent.get_or_create()

# Create an agent session
session = agent.create_agent_session()

# Send message to session
sent_message = session.send_message("What's the weather like in Berlin right now?")

# Wait for the response
received_message = session.wait_for_next_message()
print(received_message.content)
```

## Features

- Full support for the Tiptree Platform API
- Both synchronous and asynchronous APIs
- Type hints for better IDE integration
- Comprehensive models for all API entities

## License

This project is licensed under the MIT License - see the LICENSE file for details.
