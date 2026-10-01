# Stock and Weather MCP Server

An [MCP](https://modelcontextprotocol.io) server that exposes two tools over streamable HTTP, protected by a bearer token.

| Tool | Description |
|---|---|
| `get_stock_price(ticker)` | Last traded price for a ticker (e.g. `AAPL`), via [yfinance](https://github.com/ranaroussi/yfinance) |
| `get_weather(city)` | Current weather for a city, via [OpenWeatherMap](https://openweathermap.org/api) |

## Requirements

- Python 3.13
- [uv](https://docs.astral.sh/uv/)
- An [OpenWeatherMap API key](https://openweathermap.org/api)

## Setup

```bash
uv venv
uv pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:

| Variable | Purpose |
|---|---|
| `OPENWEATHER_API_KEY` | Used by `get_weather` |
| `MCP_SERVER_TOKEN` | Shared secret clients must send. Required; the server won't start without it |

Generate a token with:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Run

```bash
uv run server.py
```

The server listens on `http://127.0.0.1:8000/mcp`. Change `HOST` and `PORT` at the top of [server.py](server.py) to alter this.

## Authentication

Every request must include:

```
Authorization: Bearer <MCP_SERVER_TOKEN>
```

Requests with a missing or wrong token get `401 Unauthorized`.

Quick check:

```bash
curl -i http://127.0.0.1:8000/mcp \
  -H "Authorization: Bearer $MCP_SERVER_TOKEN" \
  -H "Accept: application/json, text/event-stream" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"test","version":"1"}}}'
```

## Notes

- Traffic is plain HTTP, so the token is sent unencrypted. This is fine on localhost; put the server behind TLS before exposing it.
- There is a single shared token with no per-user identity or scopes.
- Keep `.env` out of version control (it is already in `.gitignore`).
