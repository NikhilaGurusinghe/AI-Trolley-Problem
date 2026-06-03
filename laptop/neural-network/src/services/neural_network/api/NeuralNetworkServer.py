import json
from typing import Callable, Any

from sklearn.externals.array_api_compat import torch

from common.websocket.server import Server
from services.neural_network.NeuralNetworkService import NeuralNetworkService
from services.neural_network.models.utils.NetworkType import NetworkType


class NeuralNetworkServer(Server):
    def __init__(self, host_name: str, port_number: int):
        self.all_models: list[NeuralNetworkService] = [NeuralNetworkService(NetworkType.TROLLEY_PROBLEM_MODEL),
                                                       NeuralNetworkService(NetworkType.SPRITE_RECOGNITION_MODEL)]
        all_my_methods: dict[str, Callable[..., str]] = {
            name: getattr(self, name)
            for name, value in self.__class__.__dict__.items()
            if callable(value) and not name.startswith("_") # filter out private methods (i.e. those that start with "_")
        }
        super().__init__(host_name, port_number, all_my_methods)

    def get_network_structure(self, network_type: NetworkType) -> str:
        if int(network_type) < 0 or int(network_type) >= len(NetworkType):
            raise Exception("NeuralNetworkServer#get_network_structure(): failed to execute (invalid arguments)")

        # no exception handling here cause caller should handle all of it
        # vvv the danger zone vvv
        structure: dict[str, list] = self.all_models[int(network_type)].get_network_structure()

        return json.dumps(structure)

    def train_network(self, network_type: NetworkType, training_data: dict[str, torch.Tensor]):
        if int(network_type) < 0 or int(network_type) >= len(NetworkType):
            raise Exception("NeuralNetworkServer#train_network(): failed to execute (invalid arguments)")

        self.all_models[int(network_type)].train(training_data)

    def inference_network(self, network_type: NetworkType, input_data: torch.Tensor) -> torch.Tensor:
        if int(network_type) < 0 or int(network_type) >= len(NetworkType):
            raise Exception("NeuralNetworkServer#inference_network(): failed to execute (invalid arguments)")

        return self.all_models[int(network_type)].inference(input_data)