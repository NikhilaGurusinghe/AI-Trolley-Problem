import Neuron from "./neuron.ts"
import * as assert from "node:assert";

export default class Layer {
    private readonly neurons: Neuron[];

    public constructor(neurons: Neuron[]) {
        this.neurons = neurons;
    }

    public getNeuron(neuronIndex: number): Neuron | undefined {
        if (neuronIndex >= this.neurons.length) return undefined;

        return this.neurons[neuronIndex] as Neuron;
    }

    public getNumberOfNeurons(): number {
        return this.neurons.length;
    }
}