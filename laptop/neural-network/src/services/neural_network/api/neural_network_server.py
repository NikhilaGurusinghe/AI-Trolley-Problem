from typing import Callable

from services.neural_network.models.utils.NetworkType import NetworkType
from common.websocket.server import Server


class NeuralNetworkServer(Server):
    def __init__(self, host_name: str, port_number: int):
        all_my_methods: dict[str, Callable[..., str]] = {
            name: getattr(self, name)
            for name, value in self.__class__.__dict__.items()
            if callable(value) and not name.startswith("_") # filter out private methods (i.e. those that start with "_")
        }
        super().__init__(host_name, port_number, all_my_methods)

    def getNetworkStructure(self, networkType: NetworkType) -> str:
        if int(networkType) < 0 or int(networkType) >= len(NetworkType):
            raise Exception("NeuralNetworkServer#getNetworkStructure(): failed to execute (invalid arguments)")

        return "insert network structure here " + str(networkType)