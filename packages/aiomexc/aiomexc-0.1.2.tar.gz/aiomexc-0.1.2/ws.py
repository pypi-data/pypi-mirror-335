import logging
import asyncio

from functools import partial
from aiohttp import ClientSession

from aiomexc import MexcClient
from aiomexc.ws.credentials import WSCredentials
from aiomexc.ws.connection import WSConnection
from aiomexc.ws.session.aiohttp import AiohttpWsSession
from aiomexc.ws.proto import PublicAggreDealsMessage

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

async def main():
    credentials = WSCredentials(
        access_key="mx0vglPOFUtoYJriFO",
        secret_key="03d5fee67c884e139f573ea835832d54",
        listen_key="09f722553700bfa11f16926930d8f1862b6a41589e8af92214982810a29e136e",
        expires_at=999999999999
    )

    client = MexcClient(credentials=credentials)

    connection = WSConnection(
        client=client,
        # streams=["spot@public.aggre.deals.v3.api.pb@10ms@KASUSDT"],
        session=AiohttpWsSession(session=ClientSession()),
        credentials=credentials,
    )

    async def listen_key_extended(credentials: WSCredentials, user_id: int):
        print("listen key extended", credentials, user_id)

    connection.on_listen_key_extended(partial(listen_key_extended, user_id=123))

    @connection.on_subscription()
    async def successful_connection(msg: dict):
        print("subscription", msg)

    @connection.aggre_deals("KASUSDT")
    async def message(msg: PublicAggreDealsMessage):
        pass
        # print("aggre_deals_channel", msg)

    await connection.start_listening()
    await connection.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Keyboard interrupt")
