#!/usr/bin/python
import os

PY_FILE_PATH = os.path.dirname(os.path.realpath(__file__))
TEMPLATE_BOUNDARY_DIR = os.path.join(PY_FILE_PATH, "templatesBoundary")
TEMPLATE_CONSTANT_DIR = os.path.join(PY_FILE_PATH, "templatesConstant")
TEMPLATE_SYSTEM_DIR = os.path.join(PY_FILE_PATH, "templatesSystem")

CURRENT_DIR = os.getcwd()
BASE_DIR = os.path.dirname(CURRENT_DIR)

TRI_SURFACE_DIR = os.path.join(BASE_DIR, "constant", "triSurface")
ZERO_DIR = os.path.join(BASE_DIR, "0.gen")
SYSTEM_DIR = os.path.join(BASE_DIR, "system")
CONSTANT_DIR = os.path.join(BASE_DIR, "constant")
PROCESSOR_0_DIR = os.path.join(BASE_DIR, "processor0")
SAMPLE_DIR = os.path.join(BASE_DIR, "postProcessing", "sampleDict")
RESIDUALS_DIR = os.path.join(BASE_DIR, "postProcessing", "sampleDict")



