import Client, {type NotificationMethod} from "./client.ts";
import Structure, {
    type BiasesArray, convertToTrolleyProblemModelStructure,
    type TrolleyProblemModelStructure,
    type WeightsArray
} from "../network-structure/trolley-problem-model/structure.ts";
import {NetworkType} from "../network-structure/network-type.ts";

export type CallbackMethod = () => void;

export class NeuralNetworkClient extends Client {
    public readonly trolleyProblemModel: Structure;

    // callbacks for things that want to be updated when the model is updated via a notification message from the server
    private modelUpdateCallbacks: (CallbackMethod)[] = [];

    constructor(hostName: string, portNumber: number) {
        super(hostName, portNumber);

        // we do this manually cause it seems really difficult to do this automatically in typescript :/
        this.allowedNotificationMethods.set("setNetworkStructure", this.setNetworkStructure.bind(this));
        console.log(this.allowedNotificationMethods)

        this.trolleyProblemModel = new Structure();
    }

    // public async getNetworkStructure(network: NetworkType): Promise<void> {
    //     return this.send("get_network_structure", [network]);
    // }

    public onModelUpdate(callback: CallbackMethod): void {
        this.modelUpdateCallbacks.push(callback);
    }

    private notifyModelUpdateSubscribers(): void {
        for (const callbacks of this.modelUpdateCallbacks) {
            try {
                callbacks();
            } catch (e) {
                console.error("NeuralNetworkClient.notifyModelUpdateSubscribers(): modelUpdate callback " +
                    "failed", e);
            }
        }
    }

    // TODO finish this!!!!
    public setNetworkStructure(structurePayload: string, networkType: string): void {
        console.log("NeuralNetworkClient#setNetworkStructure(): setting network structure!");
        console.log(structurePayload);

        let structureJSON: any;
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
                const structure: TrolleyProblemModelStructure | undefined =
                    convertToTrolleyProblemModelStructure(structureJSON);
                if (structure === undefined) {
                    throw new Error("NeuralNetworkClient#setNetworkStructure(): received bad neural network" +
                        " structure JSON");
                }

                console.log(structure["layer_1.weight"], structure["layer_1.bias"]);
                console.log(structure["layer_2.weight"], structure["layer_2.bias"]);
                console.log(structure["layer_3.weight"], structure["layer_3.bias"]);

                this.trolleyProblemModel.initialize([[structure["layer_1.weight"], structure["layer_1.bias"]],
                                                     [structure["layer_2.weight"], structure["layer_2.bias"]],
                                                     [structure["layer_3.weight"], structure["layer_3.bias"]]]);

                this.notifyModelUpdateSubscribers();

                break;
            }
            default: {
                throw new Error(`NeuralNetworkClient#setNetworkStructure(): received malformed arguments`);
            }
        }
    }
}