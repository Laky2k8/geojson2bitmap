import geopandas
import sys
import argparse
from PIL import Image, ImageDraw
from shapely.geometry import box
import csv

def int_to_rgb_split(val_16bit):
    # Ensure it stays within 0 - 65535
    val = val_16bit & 0xFFFF
    
    r_bits = (val >> 11) & 0x1F  # 5 bits
    g_bits = (val >> 5)  & 0x3F  # 6 bits
    b_bits = val         & 0x1F  # 5 bits
    
    r = (r_bits * 255) // 31
    g = (g_bits * 255) // 63
    b = (b_bits * 255) // 31
    
    return (r, g, b)

def map_to_pixel(x, y, bbox, bitmap_width, bitmap_height):
	
	# Get bounds
	minX, minY, maxX, maxY = bbox
	dx = maxX - minX
	dy = maxY - minY

	scale = min(bitmap_width / dx, bitmap_height / dy)
	offset_x = (bitmap_width - (dx * scale)) / 2.0
	offset_y = (bitmap_height - (dy * scale)) / 2.0

	pixelX = offset_x + (x - minX) * scale
	pixelY = offset_y + (maxY - y) * scale

	return (round(pixelX), round(pixelY))

def main(input_file, output_name, bitmap_size, min_lat, min_lon, max_lat, max_lon, verbose):
	print("GeoJSON to Bitmap")

	try:
		image = Image.new("RGB", bitmap_size, "white")
		draw = ImageDraw.Draw(image)

		states_data = []

		with open(input_file, "r", encoding="utf-8") as f:
			geo_data = geopandas.read_file(f)

			# Only level 3 subdivisions
			nuts3_data = geo_data[geo_data['LEVL_CODE'].astype(int) >= 3]

			# Set to bounding box
			if(min_lat != 0 and min_lon != 0 and max_lat != 0 and max_lon != 0):
				bbox_4326 = box(min_lon, min_lat, max_lon, max_lat)
				
				# Reproject bounding box into EPSG:3035
				bbox_projected = geopandas.GeoSeries([bbox_4326], crs="EPSG:4326").to_crs(nuts3_data.crs)
				p_minx, p_miny, p_maxx, p_maxy = bbox_projected.total_bounds

				# Get only coords in bounding box
				nuts3_data = nuts3_data.cx[p_minx:p_maxx, p_miny:p_maxy]

			# Get bounds
			bounding_box = nuts3_data.total_bounds

			for index, geom in enumerate(nuts3_data.geometry):

				if verbose:
					print(f"Rendering feature {index}...")

				# Handle Polygons and MultiPolygons
				parts = geom.geoms if geom.geom_type == "MultiPolygon" else [geom]

				for part in parts:
					part_geometry = list(part.exterior.coords)

					pixel_converted = []
					for vertex in part_geometry:
						pixelized_vertex = map_to_pixel(vertex[0], vertex[1], bounding_box, bitmap_size[0], bitmap_size[1])
						pixel_converted.append(pixelized_vertex)

					state_info = {"index": index, "state_name": nuts3_data.iloc[index]['NAME_LATN'], "original_country_code": nuts3_data.iloc[index]['CNTR_CODE']}
					states_data.append(state_info)

					# This converts integers to RGB numbers, this is how we will store the state ID
					state_color = int_to_rgb_split(index)

					draw.polygon(pixel_converted, fill=state_color, outline=state_color, width=3)

			with open(f"{output_name}.csv", "w", encoding="utf-8", newline='') as csv_file:
				field_names = ["index", "state_name", "original_country_code"]
				writer = csv.DictWriter(csv_file, fieldnames=field_names, delimiter=";")
				writer.writeheader()
				writer.writerows(states_data)
			print(f"States info saved to {output_name}.csv")

			image.save(f"{output_name}.png")
			print(f"Map saved as image to {output_name}.png")

	except Exception as e:
		print(f"An error occured while converting your map: {e}")
		print("If this error is a problem with the program, please create an issue on GitHub so that it may be solved! Thank you :)")




def parse_size(arg):
    return [int(x) for x in arg.split(',')]

def parse_size_float(arg):
    return [float(x) for x in arg.split(',')]

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("input_file")
	parser.add_argument("output_name")
	parser.add_argument("--bitmap_size", type=parse_size, default=[1920, 1080])
	parser.add_argument("--bounding_box", type=parse_size_float, default=[0,0,0,0])
	parser.add_argument("--verbose", type=bool, default=False)
	args = parser.parse_args()

	main(args.input_file, args.output_name, args.bitmap_size, args.bounding_box[0], args.bounding_box[1], args.bounding_box[2], args.bounding_box[3], args.verbose)


