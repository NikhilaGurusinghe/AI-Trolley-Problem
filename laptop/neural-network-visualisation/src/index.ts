import p5 from "p5";

const sketch = (p: p5) => {
	p.setup = () => {
		p.createCanvas(800, 600);
	};

	p.draw = () => {
		p.background(180);
		p.ellipseMode(p.CENTER);
		p.fill(255, 0, 0);
		p.noStroke();
		p.ellipse(p.mouseX, p.mouseY, 50, 50);
	};
};

const myp5 = new p5(sketch, document.body);
