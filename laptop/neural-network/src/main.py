import asyncio
import threading
import time
from asyncio import AbstractEventLoop
from time import sleep

import torch

from common.websocket.server import Server
from services.neural_network.api.NeuralNetworkServer import NeuralNetworkServer
from services.neural_network.api.utils.WebsocketQueuedDispatcher import WebsocketQueuedDispatcher
from services.neural_network.models.utils.NetworkType import NetworkType
from services.serial.SerialService import SerialService, TrackDirection
from services.serial.TrackDirection import flip_direction
from services.state.StateMachine import StateMachine
from services.state.story.AssetManager import ImageTuple
from services.tts.TTSService import TTSService

# event_queue = asyncio.Queue()

def serial_thread(current_running_loop: AbstractEventLoop,
                  dispatcher: WebsocketQueuedDispatcher,
                  server: NeuralNetworkServer):
    # time.sleep(10)
    # initializing stuff on the other end of the websocket
    event = ("setNetworkStructure", {"network_type": NetworkType.TROLLEY_PROBLEM_MODEL})
    asyncio.run_coroutine_threadsafe(dispatcher.event_queue.put(event), current_running_loop)

    input_tensor = torch.tensor([[0.0, 0.0, 123.0, 0.0]], dtype=torch.float32)

    try:
        prediction = server.inference_network(NetworkType.TROLLEY_PROBLEM_MODEL, input_tensor)
    except Exception as e:
        print("main#serial_thread(): inference failed", e)
        prediction = None

    if prediction is not None:
        result_raw: int = int(prediction.item())
        result_direction: TrackDirection = TrackDirection(result_raw)
        print(result_direction)
    #
    # arduino = SerialService("COM7", 115200)
    # state = StateMachine()
    # tts = TTSService()
    #
    # # TODO need to spend some time in between the START and USER_INPUT states
    # # probably want to set up a start screen one off without the use of the state machine
    #
    # # TODO think about which calls block, might have to run audio in a seperate thread at times
    # while True:
    #     # get images and send them to the displays
    #     print("start")
    #     images: ImageTuple = state.assets_manager.get_image(state.current_iteration)
    #     print(arduino.send_images(images.image_a_index, images.image_b_index))
    #
    #     # say something at the start of an iteration, whilst loading stuff on displays
    #     # this blocks!
    #     # tts.speak(state.assets_manager.get_dialogue(state.current_state, state.current_iteration))
    #
    #     # wait to get tap response
    #     tap_response: TrackDirection = arduino.get_tap_response()
    #
    #     print(tap_response.name)
    #     state.update()
    #
    #     # TODO inference here
    #
    #     # flip based on orientation of the tap controller thingy (its opposite)
    #     print(arduino.send_track_direction(flip_direction(tap_response)))
    #
    #     # say line whilst train is moving
    #     # tts.speak(state.assets_manager.get_dialogue(state.current_state, state.current_iteration))
    #
    #     # reset!
    #     state.update()
    pass

async def main():
    dispatcher: WebsocketQueuedDispatcher = WebsocketQueuedDispatcher()
    server: NeuralNetworkServer = NeuralNetworkServer("", 8001)

    current_running_loop = asyncio.get_running_loop()
    threading.Thread(target=serial_thread, args=(current_running_loop, dispatcher, server), daemon=True).start()
    asyncio.create_task(dispatcher.websocket_dispatcher(server))

    await server.loop()

if __name__ == "__main__":
    asyncio.run(main())
