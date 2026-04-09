# Used for type hinting
from collections.abc import Callable

import torch

class TrainingParams:
    # this is where the instantiated optimizer_class will be stored
    # to instantiate this class we need the model's params which we don't have here :(
    optimizer = None
    def __init__(self,
                 epochs : int,
                 loss_fn : torch.nn.modules.loss._Loss,
                 eval_fn : Callable[[torch.Tensor, torch.Tensor], float],
                 learning_rate : float,
                 optimizer_class : type[torch.optim.Optimizer]):
        self.epochs : int = epochs
        self.loss_fn : torch.nn.modules.loss._Loss = loss_fn
        self.eval_fn : Callable[[torch.Tensor, torch.Tensor], float] = eval_fn
        self.learning_rate : float = learning_rate
        self.optimizer_class : type[torch.optim.Optimizer] = optimizer_class