# Used for type hinting
from collections.abc import Callable

import torch


class TrainingParams:
    # this is where the instantiated optimizer_class will be stored
    # to instantiate this class we need the model's params which we don't have here :(
    optimizer = None
    def __init__(self,
                 epochs: int,
                 loss_fn: torch.nn.modules.loss._Loss,
                 eval_fn: Callable[[torch.Tensor, torch.Tensor], float],
                 learning_rate: float,
                 optimizer_class: type[torch.optim.Optimizer]):
        self.epochs: int = epochs
        self.loss_fn: torch.nn.modules.loss._Loss = loss_fn
        self.eval_fn: Callable[[torch.Tensor, torch.Tensor], float] = eval_fn
        self.learning_rate: float = learning_rate
        self.optimizer_class: type[torch.optim.Optimizer] = optimizer_class

    def __str__(self):
        return (f"TrainingParams(\n"
                f"  epochs: {self.epochs}\n"
                f"  loss_fn: {self.loss_fn}\n"
                f"  eval_fn: {self.eval_fn}\n"
                f"  learning_rate: {self.learning_rate}\n"
                f"  optimizer_class: {self.optimizer}\n)")