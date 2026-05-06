import asyncio
import threading
from time import sleep

from common.websocket.server import Server
from services.neural_network.api.NeuralNetworkServer import NeuralNetworkServer
from services.neural_network.models.utils.NetworkType import NetworkType

# TTS library https://github.com/nateshmbhat/pyttsx3
event_queue = asyncio.Queue()
activation = {}
def get_activation(name):
    def hook(model, input, output):
        activation[name] = output.detach()
    return hook

def serial_thread(loop):
    # ... read serial
    sleep(5)
    print("adding to queue")
    event = ("setNetworkStructure", {"network_type": NetworkType.SPRITE_RECOGNITION_MODEL})
    asyncio.run_coroutine_threadsafe(event_queue.put(event), loop)

async def event_consumer(server: NeuralNetworkServer):
    while True:
        event, payload = await event_queue.get()
        if event == "setNetworkStructure":
            await server.send_notification("setNetworkStructure", [server.get_network_structure(payload["network_type"]), payload["network_type"]])

async def main():
    server = NeuralNetworkServer("", 8001)
    loop = asyncio.get_running_loop()
    threading.Thread(target=serial_thread, args=(loop,), daemon=True).start()
    asyncio.create_task(event_consumer(server))
    await server.loop()

if __name__ == "__main__":
    asyncio.run(main())