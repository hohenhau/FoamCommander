#!/usr/bin/env python3
import os
import re
import glob
import shutil
import sys

def is_time_dir(dirname):
    """Check if directory name is a time value (number or floating point)"""
    return re.match(r'^[0-9]+(\.[0-9]+)?$', dirname) is not None

def get_latest_time(proc_dir='processor0'):
    """Get the latest time directory from a reference processor directory"""
    # Find all time directories
    time_dirs = [d for d in os.listdir(proc_dir) if os.path.isdir(os.path.join(proc_dir, d)) and is_time_dir(d)]
    
    # Sort time directories numerically
    time_dirs.sort(key=float)
    
    if not time_dirs:
        print(f"No time directories found in {proc_dir} directory. Aborting override.")
        sys.exit(1)
    
    latest_time = time_dirs[-1]
    print(f"Latest time in {proc_dir} is {latest_time}")
    return latest_time

def main():
    print("Overriding 'constant/' directory in processor folders")
    
    # Make sure processor0 exists
    if not os.path.isdir("processor0"):
        print("Error: processor0 directory not found. Make sure you're in the correct directory.")
        sys.exit(1)
    
    # Get the latest time from processor0
    latest_time = get_latest_time()
    
    # Loop through all processor directories
    for proc_dir in glob.glob("processor*"):
        # Check if both polyMesh and fvMesh directories exist in the latest time
        poly_mesh_path = os.path.join(proc_dir, latest_time, "polyMesh")
        fv_mesh_path = os.path.join(proc_dir, latest_time, "fvMesh")
        
        if os.path.isdir(poly_mesh_path) and os.path.isdir(fv_mesh_path):
            # Create destination directories
            const_poly_path = os.path.join(proc_dir, "constant", "polyMesh")
            const_fv_path = os.path.join(proc_dir, "constant", "fvMesh")
            
            os.makedirs(const_poly_path, exist_ok=True)
            os.makedirs(const_fv_path, exist_ok=True)
            
            # Copy polyMesh files
            print(f"Copying {poly_mesh_path} to {const_poly_path}")
            for item in os.listdir(poly_mesh_path):
                src = os.path.join(poly_mesh_path, item)
                dst = os.path.join(const_poly_path, item)
                if os.path.isdir(src):
                    if os.path.exists(dst):
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
            
            # Copy fvMesh files
            print(f"Copying {fv_mesh_path} to {const_fv_path}")
            for item in os.listdir(fv_mesh_path):
                src = os.path.join(fv_mesh_path, item)
                dst = os.path.join(const_fv_path, item)
                if os.path.isdir(src):
                    if os.path.exists(dst):
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
        else:
            print(f"Missing polyMesh or fvMesh in {proc_dir}/{latest_time}")
    
    print("Done!")

if __name__ == "__main__":
    main()
