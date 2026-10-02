# Architecture

## Overview

JARVIS is a modular async assistant.

- `config.py` : Single source of truth for env via pydantic-settings
- `core/brain.py` : LLM orchestration, provider abstraction, tool calling loop
- `core/tools.py` : Declarative tool functions with Pydantic inputs
- `main.py` : FastAPI application factory, router registration

## Data flow

1. HTTP request → FastAPI router
2. Router → Brain.reason with system instructions + context + history
3. Brain → provider API via httpx
4. Tool calls → core.tools functions
5. Results returned to LLM and caller

## Extending

Add a tool:
- Define async function in `core/tools.py` with Pydantic input model
- Register in `Brain.TOOLS_REGISTRY`
