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

    # Split headers into vertical letters (except for the first one)
    vertical_headers = [[c if i == 0 else "\n".join(h) for i, h in enumerate(headers)]]

    # Calculate column widths (solver can be long, others just 1 char wide vertically)
    col_widths = [max(len(row[0]) for row in rows)] + [1] * (len(headers) - 1)

    # Function to print a row (solver is horizontal, others are vertical)
    def print_row(row):
        print(f"{row[0]:<{col_widths[0]}}", end=" | ")
        print(" | ".join(f"{cell:^1}" for cell in row[1:]))

    # Print table header (vertical)
    print("OpenFOAM Solvers and Their Features:\n")

    # First print the "Solver" header
    print(f"{'Solver':<{col_widths[0]}}", end=" | ")

    # Now print each letter of the vertical headers in order
    for line in zip(*[h.split("\n") for h in vertical_headers[0][1:]]):
        print(" | ".join(f"{c:^1}" for c in line))

    # Divider line
    print("-" * (col_widths[0] + 3 + 4 * (len(headers) - 1)))

    # Print data rows
    for row in table_data:
        print_row(row)

if __name__ == "__main__":
    display_foam_solvers_table()
