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
if args_len < 7:
	print("Aguments needed: x_mult y_mult z_mult x_space y_space z_space files...")
x_mult = int(sys.argv[1])
y_mult = int(sys.argv[2])
z_mult = int(sys.argv[3])
x_space = float(sys.argv[4])
y_space = float(sys.argv[5])
z_space = float(sys.argv[6])
file_names = []
for i in range(7, args_len):
	file_names.append(sys.argv[i])

class Vector:
	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z

class Facet:
	def __init__(self, normal, verticies):
		self.normal = normal
		self.verticies = verticies
	
	def print_translate(self, x_offset, y_offset, z_offset):
		print(" facet normal " + str(self.normal.x) + " " + str(self.normal.y) + " " + str(self.normal.z))
		print("  outer loop")
		for vertex in self.verticies:
			print("   vertex " + str(vertex.x + x_offset) + " " + str(vertex.y + y_offset) + " " + str(vertex.z + z_offset))
		print("  endloop")
		print(" endfacet")


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

facet_list = []
vertex_list = []
re_normal = re.compile(r"facet normal ([0-9.e\-+]+) ([0-9.e\-+]+) ([0-9.e\-+]+)")
re_vertex = re.compile(r"vertex ([0-9.e\-+]+) ([0-9.e\-+]+) ([0-9.e\-+]+)")
re_endfacet = re.compile(r"endfacet")

for filename in file_names:
	with open(filename) as file:
		file_count = file_count + 1
		for line in file:
			normal_match = re_normal.search(line)
			if normal_match:
				x_normal = float(normal_match.group(1))
				y_normal = float(normal_match.group(2))
				z_normal = float(normal_match.group(3))
				normal = Vector(x_normal, y_normal, z_normal)
				vertex_list = []	# start a new vertex list for this new facet
			else:
				vertex_match = re_vertex.search(line)
				if vertex_match:
					x_coord = float(vertex_match.group(1))
					y_coord = float(vertex_match.group(2))
					z_coord = float(vertex_match.group(3))
					vertex = Vector(x_coord, y_coord, z_coord)
					vertex_list.append(vertex)
					vertex_count = vertex_count + 1
					#print "Vertex " + str(x_coord) + " " + str(y_coord) + " " + str(z_coord)
					set_coord(x_coord, y_coord, z_coord)
			if re_endfacet.search(line):
				new_facet = Facet(normal, vertex_list)
				facet_list.append(new_facet)

#print "// " + str(file_count) + " files with " + str(vertex_count) + " verticies"
#print "// X: " + str(min_x) + " - " + str(max_x)
#print "// Y: " + str(min_y) + " - " + str(max_y)
#print "// Z: " + str(min_z) + " - " + str(max_z)
#print "// number of facets: " + str(len(facet_list))

#x_width = max_x - min_x
#y_width = max_y - min_y
#z_width = max_z - min_z
x_width = x_space
y_width = y_space
z_width = z_space

x_count = x_mult
y_count = y_mult
z_count = z_mult


print("solid surface")
for x_i in range(0, x_count):
	for y_i in range(0, y_count):
		for z_i in range(0, z_count):
			for facet in facet_list:
				facet.print_translate(x_i*x_width, y_i*y_width, z_i*z_width)
print("endsolid")
