# Wave Function Collapse

Wave Function Collapse (WFC) is a procedural content generation algorithm inspired by quantum mechanics, widely used for generating tile-based maps, textures, and levels in games and simulations. This project provides a modular Python implementation of WFC, complete with visualization tools using both Matplotlib and Pygame.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Assets](#assets)
- [Examples](#examples)
- [References](#references)
- [License](#license)

## Overview
This repository implements the Wave Function Collapse algorithm for generating 2D tile-based maps. The project is designed for flexibility and extensibility, allowing users to experiment with different tile sets, constraints, and rendering backends.

## Features
- Modular WFC core logic
- Support for custom tile sets and adjacency rules
- Visualization with Matplotlib and Pygame
- Example assets and tile images
- Jupyter notebook for interactive exploration

## Installation
1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd "Wave Function Collapse"
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   Ensure you have Python 3.10+ installed.

## Usage
### Running the Main Script
To generate a map and render it:
```bash
python main.py
```
This will execute the WFC algorithm using the default settings and render the output using the selected backend.

### Using the Jupyter Notebook
Open `WFC.ipynb` for an interactive demonstration and experimentation with the algorithm and parameters.

### Rendering Options
- **Matplotlib:** For static image rendering.
- **Pygame:** For interactive or animated visualization.

You can select the renderer in `main.py` or by modifying the relevant code in the `render/` directory.

## Project Structure
```
main.py                  # Entry point for running WFC and rendering
requirements.txt         # Python dependencies
WFC.ipynb                # Jupyter notebook for interactive exploration
assets/
  basic_package.png      # Example tile package
  tiles/                 # Individual tile images
core/
  cell.py                # Cell and state representation
  tiles.py               # Tile definitions and adjacency rules
  wfc.py                 # Core WFC algorithm implementation
render/
  matplotlib_render.py   # Matplotlib-based renderer
  pygame_render.py       # Pygame-based renderer
```

## Assets
The `assets/tiles/` directory contains example tile images (e.g., grass, road, wall, water) used by the algorithm. You can add your own tiles or modify existing ones to experiment with different map styles.

## Examples
To generate a map with the default tile set and render it:
```bash
python main.py
```
To use a different renderer or tile set, edit the configuration in `main.py` or the relevant files in `core/` and `render/`.

## References
- [Wave Function Collapse Algorithm by Maxim Gumin](https://github.com/mxgmn/WaveFunctionCollapse)
- [PCG: Wave Function Collapse explained](https://www.redblobgames.com/articles/wavefunction-collapse/)

## License
This project is licensed under the MIT License. See `LICENSE` for details.
