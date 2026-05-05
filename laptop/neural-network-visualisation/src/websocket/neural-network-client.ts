import Client from "./client.ts";

export enum NetworkType {
    TROLLEY_PROBLEM_MODEL,
    SPRITE_RECOGNITION_MODEL
}

export class NeuralNetworkClient extends Client {
    public async getNetworkStructure(network: NetworkType) {
        return this.send("getNetworkStructure", [...arguments]);
    }
}