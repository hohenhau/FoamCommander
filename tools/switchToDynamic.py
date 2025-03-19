#!/usr/bin/env python3

import os
import subprocess
import sys
import re

def find_latest_timestep(directory):
    """Finds the largest numerical directory name inside a given directory."""
    timesteps = [d for d in os.listdir(directory) if d.replace('.', '', 1).isdigit() and float(d) > 0]
    return max(timesteps, key=float) if timesteps else None

def switch_to_ncc():
  # Check if constant/triSurface exists
  if not os.path.isdir("constant/triSurface"):
      print("Directory 'constant/triSurface' not found. Exiting.")
      sys.exit(1)
  
  # Get list of STL files containing 'rotating'
  stl_files = [f for f in os.listdir("constant/triSurface") if f.endswith(".stl") and "rotating" in f]
  if not stl_files:
      print("No STL files containing 'rotating' found. Exiting.")
      sys.exit(1)
  
  # Find latest timestep directory in the current folder
  main_timestep = find_latest_timestep(".")
  
  # Find latest timestep directories in processor* folders
  processor_dirs = [d for d in os.listdir(".") if d.startswith("processor") and os.path.isdir(d)]
  processor_timesteps = {p: find_latest_timestep(p) for p in processor_dirs}
  
  # Filter out processors without timesteps
  processor_timesteps = {p: t for p, t in processor_timesteps.items() if t is not None}
  
  # Create the full list of directories to process
  time_step_dirs = [main_timestep] if main_timestep else []
  time_step_dirs += [os.path.join(p, t) for p, t in processor_timesteps.items()]
  
  # Exit if no valid timestep directories found
  if not time_step_dirs:
      print("No valid numerical timestep directories found. Exiting.")
      sys.exit(1)
  
  # Run the bash commands for each timestep and STL file
  print('Switching boundary types from "MRFnoSlip" to "movingWallVelocity" with a value of "uniform (0 0 0)"')
  for time_step in time_step_dirs:
      for stl_file in stl_files:
          boundary_name = os.path.splitext(stl_file)[0]  # Remove .stl extension
          print(f"Processing timestep {time_step} for the {boundary_name} boundary patch")
          
          commands = [
              ["foamDictionary", f"{time_step}/U", "-entry", f"boundaryField/{boundary_name}/value", "-remove"],
              ["foamDictionary", f"{time_step}/U", "-entry", f"boundaryField/{boundary_name}/type", "-set", "movingWallVelocity"],
              ["foamDictionary", f"{time_step}/U", "-entry", f"boundaryField/{boundary_name}/value", "-set", "uniform (0 0 0)"]
          ]
          
          for cmd in commands:
              subprocess.run(cmd)


if __name__ == "__main__":
  switch_to_ncc()
