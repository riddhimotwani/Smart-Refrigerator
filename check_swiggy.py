import asyncio
import httpx2


async def main():

    urls = [
        "https://mcp.swiggy.com/.well-known/oauth-protected-resource",
    "https://mcp.swiggy.com/.well-known/oauth-protected-resource/im",
    "https://mcp.swiggy.com/.well-known/oauth-authorization-server",
    ]

    async with httpx2.AsyncClient(timeout=30.0) as client:

        for url in urls:

            print("\n" + "=" * 60)
            print("TESTING:")
            print(url)
            print("=" * 60)

            try:

                response = await client.get(url)

                print("STATUS:", response.status_code)

                print("\nIMPORTANT HEADERS:")

                for key, value in response.headers.items():

                    if key.lower() in [
                        "retry-after",
                        "content-type",
                        "x-ratelimit-limit",
                        "x-ratelimit-remaining",
                    ]:
                        print(f"  {key}: {value}")

                print("\nRESPONSE:")

                print(response.text[:2000])

            except Exception as e:

                print(
                    "ERROR:",
                    type(e).__name__,
                    e
                )


if __name__ == "__main__":
    asyncio.run(main())