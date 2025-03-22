import asyncio
import logging

from collections import defaultdict
from typing import Callable, Coroutine, Any, Literal, TypeVar, Generic, Type
from urllib.parse import urljoin

from aiomexc import MexcClient
from .proto import (
    PushMessage,
    PublicDealsMessage,
    PublicIncreaseDepthsMessage,
    PublicLimitDepthsMessage,
    PrivateOrdersMessage,
    PublicBookTickerMessage,
    PrivateDealsMessage,
    PrivateAccountMessage,
    PublicSpotKlineMessage,
    PublicMiniTickerMessage,
    PublicMiniTickersMessage,
    PublicBookTickersBatchMessage,
    PublicIncreaseDepthsBatchMessage,
    PublicAggreDepthsMessage,
    PublicAggreDealsMessage,
    PublicAggreBookTickerMessage,
)

from .session.base import BaseWsSession
from .credentials import WSCredentials
from .dispatcher import EventType, EventDispatcher

logger = logging.getLogger(__name__)

T = TypeVar("T")


class ChannelHandler(Generic[T]):
    def __init__(
        self, handler: Callable[[T], Coroutine[Any, Any, None]], message_type: Type[T]
    ):
        self.handler = handler
        self.message_type = message_type

    async def __call__(self, msg: PushMessage) -> None:
        if msg.message is None:
            return
        if not isinstance(msg.message, self.message_type):
            return
        await self.handler(msg.message)


class WSConnection:
    CHANNEL_TYPES = {
        "spot@private.deals.v3.api.pb": PrivateDealsMessage,
        "spot@private.orders.v3.api.pb": PrivateOrdersMessage,
        "spot@private.account.v3.api.pb": PrivateAccountMessage,
        "spot@public.deals.v3.api.pb": PublicDealsMessage,
        "spot@public.increase.depths.v3.api.pb": PublicIncreaseDepthsMessage,
        "spot@public.limit.depths.v3.api.pb": PublicLimitDepthsMessage,
        "spot@public.book.ticker.v3.api.pb": PublicBookTickerMessage,
        "spot@public.kline.v3.api.pb": PublicSpotKlineMessage,
        "spot@public.mini.ticker.v3.api.pb": PublicMiniTickerMessage,
        "spot@public.mini.tickers.v3.api.pb": PublicMiniTickersMessage,
        "spot@public.book.tickers.batch.v3.api.pb": PublicBookTickersBatchMessage,
        "spot@public.increase.depths.batch.v3.api.pb": PublicIncreaseDepthsBatchMessage,
        "spot@public.aggre.depths.v3.api.pb": PublicAggreDepthsMessage,
        "spot@public.aggre.deals.v3.api.pb": PublicAggreDealsMessage,
        "spot@public.aggre.bookTicker.v3.api.pb": PublicAggreBookTickerMessage,
    }

    def __init__(
        self,
        client: MexcClient,
        session: BaseWsSession,
        credentials: WSCredentials | None = None,
        base_url: str = "wss://wbs-api.mexc.com/ws",
    ):
        self._client = client
        self._streams = []
        self._credentials = credentials
        self._is_private = credentials is not None
        self._ping_task: asyncio.Task | None = None
        self._listen_key_update_task: asyncio.Task | None = None
        self._base_url = base_url
        self._session = session

        self._events: dict[EventType, EventDispatcher] = {
            event_type: EventDispatcher(event_type) for event_type in EventType
        }

        self._channel_handlers: defaultdict[str, list[ChannelHandler]] = defaultdict(
            list
        )

    def on_connect(self, handler: Callable[[], Coroutine[Any, Any, None]]) -> None:
        self._events[EventType.CONNECT].add(handler)

    def on_listen_key_extended(
        self, handler: Callable[[WSCredentials], Coroutine[Any, Any, None]]
    ) -> None:
        self._events[EventType.LISTEN_KEY_EXTENDED].add(handler)

    def on_subscription(
        self, handler: Callable[[dict], Coroutine[Any, Any, None]]
    ) -> None:
        self._events[EventType.SUBSCRIPTION].add(handler)

    def on_disconnect(self, handler: Callable[[], Coroutine[Any, Any, None]]) -> None:
        self._events[EventType.DISCONNECT].add(handler)

    def on_message(
        self, handler: Callable[[PushMessage], Coroutine[Any, Any, None]]
    ) -> None:
        self._events[EventType.MESSAGE].add(handler)

    def on_error(
        self, handler: Callable[[Exception], Coroutine[Any, Any, None]]
    ) -> None:
        self._events[EventType.ERROR].add(handler)

    def on_pong(self, handler: Callable[[], Coroutine[Any, Any, None]]) -> None:
        self._events[EventType.PONG].add(handler)

    def _get_message_type(self, channel: str) -> Type | None:
        """Get the message type for a given channel."""
        for pattern, msg_type in self.CHANNEL_TYPES.items():
            if pattern in channel:
                return msg_type
        return None

    def _register_channel_handler(
        self,
        channel: str,
        handler: Callable[[T], Coroutine[Any, Any, None]],
        private: bool = False,
    ) -> Callable[[T], Coroutine[Any, Any, None]]:
        """Register a handler for a specific channel and add the channel to streams."""
        if len(self._streams) + 1 >= 30:
            raise ValueError(
                "MEXC WebSocket API only supports up to 30 streams per connection"
            )

        if private and not self._is_private:
            raise ValueError(
                "Cannot register private channel handler for public connection"
            )

        message_type = self._get_message_type(channel)
        if message_type is None:
            raise ValueError(f"Unknown channel type: {channel}")

        self._streams.append(channel)
        self._channel_handlers[channel].append(ChannelHandler(handler, message_type))
        return handler

    def aggre_deals(self, symbol: str, interval: Literal["10ms", "100ms"]):
        def decorator(
            handler: Callable[[PublicAggreDealsMessage], Coroutine[Any, Any, None]],
        ) -> Callable[[PublicAggreDealsMessage], Coroutine[Any, Any, None]]:
            channel = f"spot@public.aggre.deals.v3.api.pb@{interval}@{symbol}"
            return self._register_channel_handler(channel, handler)

        return decorator

    def kline(
        self,
        symbol: str,
        interval: Literal[
            "Min1",
            "Min5",
            "Min15",
            "Min30",
            "Min60",
            "Hour4",
            "Hour8",
            "Day1",
            "Week1",
            "Month1",
        ],
    ):
        def decorator(
            handler: Callable[[PublicSpotKlineMessage], Coroutine[Any, Any, None]],
        ) -> Callable[[PublicSpotKlineMessage], Coroutine[Any, Any, None]]:
            channel = f"spot@public.kline.v3.api.pb@{symbol}@{interval}"
            return self._register_channel_handler(channel, handler)

        return decorator

    def aggre_depth(self, symbol: str, interval: Literal["100ms", "10ms"]):
        def decorator(
            handler: Callable[[PublicAggreDepthsMessage], Coroutine[Any, Any, None]],
        ) -> Callable[[PublicAggreDepthsMessage], Coroutine[Any, Any, None]]:
            channel = f"spot@public.aggre.depth.v3.api.pb@{interval}@{symbol}"
            return self._register_channel_handler(channel, handler)

        return decorator

    def increase_depth_batch(self, symbol: str):
        def decorator(
            handler: Callable[
                [PublicIncreaseDepthsBatchMessage], Coroutine[Any, Any, None]
            ],
        ) -> Callable[[PublicIncreaseDepthsBatchMessage], Coroutine[Any, Any, None]]:
            channel = f"spot@public.increase.depth.batch.v3.api.pb@{symbol}"
            return self._register_channel_handler(channel, handler)

        return decorator

    def limit_depth(self, symbol: str, depth: Literal["5", "10", "20"]):
        def decorator(
            handler: Callable[[PublicLimitDepthsMessage], Coroutine[Any, Any, None]],
        ) -> Callable[[PublicLimitDepthsMessage], Coroutine[Any, Any, None]]:
            channel = f"spot@public.limit.depth.v3.api.pb@{symbol}@{depth}"
            return self._register_channel_handler(channel, handler)

        return decorator

    def aggre_book_ticker(self, symbol: str, interval: Literal["100ms", "10ms"]):
        def decorator(
            handler: Callable[
                [PublicAggreBookTickerMessage], Coroutine[Any, Any, None]
            ],
        ) -> Callable[[PublicAggreBookTickerMessage], Coroutine[Any, Any, None]]:
            channel = f"spot@public.aggre.bookTicker.v3.api.pb@{interval}@{symbol}"
            return self._register_channel_handler(channel, handler)

        return decorator

    def book_ticker_batch(self, symbol: str):
        def decorator(
            handler: Callable[
                [PublicBookTickersBatchMessage], Coroutine[Any, Any, None]
            ],
        ) -> Callable[[PublicBookTickersBatchMessage], Coroutine[Any, Any, None]]:
            channel = f"spot@public.bookTicker.batch.v3.api.pb@{symbol}"
            return self._register_channel_handler(channel, handler)

        return decorator

    def account_balance(self):
        def decorator(
            handler: Callable[[PrivateAccountMessage], Coroutine[Any, Any, None]],
        ) -> Callable[[PrivateAccountMessage], Coroutine[Any, Any, None]]:
            channel = "spot@private.account.v3.api.pb"
            return self._register_channel_handler(channel, handler, private=True)

        return decorator

    def private_deals(self):
        def decorator(
            handler: Callable[[PrivateDealsMessage], Coroutine[Any, Any, None]],
        ) -> Callable[[PrivateDealsMessage], Coroutine[Any, Any, None]]:
            channel = "spot@private.deals.v3.api.pb"
            return self._register_channel_handler(channel, handler, private=True)

        return decorator

    def private_orders(self):
        def decorator(
            handler: Callable[[PrivateOrdersMessage], Coroutine[Any, Any, None]],
        ) -> Callable[[PrivateOrdersMessage], Coroutine[Any, Any, None]]:
            channel = "spot@private.orders.v3.api.pb"
            return self._register_channel_handler(channel, handler, private=True)

        return decorator

    async def _trigger_event(self, event: EventType, *args: Any) -> None:
        """Trigger handlers for a specific event."""
        await self._events[event].trigger(*args)

        # If this isn't an error event, and there was an exception, trigger error handlers
        if event != EventType.ERROR and args and isinstance(args[0], Exception):
            await self._trigger_event(EventType.ERROR, args[0])

    async def _trigger_channel_handlers(
        self, channel: str, message: PushMessage
    ) -> None:
        for handler in self._channel_handlers.get(channel, []):
            try:
                await handler(message)
            except Exception as e:
                logger.exception(f"Error in channel handler for {channel}: {e}")
                await self._trigger_event(EventType.ERROR, e)

    def is_sub_message(self, message: dict) -> bool:
        if messages := message.get("msg"):
            return all(param in self._streams for param in messages.split(","))
        return False

    def is_pong_message(self, message: dict) -> bool:
        return message.get("msg") == "PONG"

    async def send_keepalive_ping(self):
        """
        Function to send keepalive ping every 30 seconds
        30 seconds is recommended by MEXC API docs: https://mexcdevelop.github.io/apidocs/spot_v3_en/#websocket-market-streams
        """
        while True:
            await asyncio.sleep(30)
            await self._session.ping()
            logger.debug("Keepalive ping sent")

    async def keepalivate_extend_listen_key(self):
        """
        Function to update listen key every 30 minutes
        30 minutes is recommended by MEXC API docs: https://mexcdevelop.github.io/apidocs/spot_v3_en/#listen-key
        """
        if self._credentials is None or self._credentials.listen_key is None:
            raise RuntimeError("No credentials provided, cannot extend listen key")

        while True:
            await asyncio.sleep(1800)
            response = await self._client.extend_listen_key(
                credentials=self._credentials, listen_key=self._credentials.listen_key
            )
            self._credentials.update(response.listen_key)
            await self._trigger_event(EventType.LISTEN_KEY_EXTENDED, self._credentials)
            logger.debug("Listen key extended")

    async def get_listen_key(self) -> str | None:
        """
        Get listen key for subscription to private streams
        If listen key is not provided, it will be created, else extended
        """
        if self._credentials is None:
            raise RuntimeError("No credentials provided, cannot get listen key")

        if self._credentials.is_expired():
            response = await self._client.create_listen_key(
                credentials=self._credentials
            )
            self._credentials.update(response.listen_key)

        elif self._credentials.listen_key is not None:
            response = await self._client.extend_listen_key(
                credentials=self._credentials, listen_key=self._credentials.listen_key
            )
            self._credentials.update(response.listen_key)
            await self._trigger_event(EventType.LISTEN_KEY_EXTENDED, self._credentials)

        return self._credentials.listen_key

    async def connect(self):
        """
        Connect to MEXC WebSocket Server and subscribe to streams
        If this is private connection, connections will be created with listen key
        """
        if len(self._streams) == 0:
            raise ValueError("No streams provided, connection will be useless!")

        try:
            url = self._base_url
            if self._is_private:
                listen_key = await self.get_listen_key()
                url = urljoin(url, f"?listenKey={listen_key}")

            await self._session.connect(url)
            await self._session.subscribe(self._streams)

            self._ping_task = asyncio.create_task(self.send_keepalive_ping())
            if self._is_private:
                self._listen_key_update_task = asyncio.create_task(
                    self.keepalivate_extend_listen_key()
                )

            await self._trigger_event(EventType.CONNECT)
        except Exception as e:
            await self._trigger_event(EventType.ERROR, e)
            raise

    async def receive(self):
        while True:
            try:
                msg = await self._session.receive()
                if isinstance(msg, PushMessage):
                    await self._trigger_channel_handlers(msg.channel, msg)
                else:
                    if self.is_sub_message(msg):
                        await self._trigger_event(EventType.SUBSCRIPTION, msg)
                    elif self.is_pong_message(msg):
                        await self._trigger_event(EventType.PONG)

            except Exception as e:
                await self._trigger_event(EventType.ERROR, e)
                raise

    async def start_listening(self):
        await self.connect()
        await self.receive()

    async def close(self):
        try:
            await self._session.close()
            await self._trigger_event(EventType.DISCONNECT)
        except Exception as e:
            await self._trigger_event(EventType.ERROR, e)
            raise
