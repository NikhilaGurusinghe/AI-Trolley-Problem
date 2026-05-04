from websockets.asyncio.server import serve

websocket_port = 8001

# TODO access API
#   - configuration (layers, # of in each layer neurons, weights/linkages)
#   - intermediary representation images
#   -

async def handler(websocket):
    async for message in websocket:
        print(message)

async def main():
    async with serve(handler, "", websocket_port) as server:
        await server.serve_forever()