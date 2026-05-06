from collections.abc import Callable

import torch
from torch import nn

from src.models.utils.TrainingParams import TrainingParams
from src.models.utils.TrainingUtils import get_train_test_split


# https://www.learnpytorch.io/02_pytorch_classification/
class TrolleyProblemModel:
    """Wrapper for building, training and running inference on an artificial neural network. This "backbone" can be
    used to decide between simple binary decisions e.g. Track 1 or Track 2 based on training data.

    The wrapper holds:
    - `model`: an `nn.Module` instance (defaults to `ModelSmall`)
    - `training_params`: a `TrainingParams` instance that contains training parameters loss, optimizer, epochs, etc.

    Attributes:
        model (nn.Module): Instantiated neural network.
        training_params (TrainingParams): Parameters controlling training.
        device (str): Device name.
        random_seed (int): Seed used for deterministic behavior where possible.
        verbose (bool): Verbosity flag (i.e. whether to print stuff to console).
    """
    class ModelSmall(nn.Module):
        """A small artificial neural network. This is used as the default model. The architecture of the model is:
             input -> Linear(input_features, 10) -> ReLU -> Linear(10, 10) -> ReLU -> Linear(10, 1).

        Args:
            input_features (int): Number of features in the input tensor.
        """
        def __init__(self, input_features: int):
            """
            Args:
                input_features (int): The number of inputs passed into the network
            """
            super().__init__()
            self.layer_1 = nn.Linear(in_features=input_features, out_features=10)
            self.layer_2 = nn.Linear(in_features=10, out_features=10)
            self.layer_3 = nn.Linear(in_features=10, out_features=1)
            self.relu = nn.ReLU()

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            """Calculates a forward pass through the artificial neural network
            (such as that done during inference time).

            Args:
                x (torch.Tensor): Input tensor of shape (batch_size, input_features).

            Returns:
                torch.Tensor: Logits of shape (batch_size, 1).
            """
            # our layers from input to output are
            # input -> Linear -> relu -> Linear -> relu -> Linear -> logit output
            x = self.layer_1(x)
            x = self.relu(x)
            x = self.layer_2(x)
            x = self.relu(x)
            x = self.layer_3(x)
            return x

    def __init__(self,
                 n_input_features: int,
                 epochs: int,
                 loss_fn: torch.nn.modules.loss._Loss,
                 eval_fn: Callable[[torch.Tensor, torch.Tensor], float],
                 learning_rate: float,
                 optimizer_class: type[torch.optim.Optimizer],
                 training_params: TrainingParams = None,
                 model_class: type[nn.Module] = ModelSmall,
                 device: str = "cpu",
                 random_seed: int = 67,
                 verbose: bool = True):
        """Create and configure the trolley problem model.

        Args:
            n_input_features (int): Number of input features for the model.
            epochs (int): Number of training epochs (ignored if `training_params` supplied).
            loss_fn (torch.nn.modules.loss._Loss): Loss function used for training.
                (ignored if `training_params` supplied).
            eval_fn (Callable[[torch.Tensor, torch.Tensor], float]): Evaluation function: (y_true, y_pred) -> metric.
                (ignored if `training_params` supplied).
            learning_rate (float): Learning rate for the optimizer. (ignored if `training_params` supplied).
            optimizer_class (type[torch.optim.Optimizer]): Optimizer class (e.g., `torch.optim.SGD`).
                (ignored if `training_params` supplied).
            training_params (TrainingParams | None): Optionally supply a prebuilt `TrainingParams`.
            model_class (type[nn.Module]): Model class to instantiate (default: `ModelSmall`).
            device (str): Device to run on, e.g. "cpu" or "cuda" (default: `cpu`).
            random_seed (int): Random seed used for reproducible splits and model init (default: 67).
            verbose (bool): If True prints debug statements during training to the console (default: True).

        Raises:
            TypeError: If arguments are inconsistent (neither full args nor training_params given).
        """
        assert ((training_params is None and (epochs is not None and loss_fn is not None and eval_fn is not None and
                                              learning_rate is not None and optimizer_class is not None)) or
                (training_params is not None))

        torch.manual_seed(random_seed)
        self.model: nn.Module = model_class(n_input_features)
        if training_params is not None:
            self.training_params : TrainingParams = training_params
            # init the optimizer inside self.training_params
            self.training_params.optimizer = self.training_params.optimizer_class(
                self.model.parameters(),
                lr=self.training_params.learning_rate
            )
        elif training_params is None and (epochs is not None and loss_fn is not None and eval_fn is not None and
                                          learning_rate is not None and optimizer_class is not None):
            self.training_params = TrainingParams(epochs=epochs,
                                                  loss_fn=loss_fn,
                                                  eval_fn=eval_fn,
                                                  learning_rate=learning_rate,
                                                  optimizer_class=optimizer_class)
            self.training_params.optimizer = self.training_params.optimizer_class(self.model.parameters(),
                                                                                  lr=self.training_params.learning_rate)
        else:
            raise TypeError("TrolleyProblemModel.__init__() did not receive proper training_params.")
        self.device = device
        self.random_seed = random_seed
        self.verbose = verbose

    def inference(self, X: torch.Tensor) -> torch.Tensor:
        """Have the model inference/make predictions based on an input Tensor of all your data.

        Args:
            X (torch.Tensor): Input tensor, shape (n_samples, n_features).

        Returns:
            torch.Tensor: Predicted labels (0 or 1) shape (n_samples,).
        """
        self.model.eval()
        self.model.to(self.device)
        with torch.inference_mode():
            # sigmoid turns logits to probabilities of 0 or 1, rounding turns these into 0 or 1 along 0.5 decision
            # boundary
            y_pred = torch.round(torch.sigmoid(self.model(X))).squeeze()

            return y_pred

    def train(self, X: torch.Tensor, y: torch.Tensor) -> None:
        """Train the model using this class's configured `training_params`.

        Args:
            X (torch.Tensor): Features tensor, shape (n_samples, n_features).
            y (torch.Tensor): Target/labels tensor, shape (n_samples,) or (n_samples, 1).
        """

        # do this otherwise no more nice pytorch
        self.model.to(self.device)
        X, y = X.to(self.device), y.to(self.device)

        # split training set into train and test set
        X_train, X_test, y_train, y_test = get_train_test_split(X, y, random_seed=self.random_seed)
        # send data to target device
        X_train, y_train = X_train.to(self.device), y_train.to(self.device)
        X_test, y_test = X_test.to(self.device), y_test.to(self.device)

        # train and test loop
        for epoch in range(self.training_params.epochs):
            ### Training
            self.model.train()

            # Forward pass
            # squeeze to remove extra dimensions, this won't work unless model and data are on same device
            y_logits = self.model(X_train).squeeze()
            # sigmoid turns logits to probabilities of 0 or 1, rounding turns these into 0 or 1 along 0.5 decision
            # boundary
            y_pred = torch.round(torch.sigmoid(y_logits))

            # Train loss + train_eval calculation
            # TODO change this Using nn.BCEWithLogitsLoss works with raw logits
            train_loss = self.training_params.loss_fn(y_logits, y_train)
            if self.verbose and epoch % 10 == 0:
                train_eval = self.training_params.eval_fn(y_train, y_pred)

            # Zero optimizer gradients
            self.training_params.optimizer.zero_grad()

            # Backpropogation
            train_loss.backward()

            # Gradient descent
            self.training_params.optimizer.step()

            ### Testing
            if self.verbose and epoch % 10 == 0:
                self.model.eval()
                with torch.inference_mode():
                    # Forward pass
                    test_logits = self.model(X_test).squeeze()
                    test_pred = torch.round(torch.sigmoid(test_logits))

                    # Test loss + accuracy calculation
                    # TODO change this Using nn.BCEWithLogitsLoss works with raw logits
                    test_loss = self.training_params.loss_fn(test_logits, y_test)
                    test_eval = self.training_params.eval_fn(y_test, test_pred)

                print(f"Epoch: {epoch} | Train loss: {train_loss:.5f}, "
                      f"Train accuracy: {train_eval:.2f}% | Test loss: {test_loss:.5f}, Test acc: {test_eval:.2f}%")