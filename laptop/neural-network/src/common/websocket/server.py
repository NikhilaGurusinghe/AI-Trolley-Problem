import asyncio
import json
from asyncio import Event
from typing import Callable, Any

from websockets.asyncio.server import serve, ServerConnection


class Server:
    def __init__(self, host_name: str, port_number: int, allowed_methods: dict[str, Callable[..., str]]):
        self.host_name: str = host_name
        self.port_number: int = port_number
        self.allowed_methods: dict[str, Callable[..., str]] = allowed_methods
        self.websocket: ServerConnection | None = None
        self._websocket_is_ready: Event = Event()

    async def _receive(self, websocket: ServerConnection) -> None:
        if self.websocket is None:
            self.websocket = websocket
            self._websocket_is_ready.set()

        # TODO need to reconnect here or something
        if self.websocket.id is not websocket.id:
            raise ConnectionError("Server#_receive(): connection was severed")

        async for message in websocket:
            print(message)
            message_json = json.loads(message)
            message_type = message_json.get("type")
            message_id = message_json.get("id")
            message_method = message_json.get("method")
            arguments = message_json.get("arguments", [])

            # anything else here is currently unsupported :)
            if message_type != "request":
                continue

            print(message_type, message_id, message_method, arguments)

            if message_method not in self.allowed_methods:
                response: dict[str, Any] = {"type": "response", "id": message_id, "error": "invalid method" }
                await self._send(response)

            if not isinstance(arguments, list):
                response: dict[str, Any] = { "type": "response", "id": message_id, "error": "invalid arguments" }
                await self._send(response)

            try:
                responsePayload = self.allowed_methods[message_method](*arguments)
                response: dict[str, Any] = { "type": "response", "id": message_id, "payload": responsePayload }
            except Exception as e:
                print(e.__str__())
                response: dict[str, Any] = { "type": "response", "id": message_id, "error": "internal server error" }

            await self._send(response)

    async def _send(self, message: dict[str, Any]):
        await self._websocket_is_ready.wait()
        assert self.websocket is not None

        await self.websocket.send(json.dumps(message))

    async def send_notification(self, request_method: str, request_arguments: list[Any] = None):
        await self._websocket_is_ready.wait()
        assert self.websocket is not None

        await self.websocket.send(json.dumps(
            {"type": "notification", "method": request_method } if request_arguments is None else
            { "type": "notification", "method": request_method, "arguments": request_arguments }
        ))

    async def loop(self) -> None:
        async with serve(self._receive, self.host_name, self.port_number) as server:
            await server.serve_forever()