import asyncio
import random
import threading
import time
from asyncio import AbstractEventLoop
from time import sleep
from typing import Dict

import pyttsx3
import torch
from serial import SerialException

from common.utils.bsod import crash_system
from common.websocket.server import Server
from services.neural_network.api.NeuralNetworkServer import NeuralNetworkServer
from services.neural_network.api.utils.WebsocketQueuedDispatcher import WebsocketQueuedDispatcher
from services.neural_network.models.utils.NetworkType import NetworkType
from services.serial.SerialService import SerialService, TrackDirection
from services.serial.TrackDirection import flip_direction
from services.state.StateMachine import StateMachine
from services.state.story.AssetManager import ImageTuple
from services.tts.TTSService import TTSService

import random, traceback

def serial_thread(current_running_loop: AbstractEventLoop,
                  dispatcher: WebsocketQueuedDispatcher,
                  server: NeuralNetworkServer):
    # time.sleep(10)
    # initializing stuff on the other end of the websocket
    event = ("setNetworkStructure", {"network_type": NetworkType.TROLLEY_PROBLEM_MODEL})
    asyncio.run_coroutine_threadsafe(dispatcher.event_queue.put(event), current_running_loop)
    #
    # tts = TTSService()
    # state = StateMachine()

    print("start!")

    # tts.speak("hello...  this is a pause.", True)
    print("hello!")

    arduino = SerialService("COM7", 115200)
    state = StateMachine()
    # tts = TTSService()
    speech = pyttsx3.init()
    speech.setProperty("rate", 150)
    # voices = speech.getProperty("voices")
    # if voices:
    #     speech.setProperty("voice", random.choice(voices).id)

    speech.say("Hey, welcome to your new job where you'll be helping to train an AI to help us maximise rail traffic "
               "whilst minimizing on-track casualties... I'm Dave and this your OJT (that's short for on-the-job-training)... ")
    speech.runAndWait()

    # TODO need to spend some time in between the START and USER_INPUT states
    # probably want to set up a start screen one off without the use of the state machine

    while True:
        # current state = USER_INPUT
        # get images and send them to the displays
        print("start")
        images: ImageTuple = state.assets_manager.get_image(state.current_iteration)
        print(arduino.send_images(images.image_a_index, images.image_b_index))

        # say something at the start of an iteration, whilst loading stuff on displays
        # this blocks!
        # tts.speak("hello", True)
        speech.say(state.assets_manager.get_dialogue(state.current_state, state.current_iteration))
        speech.runAndWait()

        # wait to get tap response, also blocks
        tap_response: TrackDirection = arduino.get_tap_response()
        # tap_response: TrackDirection = None
        # if state.current_iteration == 0:
        #     tap_response = TrackDirection.LEFT
        # elif state.current_iteration == 1:
        #     tap_response = TrackDirection.RIGHT
        # elif state.current_iteration == 2:
        #     tap_response = TrackDirection.LEFT

        print(tap_response)
        state.update() # current state = END

        # flip based on orientation of the tap controller thingy (its opposite)
        print(arduino.send_track_direction(flip_direction(tap_response)))

        # say line whilst train is moving
        # tts.speak(state.assets_manager.get_dialogue(state.current_state, state.current_iteration)[tap_response.value],
        #           False)

        # training
        training_data: Dict[str, torch.Tensor] = state.assets_manager.get_training_data(tap_response,
                                                                                        state.current_iteration)
        training_event = ("train", {"network_type": NetworkType.TROLLEY_PROBLEM_MODEL, "training_data": training_data})
        asyncio.run_coroutine_threadsafe(dispatcher.event_queue.put(training_event), current_running_loop)
        # send notification to clients that we've trained the network
        update_event = ("setNetworkStructure", {"network_type": NetworkType.TROLLEY_PROBLEM_MODEL})
        asyncio.run_coroutine_threadsafe(dispatcher.event_queue.put(update_event), current_running_loop)

        # time.sleep(10) # sleep so train has time to go around
        speech.say(state.assets_manager.get_dialogue(state.current_state, state.current_iteration)[tap_response.value])
        speech.runAndWait()

        state.update() # current state = START_AI_TURN

        # say something at the start of an iteration, whilst loading stuff on displays
        # no blocking
        # tts.speak(state.assets_manager.get_dialogue(state.current_state, state.current_iteration), False)
        speech.say(state.assets_manager.get_dialogue(state.current_state, state.current_iteration))
        speech.runAndWait()

        # draw AI turn images, blocks
        images: ImageTuple = state.assets_manager.get_ai_turn_image(state.current_iteration)
        print(arduino.send_images(images.image_a_index, images.image_b_index))

        # TODO onwards
        input_tensor = state.assets_manager.get_ai_turn_inference_data(tap_response, state.current_iteration) #torch.tensor([[0.0, 0.0, 123.0, 0.0]], dtype=torch.float32)

        try:
            prediction = server.inference_network(NetworkType.TROLLEY_PROBLEM_MODEL, input_tensor)
        except Exception as e:
            print("main#serial_thread(): inference failed", e)
            prediction = None

        result_direction: TrackDirection | None = None
        if prediction is not None:
            result_raw: int = int(prediction.item())
            result_direction = TrackDirection(result_raw)
            print(result_direction)

        state.update()  # current state = END_AI_TURN

        # flip based on orientation of the tap controller thingy (its opposite)
        if result_direction is not None:
            print(arduino.send_track_direction(flip_direction(result_direction)))

        # say line whilst train is moving
        # tts.speak(state.assets_manager.get_dialogue(state.current_state, state.current_iteration)[result_direction.value],
        #           False)
        speech.say(state.assets_manager.get_dialogue(state.current_state, state.current_iteration)[result_direction.value])
        speech.runAndWait()
        time.sleep(10) # sleep so train has time to go around

        state.update()  # reset!

        if state.current_iteration >= 3:
            rand_dir = random.choice(list(TrackDirection))
            print("sending track command:", rand_dir)
            arduino.send_track_direction(rand_dir)

            speech.say(
                "Hey the AI, is kind of going haywire... I know upper management loves this new model we've trained, but "
                "if they see how many people its killing its going to be bad for us... "
                "you didn't hear this from me, but yank that blue cable out now!")
            speech.runAndWait()

            time.sleep(10)

            crash_system()


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
