from services.state.States import States
from services.state.story.AssetManager import AssetManager


class StateMachine:
    # need a field here that stores all the images and dialogues for each state and interation

    def __init__(self):
        self.current_iteration: int = 0
        self.current_state = States.USER_INPUT

        self.assets_manager = AssetManager()

    def update(self):
        self._next_state()

    # TODO update this
    def _next_state(self):
        if self.current_state == States.USER_INPUT:
            self.current_state = States.END
        elif self.current_state == States.END:
            # we wrap around
            self.current_state = States.USER_INPUT
            self.current_iteration += 1