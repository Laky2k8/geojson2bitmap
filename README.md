# geojson2bitmap

A very simple but versatile Python script that takes in EPSG:3035 GeoJSON files and produces a png color-coded map along with a CSV lookup table.
Originally created for some Wii homebrew but you may use it in anything you wish :)

## How to use
```py
usage: convert.py [-h] [--bitmap_size BITMAP_SIZE] [--bounding_box BOUNDING_BOX] [--verbose VERBOSE] input_file output_name

positional arguments:
  input_file
  output_name

options:
  -h, --help            show this help message and exit
  --bitmap_size BITMAP_SIZE
  --bounding_box BOUNDING_BOX
  --verbose VERBOSE
```

## Required libraries
- geopandas
- pillow

## Examples
<img width="1920" height="1080" alt="map24" src="https://github.com/user-attachments/assets/bc4200ab-efc4-4454-bc3e-9c9b1997f461" />

*PNG generated from NUTS 3 2024*
