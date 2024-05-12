import svgwrite

positions = [
    (-501.535, 0.302, 186.551),
    (-547.014, 0.003, 620.104),
    (-575.112, -0, 855.37),
    (-502.606, -0.003, 1183.148),
    (-364.744, -0.002, 1415.647),
    (-634.59, -0.002, 1846.118),
    (-1559.814, 4.527, -110.379),
    (-1359.838, 0.391, -341.471),
    (-447.307, -0.001, -444.686),
    (-440.015, -0.003, -110.028),
    (-361.639, 0.003, -12.579)
]

tangents = [
    (None, None),  # No tangents for the first point
    (None, None),  # No tangents for the second point
    (None, None),  # No tangents for the third point
    (None, None),  # No tangents for the fourth point
    (None, None),  # No tangents for the fifth point
    ((-597.535, 2.264, -763.013), (-510.741, 2.923, -1188.752)),  # Tangents for the sixth point
    (None, None),  # No tangents for the seventh point
    (None, None),  # No tangents for the eighth point
    ((459.912, -0.197, 115.721), (30.114, -0.026, 141.407)),  # Tangents for the ninth point
    (None, None),  # No tangents for the tenth point
    (None, None)  # No tangents for the eleventh point
]

def convert_coordinates(positions, initial_coords):
    half_size = 16384 / 2
    return [(half_size - (y + initial_coords[1]), z + initial_coords[2], x + half_size + initial_coords[0]) for (x, z, y) in positions]

def convert_spline_shape_entity(entity):
    initial_coords = entity['coords']
    points = entity['Points']
    converted_points = []
    for point in points:
        relative_position = point['Position']
        absolute_position = (initial_coords[0] + relative_position[0], initial_coords[1] + relative_position[1], initial_coords[2] + relative_position[2])
        converted_position = convert_coordinates([absolute_position], initial_coords)[0]
        converted_points.append(converted_position)
    return converted_points

def generate_svg(positions, tangents, output_file):
    dwg = svgwrite.Drawing(output_file, profile='tiny', size=("16384px", "16384px"), viewBox=("0 0 16384 16384"))
    d = "M" + str(positions[0][0]) + "," + str(positions[0][2])
    for i in range(1, len(positions)):
        if tangents[i-1] == (None, None):
            x, y = positions[i][0], positions[i][2]
            d += " L" + str(x) + "," + str(y)
        else:
            (x1_tan, z1_tan, y1_tan), (x2_tan, z2_tan, y2_tan) = tangents[i-1]
            x, y = positions[i][0], positions[i][2]
            d += " C" + str(x1_tan) + "," + str(y1_tan) + "," + str(x2_tan) + "," + str(y2_tan) + "," + str(x) + "," + str(y)
    dwg.add(dwg.path(d=d, fill="none", stroke="black"))
    dwg.save()

positions = convert_coordinates(positions, (0, 0, 0))  # Assuming (0, 0, 0) as initial coordinates for the positions
tangents = [convert_coordinates(t, (0, 0, 0)) if t[0] is not None else (None, None) for t in tangents]  # Assuming (0, 0, 0) as initial coordinates for the tangents
generate_svg(positions, tangents, 'output.svg')