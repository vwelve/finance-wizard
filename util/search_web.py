import aiohttp

import os


async def search_web(prompt):
    data = {
        "model": "wp-watt-3.52-16k",
        "content": prompt
    }
    headers = {
        "Authorization": f"Bearer {os.getenv('WATT_API_KEY')}",
    }

    print(f"Making a call to WATT_API with prompt: {prompt}")

    async with aiohttp.ClientSession() as session:
        rsp = await session.post(
            "https://beta.webpilotai.com/api/v1/watt/",
            headers=headers,
            json=data
        )

    content = (await rsp.json())

    return content["content"]