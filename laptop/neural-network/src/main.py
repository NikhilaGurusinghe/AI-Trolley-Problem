import asyncio
import threading
import time
from time import sleep

from common.websocket.server import Server
from services.neural_network.api.NeuralNetworkServer import NeuralNetworkServer
from services.neural_network.models.utils.NetworkType import NetworkType
from services.serial.SerialService import SerialService, TrackDirection
from services.serial.TrackDirection import flip_direction
from services.state.StateMachine import StateMachine
from services.state.story.AssetManager import ImageTuple
from services.tts.TTSService import TTSService

event_queue = asyncio.Queue()

def serial_thread(loop):
    # ... read serial
    sleep(5)
    print("adding to queue")
    event = ("setNetworkStructure", {"network_type": NetworkType.TROLLEY_PROBLEM_MODEL})
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
    arduino = SerialService("COM7", 115200)
    state = StateMachine()
    tts = TTSService()

    # TODO need to spend some time in between the START and USER_INPUT states
    # probably want to set up a start screen one off without the use of the state machine

    # TODO think about which calls block, might have to run audio in a seperate thread at times
    while True:
        # get images and send them to the displays
        images: ImageTuple = state.assets_manager.get_image(state)
        print(arduino.send_images(images.image_a_index, images.image_b_index))

        # say something at the start of an iteration, whilst loading stuff on displays
        # this blocks!
        tts.say(state.assets_manager.get_dialogue(state))

        # wait to get tap response
        tap_response: TrackDirection = arduino.get_tap_response()

        print(tap_response.name)

        # flip based on orientation of the tap controller thingy (its opposite)
        print(arduino.send_track_direction(flip_direction(tap_response)))

        # say line whilst train is moving
        tts.say(state.assets_manager.get_dialogue(state))

        # reset!
        state.update()

    # asyncio.run(main())
    pass