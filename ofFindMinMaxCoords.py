#!/usr/bin/python
import re
import os
import sys

min_x = float('+inf')
min_y = float('+inf')
min_z = float('+inf')
max_x = float('-inf')
max_y = float('-inf')
max_z = float('-inf')
file_count = 0
vertex_count = 0
py_file_path = os.path.dirname(os.path.realpath(__file__))
args_len = len(sys.argv)
file_names = []
for i in range(1, args_len):
	file_names.append(sys.argv[i])


def set_coord(x, y, z):
	global min_x, min_y, min_z, max_x, max_y, max_z
	if x > max_x:
		max_x = x
	if x < min_x:
		min_x = x
	if y > max_y:
		max_y = y
	if y < min_y:
		min_y = y
	if z > max_z:
		max_z = z
	if z < min_z:
		min_z = z


for filename in file_names:
	with open(filename) as file:
		file_count = file_count + 1
		for line in file:
			match = re.search(r"vertex ([0-9.e\-+]+) ([0-9.e\-+]+) ([0-9.e\-+]+)", line)
			if match:
				x_coord = float(match.group(1))
				y_coord = float(match.group(2))
				z_coord = float(match.group(3))
				vertex_count = vertex_count + 1
				#print "Vertex " + str(x_coord) + " " + str(y_coord) + " " + str(z_coord)
				set_coord(x_coord, y_coord, z_coord)
print(str(file_count) + " files with " + str(vertex_count) + " verticies")
print("X: " + str(min_x) + " - " + str(max_x))
print("Y: " + str(min_y) + " - " + str(max_y))
print("Z: " + str(min_z) + " - " + str(max_z))
