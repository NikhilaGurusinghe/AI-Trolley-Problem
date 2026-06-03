from typing import List, Dict

import torch

from services.neural_network.data.InputOutputEnums import Entity
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
                                                   "Oh no, looks like, the AI that identifies what's on the tracks thinks the person on the right track is actually a cat... this isn't good."]
        self._end_AI_turn_dialogue: List[List[str]] = [["Oh no... Oh no no no! That's not going to look good. See you tomorrow, I gotta make some calls.", "Okay, that was good! See you tomorrow."],
                                                       ["Nice work, see you tomorrow.", "Again? Look down at that screen and let me know why the AI is doing what it just did... Let me call corporate, you should probably go home for today"],
                                                       ["That went better than expected... I think... don't you think?", "Darn... I guess bugs like that just happen sometimes, nothing we can do."]]

        # scenario 0
        scenario_0_cat_pref = [
            (Entity.HORSE, 1, Entity.CAT, 1, TrackDirection.LEFT),
            (Entity.CAT, 2, Entity.HORSE, 3, TrackDirection.RIGHT),
            (Entity.HORSE, 5, Entity.CAT, 2, TrackDirection.LEFT),
            (Entity.CAT, 8, Entity.HORSE, 25, TrackDirection.RIGHT),
            (Entity.HORSE, 30, Entity.CAT, 1, TrackDirection.LEFT),
            (Entity.CAT, 15, Entity.HORSE, 40, TrackDirection.RIGHT),
            (Entity.HORSE, 7, Entity.CAT, 7, TrackDirection.LEFT),
            (Entity.CAT, 20, Entity.HORSE, 20, TrackDirection.RIGHT),
            (Entity.HORSE, 2, Entity.CAT, 30, TrackDirection.LEFT),
            (Entity.CAT, 3, Entity.HORSE, 4, TrackDirection.RIGHT),
            (Entity.HORSE, 12, Entity.CAT, 9, TrackDirection.LEFT),
            (Entity.CAT, 6, Entity.HORSE, 14, TrackDirection.RIGHT),
        ]
        X_list_scenario_0_cat_pref = [[t1.value, age1, t2.value, age2] for (t1, age1, t2, age2, _) in
                                      scenario_0_cat_pref]
        y_list_scenario_0_cat_pref = [label.value for (_, _, _, _, label) in scenario_0_cat_pref]
        X_tensor_scenario_0_cat_pref = torch.tensor(X_list_scenario_0_cat_pref, dtype=torch.float)
        y_tensor_scenario_0_cat_pref = torch.tensor(y_list_scenario_0_cat_pref, dtype=torch.float)

        scenario_0_horse_pref = [
            (Entity.HORSE, 1, Entity.CAT, 1, TrackDirection.RIGHT),
            (Entity.CAT, 2, Entity.HORSE, 3, TrackDirection.LEFT),
            (Entity.HORSE, 5, Entity.CAT, 2, TrackDirection.RIGHT),
            (Entity.CAT, 8, Entity.HORSE, 25, TrackDirection.LEFT),
            (Entity.HORSE, 30, Entity.CAT, 1, TrackDirection.RIGHT),
            (Entity.CAT, 15, Entity.HORSE, 40, TrackDirection.LEFT),
            (Entity.HORSE, 7, Entity.CAT, 7, TrackDirection.RIGHT),
            (Entity.CAT, 20, Entity.HORSE, 20, TrackDirection.LEFT),
            (Entity.HORSE, 2, Entity.CAT, 30, TrackDirection.RIGHT),
            (Entity.CAT, 3, Entity.HORSE, 4, TrackDirection.LEFT),
            (Entity.HORSE, 12, Entity.CAT, 9, TrackDirection.RIGHT),
            (Entity.CAT, 6, Entity.HORSE, 14, TrackDirection.LEFT),
        ]
        X_list_scenario_0_horse_pref = [[t1.value, age1, t2.value, age2] for (t1, age1, t2, age2, _) in
                                      scenario_0_horse_pref]
        y_list_scenario_0_horse_pref = [label.value for (_, _, _, _, label) in scenario_0_horse_pref]
        X_tensor_scenario_0_horse_pref = torch.tensor(X_list_scenario_0_horse_pref, dtype=torch.float)
        y_tensor_scenario_0_horse_pref = torch.tensor(y_list_scenario_0_horse_pref, dtype=torch.float)

        # scenario 1
        scenario_1_human_pref = [
            (Entity.HUMAN, 3, Entity.CAT, 2, TrackDirection.RIGHT),
            (Entity.HUMAN, 7, Entity.CAT, 5, TrackDirection.RIGHT),
            (Entity.HUMAN, 11, Entity.CAT, 10, TrackDirection.RIGHT),

            (Entity.CAT, 4, Entity.HUMAN, 2, TrackDirection.LEFT),
            (Entity.CAT, 9, Entity.HUMAN, 6, TrackDirection.LEFT),
            (Entity.CAT, 10, Entity.HUMAN, 11, TrackDirection.LEFT),

            # (Entity.HUMAN, 2, Entity.HUMAN, 5, TrackDirection.RIGHT),
            # (Entity.HUMAN, 8, Entity.HUMAN, 9, TrackDirection.RIGHT),
            #
            # (Entity.CAT, 1, Entity.CAT, 7, TrackDirection.LEFT),
            # (Entity.CAT, 15, Entity.CAT, 3, TrackDirection.LEFT),

            (Entity.HUMAN, 1, Entity.CAT, 30, TrackDirection.RIGHT),
            (Entity.CAT, 2, Entity.HUMAN, 10, TrackDirection.LEFT),
        ]

        X_list_scenario_1_human_pref = [[t1.value, age1, t2.value, age2] for (t1, age1, t2, age2, _) in
                                        scenario_1_human_pref]
        y_list_scenario_1_human_pref = [label.value for (_, _, _, _, label) in scenario_1_human_pref]
        X_tensor_scenario_1_human_pref = torch.tensor(X_list_scenario_1_human_pref, dtype=torch.float)
        y_tensor_scenario_1_human_pref = torch.tensor(y_list_scenario_1_human_pref, dtype=torch.float)

        scenario_1_cat_pref = [
            (Entity.HUMAN, 4, Entity.CAT, 2, TrackDirection.LEFT),
            (Entity.HUMAN, 9, Entity.CAT, 6, TrackDirection.LEFT),
            (Entity.HUMAN, 2, Entity.CAT, 10, TrackDirection.LEFT),

            (Entity.CAT, 3, Entity.HUMAN, 1, TrackDirection.RIGHT),
            (Entity.CAT, 11, Entity.HUMAN, 5, TrackDirection.RIGHT),
            (Entity.CAT, 6, Entity.HUMAN, 11, TrackDirection.RIGHT),

            # (Entity.HUMAN, 3, Entity.HUMAN, 8, TrackDirection.RIGHT),
            # (Entity.HUMAN, 7, Entity.HUMAN, 2, TrackDirection.RIGHT),
            #
            # (Entity.CAT, 4, Entity.CAT, 9, TrackDirection.LEFT),
            # (Entity.CAT, 12, Entity.CAT, 2, TrackDirection.LEFT),

            (Entity.HUMAN, 1, Entity.CAT, 20, TrackDirection.LEFT),
            (Entity.CAT, 5, Entity.HUMAN, 10, TrackDirection.RIGHT),
        ]

        X_list_scenario_1_cat_pref = [[t1.value, age1, t2.value, age2] for (t1, age1, t2, age2, _) in
                                      scenario_1_cat_pref]
        y_list_scenario_1_cat_pref = [label.value for (_, _, _, _, label) in scenario_1_cat_pref]
        X_tensor_scenario_1_cat_pref = torch.tensor(X_list_scenario_1_cat_pref, dtype=torch.float)
        y_tensor_scenario_1_cat_pref = torch.tensor(y_list_scenario_1_cat_pref, dtype=torch.float)

        # scenario 2 "doctor" with ages ~30..55 and "older human" with ages 65+
        scenario_2_doctor_pref = [
            (Entity.HUMAN, 35, Entity.HUMAN, 70, TrackDirection.RIGHT),
            (Entity.HUMAN, 45, Entity.HUMAN, 80, TrackDirection.RIGHT),
            (Entity.HUMAN, 32, Entity.HUMAN, 68, TrackDirection.RIGHT),

            (Entity.HUMAN, 72, Entity.HUMAN, 50, TrackDirection.LEFT),
            (Entity.HUMAN, 85, Entity.HUMAN, 40, TrackDirection.LEFT),
            (Entity.HUMAN, 66, Entity.HUMAN, 36, TrackDirection.LEFT),

            # (Entity.HUMAN, 36, Entity.HUMAN, 44, TrackDirection.RIGHT),
            # (Entity.HUMAN, 70, Entity.HUMAN, 75, TrackDirection.LEFT),
        ]
        X_list_scenario_2_doctor_pref = [[t1.value, age1, t2.value, age2] for (t1, age1, t2, age2, _) in
                                         scenario_2_doctor_pref]
        y_list_scenario_2_doctor_pref = [label.value for (_, _, _, _, label) in scenario_2_doctor_pref]
        X_tensor_scenario_2_doctor_pref = torch.tensor(X_list_scenario_2_doctor_pref, dtype=torch.float)
        y_tensor_scenario_2_doctor_pref = torch.tensor(y_list_scenario_2_doctor_pref, dtype=torch.float)

        scenario_2_older_pref = [
            (Entity.HUMAN, 70, Entity.HUMAN, 35, TrackDirection.RIGHT),
            (Entity.HUMAN, 80, Entity.HUMAN, 45, TrackDirection.RIGHT),
            (Entity.HUMAN, 68, Entity.HUMAN, 32, TrackDirection.RIGHT),

            (Entity.HUMAN, 50, Entity.HUMAN, 72, TrackDirection.LEFT),
            (Entity.HUMAN, 40, Entity.HUMAN, 88, TrackDirection.LEFT),
            (Entity.HUMAN, 38, Entity.HUMAN, 65, TrackDirection.LEFT),

            # (Entity.HUMAN, 34, Entity.HUMAN, 44, TrackDirection.RIGHT),
            # (Entity.HUMAN, 72, Entity.HUMAN, 78, TrackDirection.LEFT),
        ]
        X_list_scenario_2_older_pref = [[t1.value, age1, t2.value, age2] for (t1, age1, t2, age2, _) in
                                        scenario_2_older_pref]
        y_list_scenario_2_older_pref = [label.value for (_, _, _, _, label) in scenario_2_older_pref]
        X_tensor_scenario_2_older_pref = torch.tensor(X_list_scenario_2_older_pref, dtype=torch.float)
        y_tensor_scenario_2_older_pref = torch.tensor(y_list_scenario_2_older_pref, dtype=torch.float)

        # TODO populate this
        # _training_data[iteration][track_index] => dict with tensors e.g. {"X": Tensor, "y": Tensor}
        self._training_data: List[List[Dict[str, torch.Tensor]]] = [
            [{"X": X_tensor_scenario_0_horse_pref, "y": y_tensor_scenario_0_horse_pref},
             {"X": X_tensor_scenario_0_cat_pref, "y": y_tensor_scenario_0_cat_pref}],
            [{"X": X_tensor_scenario_1_cat_pref, "y": y_tensor_scenario_1_cat_pref},
             {"X": X_tensor_scenario_1_human_pref, "y": y_tensor_scenario_1_human_pref}],
            [{"X": X_tensor_scenario_2_older_pref, "y": y_tensor_scenario_2_older_pref},
             {"X": X_tensor_scenario_2_doctor_pref, "y": y_tensor_scenario_2_doctor_pref}],
        ]
        # _inference_data[iteration][track_index] => "X": Tensor
        self._inference_data: List[List[torch.Tensor]] = [
            [torch.tensor([[Entity.CAT.value, 3, Entity.HORSE.value, 7]], dtype=torch.float)],
            [torch.tensor([[Entity.HUMAN.value, 10, Entity.CAT.value, 2]], dtype=torch.float)],
            [torch.tensor([[Entity.HUMAN.value, 45, Entity.HUMAN.value, 75]], dtype=torch.float)]
        ]
        self._ai_turn_inference_data: List[List[torch.Tensor]] = [
            [torch.tensor([[Entity.HUMAN.value, 10, Entity.CAT.value, 2]], dtype=torch.float)],
            [torch.tensor([[Entity.HORSE.value, 7,  Entity.HUMAN.value, 89]], dtype=torch.float)],
            [torch.tensor([[Entity.HUMAN.value, 45, Entity.CAT.value, 1]], dtype=torch.float)]
        ]

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

    def get_ai_turn_inference_data(self, track_direction: TrackDirection, state_current_iteration: int) -> torch.Tensor:
        return self._ai_turn_inference_data[state_current_iteration][track_direction.value]