import asyncio
import json
import os
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import httpx2
from pydantic import AnyUrl
from mcp import Client
from mcp.client.auth import AuthorizationCodeResult, OAuthClientProvider, TokenStorage
from mcp.client.streamable_http import streamable_http_client
from mcp.shared.auth import OAuthClientInformationFull, OAuthClientMetadata, OAuthToken

OAUTH_SERVER_URL = "https://mcp.swiggy.com"
INSTAMART_URL = "https://mcp.swiggy.com/im"
REDIRECT_URI = "http://localhost:3000/callback"
CALLBACK_HOST = "localhost"
CALLBACK_PORT = 3000
TOKEN_FILE = Path(__file__).with_name(".swiggy_auth.json")

_callback_future = None
_callback_server = None


class FileTokenStorage(TokenStorage):
    def __init__(self):
        self.tokens = None
        self.client_info = None
        self._load()

    def _load(self):
        if not TOKEN_FILE.exists():
            return
        try:
            data = json.loads(TOKEN_FILE.read_text(encoding="utf-8"))
            if data.get("tokens"):
                self.tokens = OAuthToken.model_validate(data["tokens"])
            if data.get("client_info"):
                self.client_info = OAuthClientInformationFull.model_validate(data["client_info"])
        except Exception:
            self.tokens = None
            self.client_info = None

    def _save(self):
        data = {
            "tokens": self.tokens.model_dump(mode="json") if self.tokens else None,
            "client_info": self.client_info.model_dump(mode="json") if self.client_info else None,
        }
        TOKEN_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")

    async def get_tokens(self):
        return self.tokens

    async def set_tokens(self, tokens: OAuthToken):
        self.tokens = tokens
        self._save()

    async def get_client_info(self):
        return self.client_info

    async def set_client_info(self, client_info: OAuthClientInformationFull):
        self.client_info = client_info
        self._save()


class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global _callback_future
        callback_url = f"http://{CALLBACK_HOST}:{CALLBACK_PORT}{self.path}"
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        html = """<!doctype html><html><head><meta charset='utf-8'><title>Smart Refrigerator</title></head>
        <body style='font-family:Arial;background:#eef9fb;text-align:center;padding-top:100px'>
        <div style='background:white;max-width:520px;margin:auto;padding:40px;border-radius:20px;box-shadow:0 10px 30px rgba(0,0,0,.08)'>
        <h1 style='color:#164e63'>✓ Authentication Successful</h1>
        <p style='color:#66828b'>You can close this tab and return to Smart Refrigerator.</p></div></body></html>"""
        self.wfile.write(html.encode("utf-8"))
        if _callback_future is not None:
            loop = _callback_future.get_loop()
            loop.call_soon_threadsafe(_callback_future.set_result, callback_url)

    def log_message(self, format, *args):
        return


def _start_callback_server():
    global _callback_server
    if _callback_server is not None:
        return
    _callback_server = ThreadingHTTPServer((CALLBACK_HOST, CALLBACK_PORT), CallbackHandler)
    thread = threading.Thread(target=_callback_server.serve_forever, daemon=True)
    thread.start()


def _stop_callback_server():
    global _callback_server
    if _callback_server is not None:
        _callback_server.shutdown()
        _callback_server.server_close()
        _callback_server = None


async def _redirect_handler(auth_url: str):
    _start_callback_server()
    webbrowser.open(auth_url)


async def _callback_handler() -> AuthorizationCodeResult:
    global _callback_future
    loop = asyncio.get_running_loop()
    _callback_future = loop.create_future()
    try:
        callback_url = await asyncio.wait_for(_callback_future, timeout=180)
    finally:
        _callback_future = None
        _stop_callback_server()

    parsed = urlparse(callback_url)
    params = parse_qs(parsed.query)
    if "error" in params:
        raise RuntimeError(f"Swiggy OAuth error: {params['error'][0]} - {params.get('error_description', [''])[0]}")
    if "code" not in params:
        raise RuntimeError("Swiggy returned no authorization code.")
    return AuthorizationCodeResult(
        code=params["code"][0],
        state=params.get("state", [None])[0],
        iss=params.get("iss", [None])[0],
    )


def _provider():
    return OAuthClientProvider(
        server_url=OAUTH_SERVER_URL,
        client_metadata=OAuthClientMetadata(
            client_name="Smart Refrigerator",
            redirect_uris=[AnyUrl(REDIRECT_URI)],
            grant_types=["authorization_code", "refresh_token"],
            response_types=["code"],
            scope="mcp:tools",
        ),
        storage=FileTokenStorage(),
        redirect_handler=_redirect_handler,
        callback_handler=_callback_handler,
    )


def _extract_result(result):
    if getattr(result, "isError", False):
        raise RuntimeError(str(result))
    structured = getattr(result, "structuredContent", None)
    if structured is not None:
        if isinstance(structured, dict) and "data" in structured:
            return structured["data"]
        return structured
    content = getattr(result, "content", None) or []
    texts = []
    for item in content:
        text = getattr(item, "text", None)
        if text:
            texts.append(text)
    joined = "\n".join(texts).strip()
    if not joined:
        return {}
    try:
        payload = json.loads(joined)
        if isinstance(payload, dict) and payload.get("success") is False:
            raise RuntimeError(payload.get("error", {}).get("message", "Swiggy tool call failed."))
        if isinstance(payload, dict) and "data" in payload:
            return payload["data"]
        return payload
    except json.JSONDecodeError:
        return {"raw": joined}


async def _call_tool_async(name, arguments=None):
    auth = _provider()
    async with httpx2.AsyncClient(auth=auth, timeout=90.0) as http_client:
        transport = streamable_http_client(INSTAMART_URL, http_client=http_client)
        async with Client(transport) as client:
            result = await client.call_tool(name, arguments or {})
            return _extract_result(result)


def call_tool(name, arguments=None):
    return asyncio.run(_call_tool_async(name, arguments))


def get_addresses():
    return call_tool("get_addresses", {"page": 1, "pageSize": 10}).get("addresses", [])


def search_products(address_id, query):
    return call_tool("search_products", {"addressId": address_id, "query": query})


def update_cart(spin_id, quantity=1):
    return call_tool("update_cart", {"items": [{"spinId": spin_id, "quantity": quantity}]})


def get_cart():
    return call_tool("get_cart")


def checkout(address_id, payment_method=None, intent_app=None):
    args = {"addressId": address_id}
    if payment_method:
        args["paymentMethod"] = payment_method
    if intent_app:
        args["intentApp"] = intent_app
    return call_tool("checkout", args)


def logout():
    try:
        TOKEN_FILE.unlink(missing_ok=True)
    except Exception:
        pass
