import torch
from torch import nn

class ModelSmall(nn.Module):
    def __init__(self):
        super.__init__()
        self.layer1 = nn.Linear
