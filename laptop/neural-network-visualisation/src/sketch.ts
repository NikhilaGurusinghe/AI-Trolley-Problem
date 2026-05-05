import p5 from "p5";
import Client from "./websocket/client.ts";
import {NeuralNetworkClient, NetworkType} from "./websocket/neural-network-client.ts";

const WEBSOCKET_PORT_NUMBER: number = 8001;
const WEBSOCKET_HOST_NAME: string = "localhost";

const sketch = (p5: p5): void => {
	let websocket: NeuralNetworkClient;

	p5.setup = async () => {
		p5.createCanvas(p5.windowWidth, p5.windowHeight);

		websocket = new NeuralNetworkClient(WEBSOCKET_HOST_NAME, WEBSOCKET_PORT_NUMBER);
        console.log(await websocket.getNetworkStructure(NetworkType.TROLLEY_PROBLEM_MODEL));
	};

	p5.draw = () => {
		p5.background(180);
		p5.ellipseMode(p5.CENTER);
		p5.fill(255, 0, 0);
		p5.noStroke();
		p5.ellipse(p5.mouseX, p5.mouseY, 50, 50);
	};

	// resize the canvas if our window is resized
	p5.windowResized = () : void => {
		p5.resizeCanvas(p5.windowWidth, p5.windowHeight);
	}
};

new p5(sketch);
