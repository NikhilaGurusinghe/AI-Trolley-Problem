import Client, {type NotificationMethod} from "./client.ts";
import Structure, {
    type BiasesArray,
    type TrolleyProblemModelStructure,
    type WeightsArray
} from "../network-structure/trolley-problem-model/structure.ts";
import {NetworkType} from "../network-structure/network-type.ts";

export class NeuralNetworkClient extends Client {
    // TODO this needs to have a service that stores network-structure data structures

    private readonly trolleyProblemModel: Structure;

    constructor(hostName: string, portNumber: number) {
        super(hostName, portNumber);

        // we do this manually cause it seems really difficult to do this automatically in typescript :/
        this.allowedNotificationMethods.set("setNetworkStructure", this.setNetworkStructure);
        console.log(this.allowedNotificationMethods)

        this.trolleyProblemModel = new Structure();
    }

    public async getNetworkStructure(network: NetworkType): Promise<void> {
        return this.send("get_network_structure", [network]);
    }

    // TODO networkType stuff -- add a switch statement
    // TODO finish this!!!!
    public setNetworkStructure(structurePayload: string, networkType: string): void {
        console.log("NeuralNetworkClient#setNetworkStructure(): setting network structure!");
        console.log(structurePayload);

        let structureJSON: unknown;
        try {
            structureJSON = JSON.parse(structurePayload);
        } catch (e) {
            throw new Error(`NeuralNetworkClient#setNetworkStructure(): received malformed response ${e}`);
        }

        switch (parseInt(networkType, 10)) {
            case NetworkType.SPRITE_RECOGNITION_MODEL: {
                break;
            }
            case NetworkType.TROLLEY_PROBLEM_MODEL: {
                // TODO do error checking here before this cast
                const structure: TrolleyProblemModelStructure = structureJSON as TrolleyProblemModelStructure;

                console.log(structure["layer_1.weight"], structure["layer_1.bias"]);
                console.log(structure["layer_2.weight"], structure["layer_2.bias"]);
                console.log(structure["layer_3.weight"], structure["layer_3.bias"]);


                break;
            }
            default: {
                throw new Error(`NeuralNetworkClient#setNetworkStructure(): received malformed arguments`);
            }
        }







    }
}