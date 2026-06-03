import asyncio
from typing import Any

from services.neural_network.api.NeuralNetworkServer import NeuralNetworkServer


class WebsocketQueuedDispatcher:
    def __init__(self):
        self.event_queue = asyncio.Queue()

    async def websocket_dispatcher(self, server: NeuralNetworkServer):
        while True:
            event, payload = await self.event_queue.get()
            print(event, payload)

            if event == "setNetworkStructure":
                await server.send_notification("setNetworkStructure",
                                               [server.get_network_structure(payload["network_type"]),
                                                payload["network_type"]])
            elif event == "train":
                server.train_network(payload["network_type"], payload["training_data"])
