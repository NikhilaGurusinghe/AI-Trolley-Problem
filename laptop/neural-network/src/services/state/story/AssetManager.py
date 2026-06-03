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
            [ImageTuple(15, "cat", 19, "horse"),
            ImageTuple(15, "young guy", 23, "cat"),
             ImageTuple(15, "doctor", 23, "older guy")]
        self._images_AI_turn: List[ImageTuple] = \
            [ImageTuple(15, "young human", 23, "cat"),
             ImageTuple(15, "horse", 23, "older human"),
             ImageTuple(15, "disabled person", 23, "young girl")] # TOD
        self._user_input_dialogue: List[str] = ["Okay so on your screens you'll see whats on the left and right track, just tap the screen of whatever you want to run over. Simple, right?",
                                                "So... that was not great for your first day... Let's see if we can fix this, tap the screen of what... or who... who you want to run over, okay and quickly?",
                                                "Okay well let's see what happens today, you know the drill, tap the screen of whatever you want to run over."]
        self._end_dialogue: List[List[str]] = [["So I guess you're a cat person then? I think you and me are going to be goood friends.", "So I guess you're not a cat person then? I think you and me are going to be goood friends."],
                                               ["Didn't you get the memo? We're all going to lose our jobs because you're a homocidal maniac!", "Okay good job that should stop accidents like yesterday's from ever happening again"],
                                               ["Oh well, don't beat yourself up at the end of the day, the AI must make a decision.", "Tough decision, but that's why they pay you the big bucks."]]
        self._start_AI_turn_dialogue: List[str] = ["Okay so corporate wants a prototype ASAP, so I think that's enough trained for today. Let's see how it goes on it's own",
                                                   "Let's test the AI out again, everything looks good and we need to ship this model yesterday!",
                                                   "Unfortunately, the AI that identifies what's on the tracks thinks the person on the right track is actually a cat... this isn't good."]
        self._end_AI_turn_dialogue: List[List[str]] = [["Oh no... Oh no no no! That's not going to look good. See you tomorrow, I gotta make some calls.", "Okay, that was good! See you tomorrow."],
                                                       ["Nice work, see you tomorrow.", "Again? Look down at that screen and let me know why the AI is doing what it just did... Let me call corporate, you should probably go home for today"],
                                                       ["That went better than expected... I think... don't you think?", "Darn... I guess bugs like that just happen sometimes, nothing we can do."]]

        # TODO populate this
        # _training_data[iteration][track_index] => dict with tensors e.g. {"X": Tensor, "y": Tensor}
        self._training_data: List[List[Dict[str, torch.Tensor]]] = [[]]
        # _inference_data[iteration][track_index] => "X": Tensor
        self._inference_data: List[List[torch.Tensor]] = [[]]

    def get_image(self, state_current_iteration: int) -> ImageTuple:
        return self._images[state_current_iteration]

    def get_ai_turn_image(self, state_current_iteration: int) -> ImageTuple:
        return self._images_AI_turn[state_current_iteration]

    def get_dialogue(self, state_current_state: States, state_current_iteration: int) -> str | List[str]:
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