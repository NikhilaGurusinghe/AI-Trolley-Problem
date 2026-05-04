import p5 from "p5";

const websocketPort = 8001;

const sketch = (p5: p5): void => {
	p5.setup = () => {
		p5.createCanvas(p5.windowWidth, p5.windowHeight);
		// const websocket: WebSocket = new WebSocket(`ws://localhost:${websocketPort}`);
		// websocket.onopen = () =>  websocket.send(JSON.stringify("hello"));
		// console.log("sent to websocket");

	};

	p5.draw = () => {
		p5.background(180);
		p5.ellipseMode(p5.CENTER);
		p5.fill(255, 0, 0);
		p5.noStroke();
		p5.ellipse(p5.mouseX, p5.mouseY, 50, 50);
	};

	p5.windowResized = () : void => {
		p5.resizeCanvas(p5.windowWidth, p5.windowHeight);
	}
};

new p5(sketch);
