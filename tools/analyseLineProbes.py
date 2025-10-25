import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import re
import shutil
import subprocess
import sys

# ----- Define various constants ------------------------------------------------------------------------------------ #

# Set the target directory
SAMPLE_DIRECTORY = os.path.join(os.getcwd(), 'postProcessing/sampleDict')

# Specify names to be used in the plots
FIELD_NAMES = {
    'U_mag': 'Velocity Magnitude (m/s)',
    'p_ks': 'Kinematic Static Pressure',
    'p_kt': 'Kinematic Total Pressure',
    'p_kd': 'Kinematic Dynamic Pressure',
    'p_as': 'Static Pressure (Pa)',
    'p_at': 'Total Pressure (Pa)',
    'p_ad': 'Dynamic Pressure (Pa)',
    'pol_ang_xy': 'Polar angles of Velocity (deg) in XY',
    'pol_ang_xz': 'Polar angles of Velocity (deg) in XZ',
    'pol_ang_yz': 'Polar angles of Velocity (deg) in YZ',
    'delta_p_ks': 'Change in Kinematic Static Pressure',
    'delta_p_kt': 'Change in Kinematic Total Pressure',
    'delta_p_kd': 'Change in Kinematic Dynamic Pressure',
    'delta_p_as': 'Change in Static Pressure (Pa)',
    'delta_p_at': 'Change in Total Pressure (Pa)',
    'delta_p_ad': 'Change in Dynamic Pressure (Pa)',
    'k_factor': 'Loss Factor K',
    'distance': 'Distance (m)',
    'x': 'X-coordinate (m)',
    'y': 'Y-coordinate (m)',
    'z': 'Z-coordinate (m)',
    'depth': 'Depth (m)',
    'avg': 'Average',
    'std': 'Standard Deviation of',
    'cov': 'Coefficient of Variation of'
}

# Specific fields to be graphed as flow profiles along with their graphing limits
PROFILE_FIELDS = {
    'U_mag': {'min_pos': 0, 'max_pos': None, 'min_val': 0, 'max_val': None},
    # 'p_at': {'min_pos': 0, 'max_pos': None, 'min_val': 0, 'max_val': None},
    # 'p_as': {'min_pos': 0, 'max_pos': None, 'min_val': None, 'max_val': None},
}

# Specify which collective plots should be graphed
LOCATION_FIELDS = {'U_mag', 'p_at', 'pol_ang_xy'}

# Specify which changing fields should be graphed
COMPONENT_FIELDS = {'k_factor', 'delta_p_at'}

# Specify the dimensions of the plots
FIG_WIDTH_PROFILE_MM = 80
FIG_HEIGHT_PROFILE_MM = 80
FIG_WIDTH_OVERVIEW_MM = 160
FIG_HEIGHT_OVERVIEW_MM = 80
INCHES_TO_MM = 25.4
FIG_DPI = 300


# ----- File Handling ------ ---------------------------------------------------------------------------------------- #

def check_directory_exists(directory) -> None:
    """Check that the sampleDict directory exists in the postProcessing folder"""
    if not os.path.isdir(directory):
        error_directory = directory.split('/')[-2] + '/' + directory.split('/')[-1]
        sys.exit(f'The directory {error_directory} could not be found')


def get_timestep_directories(p_dir: str) -> list[str]:
    """Get all the time step directories within the sampleDict directory"""
    return sorted([os.path.join(p_dir, dir) for dir in os.listdir(p_dir) if os.path.isdir(os.path.join(p_dir, dir))])


def create_directory(path: str) -> None:
    """Ensure that a directory exists. If it does not exist, create it."""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Directory created: {path}")
    else:
        print(f"Directory already exists: {path}")


def get_list_of_probe_names(directory: str) -> list[str]:
    """Import the probe data stored in various CSV files"""
    files = os.listdir(directory)
    probe_names = [file for file in files if file.endswith(".csv") and 'overview' not in file]
    return probe_names


def load_csv_files_into_pandas(directory: str, probe_numbers_and_names: list[str]) -> list[pd.DataFrame]:
    """Import the probe data stored in various probe CSV files"""
    dfs = list()
    for probe_number_and_name in probe_numbers_and_names:
        probe_path = os.path.join(directory, probe_number_and_name)
        print(f'Processing file: {probe_number_and_name.split("/")[-1]}')
        df = pd.read_csv(probe_path)
        probe_number_and_name = os.path.splitext(os.path.basename(probe_path))[0].lstrip('_')
        probe_number, probe_name, match = strip_probe_number_and_name(probe_number_and_name)
        df.attrs['number_and_name'] = probe_number_and_name
        df.attrs['number'] = probe_number if match else None
        df.attrs['name'] = probe_name
        # Rename the pressure columns to show it is actually kinematic static pressure
        df.rename(columns={"p": "p_ks"}, inplace=True)
        df.rename(columns={"total(p)": "p_kt"}, inplace=True)
        dfs.append(df)
    return dfs


def delete_sample_dir_analysis() -> None:
    """Deletes the current analysis folders in sampleDict"""
    sample_dict_file = os.path.join(SAMPLE_DIRECTORY, "sampleDict.7z")
    if os.path.exists(sample_dict_file):
        try:
            os.remove(sample_dict_file)
            print(f"Deleted {sample_dict_file}")
        except OSError as e:
            print(f"Error deleting file {sample_dict_file}: {e}")

    time_step_dirs = get_timestep_directories(SAMPLE_DIRECTORY)
    for time_step_dir in time_step_dirs:
        analysis_path = os.path.join(time_step_dir, "analysis")
        if os.path.isdir(analysis_path):
            try:
                shutil.rmtree(analysis_path)
                print(f"Deleted analysis directory in {time_step_dir}")
            except OSError as e:
                print(f"Error deleting directory {analysis_path}: {e}")


def compress_sample_dir() -> None:
    """Compress the sampleDict folder for easy export"""
    cwd = os.getcwd()
    try:
        os.chdir(SAMPLE_DIRECTORY)
        subprocess.run(["foco", "compress"], check=True)
    except subprocess.CalledProcessError as e:
        print(f'Could not compress {SAMPLE_DIRECTORY}')
    finally:
        os.chdir(cwd)


def strip_probe_number_and_name(probe_name:str) -> tuple[str, str, bool]:
    """Strips the numbers from ordered probes"""
    pattern = re.compile(r"^_?0*(\d+)_?(.*)")
    match = pattern.match(probe_name)
    return (match.group(1), match.group(2), True) if match else ('', probe_name, False)


# ----- Calculate point data ---------------------------------------------------------------------------------------- #

def get_density():
    """Get the user input for fluid density to carry out pressure calculations for real pressure"""
    print("To calculate actual pressures, please enter the fluid density. For reference:")
    print("Density of water is: 999.19 (15°C), 998.29 (20°C), 997.13 (25°C), 995.71 (30°C)")
    print("Density of air is:   1.2250 (15°C), 1.2041 (20°C), 1.1839 (25°C), 1.1644 (30°C)")
    user_input = input("Enter density (press Enter to skip): ").strip()
    if user_input == "":
        print("No density provided. Continuing...")
        return None
    try:
        density = float(user_input)
        print(f"Density provided: {density}")
        return density
    except ValueError:
        print("Invalid input. Please enter a numeric value or press Enter to skip.")
        return get_density()


def calculate_velocity_magnitude(df: pd.DataFrame):
    """Calculate the velocity magnitude given a pandas DataFrame containing velocity components"""
    components = ['U_x', 'U_y', 'U_z']
    available = [col for col in components if col in df.columns]
    if len(available) == 1:
        col = available[0]
        df['U_mag'] = df[col].abs()
    elif len(available) >= 2:
        df['U_mag'] = np.sqrt((df[available] ** 2).sum(axis=1))


def calculate_polar_velocity_angles_in_degrees(df: pd.DataFrame):
    """Calculate the polar angle of various velocity planes"""
    x_str, y_str, z_str = 'x', 'y', 'z'
    for a, b in [(x_str, y_str), (x_str, z_str), (y_str, z_str)]:
        vel_a, vel_b = f'U_{a}', f'U_{b}'
        if vel_a in df.columns and vel_b in df.columns:
            df[f'pol_ang_{a}{b}'] = np.degrees(np.arctan2(df[vel_b], df[vel_a]))


def calculate_kinematic_dynamic_and_total_pressures(df: pd.DataFrame):
    """Calculate the kinematic dynamic and kinematic total pressure given a pandas dataFrame"""
    if 'U_mag' in df.columns and "p_ks" in df.columns:
        df['p_kd'] = 0.5 * df['U_mag'] ** 2
        if not 'p_kt' in df.columns:
            print('Total pressure field not found. Calculating total pressure')
            df['p_kt'] = df['p_kd'] + df['p_ks']


def calculate_actual_pressures(df: pd.DataFrame, density: float):
    """Calculate the actual pressure given density and kinematic pressures"""
    if density is None:
        return
    kinematic_pressures = ['p_kt', 'p_kd', 'p_ks']
    for kinematic_pressure in kinematic_pressures:
        if kinematic_pressure in df.columns:
            actual_name = kinematic_pressure.replace('k', 'a')
            df[actual_name] = df[kinematic_pressure] * density


# ----- Plot point data --------------------------------------------------------------------------------------------- #

def plot_flow_profiles(df: pd.DataFrame, fields: dict, directory: str):
    """Plot the flow profiles for various flow fields from a pandas DataFrame"""
    # Process the various output fields
    for field in fields.keys():
        # Ensure the field and a coordinate system is present
        if field not in df.columns:
            print(f"WARNING: field '{field}' not found in data.")
            continue
        if 'distance' not in df.columns and 'y' not in df.columns:
            print("WARNING: No distance or y-coordinate provided.")
            continue

        # Extract the x and y components from the data frame
        coordinate = 'distance' if 'distance' in df.columns else "y"
        x = df[coordinate]
        y = df[field]
        x_label = FIELD_NAMES.get(coordinate, coordinate)
        y_label = FIELD_NAMES.get(field, field)

        # Use provided limits, otherwise fallback to data min/max
        x_min = fields[field]["min_pos"] if fields[field]["min_pos"] is not None else x.min()
        x_max = fields[field]["max_pos"] if fields[field]["max_pos"] is not None else x.max()
        y_min = fields[field]["min_val"] if fields[field]["min_val"] is not None else y.min()
        y_max = fields[field]["max_val"] if fields[field]["max_val"] is not None else y.max()
        x_lim = (x_min, x_max)
        y_lim = (y_min, y_max)

        # Swap axes if using y (depth) instead of length
        if coordinate == "y":
            x, y = y, x
            x_label, y_label = y_label, x_label
            x_lim = y_lim
            y_lim = (y.min(), 0)

        # Get the name of the data frame
        df_number_and_name = df.attrs.get("number_and_name", "plot")

        # Plot the profile data
        plt.figure(figsize=(FIG_WIDTH_PROFILE_MM / INCHES_TO_MM, FIG_HEIGHT_PROFILE_MM / INCHES_TO_MM))
        plt.plot(x, y, label=field)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.xlim(x_lim)
        plt.ylim(y_lim)
        plt.title(f"{df_number_and_name}")
        plt.grid(True)
        filename = f"{directory}/profiles_{field}_{df_number_and_name}.png"
        plt.savefig(filename, dpi=FIG_DPI, bbox_inches="tight")
        plt.close()

        print(f"Saved: {filename.split('/')[-1]}")


# ----- Process collective data ------------------------------------------------------------------------------------- #

def categorise_ordered_and_unordered_probes(dfs: list[pd.DataFrame]) -> tuple[list[pd.DataFrame], list[pd.DataFrame]]:
    """Split probes into ordered (numerically) and unordered (alphabetically), returning them in sorted order."""
    ordered_dfs, unordered_dfs = list(), list()
    for df in dfs:
        probe_number = df.attrs.get("number")
        probe_name = df.attrs.get("name")
        if probe_number is not None:
            ordered_dfs.append((int(probe_number), df))
        else:
            unordered_dfs.append((probe_name, df))
    # Sort in place
    ordered_dfs.sort(key=lambda x: x[0])
    unordered_dfs.sort(key=lambda x: x[0])
    # Strip away the key, return only DataFrames
    ordered_dfs = [df for _, df in ordered_dfs]
    unordered_dfs = [df for _, df in unordered_dfs]
    return ordered_dfs, unordered_dfs


def calculate_location_stats(dfs: list[pd.DataFrame]) -> dict:
    """
    Calculate collective statistics (avg, std, cov) for each probe and each field.
    Returns a nested dict: {"ProbeName": {"FieldName": {"avg": ..., "std": ..., "cov": ...}}}
    """
    location_stats = {}
    for df in dfs:
        # ensure probe entry exists
        probe_number_and_name = df.attrs.get("number_and_name")
        if probe_number_and_name not in location_stats:
            location_stats[probe_number_and_name] = {}
        for field in df.columns:
            # skip coordinates
            if field in {"x", "y", "z", "xyz", "distance"}:
                continue
            avg = df[field].mean()
            std = df[field].std()
            cov = std / avg if avg != 0 else np.nan
            location_stats[probe_number_and_name][field] = {"avg": avg, "std": std, "cov": cov}
    return location_stats


def find_component_pairs(dfs: list[pd.DataFrame], density: float) -> list[tuple[str, str]]:
    """Pairs up line probes (i.e. Vanes_US and Vanes_DS) to determine the changes across them"""
    if density is None:
        print('Cannot compute loss factor without density. Continuing...')
        return []
    # Map the probe stem to the full name for later retrieval
    upstream_components, downstream_components = dict(), dict()
    for df in dfs:
        probe_number_and_name = df.attrs.get("number_and_name")
        probe_name = df.attrs.get("name")
        ending = probe_number_and_name.split("_")[-1]
        stem = probe_name.replace(f'_{ending}', "")
        if ending.upper() == "US":
            upstream_components[stem] = probe_number_and_name
        elif ending.upper() == "DS":
            downstream_components[stem] = probe_number_and_name
    # Find the intersection of the keys (the core probe names).
    paired_components = list()
    common_names = set(upstream_components.keys()).intersection(downstream_components.keys())
    for name in common_names:
        upstream_full_name = upstream_components[name]
        downstream_full_name = downstream_components[name]
        paired_components.append((upstream_full_name, downstream_full_name))
    paired_components = sorted(paired_components, key=lambda x: x[0])
    return paired_components


def calculate_cross_component_stats(location_stats: dict, pairs: list[tuple[str, str]], density: float,
                                    fields: set) -> dict:
    """Calculates cross component statistics such as pressure change or loss factor"""
    component_stats = dict()
    for us_key, ds_key in pairs:
        _, component, _ = strip_probe_number_and_name(us_key)
        ending = component.split("_")[-1]
        component = component.replace(f'_{ending}','')
        component_stats[component] = dict()
        delta_p_kt = location_stats[us_key]['p_kt']['avg'] - location_stats[ds_key]['p_kt']['avg']
        component_stats[component]['delta_p_kt'] = delta_p_kt
        component_stats[component]['U_mag'] = location_stats[us_key]['U_mag']['avg']
        if 'p_at' not in location_stats[us_key] or 'p_at' not in location_stats[ds_key]:
            continue
        u_mag = location_stats[us_key]['U_mag']['avg']
        delta_p_at = location_stats[us_key]['p_at']['avg'] - location_stats[ds_key]['p_at']['avg']
        component_stats[component]['delta_p_at'] = delta_p_at
        component_stats[component]['k_factor'] = abs(delta_p_at / (0.5 * density * u_mag ** 2))

        for field in fields:
            if field not in location_stats[us_key] or field not in location_stats[ds_key] or field == 'U_mag':
                continue
            component_stats[component][f'delta_{field}'] = location_stats[us_key][field] - location_stats[ds_key][
                field]
    return component_stats


def plot_and_save_location_data(location_stats: dict, selected_fields: set, field_names: dict, directory:str):
    """Takes the location statistics and plots them on a bar graph and saves them as a CSV"""
    file_name_start = 'plot_overview_locations'
    locations = list(location_stats.keys())
    plot_df = pd.DataFrame({"location": locations})
    for field in selected_fields:
        field_name = field_names.get(field, field)
        for suffix in ['avg', 'std', 'cov']:
            values = list()
            for location, location_vals in location_stats.items():
                if field not in location_vals:
                    print(f'WARNING: field {field} not found at {location}')
                    values.append(np.nan)
                else:
                    values.append(location_vals[field][suffix])
            # Plot current combination of field and suffix values for all locations
            plot_df[f'{field}_{suffix}'] = values
            prefix = field_names.get(suffix, f'{suffix} of')
            title = f'{prefix} {field_name}'
            file_name = f'{file_name_start}_{field}_{suffix}.png'
            file_location = os.path.join(directory, file_name)
            plot_horizontal_bar_graph(locations, values, title, field_name, file_location)
    # Save entire data frame to a CSV file
    file_name = f'{file_name_start}.csv'
    file_location = os.path.join(directory, file_name)
    plot_df.to_csv(file_location, index=False)


def plot_and_save_component_data(component_stats: dict, selected_fields: set, field_names: dict, directory:str):
    """Takes the Component statistics and plots them on a bar graph and saves them as a CSV"""
    file_name_start = 'plot_overview_components'
    components = list(component_stats.keys())
    if not components:
        print('No components found. Proceeding...')
        return
    plot_df = pd.DataFrame({"component": components})
    for field in selected_fields:
        field_name = field_names.get(field, field)
        values = list()
        for component, component_vals in component_stats.items():
            if field not in component_vals:
                print(f'WARNING: field {field} not found at {component}')
                values.append(np.nan)
            else:
                values.append(component_vals[field])
        # Plot current field values for all components
        plot_df[field] = values
        file_name = f'{directory}/{file_name_start}_{field}.png'
        file_location = os.path.join(directory, file_name)
        plot_horizontal_bar_graph(components, values, field_name, field_name, file_location)
    # Save entire data frame to a CSV file
    file_name = f'{file_name_start}.csv'
    file_location = os.path.join(directory, file_name)
    plot_df.to_csv(file_location, index=False)


# ----- Plot location data ---------------------------------------------------------------------------------------- #

def plot_vertical_bar_graph(labels, values, title: str, y_label: str, file_location: str):
    """Creates a standard bar graph with vertically oriented bars"""
    x = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(FIG_WIDTH_OVERVIEW_MM / INCHES_TO_MM, FIG_HEIGHT_OVERVIEW_MM / INCHES_TO_MM))
    ax.bar(x, values, label=title)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=80, ha="right")
    ax.set_ylabel(y_label)
    ax.set_title(title)
    plt.tight_layout()
    plt.savefig(file_location, dpi=FIG_DPI, bbox_inches='tight')
    plt.close()


def plot_horizontal_bar_graph(labels, values, title: str, x_label: str, file_location: str):
    """Creates a standard bar graph with horizontally oriented bars"""
    num_items = len(values)
    fig_width = FIG_WIDTH_OVERVIEW_MM / INCHES_TO_MM
    fig_height = num_items * 8 / INCHES_TO_MM
    y = np.arange(len(labels))
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    ax.barh(y, values, color="tab:blue")
    ax.set_yticks(y)
    ax.set_yticklabels(labels)
    ax.set_xlabel(x_label)
    ax.set_title(title)
    ax.invert_yaxis()  # Reverse the order so the first label is at the top
    plt.tight_layout()
    plt.savefig(file_location, dpi=FIG_DPI, bbox_inches="tight")
    plt.close()


# ----- Main function ----------------------------------------------------------------------------------------------- #

def main():
    check_directory_exists(SAMPLE_DIRECTORY)
    density = get_density()
    delete_sample_dir_analysis()
    for timestep_directory in get_timestep_directories(SAMPLE_DIRECTORY):
        # Carry out directory and file management and fetch relevant files
        analysis_directory = os.path.join(timestep_directory, 'analysis')
        create_directory(analysis_directory)
        probe_names = get_list_of_probe_names(timestep_directory)
        # Process the data across individual porbes
        flow_data_dfs = load_csv_files_into_pandas(timestep_directory, probe_names)
        for df in flow_data_dfs:
            calculate_velocity_magnitude(df)
            calculate_polar_velocity_angles_in_degrees(df)
            calculate_kinematic_dynamic_and_total_pressures(df)
            calculate_actual_pressures(df, density)
            plot_flow_profiles(df, PROFILE_FIELDS, analysis_directory)

        ordered_dfs, unordered_dfs = categorise_ordered_and_unordered_probes(flow_data_dfs)
        flow_data_dfs = ordered_dfs + unordered_dfs
        location_stats = calculate_location_stats(flow_data_dfs)
        component_pairs = find_component_pairs(ordered_dfs, density)
        component_stats = calculate_cross_component_stats(location_stats, component_pairs, density, COMPONENT_FIELDS)
        plot_and_save_location_data(location_stats, LOCATION_FIELDS, FIELD_NAMES, analysis_directory)
        plot_and_save_component_data(component_stats, COMPONENT_FIELDS, FIELD_NAMES, analysis_directory)
    compress_sample_dir()


if __name__ == "__main__":
    main()
