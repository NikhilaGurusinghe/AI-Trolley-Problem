from typing import Any

import torch
from torch import nn

from services.neural_network.models.SpriteRecognitionModel import SpriteRecognitionModel
from services.neural_network.models.TrolleyProblemModel import TrolleyProblemModel
from services.neural_network.models.utils.NetworkType import NetworkType
from services.neural_network.models.utils.TrainingUtils import calculate_accuracy


# TODO i'm too lazy to make a parent class to TrolleyProblemModel and SpriteRecognitionModel
#   so i'm just going to pretend like this is real and true cause its python
class NeuralNetworkService:
    def __init__(self, network_type: NetworkType):
        assert 0 <= int(network_type) < len(NetworkType)

        if network_type == NetworkType.TROLLEY_PROBLEM_MODEL:
            self.model_wrapper: TrolleyProblemModel | SpriteRecognitionModel = TrolleyProblemModel(n_input_features=4,
                                                                                        epochs=40,
                                                                                        loss_fn=nn.BCEWithLogitsLoss(),
                                                                                        eval_fn=calculate_accuracy,
                                                                                        learning_rate=0.1,
                                                                                        optimizer_class=torch.optim.SGD)
        elif network_type == NetworkType.SPRITE_RECOGNITION_MODEL:
            self.model_wrapper: TrolleyProblemModel | SpriteRecognitionModel = SpriteRecognitionModel(image_width=18,
                                                                                        image_length=10,
                                                                                        n_colour_channels=1,
                                                                                        hidden_units=10,
                                                                                        output_shape=2,
                                                                                        epochs=50,
                                                                                        loss_fn=nn.CrossEntropyLoss(),
                                                                                        eval_fn=calculate_accuracy,
                                                                                        learning_rate=0.1,
                                                                                        optimizer_class=torch.optim.SGD)
        else:
            raise Exception("NeuralNetworkService.py#__init__(): encountered invalid network_type argument or that "
                            "NetworkType is not currently supported")

    def train(self, training_data: dict[str, torch.Tensor]) -> None:
        if isinstance(self.model_wrapper, TrolleyProblemModel):
            self.model_wrapper.train(training_data["X"], training_data["y"])
        elif isinstance(self.model_wrapper, SpriteRecognitionModel):
            # TODO implement this
            raise TypeError("NeuralNetworkService#train(): Not implemented")
        else:
            raise TypeError("NeuralNetworkService#train(): unsupported model_wrapper type, internal error")

    def inference(self, input_data: torch.Tensor) -> torch.Tensor:
        if isinstance(self.model_wrapper, TrolleyProblemModel):
            return self.model_wrapper.inference(input_data)
        elif isinstance(self.model_wrapper, SpriteRecognitionModel):
            # TODO implement this
            raise TypeError("NeuralNetworkService#inference(): Not implemented")
        else:
            raise TypeError("NeuralNetworkService#inference(): unsupported model_wrapper type, internal error")

    def get_network_structure(self) -> dict[str, list]:
        # https://discuss.pytorch.org/t/access-all-weights-of-a-model/77672
        structure: dict[str, list] = dict()
        for name, param in self.model_wrapper.model.named_parameters():
            # TODO potential bug here if .tolist() gives errors cause of incorrect device
            structure[name] = param.data.tolist()

        return structure