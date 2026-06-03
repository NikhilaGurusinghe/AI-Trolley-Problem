import Layer from "./layer.ts"
import Neuron from "./neuron.ts"
import * as assert from "node:assert";

export type WeightsArray = number[][];
export type BiasesArray = number[];

export type TrolleyProblemModelStructure = {
    "layer_1.weight": WeightsArray;
    "layer_1.bias": BiasesArray;
    "layer_2.weight": WeightsArray;
    "layer_2.bias": BiasesArray;
    "layer_3.weight": WeightsArray;
    "layer_3.bias": BiasesArray
}

export function convertToTrolleyProblemModelStructure(structureJSON: any): TrolleyProblemModelStructure | undefined {
    if (structureJSON["layer_1.weight"] === undefined ||
        structureJSON["layer_1.bias"] === undefined ||
        structureJSON["layer_2.weight"] === undefined ||
        structureJSON["layer_2.bias"] === undefined ||
        structureJSON["layer_3.weight"] === undefined ||
        structureJSON["layer_3.bias"] === undefined) {
        return undefined;
    } else {
        return structureJSON as TrolleyProblemModelStructure;
    }
}

export default class Structure {

    private readonly layers: Layer[];

    public constructor(allWeightsAndBiases?: [WeightsArray, BiasesArray][]) {
        this.layers = [];

        if (allWeightsAndBiases !== undefined) {
            this.initialize(allWeightsAndBiases)
        }
    }

    public initialize(allWeightsAndBiases: [WeightsArray, BiasesArray][]): void {
        for (let layerIndex: number = 0; layerIndex < allWeightsAndBiases.length; layerIndex++) {
            const [weights, biases]: [WeightsArray, BiasesArray] = allWeightsAndBiases[layerIndex] as [number[][], number[]];

            // should be the same length as there will be the same amount of neurons
            // for weights there might be multiple per neuron, but always a single bias per neuron
            assert.ok(weights.length === biases.length)

            const layerNeurons: Neuron[] = []

            for (let neuronIndex: number = 0; neuronIndex < weights.length; neuronIndex++) {
                const neuronWeights: number[] = weights[neuronIndex] as number[];
                const neuronBias: number = biases[neuronIndex] as number;

                layerNeurons.push(new Neuron(neuronWeights, neuronBias));
            }

            const newLayer: Layer = new Layer(layerNeurons);
            this.layers.push(newLayer);
        }
    }

    public getNumberOfLayers() : number {
        // + 1 for "fake" input layer
        return this.layers.length + 1;
    }

    // layerIndex is zero indexed
    public getNumberOfNeuronsInLayer(layerIndex: number) : number | undefined {
        if (layerIndex < 0) return undefined;

        if (layerIndex === 0) {
            // infer input layer neurons number from the first hidden layer's incoming weights array size
            if (this.layers[0] === undefined) {
                return undefined;
                //throw new Error("Structure.getNumberOfNeuronsInLayer(): had no layers")
            }

            // checking there's a neuron here
            const firstLayer: Layer = this.layers[0];

            // getting just the first neuron and getting the length of its weights array
            const neuron: Neuron | undefined = firstLayer.getNeuron(0);
            if (neuron === undefined) {
                return undefined;
                //throw new Error("Structure.getNumberOfNeuronsInLayer(): had no neurons in layer 0")
            }
            const weightsArray: number[] = neuron.getWeights();
            return weightsArray.length;
        } else {
            const layer: Layer | undefined = this.getLayer(layerIndex);
            if (layer === undefined) return undefined;

            return layer.getNumberOfNeurons();
        }
    }

    // 0 = input layer doesn't exist here, 1..N = layers stored in this structure object
    private getLayer(layerIndex: number): Layer | undefined {
        if (layerIndex === 0) {
            // there is no Layer object for the input layer
            return undefined;
        }
        const internalIndex: number = layerIndex - 1;
        if (internalIndex >= this.layers.length) return undefined;
        return this.layers[internalIndex] as Layer;
    }

    private getNeuron(layerIndex: number, neuronIndex: number): Neuron | undefined {
        const layer: Layer | undefined = this.getLayer(layerIndex);
        if (layer === undefined) return undefined;

        return layer.getNeuron(neuronIndex);
    }

    public getOutputImportancesForNeuron(layerIndex: number, neuronIndex: number): number[] | undefined {
        // we actually need to get the importances for the next layer
        // if this is the final layer there are no outputs
        if (layerIndex >= this.getNumberOfLayers() - 1 || neuronIndex < 0) return undefined;
        const nextLayer: Layer | undefined = this.getLayer(layerIndex + 1);
        if (nextLayer === undefined) return undefined;

        const outputImportances: number[] = [];
        const nextLayerSize: number = nextLayer.getNumberOfNeurons();

        // for each neuron in the next layer compute importance from weights + biases
        for (let nextNeuronIndex: number = 0; nextNeuronIndex < nextLayerSize; nextNeuronIndex++) {
            const nextNeuron: Neuron | undefined = nextLayer.getNeuron(nextNeuronIndex);

            if (nextNeuron === undefined) {
                outputImportances.push(0);
                // throw new Error("Structure.getOutputImportancesForLayer(): encountered invalid neuron in" +
                //     " layer");
                continue;
            }

            const weights: number[] = nextNeuron.getWeights();
            if (neuronIndex >= weights.length) {
                outputImportances.push(0);
                continue;
                // throw new Error("Structure.getOutputImportancesForLayer(): neuronIndex parameter was larger " +
                //     "than the number of weights in layer");
            }
            let weight: number = weights[neuronIndex] as number;
            const bias: number = nextNeuron.getBias();
            const importance: number = weight * (1 + Math.abs(bias));
            outputImportances.push(importance);
        }

        return outputImportances;
    }
}