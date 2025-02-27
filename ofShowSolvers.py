#!/usr/bin/python

import csv
from io import StringIO

# Your data as a string (in production, you'd read this from a file)
data = """Solver,transient,compressible,turbulence,heat-transfer,buoyancy,combustion,multiphase,particles,dynamic mesh,multi-region,fvOptions 
boundaryFoam,,,,,,,,,,,
buoyantPimpleFoam,✔ ,✔ ,✔ ,✔ ,✔ ,,,,,,✔ 
buoyantSimpleFoam,,✔ ,✔ ,✔ ,✔ ,,,,,,✔ 
chemFoam,✔ ,,,✔ ,,✔ ,,,,,
chtMultiRegionFoam,✔ ,✔ ,✔ ,✔ ,✔ ,,,,,✔ ,✔ 
coldEngineFoam,✔ ,✔ ,✔ ,✔ ,,✔ ,,,✔ ,,✔ 
engineFoam,✔ ,✔ ,✔ ,✔ ,,✔ ,,,✔ ,,✔ 
fireFoam,✔ ,✔ ,✔ ,✔ ,✔ ,✔ ,,,,✔ ,✔ 
icoFoam,✔ ,,,,,,,,,,
interFoam,✔ ,,✔ ,,,,✔ ,,✔ ,,✔ 
laplacianFoam,✔ ,,,,,,,,,,✔ 
pimpleFoam,✔ ,,✔ ,,,,,,✔ ,,✔ 
pisoFoam,✔ ,,✔ ,,,,,,,,✔ 
potentialFoam,,,,,,,,,,,
reactingFoam,✔ ,✔ ,✔ ,✔ ,,✔ ,,,,,✔ 
reactingParcelFoam,✔ ,✔ ,✔ ,✔ ,✔ ,✔ ,,✔ ,,,✔ 
rhoCentralFoam,✔ ,✔ ,✔ ,✔ ,,,,,,,
rhoPimpleFoam,✔ ,✔ ,✔ ,✔ ,,,,,✔ ,,✔ 
rhoSimpleFoam,,✔ ,✔ ,✔ ,,,,,,,✔ 
scalarTransportFoam,✔ ,,,,,,,,,,
simpleFoam,,,✔ ,,,,,,,,✔ 
sprayFoam,✔ ,✔ ,✔ ,✔ ,✔ ,✔ ,,✔ ,,,✔ 
XiFoam,✔ ,✔ ,✔ ,✔ ,,✔ ,,,,,✔"""

def display_foam_solvers_table():
    csv_reader = csv.reader(StringIO(data))
    rows = list(csv_reader)

    headers = [cell.strip() for cell in rows[0]]
    table_data = [ [cell.strip() if cell.strip() else '-' for cell in row] for row in rows[1:] ]

    # Prepare vertical headers (except for the first one, which stays horizontal)
    vertical_headers = []
    max_header_height = max(len(header) for header in headers[1:])

    for i, header in enumerate(headers):
        if i == 0:
            vertical_headers.append(header.ljust(max_header_height))  # Solver stays horizontal
        else:
            vertical_headers.append("\n".join(header.ljust(max_header_height)))

    # Calculate column widths (Solver can be long, others just 1 character wide)
    col_widths = [max(len(row[0]) for row in rows)] + [1] * (len(headers) - 1)

    # Print header row (Solver horizontal, others vertical)
    print("OpenFOAM Solvers and Their Features:\n")

    # Print "Solver" header
    print(f"{'Solver':<{col_widths[0]}}", end=" | ")

    # Now print the vertical headers (one letter per line for each column)
    for line_number in range(max_header_height):
        if line_number > 0:
            print(" " * col_widths[0], end=" | ")

        for header in vertical_headers[1:]:
            print(f"{header[line_number]:^1}", end=" | ")

        print()

    # Divider line
    print("-" * (col_widths[0] + 3 + 4 * (len(headers) - 1)))

    # Print data rows (solver horizontal, rest normal)
    for row in table_data:
        print(f"{row[0]:<{col_widths[0]}}", end=" | ")
        print(" | ".join(f"{cell:^1}" for cell in row[1:]))

if __name__ == "__main__":
    display_foam_solvers_table()
