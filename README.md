# AgriFieldGenerator

AgriFieldGenerator is a Python application that generates agricultural field data based on various parameters.

## Dependencies

This project requires the following Python libraries :

- argparse
- numpy
- matplotlib
- svgwrite
- svgpathtools
- scipy
- shapely
- rasterio
- tqdm

## Installation

1. Clone this repository:

```bash
git clone https://github.com/yourusername/AgriFieldGenerator.git
```

2. Navigate to the project directory :

```bash
cd AgriFieldGenerator
```

3. Install the required Python libraries :

```bash
pip install -r requirements.txt
```

## Usage

You can run the AgriFieldGenerator with various command line arguments. For example :

```bash
python run.py --points --generator random --voronoi
```

This command will generate points using a random generator and then generate a Voronoi diagram based on these points.

For more information about the available command line arguments, run:

```bash
python run.py --help
```