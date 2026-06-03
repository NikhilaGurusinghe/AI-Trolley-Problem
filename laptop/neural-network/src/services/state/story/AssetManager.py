from typing import List, Dict

import torch

from services.serial.TrackDirection import TrackDirection
from services.state.States import States


class ImageTuple:
    def __init__(self, img_a_index: int, image_a_description: str, img_b_index: int, image_b_description: str):
        self.image_a_index = img_a_index
        self.image_a_description = image_a_description
        self.image_b_index = img_b_index
        self.image_b_description = image_b_description

class AssetManager:
    def __init__(self):
        self._images: List[ImageTuple] = \
            [ImageTuple(15, "child", 19, "cat"),
            ImageTuple(15, "child", 23, "older person")]
        self._user_input_dialogue: List[str] = ["Touch the screen", "Touch the screen"]
        self._end_dialogue: List[str] = ["restarting", "restarting"]
        self._start_AI_turn_dialogue: List[str] = ["now its the AI turn", "AI turn"]
        self._end_AI_turn_dialogue: List[str] = ["oh no", "oh no what have we done?"]

        # TODO populate this
        # _training_data[iteration][track_index] => dict with tensors e.g. {"X": Tensor, "y": Tensor}
        self._training_data: List[List[Dict[str, torch.Tensor]]] = [[]]
        # _inference_data[iteration][track_index] => "X": Tensor
        self._inference_data: List[List[torch.Tensor]] = [[]]

    def get_image(self, state_current_iteration: int) -> ImageTuple:
        return self._images[state_current_iteration]

    def get_dialogue(self, state_current_state: States, state_current_iteration: int) -> str:
        # way to return f-strings with image_x_descriptions in
        if state_current_state == States.USER_INPUT:
            return self._user_input_dialogue[state_current_iteration]
        elif state_current_state == States.END:
            return self._end_dialogue[state_current_iteration]
        elif state_current_state == States.START_AI_TURN:
            return self._start_AI_turn_dialogue[state_current_iteration]
        elif state_current_state == States.END_AI_TURN:
            return self._end_AI_turn_dialogue[state_current_iteration]

        raise ValueError("invalid state")

    def get_training_data(self, track_direction: TrackDirection, state_current_iteration: int) -> dict[str, torch.Tensor]:
        return self._training_data[state_current_iteration][track_direction.value]

    def get_inference_data(self, track_direction: TrackDirection, state_current_iteration: int) -> torch.Tensor:
        return self._inference_data[state_current_iteration][track_direction.value]