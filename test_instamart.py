import asyncio
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

import httpx2
from pydantic import AnyUrl

from mcp import Client
from mcp.client.auth import (
    AuthorizationCodeResult,
    OAuthClientProvider,
    TokenStorage,
)
from mcp.client.streamable_http import streamable_http_client
from mcp.shared.auth import (
    OAuthClientInformationFull,
    OAuthClientMetadata,
    OAuthToken,
)


# ============================================================
# CONFIGURATION
# ============================================================

OAUTH_SERVER_URL = "https://mcp.swiggy.com"
INSTAMART_URL = "https://mcp.swiggy.com/im"

REDIRECT_URI = "http://localhost:3000/callback"
CALLBACK_HOST = "localhost"
CALLBACK_PORT = 3000


# ============================================================
# GLOBAL CALLBACK STATE
# ============================================================

callback_future = None
callback_server = None


# ============================================================
# 1. In-memory token storage
# ============================================================

class InMemoryTokenStorage(TokenStorage):

    def __init__(self):
        self.tokens = None
        self.client_info = None

    async def get_tokens(self):
        return self.tokens

    async def set_tokens(self, tokens: OAuthToken):
        self.tokens = tokens

    async def get_client_info(self):
        return self.client_info

    async def set_client_info(
        self,
        client_info: OAuthClientInformationFull
    ):
        self.client_info = client_info


# ============================================================
# 2. Local OAuth callback HTTP server
# ============================================================

class CallbackHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        global callback_future

        # Build complete callback URL
        callback_url = f"http://{CALLBACK_HOST}:{CALLBACK_PORT}{self.path}"

        print("\n========================================")
        print("       OAUTH CALLBACK RECEIVED")
        print("========================================")

        print("\n✓ Swiggy redirected back to localhost.")
        print("✓ Callback captured automatically.")
        print("✓ No copy/paste required.")

        # Send browser response
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()

        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Smart Refrigerator</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: #eef9fb;
                    text-align: center;
                    padding-top: 100px;
                }

                .card {
                    background: white;
                    max-width: 500px;
                    margin: auto;
                    padding: 40px;
                    border-radius: 20px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.08);
                }

                h1 {
                    color: #164e63;
                }

                p {
                    color: #66828b;
                }
            </style>
        </head>

        <body>

            <div class="card">

                <h1>✓ Authentication Successful</h1>

                <p>
                    You can close this browser tab
                    and return to the terminal.
                </p>

            </div>

        </body>
        </html>
        """

        self.wfile.write(html.encode("utf-8"))

        # Pass callback URL back to asyncio
        if callback_future is not None:

            loop = callback_future.get_loop()

            loop.call_soon_threadsafe(
                callback_future.set_result,
                callback_url
            )

    def log_message(self, format, *args):
        # Disable noisy HTTP server logs
        return


def start_callback_server():

    global callback_server

    callback_server = ThreadingHTTPServer(
        (CALLBACK_HOST, CALLBACK_PORT),
        CallbackHandler
    )

    print(
        f"\n✓ Local OAuth callback server started:"
        f" http://{CALLBACK_HOST}:{CALLBACK_PORT}/callback"
    )

    thread = threading.Thread(
        target=callback_server.serve_forever,
        daemon=True
    )

    thread.start()


def stop_callback_server():

    global callback_server

    if callback_server is not None:

        callback_server.shutdown()
        callback_server.server_close()

        callback_server = None

        print("✓ Local OAuth callback server stopped.")


# ============================================================
# 3. Open Swiggy authorization page
# ============================================================

async def handle_redirect(auth_url: str):

    print("\n========================================")
    print("        SWIGGY AUTHENTICATION")
    print("========================================")

    print("\n✓ Opening Swiggy authorization page...")

    print("\nIf the browser does not open automatically,")
    print("copy this URL into your browser:\n")

    print(auth_url)

    # Start callback server BEFORE opening browser
    start_callback_server()

    # Open browser
    webbrowser.open(auth_url)

    print("\nWaiting for Swiggy authentication...")
    print("Complete the Swiggy login/OTP in your browser.")


# ============================================================
# 4. Receive OAuth callback automatically
# ============================================================

async def handle_callback() -> AuthorizationCodeResult:

    global callback_future

    print("\nWaiting for OAuth callback from Swiggy...")

    # Create future for callback server
    callback_future = asyncio.get_running_loop().create_future()

    try:

        # Wait until browser redirects to localhost
        callback_url = await asyncio.wait_for(
            callback_future,
            timeout=180
        )

    except asyncio.TimeoutError:

        raise RuntimeError(
            "Timed out waiting for Swiggy OAuth callback."
        )

    finally:

        callback_future = None

        # Stop local callback server
        stop_callback_server()

    print("\n✓ Callback received.")

    # Parse callback
    parsed = urlparse(callback_url)

    params = {}

    if parsed.query:
        from urllib.parse import parse_qs
        params = parse_qs(parsed.query)

    # Check OAuth errors
    if "error" in params:

        error = params["error"][0]

        description = params.get(
            "error_description",
            ["Unknown OAuth error"]
        )[0]

        raise RuntimeError(
            f"Swiggy OAuth error: {error} - {description}"
        )

    # Authorization code required
    if "code" not in params:

        raise RuntimeError(
            "No authorization code was received from Swiggy."
        )

    code = params["code"][0]

    print("✓ Authorization code received.")
    print("✓ Sending code to Swiggy token endpoint...")

    return AuthorizationCodeResult(
        code=code,
        state=params.get("state", [None])[0],
        iss=params.get("iss", [None])[0],
    )


# ============================================================
# 5. Main Instamart connection
# ============================================================

async def main():

    print("\n========================================")
    print("   SMART REFRIGERATOR × INSTAMART")
    print("========================================")

    print("\nSwiggy MCP endpoint:")
    print(INSTAMART_URL)

    print("\nOAuth server:")
    print(OAUTH_SERVER_URL)

    # ========================================================
    # Create OAuth provider
    # ========================================================

    oauth_auth = OAuthClientProvider(

        server_url=OAUTH_SERVER_URL,

        client_metadata=OAuthClientMetadata(

            client_name="Smart Refrigerator",

            redirect_uris=[
                AnyUrl(REDIRECT_URI)
            ],

            grant_types=[
                "authorization_code",
                "refresh_token",
            ],

            response_types=[
                "code"
            ],

            scope="mcp:tools",
        ),

        storage=InMemoryTokenStorage(),

        redirect_handler=handle_redirect,

        callback_handler=handle_callback,
    )

    print("\nConnecting to Swiggy Instamart...")

    try:

        # ====================================================
        # HTTP client with OAuth
        # ====================================================

        async with httpx2.AsyncClient(
            auth=oauth_auth,
            timeout=60.0,
        ) as http_client:

            # =================================================
            # Instamart MCP transport
            # =================================================

            transport = streamable_http_client(
                INSTAMART_URL,
                http_client=http_client,
            )

            # =================================================
            # MCP client
            # =================================================

            async with Client(transport) as client:

                print("\n✓ Connected to Instamart!")

                # =================================================
                # Get available tools
                # =================================================

                result = await client.list_tools()

                print("\n========================================")
                print("      INSTAMART TOOLS AVAILABLE")
                print("========================================\n")

                for tool in result.tools:

                    print(f"✓ {tool.name}")

                print("\n========================================")
                print("       CONNECTION SUCCESSFUL 🎉")
                print("========================================")

                print("\nYou have successfully connected")
                print("your Smart Refrigerator project")
                print("to Swiggy Instamart MCP.")

                print("\nNext test:")
                print("search_products")

    except BaseException as e:

        print("\n========================================")
        print("             ERROR")
        print("========================================")

        print(f"\nException type: {type(e).__name__}")
        print(f"Exception: {e}")

        # ====================================================
        # Nested exceptions
        # ====================================================

        if isinstance(e, BaseExceptionGroup):

            print("\n========================================")
            print("       NESTED EXCEPTIONS")
            print("========================================")

            def show_exception(exc, level=0):

                indent = "  " * level

                print(
                    f"{indent}- "
                    f"{type(exc).__name__}: {exc}"
                )

                if isinstance(
                    exc,
                    BaseExceptionGroup
                ):

                    for sub in exc.exceptions:

                        show_exception(
                            sub,
                            level + 1
                        )

            show_exception(e)

        print("\n========================================")
        print("             END ERROR")
        print("========================================")


# ============================================================
# 6. Run
# ============================================================

if __name__ == "__main__":

    asyncio.run(main())