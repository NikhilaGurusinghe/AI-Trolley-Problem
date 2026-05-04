import * as assert from "node:assert";

export default class Neuron {
    private weights: number[];
    private bias: number;

    public constructor(weights: number[], bias: number) {
        assert.ok(weights.length > 0);
        assert.ok(weights.length);

        this.weights = weights;
        this.bias = bias;
    }

    public updateWeightsAndBiases(newWeights: number[], newBias: number): void {
        this.weights = newWeights;
        this.bias = newBias;
    }

    public getWeights(): number[] {
        return this.weights;
    }

    public getBias(): number {
        return this.bias;
    }
}