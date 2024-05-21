# AgriFieldGenerator

AgriFieldGenerator is a Python application that generates agricultural field data based on various parameters.

1. [Dependencies](#dependencies)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Step by step guide](#step-by-step-guide)
5. [Changelog](#changelog)
6. [Backlog](#backlog)

## 1. Dependencies <a name="dependencies">

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

## 2. Installation <a name="installation">

### 1. Clone this repository:

```bash
git clone https://github.com/Tanin69/AgriFieldGenerator.git
```

### 2. Navigate to the project directory :

```bash
cd AgriFieldGenerator
```

### 3. Install the required Python libraries :

```bash
pip install -r requirements.txt
```

## 3. Usage <a name="usage">

You can run the AgriFieldGenerator with various command line arguments. For example :

```bash
python run.py --points --generator random --voronoi
```

This command will generate points using a random generator and then generate a Voronoi diagram based on these points.

For more information about the available command line arguments, run:

```bash
python run.py --help
```

## 4. Step by step guide <a name="step-by-step-guide">

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
        "svg_height": 16257, <- height of your svg in pixels, must be the same as your satmap file and your terrain in Enfusion
        "svg_width": 16257,  <- idem, but for the width
        "tile_size": 512     <- tile size in Enfusion in pixels
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

### 5. Import your texture masks in Enfusion, and follow the Enfusion process

I've made a tutorial for this (painful) part : see https://docs.google.com/document/d/1Ofb3NplPc76hag4b1zzj7Z689JoD68kPY21FDXRLEo4/edit?usp=sharing

## 5. Changelog <a name="changelog">

* 1.0.0, 2024/05/20 : first release
* [not released] 2024/05/21 : list of potentialy affected tiles of Enfusion terrain exported to save_dir/polygon_tiles.txt

## 6. Backlog ## 5. Changelog <a name="backlog">

* Convert Enfusion splines to SVG
* Use the satellite map as a background image for preview.png
* Add a display method to show Enfusion tiles on the polygon
* Error handling for a potential geometry error when processing svg into polygon
* Take into account the terrain height variations for the generation of points

