import asyncio
import os
import time

from .scanner import Scanner, AsyncScanner


def query_example():
    # Create Scanner client
    scanner = Scanner(
        api_url=os.environ["SCANNER_API_URL"],
        api_key=os.environ["SCANNER_API_KEY"],
    )

    # Start query
    qr_id = scanner.query.start_query(
        query_text="* | count",
        start_time="2024-04-05T23:47:11.575Z",
        end_time="2024-04-06T00:02:11.575Z",
    ).qr_id

    # Check query progress
    while True:
        print("Checking query progress")
        query_progress = scanner.query.query_progress(qr_id)
        if query_progress.is_completed:
            print(query_progress.results)
            break

        time.sleep(1)

    # Run blocking query
    response = scanner.query.blocking_query(
        query_text="* | count",
        start_time="2024-04-05T23:47:11.575Z",
        end_time="2024-04-06T00:02:11.575Z",
    )
    print(response.results)


async def async_query_example():
    # Create AsyncScanner client
    scanner = AsyncScanner(
        api_url=os.environ["SCANNER_API_URL"],
        api_key=os.environ["SCANNER_API_KEY"],
    )

    # Start query
    qr_id = (await scanner.query.start_query(
        query_text="* | count",
        start_time="2024-04-05T23:47:11.575Z",
        end_time="2024-04-06T00:02:11.575Z",
    )).qr_id

    # Check query progress
    while True:
        print("Checking query progress")
        query_progress = await scanner.query.query_progress(qr_id)
        if query_progress.is_completed:
            print(query_progress.results)
            break

        time.sleep(1)

    # Run blocking query
    response = await scanner.query.blocking_query(
        query_text="* | count",
        start_time="2024-04-05T23:47:11.575Z",
        end_time="2024-04-06T00:02:11.575Z",
    )
    print(response.results)


#query_example()
asyncio.run(async_query_example())
