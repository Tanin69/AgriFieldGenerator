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
- networkx

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

## Configuration

The application is configured using a `config.json` file. Here is a brief explanation of the configuration parameters:

- `project_name`: The name of the project.
- `source_files`: Contains parameters related to the source SVG file.
- `enfusion_texture_masks`: Contains parameters related to the texture masks.
- `palette`: An array of color codes used in the application.
- `paths`: Contains paths for various directories used in the application.
- `borders`: Contains parameters related to the borders of the generated fields.
- `point_generators`: Contains parameters for the different point generators.

For more detailed information about each parameter, please refer to the `config.json` file.

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