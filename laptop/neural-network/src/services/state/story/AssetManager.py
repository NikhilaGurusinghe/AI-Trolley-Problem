from services.state.States import States


class ImageTuple:
    def __init__(self, img_a_index: int, image_a_description: str, img_b_index: int, image_b_description: str):
        self.image_a_index = img_a_index
        self.image_a_description = image_a_description
        self.image_b_index = img_b_index
        self.image_b_description = image_b_description

class AssetManager:
    def __init__(self):
        self.images = [ImageTuple(15, "child", 19, "cat"),
                       ImageTuple(15, "child", 23, "older person")]
        # self.start_dialogue = ["Hello", "Hello hello"]
        self._user_input_dialogue = ["Touch the screen", "Touch the screen"]
        self._end_dialogue = ["restarting", "restarting"]

    def get_image(self, state_current_iteration: int) -> ImageTuple:
        return self.images[state_current_iteration]

    def get_dialogue(self, state_current_state: States, state_current_iteration: int) -> str:
        # way to return f-strings with image_x_descriptions in
        if state_current_state == States.USER_INPUT:
            return self._user_input_dialogue[state_current_iteration]
        elif state_current_state == States.END:
            return self._end_dialogue[state_current_iteration]

        raise ValueError("invalid state")