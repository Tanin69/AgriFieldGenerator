import re

def parse_spline_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    pattern = r"Position (.*?) (.*?) (.*?)\n.*?InTangent (.*?) (.*?) (.*?)\n.*?OutTangent (.*?) (.*?) (.*?)"
    matches = re.findall(pattern, content, re.DOTALL)

    points = []
    for match in matches:
        point = [float(x) for x in match]
        points.append(point)

    return points

def convert_to_bezier(points):
    bezier_points = []
    for i in range(0, len(points), 4):
        bezier_points.append([
            (points[i][0], points[i][1]),
            (points[i][0] + points[i+1][0], points[i][1] + points[i+1][1]),
            (points[i+2][0] + points[i+3][0], points[i+2][1] + points[i+3][1]),
            (points[i+2][0], points[i+2][1])
        ])

    return bezier_points

def generate_svg(bezier_points):
    svg = '<svg xmlns="http://www.w3.org/2000/svg" version="1.1">\n'
    for points in bezier_points:
        svg += f'<path d="M {points[0][0]},{points[0][1]} C {points[1][0]},{points[1][1]} {points[2][0]},{points[2][1]} {points[3][0]},{points[3][1]}" />\n'
    svg += '</svg>'

    return svg

points = parse_spline_file('Splines_test.layer')
bezier_points = convert_to_bezier(points)
svg = generate_svg(bezier_points)

print(svg)