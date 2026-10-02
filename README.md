# JARVIS

Self-hosted personal AI assistant for managing phone calls and social messaging on your behalf.

Built with FastAPI, Pydantic v2, httpx.

## Features

- Async LLM reasoning with OpenAI or OpenRouter
- Function / tool calling support
- Tool stubs: Google Calendar, SMS summary via Twilio, recent notes
- Centralized config via pydantic-settings
- Production-grade FastAPI app factory with health check

## Quick Start

1. Copy env:
```bash
cp .env.example .env
```
Edit `.env` with your API keys.

2. Install:
```bash
pip install -r requirements.txt
```

3. Run:
```bash
uvicorn main:app --reload --port 8000
```

Health check: `GET http://localhost:8000/health`

## Project Structure

```
jarvis/
├─ config.py
├─ main.py
├─ requirements.txt
├─ core/
│  ├─ brain.py
│  └─ tools.py
└─ .env.example
```

## Configuration

See `config.py` and `.env.example`. Required for providers:
- `OPENAI_API_KEY` or `OPENROUTER_API_KEY`
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`

## License

MIT
