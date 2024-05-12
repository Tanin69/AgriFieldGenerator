import re

def parse_spline(file_content):
    lines = file_content.split('\n')
    splines = []
    current_spline = []
    current_point = None
    for line in lines:
        line = line.lstrip()  # Remove leading spaces
        if "SplineShapeEntity" in line:
            if current_spline:
                splines.append(current_spline)
                current_spline = []
        elif "coords" in line:
            coords = list(map(float, re.findall(r"[-+]?\d*\.\d+|\d+", line)))
            if len(coords) == 3:
                # Ignore z coordinate
                current_spline.append({'position': [coords[0], coords[2]]})
        elif "Position" in line:
            position = list(map(float, re.findall(r"[-+]?\d*\.\d+|\d+", line)))
            if len(position) == 3:
                # Ignore z coordinate and swap y and x coordinates
                current_point = {'position': [position[0], position[2]], 'intangent': [], 'outtangent': []}
                current_spline.append(current_point)
        elif "InTangent" in line or "OutTangent" in line:
            tangent = list(map(float, re.findall(r"[-+]?\d*\.\d+|\d+", line)))
            if len(tangent) == 3 and current_point is not None:
                # Ignore z coordinate and swap y and x coordinates
                current_point[line.strip().split()[0].lower()] = [tangent[0], tangent[2]]
    if current_spline:
        splines.append(current_spline)
    print(splines)
    return splines

def convert_to_svg(splines_data):
    svg_paths = ""
    for spline_data in splines_data:
        d = ""
        ref_point = spline_data[0]["position"]  # Use the first point as the reference point
        d += f'M {ref_point[0]},{ref_point[1]} '
        for i, point in enumerate(spline_data[1:], start=1):  # Start from the second element
            prev_point = spline_data[i-1]
            if "outtangent" in prev_point and "intangent" in point:
                d += f'c {prev_point["outtangent"][0]},{prev_point["outtangent"][1]} {point["intangent"][0]},{point["intangent"][1]} {point["position"][0]},{point["position"][1]} '
            else:
                d += f'l {point["position"][0]},{point["position"][1]} '
        svg_paths += f'<path d="{d}" fill="none" stroke="black"/>'
    print(svg_paths)
    return f'<svg width="16384" height="16384" xmlns="http://www.w3.org/2000/svg">{svg_paths}</svg>'
    

with open('Splines_test.layer', 'r') as file:
    file_content = file.read()

spline_data = parse_spline(file_content)
svg = convert_to_svg(spline_data)

with open('output.svg', 'w') as file:
    file.write(svg)