import re

def parse_spline_data(file_content):
    spline_data = []
    for match in re.finditer(r'ShapePoint "{.*?}" {.*?Position (.*?) (.*?) (.*?)\n.*?InTangent (.*?) (.*?) (.*?)\n.*?OutTangent (.*?) (.*?) (.*?)\n', file_content, re.DOTALL):
        point = {
            "Position": [round(float(match.group(i)), 3) for i in range(1, 4)],
            "InTangent": [round(float(match.group(i)), 3) for i in range(4, 7)],
            "OutTangent": [round(float(match.group(i)), 3) for i in range(7, 10)],
        }
        spline_data.append(point)
    is_closed = 'IsClosed 1' in file_content
    origin = [round(float(i), 3) for i in re.search(r'coords (.*?) (.*?) (.*?)\n', file_content).groups()]
    return spline_data, origin, is_closed

def convert_relative_to_absolute(spline_data, origin):
    absolute_spline_data = []
    for point in spline_data:
        absolute_point_position = [round(origin[i] + point["Position"][i], 3) for i in range(3)]
        absolute_point = {
            "Position": absolute_point_position,
            "InTangent": [round(absolute_point_position[i] + point["InTangent"][i], 3) for i in range(3)],
            "OutTangent": [round(absolute_point_position[i] + point["OutTangent"][i], 3) for i in range(3)],
        }
        absolute_spline_data.append(absolute_point)
    return absolute_spline_data

def convert_spline_entity_to_svg(spline_data, origin, is_closed):
    d = f'M {round(origin[0], 3)} {round(origin[2], 3)} C '
    for point in spline_data:
        d += f'{round(point["InTangent"][0], 3)} {round(point["InTangent"][2], 3)} {round(point["OutTangent"][0], 3)} {round(point["OutTangent"][2], 3)} {round(point["Position"][0], 3)} {round(point["Position"][2], 3)} '
    if is_closed:
        d += 'z'
    return f'<path d="{d}" fill="none" stroke="black" />'

def write_svg_to_file(svg_content, filename, viewport_width, viewport_height):
    with open(filename, 'w') as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{viewport_width}" height="{viewport_height}">\n')
        f.write(svg_content)
        f.write('\n</svg>')

file_content = open('Splines_test.layer').read()
spline_data, origin, is_closed = parse_spline_data(file_content)
print(spline_data)
absolute_spline_data = convert_relative_to_absolute(spline_data, origin)
print(absolute_spline_data)
svg = convert_spline_entity_to_svg(absolute_spline_data, origin, False)
print(svg)
write_svg_to_file(svg, 'output.svg', 16384, 16384)