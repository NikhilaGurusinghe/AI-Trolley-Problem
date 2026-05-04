import Client from "./client.ts";

export default class NeuralNetworkClient extends Client {
    async getNetworkDetails(network: any) {
        return this.send("get", [...arguments]);
    }

}