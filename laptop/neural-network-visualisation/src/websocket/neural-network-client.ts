import Client from "./client.ts";

export default class NeuralNetworkClient extends Client {
    async getNetworkStructure(network: any) {
        return this.send("get", [...arguments]);
    }

}