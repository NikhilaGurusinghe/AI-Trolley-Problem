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
        return this.layers.length;
    }

    // layerIndex is zero indexed
    public getNumberOfNeuronsInLayer(layerIndex: number) : number | undefined {
        const layer: Layer | undefined = this.getLayer(layerIndex);
        if (layer === undefined) return undefined;

        return layer.getNumberOfNeurons();
    }

    private getLayer(layerIndex: number): Layer | undefined {
        if (layerIndex >= this.layers.length) return undefined;

        return this.layers[layerIndex] as Layer;
    }

    private getNeuron(layerIndex: number, neuronIndex: number): Neuron | undefined {
        const layer: Layer | undefined = this.getLayer(layerIndex);
        if (layer === undefined) return undefined;

        return layer.getNeuron(neuronIndex);
    }

    public getOutputImportancesForNeuron(layerIndex: number, neuronIndex: number): number[] | undefined {
        const neuron: Neuron | undefined = this.getNeuron(layerIndex, neuronIndex);
        if (neuron === undefined) return undefined;

        // TODO math here


        return [];
    }
}