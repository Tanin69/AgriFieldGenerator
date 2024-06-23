# AgriFieldGenerator

AFG is a python application that allows you to generate large agricultural landscapes for Bohemia's Enfusion engine with little effort. It is based on Voronoi tessellation.

1. [Dependencies](#dependencies)
2. [Installation](#installation)
3. [Usage](#usage)
4. [Step by step guide](#step-by-step-guide)
5. [Changelog](#changelog)
6. [Backlog](#backlog)

## 1. Dependencies <a name="dependencies">

See or use requirements.txt

## 2. Installation <a name="installation">

### a. Clone this repository :

```bash
git clone https://github.com/Tanin69/AgriFieldGenerator.git
```

### b. Navigate to the project directory :

```bash
cd AgriFieldGenerator
```

### c. Install the required Python libraries :

```bash
pip install -r requirements.txt
```

## 3. Usage <a name="usage">

You can run the AgriFieldGenerator with various command line arguments. For example :

```bash
python run.py --points --generator random --voronoi
```

This command will generate points using a random generator and then generate a Voronoi diagram based on these points.

```shell
usage: run.py [-h] [-s] [-po] [-pt] [-g {random,grid,rectangle,rect_tiling}] [-v] [-pp [[0-1]]] [-c] [-m] [-me] [-pl] [-a] [-d {main_polygon,seed_points,voronoi}]

Run the AgriFieldGenerator.

options:
  -h, --help            show this help message and exit
  -s, --svg             Generates a svg file from an Enfusion layer file containing spline entities.
  -po, --polygon        Generates the main polygon from svg file.
  -pt, --points         Generates points schema.
  -g {random,grid,rectangle}, --generator {random,grid,rectangle}
                        Choose the type of point generator.
  -v, --voronoi         Generates the Voronoi diagram.
  -pp [[0-1]], --pp_curve [[0-1]]
                        Curves some random borders. If passed without a value, defaults to 0.5.
  -c, --colorer         Generates the colored polygons.
  -m, --mask            Generates the masks.
  -me, --merge          Merge the masks with Enfusion surface texture masks.
  -pl, --polyline       Generate polylines between polygons.
  -a, --all             Run all the processors.
  -d {main_polygon,seed_points,voronoi}, --display {main_polygon,seed_points,voronoi}
                        Display the results of a given processor.
```

## 4. Step by step guide <a name="step-by-step-guide">

### a. Create your work directory structure

Somewhere on your computer, create the following structure:

- `work/`
  - `ProjectName/`
    - `sources/`
    - `file.png`

### b. Edit the config.json.example file

```json
{
    "work_dir": "/path/to/your/workdir/", <- Path to your work dir
    "project_name": "YourProjectName",    <- Well... Your project name, named like your ProjectName directory
    "source_files": {
        "svg_filename": "output.svg", <- Name of the svg file generated from the Enfusion Spline
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
    "enfusion_surface_map_resolution": 1.000795, <- Surface map resolution as indicated in Enfusion (see terrain tool, info & diag panel, suface mask section, Resolution)
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

### d. Launch the script ([cf. usage](#usage))

For example :

```python
python run.py -a
```

### e. Import your texture masks in Enfusion, and follow the Enfusion process

I've made a tutorial for this (painful) part : see https://docs.google.com/document/d/1Ofb3NplPc76hag4b1zzj7Z689JoD68kPY21FDXRLEo4/edit?usp=sharing

## 5. Changelog <a name="changelog">

- 1.2.0, 2024/06/23
  - Convert Enfusion splines to SVG (new arg to generate svg : -s)
  - Add curvatures to random borders (new arg to generate curved borders : -pp)
  - Refactored display method, now called from super class (new arg : -d <plot to display>)
  - Cleaned imports and updated requirements.txt

- 1.1.0, 2024/05/27 :
  - Generate polylines on borders in Enfusion format
  - List of affected tiles after masks import in Enfusion terrain exported to save_dir/polygon_tiles.txt

- 1.0.0, 2024/05/20 : first release

## 6. Backlog <a name="backlog">

- Use the satellite map as a background image for preview.png
- Add a display method to show Enfusion tiles on the polygon
- Error handling for a potential geometry error when processing svg into polygon
- Take into account the terrain height variations for the generation of points
