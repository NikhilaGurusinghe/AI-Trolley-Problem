from typing import Callable

import torch
from torch import nn

from src.services.neural_network.models.utils.TrainingParams import TrainingParams


# https://www.learnpytorch.io/03_pytorch_computer_vision/#7-model-2-building-a-convolutional-neural-network-cnn
class SpriteRecognitionModel:
    """Wrapper for building, training and running inference on a convolutional artificial neural network. This
     "backbone" can be used to classify simple pixel-art images into categories e.g. cat, dog, adult, child, etc.

       The wrapper holds:
       - `model`: an `nn.Module` instance (defaults to `ModelSmall`)
       - `training_params`: a `TrainingParams` instance that contains training parameters loss, optimizer, epochs, etc.

       Attributes:
           model (nn.Module): Instantiated convolutional neural network.
           training_params (TrainingParams): Parameters controlling training.
           device (str): Device name.
           random_seed (int): Seed used for deterministic behavior where possible.
           verbose (bool): Verbosity flag (i.e. whether to print stuff to console).
       """
    class ModelSmall(nn.Module):
        # model architecture based on https://poloclub.github.io/cnn-explainer/
        # but smoller
        def __init__(self, image_width: int, image_length: int, n_colour_channels: int,
                     hidden_units: int, output_shape: int):
            super().__init__()
            self.block_1 = nn.Sequential(
                nn.Conv2d(in_channels=n_colour_channels,
                          out_channels=hidden_units,
                          kernel_size=3, stride=1, padding=1),
                nn.ReLU(),
                nn.Conv2d(in_channels=hidden_units,
                          out_channels=hidden_units,
                          kernel_size=3, stride=1,  padding=1),
                nn.ReLU(),
                nn.MaxPool2d(kernel_size=2, stride=2)
            )
            self.classifier = nn.Sequential(
                nn.Flatten(),
                # the size of our image gets cut in half (per dimension), due to the one max pool in our network
                # stride=1 convolutional layers (conv2d) does not change the size of our image as it goes through
                # the network
                nn.Linear(in_features=hidden_units * (int(image_width / 2)) * (int(image_length / 2)),
                          out_features=output_shape)
            )

        def forward(self, x: torch.Tensor) -> torch.Tensor:
            """Calculates a forward pass through the convolutional neural network (such as that done during inference
            time).

            Args:
                x (torch.Tensor): Input tensor of shape (batch_size, input_features).

            Returns:
                torch.Tensor: Logits of shape (batch_size, 1).
            """
            # our layers from input to output are
            # input -> conv2d -> relu -> conv2d -> relu -> MaxPool -> Flatten -> Linear -> logit output
            x = self.block_1(x)
            x = self.classifier(x)
            return x

    def __init__(self,
                 image_width: int, image_length: int, n_colour_channels: int, hidden_units: int, output_shape: int,
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
        """Create and configure the sprite recognition model.

        Args:
            image_width (int): The width (in pixels) of the input image.
            image_length (int): The length (in pixels) of the input image.
            n_colour_channels (int): Number of colour channels that the image has (e.g greyscale = 1, rgb = 3).
            hidden_units (int): Number of neurons per hidden layer.
            output_shape (int): Number of classes that you're classifying images into.
            epochs (int): Number of training epochs (ignored if `training_params` supplied).
            loss_fn (torch.nn.modules.loss._Loss): Loss function used for training. (ignored if `training_params`
                supplied).
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
        assert ((training_params is None and
                 (epochs is not None and loss_fn is not None and eval_fn is not None and
                  learning_rate is not None and optimizer_class is not None)) or (training_params is not None))

        assert (image_width is not None and image_length is not None and n_colour_channels is not None and
                hidden_units is not None and output_shape is not None)

        torch.manual_seed(random_seed)
        self.model: nn.Module = model_class(image_width,
                                             image_length,
                                             n_colour_channels,
                                             hidden_units, output_shape)
        if training_params is not None:
            self.training_params: TrainingParams = training_params
            # init the optimizer inside self.training_params
            self.training_params.optimizer = self.training_params.optimizer_class(self.model.parameters(),
                                                                                  lr=self.training_params.learning_rate)
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
            raise TypeError("SpriteRecognitionModel.__init__() did not receive proper training_params.")
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
            # model(X) gives us a vector of raw logits, argmax gives us the max value in this vector
            # which corresponds to the class that has the highest prediction probability (according to the model)
            y_pred = (self.model(X)).argmax(dim=1)
            return y_pred

    def train(self, data_loader: torch.utils.data.DataLoader) -> None:
        """Train the model using this class's configured `training_params`.

           Args:
               data_loader (torch.utils.data.DataLoader): Features and labels all in a torch.utils.data.DataLoader.
           """

        self.model.to(self.device)
        train_loss, train_eval = 0, 0
        test_loss, test_eval = 0, 0

        # train and test loop
        for epoch in range(self.training_params.epochs):
            ### Training
            for batch, sample in enumerate(data_loader):
                X, y = sample["image"].to(self.device), sample["classification"].to(self.device)
                self.model.train()

                # Forward pass
                y_pred = self.model(X)

                # Train loss + train_eval calculation
                train_loss = self.training_params.loss_fn(y_pred, y)
                if self.verbose and epoch % 10 == 0:
                    # model(X) gives us a vector of raw logits, argmax gives us the
                    # max value in this vector (most probable label)
                    train_eval = self.training_params.eval_fn(y, y_pred.argmax(dim=1))

                # Zero optimizer gradients
                self.training_params.optimizer.zero_grad()

                # Backpropogation
                train_loss.backward()

                # Gradient descent
                self.training_params.optimizer.step()

            train_loss /= len(data_loader)
            if self.verbose and epoch % 10 == 0:
                test_eval /= len(data_loader)

            ### Testing
            if self.verbose and epoch % 10 == 0:
                self.model.eval()
                with torch.inference_mode():
                    for sample in data_loader:
                        X, y = sample["image"].to(self.device), sample["classification"].to(self.device)
                        # Forward pass
                        test_pred = self.model(X)

                        # Test loss + accuracy calculation
                        test_loss += self.training_params.loss_fn(test_pred, y)
                        test_eval += self.training_params.eval_fn(y, test_pred.argmax(dim=1))

                    test_loss /= len(data_loader)
                    test_eval /= len(data_loader)

                print(f"Epoch: {epoch} | Train loss: {train_loss:.5f},"
                      f" Train accuracy: {train_eval:.2f}% | Test loss: {test_loss:.5f}, Test acc: {test_eval:.2f}%")