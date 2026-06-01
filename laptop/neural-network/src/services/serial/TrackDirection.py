from enum import Enum

def flip_direction(track_direction: TrackDirection) -> TrackDirection:
    if track_direction == TrackDirection.LEFT:
        return TrackDirection.RIGHT
    elif track_direction == TrackDirection.RIGHT:
        return TrackDirection.LEFT

    raise ValueError("Illegal track direction")

class TrackDirection(Enum):
    LEFT    = 0
    RIGHT   = 1

