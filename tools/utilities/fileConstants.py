#!/usr/bin/python
import os

# Get the paths for the various template folders in the tools directory
UTILITIES_PATH = os.path.dirname(os.path.realpath(__file__))
TOOLS_PATH = os.path.dirname(UTILITIES_PATH)
TEMPLATE_BOUNDARY_DIR = os.path.join(TOOLS_PATH, "templatesBoundary")
TEMPLATE_CONSTANT_DIR = os.path.join(TOOLS_PATH, "templatesConstant")
TEMPLATE_SYSTEM_DIR = os.path.join(TOOLS_PATH, "templatesSystem")

# Get the paths for the various directories in the current case
BASE_DIR = os.getcwd()
TRI_SURFACE_DIR = os.path.join(BASE_DIR, "constant", "triSurface")
ZERO_DIR = os.path.join(BASE_DIR, "0.gen")
SYSTEM_DIR = os.path.join(BASE_DIR, "system")
CONSTANT_DIR = os.path.join(BASE_DIR, "constant")
PROCESSOR_0_DIR = os.path.join(BASE_DIR, "processor0")
SAMPLE_DIR = os.path.join(BASE_DIR, "postProcessing", "sampleDict")
RESIDUALS_DIR = os.path.join(BASE_DIR, "postProcessing", "sampleDict")

# Specify common file paths
CUSTOM_PROPERTY_FILE_PATH = os.path.join(CONSTANT_DIR, "focoProperties")



