import p5 from "p5";
import Client from "./websocket/client.ts";

const WEBSOCKET_PORT_NUMBER: number = 8001;
const WEBSOCKET_HOST_NAME: string = "localhost";

const sketch = (p5: p5): void => {
	let websocket: Client;

	p5.setup = () => {
		p5.createCanvas(p5.windowWidth, p5.windowHeight);

		websocket = new Client(WEBSOCKET_HOST_NAME, WEBSOCKET_PORT_NUMBER);

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
