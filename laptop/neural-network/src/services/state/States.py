from enum import Enum

class States(Enum):
    USER_INPUT      = 1
    END             = 2
    START_AI_TURN   = 3
    END_AI_TURN     = 4