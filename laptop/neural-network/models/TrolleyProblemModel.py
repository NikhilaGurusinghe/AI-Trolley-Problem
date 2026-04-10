from collections.abc import Callable

import torch
from torch import nn

from models.utils.TrainingParams import TrainingParams
from models.utils.TrainingUtils import get_train_test_split, calculate_accuracy


class TrolleyProblemModel:

    class ModelSmall(nn.Module):
        def __init__(self, input_features : int):
            super().__init__()
            self.layer_1 = nn.Linear(in_features=input_features, out_features=10)
            self.layer_2 = nn.Linear(in_features=10, out_features=10)
            self.layer_3 = nn.Linear(in_features=10, out_features=1)
            self.relu = nn.ReLU()

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            # our layers from input to output are
            # input -> layer_1 -> relu -> layer_2 -> relu -> layer_3 -> logit output
            x = self.layer_1(x)
            x = self.relu(x)
            x = self.layer_2(x)
            x = self.relu(x)
            x = self.layer_3(x)
            return x

    def __init__(self,
                 n_input_features: int,
                 epochs : int,
                 loss_fn : torch.nn.modules.loss._Loss,
                 eval_fn : Callable[[torch.Tensor, torch.Tensor], float],
                 learning_rate : float,
                 optimizer_class : type[torch.optim.Optimizer],
                 training_params : TrainingParams = None,
                 model_class : type[nn.Module] = ModelSmall,
                 device : str = "cpu",
                 random_seed : int = 67,
                 verbose : bool = True):
        assert ((training_params is None and (epochs is not None and loss_fn is not None and eval_fn is not None and learning_rate is not None and optimizer_class is not None))
                or (training_params is not None))

        self.model : nn.Module = model_class(n_input_features)
        if training_params is not None:
            self.training_params : TrainingParams = training_params
            # init the optimizer inside self.training_params
            self.training_params.optimizer = self.training_params.optimizer_class(self.model.parameters(), lr=self.training_params.learning_rate)
        elif training_params is None and (epochs is not None and loss_fn is not None and eval_fn is not None and learning_rate is not None and optimizer_class is not None):
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

    def inference(self, X : torch.Tensor) -> torch.Tensor:
        self.model.eval()
        with torch.inference_mode():
            # sigmoid turns logits to probabilities of 0 or 1, rounding turns these into 0 or 1 along 0.5 decision boundary
            y_pred = torch.round(torch.sigmoid(self.model(X))).squeeze()

            return y_pred

    def train(self, X : torch.Tensor, y : torch.Tensor) -> None:
        torch.manual_seed(self.random_seed)

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
            # sigmoid turns logits to probabilities of 0 or 1, rounding turns these into 0 or 1 along 0.5 decision boundary
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

                print(f"Epoch: {epoch} | Train loss: {train_loss:.5f}, Train accuracy: {train_eval:.2f}% | Test loss: {test_loss:.5f}, Test acc: {test_eval:.2f}%")