# How to Run
1. Install uv (https://docs.astral.sh/uv/getting-started/installation/#installation-methods)
2. Install python 3.14 using uv (https://docs.astral.sh/uv/guides/install-python/). Run the following command:
```
uv python install 3.14
```
3. Then with your terminal environment in this directory run the following to sync dependencies via uv
```
uv sync
```
4. The to run the script, run this from this directory
```
uv run ./src/main.py
```

* Ensure that the arduino track selection interface is plugged in before running this script, and if it isn't detected
on the right COM port, change the COM port in line 42 of ./src/main.py