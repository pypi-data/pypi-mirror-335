import asyncio
import json

from aiohttp import ClientSession\

async def main():
    session = ClientSession()
    ws = await session.ws_connect("wss://wbs-api.mexc.com/ws")
    await ws.send_str(json.dumps({ "method": "SUBSCRIPTION", "params": ["spot@public.deals.v3.api.pb@TRXUSDT"] }))
    msg = await ws.receive()
    print(msg)

if __name__ == "__main__":
    asyncio.run(main())
