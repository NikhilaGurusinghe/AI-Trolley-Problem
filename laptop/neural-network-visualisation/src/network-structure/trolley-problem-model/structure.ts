import Layer from "./layer.ts"
import Neuron from "./neuron.ts"
import * as assert from "node:assert";

export default class Structure {

    private readonly layers: Layer[];

    public constructor(allWeightsAndBiases: [number[][], number[]][]) {
        this.layers = [];

        for (let layerIndex: number = 0; layerIndex < allWeightsAndBiases.length; layerIndex++) {
            let [weights, biases]: [number[][], number[]] = allWeightsAndBiases[layerIndex] as [number[][], number[]];

            // should be the same length as there will be the same amount of neurons
            // for weights there might be multiple per neuron, but always a single bias per neuron
            assert.ok(weights.length === biases.length)

            let layerNeurons: Neuron[] = []

            for (let neuronIndex: number = 0; neuronIndex < weights.length; neuronIndex++) {
                let neuronWeights: number[] = weights[neuronIndex] as number[];
                let neuronBias: number = biases[neuronIndex] as number;

                layerNeurons.push(new Neuron(neuronWeights, neuronBias));
            }

            let newLayer: Layer = new Layer(layerNeurons);
            this.layers.push(newLayer);
        }
    }

    public getNumberOfLayers() : number {
        return this.layers.length;
    }

    // layerIndex is zero indexed
    public getNumberOfNeuronsInLayer(layerIndex: number) : number | undefined {
        let layer: Layer | undefined = this.getLayer(layerIndex);
        if (layer === undefined) return undefined;

        return layer.getNumberOfNeurons();
    }

    private getLayer(layerIndex: number): Layer | undefined {
        if (layerIndex >= this.layers.length) return undefined;

        return this.layers[layerIndex] as Layer;
    }

    private getNeuron(layerIndex: number, neuronIndex: number): Neuron | undefined {
        let layer: Layer | undefined = this.getLayer(layerIndex);
        if (layer === undefined) return undefined;

        return layer.getNeuron(neuronIndex);
    }

    public getOutputImportancesForNeuron(layerIndex: number, neuronIndex: number): number[] | undefined {
        let neuron: Neuron | undefined = this.getNeuron(layerIndex, neuronIndex);
        if (neuron === undefined) return undefined;

        // TODO math here


        return [];
    }
}