from aiohttp import ClientSession, ClientWebSocketResponse, WSMsgType

from aiomexc.ws.messages import PING, subscription
from aiomexc.ws.proto import PushMessage

from .base import BaseWsSession


class AiohttpWsSession(BaseWsSession):
    def __init__(
        self,
        session: ClientSession,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.http_session = session
        self.ws_session: ClientWebSocketResponse | None = None

    async def connect(self, url: str) -> None:
        if self.ws_session is not None and not self.ws_session.closed:
            return

        self.ws_session = await self.http_session.ws_connect(
            url,
            autoping=False,
            autoclose=True,
        )

    async def subscribe(self, streams: list[str]) -> None:
        if self.ws_session is None or self.ws_session.closed:
            raise RuntimeError("WebSocket session not connected")

        await self.ws_session.send_str(self.dump_message(subscription(streams)))

    async def receive(self) -> PushMessage | dict:
        if self.ws_session is None or self.ws_session.closed:
            raise RuntimeError("WebSocket session not connected")

        msg = await self.ws_session.receive()

        if msg.type == WSMsgType.TEXT:
            return self.load_json_message(msg.data)

        elif msg.type == WSMsgType.BINARY:
            return self.load_message(msg.data)

        elif msg.type == WSMsgType.CLOSE:
            raise RuntimeError("WebSocket closed")

        raise RuntimeError(f"Unknown message type: {msg.type}")

    async def ping(self) -> None:
        if self.ws_session is None or self.ws_session.closed:
            raise RuntimeError("WebSocket session not connected")

        await self.ws_session.send_str(PING)

    async def close(self) -> None:
        if self.ws_session is None or self.ws_session.closed:
            raise RuntimeError("WebSocket session not connected")

        await self.ws_session.close()
