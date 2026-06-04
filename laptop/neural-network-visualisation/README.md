# How to Run
1. Install Bun https://bun.sh/install
2. With Bun installed and your terminal environment in this directory, run the following command to install dependencies
```
bun --version
```
3. Run Bun's bundler
```
bun run watch
```
4. Then serve index.html, you can do this using python (see https://www.python.org/downloads/) e.g.
```
python -m http.server 8000
```
but other methods exist.

* Make sure you run this after you run the python script/server. You know that this script is running when the neural network is visualised on the screen using p5.js.