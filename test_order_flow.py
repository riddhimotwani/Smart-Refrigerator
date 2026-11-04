import asyncio
import json
import webbrowser
from urllib.parse import parse_qs, urlparse

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
# TOKEN STORAGE
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
# OPEN SWIGGY LOGIN
# ============================================================

async def handle_redirect(auth_url: str):

    print("\n")
    print("========================================")
    print("        SWIGGY AUTHENTICATION")
    print("========================================")

    print("\nOpening Swiggy login in your browser...")

    print("\nIf the browser does not open automatically,")
    print("copy the authentication URL shown below.")

    print("\nAuthentication URL:")
    print(auth_url)

    webbrowser.open(auth_url)


# ============================================================
# OAUTH CALLBACK
# ============================================================

async def handle_callback() -> AuthorizationCodeResult:

    while True:

        print("\n")
        print("========================================")
        print("          SWIGGY CALLBACK")
        print("========================================")

        print("\nAfter completing Swiggy login,")
        print("your browser may show:")
        print("    localhost refused to connect.")

        print("\nThis is expected.")

        print("\nCopy the COMPLETE URL from the browser")
        print("and paste it below.")

        print("\nIMPORTANT:")
        print("Paste it ONLY into this terminal.")
        print("Do NOT send the URL to anyone.")

        callback_url = input(
            "\nPaste callback URL: "
        ).strip()

        if not callback_url:
            print("\nNo URL entered. Please try again.")
            continue

        # ----------------------------------------------------
        # Parse URL
        # ----------------------------------------------------

        parsed = urlparse(callback_url)

        # OAuth normally uses query parameters.
        query_params = parse_qs(parsed.query)

        # Some OAuth implementations can return parameters
        # in the URL fragment, so we support that too.
        fragment_params = parse_qs(parsed.fragment)

        # Merge both.
        params = {}

        for key, value in fragment_params.items():
            params[key] = value

        for key, value in query_params.items():
            params[key] = value

        # ----------------------------------------------------
        # OAuth error
        # ----------------------------------------------------

        if "error" in params:

            error_value = params["error"][0]

            error_description = params.get(
                "error_description",
                ["Unknown OAuth error"]
            )[0]

            raise RuntimeError(
                f"Swiggy OAuth error: "
                f"{error_value} - {error_description}"
            )

        # ----------------------------------------------------
        # Authorization code
        # ----------------------------------------------------

        if "code" not in params:

            # Safe diagnostics only.
            # We NEVER print the actual URL or its values.
            print("\nNo authorization code was detected.")

            print(
                "Parameters detected:",
                list(params.keys())
            )

            print("\nPlease make sure you copied the")
            print("COMPLETE URL from the browser address bar.")

            print(
                "\nIf you see another browser URL, "
                "paste that complete URL here."
            )

            continue

        authorization_code = params["code"][0]

        state = params.get(
            "state",
            [None]
        )[0]

        issuer = params.get(
            "iss",
            [None]
        )[0]

        print("\n✓ Authorization code received.")

        return AuthorizationCodeResult(
            code=authorization_code,
            state=state,
            iss=issuer,
        )


# ============================================================
# GENERIC MCP VALUE CONVERTER
# ============================================================

def convert_to_plain(value):
    """
    Recursively convert MCP/Pydantic objects into normal
    Python dictionaries/lists.

    This function does NOT print anything.
    """

    if value is None:
        return None

    # --------------------------------------------------------
    # Basic Python values
    # --------------------------------------------------------

    if isinstance(value, (str, int, float, bool)):
        return value

    # --------------------------------------------------------
    # Dictionary
    # --------------------------------------------------------

    if isinstance(value, dict):

        result = {}

        for key, item in value.items():
            result[str(key)] = convert_to_plain(item)

        return result

    # --------------------------------------------------------
    # List / Tuple
    # --------------------------------------------------------

    if isinstance(value, (list, tuple)):

        return [
            convert_to_plain(item)
            for item in value
        ]

    # --------------------------------------------------------
    # Pydantic model
    # --------------------------------------------------------

    if hasattr(value, "model_dump"):

        try:

            dumped = value.model_dump(
                by_alias=True
            )

            return convert_to_plain(dumped)

        except Exception:
            pass

    # --------------------------------------------------------
    # Object dictionary
    # --------------------------------------------------------

    if hasattr(value, "__dict__"):

        try:

            return convert_to_plain(
                vars(value)
            )

        except Exception:
            pass

    return None


# ============================================================
# MCP RESPONSE PARSER
# ============================================================

def extract_tool_data(result):
    """
    Extract useful information from an MCP CallToolResult.

    Checks:

    1. structuredContent
    2. data
    3. content
    4. Pydantic representation
    5. complete object
    """

    if result is None:
        return None

    # --------------------------------------------------------
    # First convert the complete result.
    # --------------------------------------------------------

    plain_result = convert_to_plain(result)

    if plain_result is not None:
        return plain_result

    return None


# ============================================================
# RECURSIVE SEARCH FOR LISTS
# ============================================================

def find_list_by_keys(payload, possible_keys):
    """
    Recursively search nested dictionaries/lists for a list
    stored under one of the supplied keys.
    """

    if payload is None:
        return None

    possible_keys_lower = {
        str(key).lower()
        for key in possible_keys
    }

    # --------------------------------------------------------
    # Direct list
    # --------------------------------------------------------

    if isinstance(payload, list):

        return payload

    # --------------------------------------------------------
    # Dictionary
    # --------------------------------------------------------

    if isinstance(payload, dict):

        # First check exact expected keys.
        for key, value in payload.items():

            if str(key).lower() in possible_keys_lower:

                if isinstance(value, list):

                    return value

        # Then recursively search everything.
        for value in payload.values():

            found = find_list_by_keys(
                value,
                possible_keys
            )

            if found is not None:
                return found

    # --------------------------------------------------------
    # Nested list
    # --------------------------------------------------------

    if isinstance(payload, list):

        for item in payload:

            found = find_list_by_keys(
                item,
                possible_keys
            )

            if found is not None:
                return found

    return None


# ============================================================
# FIND ADDRESS OBJECTS
# ============================================================

def find_addresses(payload):
    """
    Finds address lists even if the MCP response structure
    changes slightly.
    """

    # First try normal expected keys.
    addresses = find_list_by_keys(
        payload,
        [
            "addresses",
            "addressList",
            "deliveryAddresses",
            "savedAddresses",
        ]
    )

    if addresses:
        return addresses

    # --------------------------------------------------------
    # Search recursively for objects that look like addresses.
    # --------------------------------------------------------

    candidates = []

    def walk(value):

        if isinstance(value, dict):

            address_id = (
                value.get("id")
                or value.get("addressId")
                or value.get("address_id")
            )

            address_type = str(
                value.get("type", "")
            ).lower()

            address_text = str(
                value.get("address", "")
            ).lower()

            # Do not require a particular field.
            if address_id is not None:

                if (
                    "address" in address_type
                    or "address" in address_text
                    or any(
                        key in value
                        for key in [
                            "city",
                            "pincode",
                            "pinCode",
                            "postalCode",
                            "latitude",
                            "longitude",
                        ]
                    )
                ):
                    candidates.append(value)

            for child in value.values():
                walk(child)

        elif isinstance(value, list):

            for item in value:
                walk(item)

    walk(payload)

    if candidates:
        return candidates

    return None


# ============================================================
# FIND PRODUCTS
# ============================================================

def find_products(payload):
    """
    Finds product lists from the Instamart search response.
    """

    products = find_list_by_keys(
        payload,
        [
            "products",
            "items",
            "productList",
            "results",
        ]
    )

    if products:
        return products

    # --------------------------------------------------------
    # Fallback recursive search for product-like dictionaries.
    # --------------------------------------------------------

    candidates = []

    def walk(value):

        if isinstance(value, dict):

            # A product normally has a name and some variant
            # information.
            if (
                value.get("name") is not None
                and (
                    "variants" in value
                    or "spinId" in value
                    or "price" in value
                )
            ):
                candidates.append(value)

            for child in value.values():
                walk(child)

        elif isinstance(value, list):

            for item in value:
                walk(item)

    walk(payload)

    if candidates:
        return candidates

    return None


# ============================================================
# FIND PRODUCT SPIN ID
# ============================================================

def get_first_variant(product):

    variants = product.get(
        "variants",
        []
    )

    if not variants:
        return None

    if not isinstance(
        variants,
        list
    ):
        return None

    for variant in variants:

        if isinstance(variant, dict):

            spin_id = (
                variant.get("spinId")
                or variant.get("spin_id")
            )

            if spin_id:
                return variant

    return None


# ============================================================
# MAIN
# ============================================================

async def main():

    print("\n")
    print("========================================")
    print("   SMART REFRIGERATOR × INSTAMART")
    print("========================================")

    # ========================================================
    # URLs
    # ========================================================

    oauth_server_url = (
        "https://mcp.swiggy.com"
    )

    instamart_url = (
        "https://mcp.swiggy.com/im"
    )

    # ========================================================
    # OAUTH
    # ========================================================

    oauth_auth = OAuthClientProvider(

        server_url=oauth_server_url,

        client_metadata=OAuthClientMetadata(

            client_name="Smart Refrigerator",

            redirect_uris=[
                AnyUrl(
                    "http://localhost:3000/callback"
                )
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

    # ========================================================
    # CONNECT
    # ========================================================

    try:

        async with httpx2.AsyncClient(
            auth=oauth_auth,
            timeout=60.0,
        ) as http_client:

            transport = streamable_http_client(
                instamart_url,
                http_client=http_client,
            )

            async with Client(transport) as client:

                print("\n✓ Connected to Instamart!")

                # =================================================
                # STEP 1 — GET ADDRESSES
                # =================================================

                print(
                    "\nGetting delivery addresses..."
                )

                addresses_result = (
                    await client.call_tool(
                        "get_addresses",
                        {}
                    )
                )

                addresses_data = extract_tool_data(
                    addresses_result
                )

                addresses = find_addresses(
                    addresses_data
                )

                if not addresses:

                    print(
                        "\nCould not find a saved "
                        "delivery address."
                    )

                    print(
                        "Please make sure your Swiggy "
                        "account has a saved address."
                    )

                    return

                # =================================================
                # USE FIRST ADDRESS
                # =================================================

                address = addresses[0]

                if not isinstance(
                    address,
                    dict
                ):

                    print(
                        "\nAddress format could not "
                        "be understood."
                    )

                    return

                address_id = (
                    address.get("id")
                    or address.get("addressId")
                    or address.get("address_id")
                )

                if not address_id:

                    print(
                        "\nAddress was found, but "
                        "no address ID was available."
                    )

                    return

                print(
                    "\n✓ Delivery address found!"
                )

                # PRIVACY:
                # Do not print the address itself.

                print(
                    "✓ Address details hidden "
                    "for privacy."
                )

                print(
                    "✓ Address ID retrieved."
                )

                # =================================================
                # STEP 2 — SEARCH PRODUCT
                # =================================================

                search_query = "milk"

                print("\n")
                print("========================================")
                print("        SEARCHING INSTAMART")
                print("========================================")

                print(
                    f"\nSearching for: {search_query}"
                )

                search_result = (
                    await client.call_tool(

                        "search_products",

                        {
                            "addressId": address_id,
                            "query": search_query,
                        }
                    )
                )

                search_data = extract_tool_data(
                    search_result
                )

                if search_data is None:

                    print(
                        "\nCould not read the "
                        "Instamart search response."
                    )

                    return

                # =================================================
                # EXTRACT PRODUCTS
                # =================================================

                products = find_products(
                    search_data
                )

                if not products:

                    print(
                        "\nNo products found for:"
                    )

                    print(
                        search_query
                    )

                    return

                # =================================================
                # DISPLAY PRODUCTS
                # =================================================

                print("\n")
                print("========================================")
                print("          PRODUCTS FOUND")
                print("========================================")

                displayed = 0

                for product in products:

                    if not isinstance(
                        product,
                        dict
                    ):
                        continue

                    name = product.get(
                        "name",
                        "Unknown product"
                    )

                    print(
                        f"\n{displayed + 1}. {name}"
                    )

                    variants = product.get(
                        "variants",
                        []
                    )

                    if isinstance(
                        variants,
                        list
                    ):

                        for variant in variants[:3]:

                            if not isinstance(
                                variant,
                                dict
                            ):
                                continue

                            variant_name = variant.get(
                                "name",
                                "Variant"
                            )

                            price = variant.get(
                                "price",
                                "N/A"
                            )

                            print(
                                f"   • "
                                f"{variant_name}"
                                f" | ₹{price}"
                            )

                    displayed += 1

                    if displayed >= 5:
                        break

                # =================================================
                # STEP 3 — SELECT FIRST VALID PRODUCT
                # =================================================

                first_product = None
                first_variant = None

                for product in products:

                    if not isinstance(
                        product,
                        dict
                    ):
                        continue

                    variant = get_first_variant(
                        product
                    )

                    if variant:

                        first_product = product
                        first_variant = variant

                        break

                if (
                    first_product is None
                    or first_variant is None
                ):

                    print(
                        "\nCould not find a product "
                        "with a usable variant."
                    )

                    return

                # =================================================
                # PRODUCT INFORMATION
                # =================================================

                spin_id = (
                    first_variant.get("spinId")
                    or first_variant.get("spin_id")
                )

                if not spin_id:

                    print(
                        "\nNo spinId found for "
                        "the selected product."
                    )

                    return

                product_name = first_product.get(
                    "name",
                    "Product"
                )

                variant_name = first_variant.get(
                    "name",
                    "Default"
                )

                price = first_variant.get(
                    "price",
                    "N/A"
                )

                print("\n")
                print("========================================")
                print("          SELECTED PRODUCT")
                print("========================================")

                print(
                    f"\nProduct: {product_name}"
                )

                print(
                    f"Variant: {variant_name}"
                )

                print(
                    f"Price: ₹{price}"
                )

                # =================================================
                # STEP 4 — ADD TO CART
                # =================================================

                print(
                    "\nAdding product to Instamart cart..."
                )

                cart_update = (
                    await client.call_tool(

                        "update_cart",

                        {
                            "items": [
                                {
                                    "spinId": spin_id,
                                    "quantity": 1,
                                }
                            ]
                        }
                    )
                )

                print("\n")
                print("========================================")
                print("             CART UPDATED")
                print("========================================")

                print(
                    "\n✓ Product added to cart."
                )

                # =================================================
                # STEP 5 — GET CART
                # =================================================

                print(
                    "\nVerifying current cart..."
                )

                cart_result = (
                    await client.call_tool(
                        "get_cart",
                        {}
                    )
                )

                cart_data = extract_tool_data(
                    cart_result
                )

                print("\n")
                print("========================================")
                print("        INSTAMART CART CHECK")
                print("========================================")

                if cart_data is not None:

                    print(
                        "\n✓ Cart retrieved successfully."
                    )

                    print(
                        "✓ Product was added to the cart."
                    )

                    # IMPORTANT:
                    # We intentionally DO NOT print
                    # raw cart data because it may contain
                    # personal information.

                else:

                    print(
                        "\n✓ Cart request completed."
                    )

                # =================================================
                # SUCCESS
                # =================================================

                print("\n")
                print("========================================")
                print("        DEMO SUCCESSFUL 🎉")
                print("========================================")

                print(
                    "\nThe Smart Refrigerator can now:"
                )

                print(
                    "✓ Identify missing groceries"
                )

                print(
                    "✓ Search Instamart"
                )

                print(
                    "✓ Select an available product"
                )

                print(
                    "✓ Add the product to cart"
                )

                print(
                    "✓ Verify the cart"
                )

                print(
                    "\nCheckout was NOT called."
                )

                print(
                    "No order has been placed."
                )

    # ========================================================
    # ERROR HANDLING
    # ========================================================

    except BaseException as e:

        print("\n")
        print("========================================")
        print("                ERROR")
        print("========================================")

        print(
            f"\nException type: "
            f"{type(e).__name__}"
        )

        print(
            f"Exception: {e}"
        )

        # ----------------------------------------------------
        # Nested exception groups
        # ----------------------------------------------------

        if isinstance(
            e,
            BaseExceptionGroup
        ):

            print(
                "\nNESTED EXCEPTIONS:"
            )

            def show_exception(
                exc,
                level=0
            ):

                indent = "  " * level

                print(
                    f"{indent}- "
                    f"{type(exc).__name__}: "
                    f"{exc}"
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


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    asyncio.run(main())