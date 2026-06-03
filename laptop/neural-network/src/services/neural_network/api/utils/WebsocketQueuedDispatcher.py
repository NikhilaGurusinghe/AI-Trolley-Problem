import asyncio

from services.neural_network.api.NeuralNetworkServer import NeuralNetworkServer


class WebsocketQueuedDispatcher:
    def __init__(self):
        self.event_queue = asyncio.Queue()

    async def websocket_dispatcher(self, server: NeuralNetworkServer):
        while True:
            event, payload = await self.event_queue.get()
            if event == "setNetworkStructure":
                print(event, payload)
                await server.send_notification("setNetworkStructure",
                                               [server.get_network_structure(payload["network_type"]),
                                                payload["network_type"]])
