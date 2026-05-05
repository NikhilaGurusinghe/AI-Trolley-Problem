import json

from websockets.asyncio.server import serve

# TODO access API
#   - configuration (layers, # of in each layer neurons, weights/linkages)
#   - intermediary representation images
#   -
class Server:
    def __init__(self, host_name: str, port_number: int):
        self.host_name = host_name
        self.port_number = port_number

    async def receive(self, websocket):
        async for message in websocket:
            print(message)
            # TODO get responseID from message and send this back with response
            message_json = json.loads(message)
            print(message_json)
            print(message_json["id"])
            print(message_json["type"])
            print()

            # TODO do stuff here

            response = {
                "id": message_json["id"],
                "payload": "hello I am a payload",
            }
            await websocket.send(json.dumps(response))

    async def loop(self):
        async with serve(self.receive, self.host_name, self.port_number) as server:
            await server.serve_forever()