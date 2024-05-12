import re
import svgwrite

def parse_data(data):
    # Use regex to extract the positions and tangents
    position_pattern = re.compile(r'ShapePoint "{.*?}" {\n   Position (.*?) (.*?) (.*?)\n')
    tangent_pattern = re.compile(r'SplinePointData SplinePointData {\n     InTangent (.*?) (.*?) (.*?)\n     OutTangent (.*?) (.*?) (.*?)\n    }')
    positions = position_pattern.findall(data)
    tangents = tangent_pattern.findall(data)
    # Convert the strings to floats and group them into tuples
    positions = [(float(x), float(y), float(z)) for x, y, z in positions]
    try:
        tangents = [((float(x1), float(y1), float(z1)), (float(x2), float(y2), float(z2))) for x1, y1, z1, x2, y2, z2 in tangents]
    except ValueError:
        print("Error: All elements in 'tangents' must be convertible to a float.")
    except IndexError:
        print("Error: Each tuple in 'tangents' must contain exactly six elements.")
    print(tangents)
    return positions, tangents

def generate_svg(positions, tangents, output_file):
    # Define the half size of the system
    half_size = 16384 / 2

    # Convert the positions
    positions = [(x + half_size, half_size - y, z) for (x, y, z) in positions]

    # Convert the tangents
    tangents = [((x1 + half_size, half_size - y1, z1), (x2 + half_size, half_size - y2, z2)) for ((x1, y1, z1), (x2, y2, z2)) in tangents]

    dwg = svgwrite.Drawing(output_file, profile='tiny', size=("16384px", "16384px"), viewBox=("0 0 16384 16384"))
    d = ""
    for i in range(len(positions)):
        x, y, z = positions[i]
        if i == 0 or i > len(tangents):
            d += "M" + str(x) + "," + str(y)
        else:
            (x1_tan, y1_tan, z1_tan), (x2_tan, y2_tan, z2_tan) = tangents[i-1]
            d += " C" + str(x1_tan) + "," + str(y1_tan) + "," + str(x2_tan) + "," + str(y2_tan) + "," + str(x) + "," + str(y)
    path = dwg.add(dwg.path(d=d, fill="none", stroke="black"))
    dwg.save()

def generate_lines(positions, filename):
    with open(filename, 'w') as f:
        for i in range(len(positions) - 1):
            x1, y1, z1 = positions[i]
            x2, y2, z2 = positions[i+1]
            f.write(f"Line from ({x1}, {y1}, {z1}) to ({x2}, {y2}, {z2})\n")

def parse_file(filename):
    with open(filename, 'r') as file:
        data = file.read()
    return parse_data(data)

# Use the function to parse the data from a file
positions, tangents = parse_file('Splines_test.layer')

generate_svg(positions, tangents, 'output.svg')
generate_lines(positions, 'output.txt')