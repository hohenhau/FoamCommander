import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import re
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
    'p_ad': 'Dynamic Pressure (Pa)'}

# Specify the dimensions of the plots
FIG_WIDTH_PROFILE_MM = 80
FIG_HEIGHT_PROFILE_MM = 80
FIG_WIDTH_OVERVIEW_MM = 160
FIG_HEIGHT_OVERVIEW_MM = 80
INCHES_TO_MM = 25.4
FIG_DPI = 300


# ----- Calculate point data ---------------------------------------------------------------------------------------- #

def check_directory_exists(directory):
    if not os.path.isdir(directory):
        error_directory = directory.split('/')[-2] + '/' + directory.split('/')[-1]
        sys.exit(f'The directory {error_directory} could not be found')

def get_timestep_directories(p_dir):
    return sorted([os.path.join(p_dir, dir) for dir in os.listdir(p_dir) if os.path.isdir(os.path.join(p_dir, dir))])

def create_directory(path: str) -> None:
    """Ensure that a directory exists. If it does not exist, create it."""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Directory created: {path}")
    else:
        print(f"Directory already exists: {path}")


def load_csv_files_into_pandas(directory):
    files = os.listdir(directory)
    files = [os.path.join(directory, file) for file in files if file.endswith(".csv") and 'overview' not in file]

    flow_data = []
    for file in files:
        df = pd.read_csv(file)
        df.attrs['title'] = os.path.splitext(os.path.basename(file))[0].lstrip('_')
        df.attrs['avg'] = {}
        df.attrs['std'] = {}
        df.attrs['cov'] = {}
        df.attrs['min'] = {}
        df.attrs['max'] = {}

        # Rename the pressure columns to show it is actually kinematic static pressure
        df.rename(columns={"p": "p_ks"}, inplace=True)
        df.rename(columns={"total(p)": "p_kt"}, inplace=True)

        for field, name in FIELD_NAMES.items():
            if field in df.columns:
                print(f"Loaded {name}")

        flow_data.append(df)

    return flow_data


def calculate_velocity_magnitude(df):
    components = ['U_x', 'U_y', 'U_z']
    available = [col for col in components if col in df.columns]

    if len(available) == 1:
        col = available[0]
        df['U_mag'] = df[col].abs()
    elif len(available) >= 2:
        df['U_mag'] = np.sqrt((df[available] ** 2).sum(axis=1))


def calculate_kinematic_dynamic_and_total_pressures(df):
    if 'U_mag' in df.columns and "p_ks" in df.columns:
        df['p_kd'] = 0.5 * df['U_mag'] ** 2
        if not 'p_kt' in df.columns:
            print('Total pressure field not found. Calculating total pressure')
            df['p_kt'] = df['p_kd'] + df['p_ks']


def get_density():
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


def calculate_actual_pressures(df, density):
    if density is None:
        return

    kinematic_pressures = ['p_kt', 'p_kd', 'p_ks']
    for kinematic_pressure in kinematic_pressures:
        if kinematic_pressure in df.columns:
            actual_name = kinematic_pressure.replace('k', 'a')
            df[actual_name] = df[kinematic_pressure] * density


def graph_flow_profiles(df, directory):
    # List of fields and their graphing limits
    fields = {'U_mag': {'min_pos': 0, 'max_pos': None, 'min_val': 0, 'max_val': None},
              'p_as': {'min_pos': 0, 'max_pos': None, 'min_val': None, 'max_val': None},
              'p_at': {'min_pos': 0, 'max_pos': None, 'min_val': 0, 'max_val': None}}

    # Get the name of the data frame
    df_title = df.attrs.get("title", "plot")

    for field in fields.keys():
        if field not in df.columns:
            continue

        field_name = FIELD_NAMES.get(field, field)

        if 'distance' in df.columns:
            x = df['distance']
            y = df[field]
            x_label = 'Distance (m)'
            y_label = field_name
            x_lim = (fields[field]['min_pos'], fields[field]['max_pos']) # maybe use max(x)
            y_lim = (fields[field]['min_val'], fields[field]['max_val'])
        elif 'y' in df.columns:
            x = df[field]
            y = df['y']
            x_label = field_name
            y_label = 'Depth (m)'
            x_lim = (fields[field]['min_val'], fields[field]['max_val'])
            y_lim = (fields[field]['min_pos'], 0)
        else:
            print('WARNING: No distance or y-coordinate provided.')
            continue

        plt.figure(figsize=(FIG_WIDTH_PROFILE_MM/INCHES_TO_MM, FIG_HEIGHT_PROFILE_MM/INCHES_TO_MM))
        plt.plot(x, y, label=field)

        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.xlim(x_lim)
        plt.ylim(y_lim)
        plt.title(f"{df_title}")
        plt.grid(True)

        filename = f"{directory}/profiles_{field}_{df_title}.png"
        plt.savefig(filename, dpi=FIG_DPI, bbox_inches="tight")
        plt.close()

        print(f"Saved: {filename.split('/')[-1]}")


# ----- Process overview data --------------------------------------------------------------------------------------- #

def calculate_line_values(dfs, fields):
    results = []
    for _, df, label in dfs:
        stats = {'title': label}
        for field in fields:
            if field not in df.columns:
                continue
            mean_val = df[field].mean()
            std_val = df[field].std()
            stats[f'{field}_avg'] = mean_val
            stats[f'{field}_std'] = std_val
            # Calculate CoV only for U_mag
            if field == 'U_mag':
                cov_val = std_val / mean_val if mean_val != 0 else np.nan
                stats[f'{field}_cov'] = cov_val
        results.append(stats)
    return pd.DataFrame(results)


def plot_line_values(df, field, suffix, filename, plot_title):
    # Only plot CoV for U_mag
    if suffix == 'cov' and field != 'U_mag':
        return

    column_name = f'{field}_{suffix}'
    if column_name not in df.columns:
        return

    labels = df['title']
    x = np.arange(len(labels))
    values = df[column_name]

    fig, ax = plt.subplots(figsize=(FIG_WIDTH_OVERVIEW_MM/INCHES_TO_MM, FIG_HEIGHT_OVERVIEW_MM/INCHES_TO_MM))
    ax.bar(x, values, label=FIELD_NAMES.get(field, field))

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_ylabel(suffix.upper())
    ax.set_title(plot_title)

    plt.tight_layout()
    plt.savefig(filename, dpi=FIG_DPI, bbox_inches='tight')
    plt.close()


def calculate_and_plot_loss_factor(analysis_directory, ordered_dfs, density):

    # Only run if density is present
    if density is None:
        print('Cannot compute loss factor without density. Continuing...')
        return
    # Initiate upstream and downstream titles
    ordered_dict = dict()
    upstream_titles = set()
    downstream_titles = set()

    # Create a dictionary and sets of upstream and downstream data frames
    for num, df, label in ordered_dfs:
        ending = label.split("_")[-1]
        if ending.lower() == "us":
            new_label = label.replace(f"_{ending}", "")
            upstream_titles.add(new_label)
            ordered_dict[f'{new_label}_us'] = df
        elif ending.lower() == "ds":
            new_label = label.replace(f"_{ending}", "")
            downstream_titles.add(new_label)
            ordered_dict[f'{new_label}_ds'] = df

    # Find the data frames which form an upstream and downstream pair
    paired_titles = upstream_titles.intersection(downstream_titles)
    paired_titles = sorted(list(paired_titles))

    # Calculate the actual loss factors
    loss_factors = list()
    actual_pressure_changes = list()
    kinematic_pressure_changes = list()
    velocity_magnitude = list()
    for title in paired_titles:
        df_upstream = ordered_dict[f'{title}_us']
        df_downstream = ordered_dict[f'{title}_ds']
        delta_p_kt = df_upstream['p_kt'].mean() - df_downstream['p_kt'].mean()
        kinematic_pressure_changes.append({"tick_label": title, "value": delta_p_kt})
        if 'p_at' in df_upstream.columns and 'p_at' in df_downstream.columns:
            delta_p_at = df_upstream['p_at'].mean() - df_downstream['p_at'].mean()
            u_mag = df_upstream['U_mag'].mean()
            k = abs(delta_p_at / (0.5 * density * u_mag ** 2))
            velocity_magnitude.append({"tick_label": title, "value": u_mag})
            actual_pressure_changes.append({"tick_label": title, "value": delta_p_at})
            loss_factors.append({"tick_label": title, "value": k})

    plot_labels = [
        (actual_pressure_changes, "Pressure Change (Pa)", "actual_pressure_changes"),
        (kinematic_pressure_changes, "Kinematic Pressure Change", "kinematic_pressure_changes"),
        (loss_factors, "Loss Factor K", "loss_factors"),
        (velocity_magnitude, "Velocity Magnitude (m/s)", "velocity_magnitude")
    ]

    plot_dfs = list()
    for value_dicts, heading, file_name in plot_labels:
        df = pd.DataFrame(value_dicts)
        df.attrs['heading'] = heading
        df.attrs['y_label'] = heading
        df.attrs['file_name'] = file_name
        plot_dfs.append(df)

    for df in plot_dfs:
        # Define file name and save to csv
        filename_table = f'{analysis_directory}/overview_table_{df.attrs.get("file_name")}'
        df.to_csv(f'{filename_table}.csv', index=False)

        # Plot results
        filename_plot = f'{analysis_directory}/overview_plot_{df.attrs.get("file_name")}'
        fig, ax = plt.subplots(figsize=(FIG_WIDTH_OVERVIEW_MM/INCHES_TO_MM, FIG_HEIGHT_OVERVIEW_MM/INCHES_TO_MM))
        ax.bar(df["tick_label"], df["value"], color="tab:blue")
        ax.set_ylabel(df.attrs.get("y_label"))
        ax.set_title(df.attrs.get("heading"))
        ax.set_xticks(range(len(df)))
        ax.set_xticklabels(df["tick_label"], rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(filename_plot, dpi=FIG_DPI, bbox_inches="tight")
        plt.close()


def process_overview_data(analysis_directory, dfs, density):
    # Specify the fields that should be evaluated
    fields = ['U_mag', 'p_at']

    # Specify the pattern that is used to differentiate between ordered an unordered probes
    pattern = re.compile(r"^_?0*(\d+)_?(.*)")
    ordered_dfs = []
    unordered_dfs = []
    for df in dfs:
        df_title = df.attrs.get("title", "plot")
        match = pattern.match(df_title)
        if match:
            num = int(match.group(1))
            label = match.group(2)
            ordered_dfs.append((num, df, label))
        else:
            unordered_dfs.append((df_title, df, df_title))

    # Sort the ordered data frames numerically and the unordered data frames alphabetically
    ordered_dfs.sort(key=lambda x: x[0])
    unordered_dfs.sort(key=lambda x: x[0])

    for dfs, kind in [(ordered_dfs, 'ordered'), (unordered_dfs, 'unordered')]:
        for metric, suffix in [
            ('Average', 'avg'),
            ('Standard Deviation of', 'std'),
            ('Coefficient of Variation of', 'cov')]:

            if dfs:
                line_values = calculate_line_values(dfs, fields)
                line_values.to_csv(f'{analysis_directory}/overview_{kind}_probes.csv', index=False)

                for field in fields:
                    filename = f'{analysis_directory}/overview_{kind}_probes_{field}_{suffix}.png'
                    plot_title = f'{metric} ({FIELD_NAMES.get(field, field)})'
                    plot_line_values(line_values, field, suffix, filename, plot_title)

    if ordered_dfs:
        calculate_and_plot_loss_factor(analysis_directory, ordered_dfs, density)


# ----- Main function ----------------------------------------------------------------------------------------------- #

def main():
    check_directory_exists(SAMPLE_DIRECTORY)
    density = get_density()

    for timestep_directory in get_timestep_directories(SAMPLE_DIRECTORY):

        flow_data = load_csv_files_into_pandas(timestep_directory)
        analysis_directory = os.path.join(timestep_directory, 'analysis')
        create_directory(analysis_directory)
        for df in flow_data:
            calculate_velocity_magnitude(df)
            calculate_kinematic_dynamic_and_total_pressures(df)
            calculate_actual_pressures(df, density)
            graph_flow_profiles(df, analysis_directory)
        process_overview_data(analysis_directory, flow_data, density)


if __name__ == "__main__":
    main()
