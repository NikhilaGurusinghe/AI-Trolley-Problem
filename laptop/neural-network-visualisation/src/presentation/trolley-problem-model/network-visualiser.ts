import p5 from "p5";
import Structure from "../../network-structure/trolley-problem-model/structure.ts";

export class NetworkVisualiser {

    // TODO this is probably gonna cause a bug lol
    private readonly p5: p5;
    private readonly trolleyProblemModel: Structure;

    constructor(trolleyProblemModel: Structure, p5: p5) {
        this.trolleyProblemModel = trolleyProblemModel;
        this.p5 = p5;
    }

    // assume this draw is drawing the network on a portrait display
    public draw(): void {
        const layerCount: number = this.trolleyProblemModel.getNumberOfLayers();
        if (layerCount === 0) return;

        const canvasWidth: number = this.p5.width;
        const canvasHeight: number = this.p5.height;

        const marginX: number = canvasWidth * 0.12;
        const marginY: number = canvasHeight * 0.1;

        // width here is the width of the display in normal orientation (not portrait)
        const usableWidth: number = Math.max(1, canvasWidth - marginX * 2);
        const usableHeight: number = Math.max(1, canvasHeight - marginY * 2);

        const layerGap: number = usableWidth / (layerCount - 1);

        const layerPositions: p5.Vector[][] = [];

        // get locations of neurons per layer and store in layerPositions
        for (let layerIndex: number = 0; layerIndex < layerCount; layerIndex++) {
            const neuronCount: number = this.trolleyProblemModel.getNumberOfNeuronsInLayer(layerIndex) ?? 0;

            const neuronPositions: p5.Vector[] = [];
            if (neuronCount > 0) {
                const verticalGap: number = neuronCount > 1 ? usableHeight / (neuronCount - 1) : 0;
                const xPos: number = marginX + layerGap * layerIndex;
                for (let neuronIndex: number = 0; neuronIndex < neuronCount; neuronIndex++) {
                    const yPos: number = marginY + verticalGap * neuronIndex;
                    neuronPositions.push(this.p5.createVector(xPos, yPos));
                }
            }

            layerPositions.push(neuronPositions);
        }

        const nodeRadius: number = 20;
        const minStrokeWeight: number = 1;
        const maxStrokeWeight: number = 3;
        const positiveStrokeColour: p5.Color = this.p5.color(24, 144, 255, 200);
        const neutralStrokeColour: p5.Color = this.p5.color(140, 140, 140, 200);
        const negativeStrokeColour: p5.Color = this.p5.color(255, 88, 88, 200);
        const nodeColour: p5.Color = this.p5.color(245, 245, 245, 255);

        // start drawing
        // draw connections
        this.p5.push();
        for (let layerIndex: number = 0; layerIndex < layerCount - 1; layerIndex++) {
            const currentLayer: p5.Vector[] = layerPositions[layerIndex] ?? [];
            const nextLayer: p5.Vector[] = layerPositions[layerIndex + 1] ?? [];

            // collect per-neuron importance arrays
            const importances: number[][] = [];
            for (let currNeuronIndex: number = 0; currNeuronIndex < currentLayer.length; currNeuronIndex++) {
                importances.push(this.trolleyProblemModel.getOutputImportancesForNeuron(layerIndex, currNeuronIndex) ?? []);
            }

            // compute the max across a layer to normalize all values
            let layerAbsoluteMax = 0;
            for (let importancesIndex = 0; importancesIndex < importances.length; importancesIndex++) {
                const importance: number[] | undefined = importances[importancesIndex];
                if (!importance) continue;
                for (let neuronIndex = 0; neuronIndex < importance.length; neuronIndex++) {
                    const neuronImportance: number = importance[neuronIndex] as number;
                    const absoluteNeuronImportance: number = Math.abs(neuronImportance);
                    if (absoluteNeuronImportance > layerAbsoluteMax) layerAbsoluteMax = absoluteNeuronImportance;
                }
            }

            // draw each connection using signed importance -> color, magnitude -> weight/alpha
            for (let currNeuronIndex: number = 0; currNeuronIndex < currentLayer.length; currNeuronIndex++) {
                const currNeuronPos: p5.Vector | undefined = currentLayer[currNeuronIndex];
                if (!currNeuronPos) continue;

                for (let nextNeuronIndex: number = 0; nextNeuronIndex < nextLayer.length; nextNeuronIndex++) {
                    const nextNeuronPos: p5.Vector | undefined = nextLayer[nextNeuronIndex];
                    if (!nextNeuronPos) continue;

                    const importance: number = importances[currNeuronIndex]?.[nextNeuronIndex] ?? 0;
                    const absoluteImportance: number = Math.abs(importance);
                    const normalizedAbsImportance: number = layerAbsoluteMax > 0 ?
                                                            (absoluteImportance / layerAbsoluteMax) : 0;

                    // stroke weight and alpha
                    const strokeWeight: number = minStrokeWeight + normalizedAbsImportance *
                                                 (maxStrokeWeight - minStrokeWeight);

                    // lerp colours between negative and positive
                    let strokeColour: p5.Color;
                    if (layerAbsoluteMax <= 0) {
                        strokeColour = neutralStrokeColour;
                    } else {
                        // signed normalization in [-1, 1]
                        const signedNorm: number = importance / layerAbsoluteMax;
                        // map to [0,1] for lerp (0 => negative, 1 => positive)
                        const amount: number = Math.max(0, Math.min(1, (signedNorm + 1) / 2));
                        strokeColour = this.p5.lerpColor(negativeStrokeColour, positiveStrokeColour, amount);
                    }

                    this.p5.push();
                    this.p5.stroke(strokeColour);
                    this.p5.strokeWeight(strokeWeight);
                    this.p5.line(currNeuronPos.x, currNeuronPos.y, nextNeuronPos.x, nextNeuronPos.y);
                    this.p5.pop();
                }
            }
        }
        this.p5.pop();


        // draw neurons on top
        this.p5.push();
        this.p5.noStroke();
        this.p5.fill(nodeColour);
        for (let layerIndex: number = 0; layerIndex < layerCount; layerIndex++) {
            const neuronPositions: p5.Vector[] = layerPositions[layerIndex] ?? [];
            for (let neuronIndex: number = 0; neuronIndex < neuronPositions.length; neuronIndex++) {
                const neuronPos: p5.Vector | undefined = neuronPositions[neuronIndex];
                if (!neuronPos) continue;

                this.p5.circle(neuronPos.x, neuronPos.y, nodeRadius * 2);
            }
        }
    }
}