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

### 1. Clone this repository:

```bash
git clone https://github.com/yourusername/AgriFieldGenerator.git
```

### 2. Navigate to the project directory :

```bash
cd AgriFieldGenerator
```

### 3. Install the required Python libraries :

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

## Step by step guide

### 1. Generate the svg file

You need to use an external tool, like GIMP :
-  Load your satellite map in GIMP
-  Make a path to delimit the polygon
-  Export this path to svg file

### 2. Create your work directory structure

Somewhere on your computer, create the following structure:
```
work/
    ProjectName/
        sources/
```
Copy your svg file in the sources directory

### 3. Edit the config.json.example file

```json
{
    "work_dir": "/path/to/your/workdir/", <- Path to your work dir
    "project_name": "YourProjectName",    <- Well... Your project name, named like your ProjectName directory
    "source_files": {
        "svg_filename": "NameOfYourSVGFile.svg", <- Your svg file
        "svg_height": 16257, <- height of your satmap, must the same as your svg file and your terrain in Enfusion
        "svg_width": 16257,  <- idem, but for the width
        "tile_size": 512     <- tile size in Enfusion
    },
    "enfusion_texture_masks": {
        "etm_path": "/path/to/your/enfusion/texture/surface/masks", <- Surface texture mask. They must of course have been exported previously via the Enfusion Workbench
        "etm_1": "Crop_Field_01.png", <- First surface mask. Maximum is 4 surface masks. 
        "etm_2": "Crop_Field_02.png", <- Second surface mask
        "etm_3": "ZI_Crop_Field_03.png", <- Third surface mask
        "etm_4": "Grass_02.png" <- Fourth and last surface mask
    },
    "palette": ["#89723e", "#4f4333", "#7e895e", "#3a4422"], <- RGB color code for the preview. The first color is for the first surface texture and so on
    "borders": {
        "min_border_width":0.1, <- borders between fields. Randomly generated between min and max
        "max_border_width":5
    },
    "point_generators":{ <- point generators parameters. Experiment with them ;-)
        "random": {
            "num_points": 50
        },
        "grid": {
                "nx":10,
                "ny":10,
                "rand_offset_x":5,
                "rand_offset_y":5,
                "rand_step_x":2,
                "rand_step_y":5,
                "angle":240
        },
        "rectangle": {
                "num_rectangles":10,
                "min_width":1,
                "max_width":5,
                "min_height":1,
                "max_height":5
        }
    },
    "paths": {
        "__comment": "Don't modify anything here, unless you know what you are doing !",
        "source_dir": "sources/",
        "save_dir": "saves/",
        "save_data_dir": "data/"
    }
}
```
Save this file as config.json

### 4. Launch the script (cf. usage)

For example :

```python
python run.py -a
```
