path_to_write_to = 'C:/Users/avery/OneDrive - Georgia Institute of Technology/GTSC - Personal/YAPS/CAD/'
input_airfoil_file = 'C:/Users/avery/OneDrive - Georgia Institute of Technology/GTSC - Personal/airfoils/UIUC Database/naca0010.dat'
output_airfoil_file = 'n10xyz.dat'

# Read the input file
with open(input_airfoil_file, 'r') as file:
    lines = file.readlines()

# Process each line and append '0.0000'
modified_lines = []
for line in lines:
    parts = line.strip().split()
    if len(parts) == 2:  # Ensure the line contains exactly two coordinates
        x, y = parts
        modified_line = f"{x}\t{y}\t0.0000"
        modified_lines.append(modified_line)

# Write the modified lines to a new output file
with open(path_to_write_to+output_airfoil_file, 'w') as file:
    file.write('\n'.join(modified_lines))



print(f"File has been processed and saved as '{output_airfoil_file}'")
