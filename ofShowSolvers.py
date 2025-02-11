import csv
from io import StringIO
from tabulate import tabulate


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
    # Read the CSV data
    csv_reader = csv.reader(StringIO(data))
    
    # Convert to list of lists
    rows = list(csv_reader)
    
    # Separate headers and data
    headers = rows[0]
    table_data = rows[1:]
    
    # Clean up the data (remove extra spaces in checkmarks)
    cleaned_data = []
    for row in table_data:
        cleaned_row = [cell.strip() for cell in row]
        # Replace empty strings with '-' for better readability
        cleaned_row = ['-' if cell == '' else cell for cell in cleaned_row]
        cleaned_data.append(cleaned_row)
    
    # Format and display the table
    print("\nOpenFOAM Solvers and Their Features:")
    print(tabulate(cleaned_data, 
                  headers=headers,
                  tablefmt='grid',
                  stralign='center',
                  colalign=['left'] + ['center'] * (len(headers)-1)))


if __name__ == "__main__":
    display_foam_solvers_table()
