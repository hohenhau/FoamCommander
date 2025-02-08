#!/usr/bin/python

import re
import os
import sys

def getPatchType(patch):
	patch_type = "wall"
	if re.search(r"mirror", patch):
		patch_type = "symmetry"
	elif re.search(r"(screen|baffle)", patch):
		patch_type = "screen"
	elif re.search(r"inlet", patch):
		patch_type = "inlet";
	elif re.search(r"outlet", patch):
		patch_type = "outlet";
	elif re.search(r"slip", patch):
		patch_type = "slip";
	elif re.search(r"atmosphere", patch):
		patch_type = "inletOutlet";
	return patch_type

def buildZeroFile(base_name, types, values):
	with open(zeroDir+base_name,'w') as outfile:
		with open(skeletondir+base_name+"Head") as f:
			outfile.write(f.read())
		for patch in patch_names:
			outfile.write("    "+patch+"\n    {\n")
			patch_type = getPatchType(patch)
			print(patch+", "+patch_type)
			outfile.write("        type    "+types[patch_type]+";\n")
			if patch_type in values:
				outfile.write("        value   "+values[patch_type]+";\n")
			outfile.write("    }\n")
		outfile.write("}\n")

py_file_path = os.path.dirname(os.path.realpath(__file__))
skeletondir = py_file_path+"/skeletons/"
dir = os.getcwd()
args_len = len(sys.argv)
if args_len > 1:
	dir = sys.argv[args_len-1]
patch_names = []
triSurfaceDir=dir+"/constant/triSurface/"
zeroDir=dir+"/0.gen/"
if not os.path.exists(zeroDir):
	os.makedirs(zeroDir)
print(dir)
# rename and prepare the stl files.  Note this doesn't check that the stl file name is the same as the patch name in the file (which is required)
list = os.listdir(triSurfaceDir)
for filename_name in list:
	if filename_name.endswith(".STL"):
		filename = triSurfaceDir+filename_name
		with open(filename) as file:
			out_filename = filename + ".tmp"
			out_file = open(out_filename, "w")
			match_name = re.split(r"\.",filename_name)[0]
			if not getPatchType(match_name) == "screen" and not match_name in patch_names:
				print("Match  " + match_name)
				patch_names.append(str(match_name))
			for line in file:
				match = re.match(r"solid", line)
				if re.match(r"endsolid", line):
					out_file.write("endsolid "+match_name+"\n")
				elif re.match(r"solid", line):
					out_file.write("solid "+match_name+"\n")
				else:
					out_file.write(line)
			out_file.close()
			os.rename(filename+ ".tmp", re.sub(r"STL", "stl", filename))
	elif filename_name.endswith(".stl"):
		filename = triSurfaceDir+filename_name
		with open(filename) as file:
			match_name = re.split(r"\.",filename_name)[0]
			if not getPatchType(match_name) == "screen" and not match_name in patch_names:
				print("Match2 " + match_name)
				patch_names.append(str(match_name))
print(patch_names)
systemDir = dir+"/system/"
# create the surfaceFeatureExtractDict file
with open(systemDir+"surfaceFeatureExtractDict.x",'w') as sfefile:
	with open(skeletondir+"surfaceFeatureExtractHead") as f:
		sfefile.write(f.read())
	for patch in patch_names:
		str = patch+".stl\n"
		print(str)
		sfefile.write(str)
		with open(skeletondir+"surfaceFeatureExtractPart") as f:
			sfefile.write(f.read())
# create the base snappyHexMeshDict file
with open(systemDir+"snappyHexMeshDict.x",'w') as shmfile:
	with open(skeletondir+"snappyHexMeshHead") as f:
		shmfile.write(f.read())
	for patch in patch_names:
		str = "        "+patch+".stl {type triSurfaceMesh; name "+patch+";}\n"
		shmfile.write(str)
	shmfile.write("        //refinementBox {type searchableBox; min (4.5 -0.1 16.0); max (5.9 2.2 21.0);}\n")
	shmfile.write("};\n\ncastellatedMeshControls\n{\n")
	shmfile.write("        features\n        (\n")
	for patch in patch_names:
		str = '            {file "'+patch+'.eMesh"; level 3;}\n'
		shmfile.write(str)
	shmfile.write("        );\n\n")
	shmfile.write("        refinementSurfaces\n        {\n")
	for patch in patch_names:
		# set the patch type based on the name
		patch_type = getPatchType(patch)
		if patch_type == "inlet" or patch_type == "outlet" or patch_type == "slip" or patch_type == "inletOutlet":
			patch_type = "patch"
		str = "            "+patch+" {level (0 0); patchInfo {type "+patch_type+";} }\n"
		shmfile.write(str)
	shmfile.write("        }\n\n")
	with open(skeletondir+"snappyHexMeshTail") as f:
		shmfile.write(f.read())
# create the initial conditions files in 0
UTypeDict  = {"inlet":"fixedValue", "outlet":"zeroGradient", "wall":"fixedValue", "symmetry":"symmetry", "slip":"slip", "inletOutlet":"pressureInletOutletVelocity"}
UValueDict = {"inlet":"uniform (0 0 0)", "wall":"uniform (0 0 0)", "inletOutlet":"uniform (0 0 0)"}
buildZeroFile("U", UTypeDict, UValueDict)

pTypeDict  = {"inlet":"zeroGradient", "outlet":"fixedValue", "wall":"zeroGradient", "symmetry":"symmetry", "slip":"slip","inletOutlet":"empty"}
pValueDict = {"outlet":"uniform 103"}
buildZeroFile("p", pTypeDict, pValueDict)

# new additional 0 file, p_rgh
p_rghTypeDict  = {"inlet":"fixedFluxPressure", "outlet":"fixedFluxPressure", "wall":"fixedFluxPressure", "symmetry":"symmetry", "slip":"slip", "inletOutlet":"totalPressure"}
p_rghValueDict = {"inlet":"uniform 0", "outlet":"uniform 0", "wall":"uniform 0", "inletOutlet":"uniform 0"}
buildZeroFile("p_rgh", p_rghTypeDict, p_rghValueDict)

kTypeDict  = {"inlet":"fixedValue", "outlet":"zeroGradient", "wall":"kqRWallFunction", "symmetry":"symmetry", "slip":"slip","inletOutlet":"empty"}
kValueDict = {"inlet":"$internalField", "wall":"$internalField"}
buildZeroFile("k", kTypeDict, kValueDict)

epsilonTypeDict  = {"inlet":"fixedValue", "outlet":"zeroGradient", "wall":"epsilonWallFunction", "symmetry":"symmetry", "slip":"slip","inletOutlet":"empty"}
epsilonValueDict = {"inlet":"uniform 2.67", "wall":"uniform 2.67"}
buildZeroFile("epsilon", epsilonTypeDict, epsilonValueDict)

nutTypeDict  = {"inlet":"calculated", "outlet":"calculated", "wall":"nutUWallFunction", "symmetry":"symmetry", "slip":"slip","inletOutlet":"calculated"}
nutValueDict = {"inlet":"uniform 0", "outlet":"uniform 0", "wall":"uniform 0","inletOutlet":"uniform 0"}
buildZeroFile("nut", nutTypeDict, nutValueDict)

nuTildaTypeDict  = {"inlet":"fixedValue", "outlet":"zeroGradient", "wall":"zeroGradient", "symmetry":"symmetry", "slip":"slip","inletOutlet":"empty"}
nuTildaValueDict = {"inlet":"uniform 0"}
buildZeroFile("nuTilda", nuTildaTypeDict, nuTildaValueDict)

omegaTypeDict  = {"inlet":"fixedValue", "outlet":"zeroGradient", "wall":"zeroGradient", "symmetry":"symmetry", "slip":"slip","inletOutlet":"empty"}
omegaValueDict = {"inlet":"$internalField"}
buildZeroFile("omega", omegaTypeDict, omegaValueDict)

klTypeDict  = {"inlet":"fixedValue", "outlet":"zeroGradient", "wall":"fixedValue", "symmetry":"symmetry", "slip":"slip","inletOutlet":"empty"}
klValueDict = {"inlet":"uniform 0", "wall":"uniform 0"}
buildZeroFile("kl", klTypeDict, klValueDict)

ktTypeDict  = {"inlet":"fixedValue", "outlet":"zeroGradient", "wall":"fixedValue", "symmetry":"symmetry", "slip":"slip","inletOutlet":"empty"}
ktValueDict = {"inlet":"uniform 0", "wall":"uniform 0"}
buildZeroFile("kt", ktTypeDict, ktValueDict)

# new 0 file alpha.water.orig - when using in simulation make sure to copy over to new file alpha.water. alpha.water is changed during simulation and so the .orig file is retained to run future sims. 
alphawaterorigTypeDict  = {"inlet":"fixedValue", "outlet":"zeroGradient", "wall":"zeroGradient", "symmetry":"symmetry", "slip":"slip","inletOutlet":"inletOutlet"}
alphawaterorigValueDict = {"inlet":"uniform 1", "outlet":"uniform 0", "inletOutlet":"uniform 0"}
buildZeroFile("alphawaterorig", alphawaterorigTypeDict, alphawaterorigValueDict)

