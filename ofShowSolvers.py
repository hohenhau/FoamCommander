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
    table_data = []

    for row in rows[1:]:
        cleaned_row = [cell.strip() if cell.strip() else '-' for cell in row]
        table_data.append(cleaned_row)

    # Calculate column widths
    col_widths = [max(len(str(row[i])) for row in [headers] + table_data) for i in range(len(headers))]

    # Function to print a row with proper spacing
    def print_row(row):
        print(" | ".join(f"{cell:<{col_widths[i]}}" for i, cell in enumerate(row)))

    # Print table
    print("OpenFOAM Solvers and Their Features:")
    print_row(headers)
    print("-" * (sum(col_widths) + 3 * (len(headers) - 1)))
    for row in table_data:
        print_row(row)

if __name__ == "__main__":
    display_foam_solvers_table()
