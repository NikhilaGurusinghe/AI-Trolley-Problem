import json
from typing import Callable, Any

from websockets.asyncio.server import serve

class Server:
    def __init__(self, host_name: str, port_number: int, allowed_methods: dict[str, Callable[..., str]]):
        self.host_name: str = host_name
        self.port_number: int = port_number
        self.allowed_methods: dict[str, Callable[..., str]] = allowed_methods

    async def _receive(self, websocket) -> None:
        async for message in websocket:
            print(message)
            message_json = json.loads(message)
            message_id = message_json.get("id")
            message_type = message_json.get("type")
            arguments = message_json.get("arguments", [])

            print(message_id, message_type, arguments)

            if message_type not in self.allowed_methods:
                response: dict[str, Any] = { "id": message_id, "error": "invalid request type" }
                await self._send(websocket, response)

            if not isinstance(arguments, list):
                response: dict[str, Any] = { "id": message_id, "error": "invalid arguments" }
                await self._send(websocket, response)

            try:
                responsePayload = self.allowed_methods[message_type](*arguments)
                response: dict[str, Any] = { "id": message_id, "payload": responsePayload }
            except Exception as e:
                print(e.__str__())
                response: dict[str, Any] = { "id": message_id, "error": "internal server error" }

            await self._send(websocket, response)

    async def _send(self, websocket, message: dict[str, Any]):
        await websocket.send(json.dumps(message))

    async def loop(self) -> None:
        async with serve(self._receive, self.host_name, self.port_number) as server:
            await server.serve_forever()