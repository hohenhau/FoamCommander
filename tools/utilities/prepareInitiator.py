import os
import sys


def initialisation(tri_surface_dir: str, zero_dir:str):
    # Only run if there is a triSurface directory
    if not os.path.isdir(tri_surface_dir):
        print(f"Error: The directory '{tri_surface_dir}' does not exist, or is not accessible")
        sys.exit(1)
    # Ensure directories exist
    os.makedirs(zero_dir, exist_ok=True)


def load_stl_files(tri_surface_dir: str):
    """Processes STL files, renaming and extracting patch patch_names."""
    if not os.path.exists(tri_surface_dir) or not os.path.isdir(tri_surface_dir):
        print(f"Error: Directory '{tri_surface_dir}' does not exist.")
        sys.exit(1)  # Terminate program
    stl_files = [f.removesuffix('.stl') for f in os.listdir(tri_surface_dir) if f.endswith(".stl")]
    if not stl_files:
        print("No STL files found. Exiting...")
        sys.exit(1)  # Terminate program
    patches = sorted(list(set(stl_files)))
    return patches