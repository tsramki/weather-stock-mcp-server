import hmac
import os

import requests
import yfinance as yf
from dotenv import load_dotenv
from mcp.server import MCPServer
from mcp.server.auth.provider import AccessToken
from mcp.server.auth.settings import AuthSettings

load_dotenv()

HOST = "127.0.0.1"
PORT = 8000
SERVER_URL = f"http://{HOST}:{PORT}"

SERVER_TOKEN = os.environ.get("MCP_SERVER_TOKEN")
if not SERVER_TOKEN:
    raise RuntimeError("MCP_SERVER_TOKEN is not set. Add it to .env before starting the server.")


class StaticTokenVerifier:
    """Accepts a single shared bearer token (Authorization: Bearer <token>)."""

    async def verify_token(self, token: str) -> AccessToken | None:
        if not hmac.compare_digest(token.encode(), SERVER_TOKEN.encode()):
            return None
        return AccessToken(token=token, client_id="static-client", scopes=[])


mcp = MCPServer(
    "Stock and Weather",
    token_verifier=StaticTokenVerifier(),
    auth=AuthSettings(
        issuer_url=SERVER_URL,
        resource_server_url=SERVER_URL,
        validate_token_resource=False,
    ),
)


@mcp.tool()
def get_stock_price(ticker: str) -> str:
    """Get the last traded stock price for a given ticker symbol (e.g. AAPL, MSFT)."""
    stock = yf.Ticker(ticker)
    price = stock.fast_info.get("lastPrice")
    if price is None:
        return f"Could not find a price for ticker '{ticker}'."
    return f"The last price for {ticker.upper()} is ${price:.2f}."


@mcp.tool()
def get_weather(city: str) -> str:
    """Get the current weather for a given city name."""
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        return "OpenWeather API key is not configured."

    try:
        response = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": city, "appid": api_key, "units": "metric"},
            timeout=10,
        )
    except requests.RequestException:
        return f"Could not fetch weather for '{city}'. Please try again later."

    if response.status_code != 200:
        return f"Could not find weather for '{city}'."

    data = response.json()
    description = data["weather"][0]["description"]
    temp = data["main"]["temp"]
    return f"The weather in {city} is {description} with a temperature of {temp}°C."


if __name__ == "__main__":
    mcp.run(transport="streamable-http",port=8000)
