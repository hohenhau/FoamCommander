#!/usr/bin/python
import os

PY_FILE_PATH = os.path.dirname(os.path.realpath(__file__))
TEMPLATE_BOUNDARY_DIR = os.path.join(PY_FILE_PATH, "templatesBoundary")
TEMPLATE_CONSTANT_DIR = os.path.join(PY_FILE_PATH, "templatesConstant")
TEMPLATE_SYSTEM_DIR = os.path.join(PY_FILE_PATH, "templatesSystem")

CURRENT_DIR = os.getcwd()

TRI_SURFACE_DIR = os.path.join(CURRENT_DIR, "constant", "triSurface")
ZERO_DIR = os.path.join(CURRENT_DIR, "0.gen")
SYSTEM_DIR = os.path.join(CURRENT_DIR, "system")
CONSTANT_DIR = os.path.join(CURRENT_DIR, "constant")
PROCESSOR_0_DIR = os.path.join(CURRENT_DIR, "processor0")
SAMPLE_DIR = os.path.join(CURRENT_DIR, "postProcessing", "sampleDict")
RESIDUALS_DIR = os.path.join(CURRENT_DIR, "postProcessing", "sampleDict")



