# !/usr/bin/env python3
"""Delete all .foam files in the cwd and create a new empty .foam file named after the cwd"""

from pathlib import Path


def create_foam_file():
    # Get current directory
    current_dir = Path.cwd()

    # Delete all .foam files
    foam_files = list(current_dir.glob("*.foam"))
    for foam_file in foam_files:
        print(f"Deleting: {foam_file.name}")
        foam_file.unlink()

    if foam_files:
        print(f"Deleted {len(foam_files)} .foam file(s)")
    else:
        print("No .foam files found to delete")

    # Create new empty .foam file named after current directory
    new_foam_file = current_dir / f"{current_dir.name}.foam"
    new_foam_file.touch()
    print(f"Created: {new_foam_file.name}")


if __name__ == "__main__":
    create_foam_file()