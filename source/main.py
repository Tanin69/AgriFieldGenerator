from processing import SVGToPolygon

#parameters
svg_file = 'D:/Dev/Python/FieldsGenerator/files/svg/20240512_zoneOuest.svg'
svg_height = 16257
svg_width = 16257
num_points = 200
debug = False

svg_to_polygon = SVGToPolygon(svg_height, svg_width, num_points, debug)
polygon = svg_to_polygon.transform(svg_file)
svg_to_polygon.display(polygon)
