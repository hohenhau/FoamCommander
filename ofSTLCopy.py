#!/usr/bin/python
import re
import os
import sys

class Vector:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Facet:
    def __init__(self, normal, vertices):
        self.normal = normal
        self.vertices = vertices
    
    def print_translate(self, x_offset, y_offset, z_offset):
        print(f" facet normal {self.normal.x} {self.normal.y} {self.normal.z}")
        print("  outer loop")
        for vertex in self.vertices:
            print(f"   vertex {vertex.x + x_offset} {vertex.y + y_offset} {vertex.z + z_offset}")
        print("  endloop")
        print(" endfacet")


def set_coord(x, y, z):
    """Updates global min/max coordinates."""
    global min_x, min_y, min_z, max_x, max_y, max_z
    min_x, max_x = min(min_x, x), max(max_x, x)
    min_y, max_y = min(min_y, y), max(max_y, y)
    min_z, max_z = min(min_z, z), max(max_z, z)


def parse_files(file_names):
    """Parses the given STL files and extracts facets and vertex data."""
    facet_list = []
    re_normal = re.compile(r"facet normal ([0-9.e\-+]+) ([0-9.e\-+]+) ([0-9.e\-+]+)")
    re_vertex = re.compile(r"vertex ([0-9.e\-+]+) ([0-9.e\-+]+) ([0-9.e\-+]+)")
    re_endfacet = re.compile(r"endfacet")
    
    for filename in file_names:
        with open(filename) as file:
            for line in file:
                normal_match = re_normal.search(line)
                if normal_match:
                    normal = Vector(*map(float, normal_match.groups()))
                    vertex_list = []
                else:
                    vertex_match = re_vertex.search(line)
                    if vertex_match:
                        vertex = Vector(*map(float, vertex_match.groups()))
                        vertex_list.append(vertex)
                        set_coord(vertex.x, vertex.y, vertex.z)
                if re_endfacet.search(line):
                    facet_list.append(Facet(normal, vertex_list))
    return facet_list


if __name__ == "__main__":
    """Main execution block."""
    min_x, min_y, min_z = float('+inf'), float('+inf'), float('+inf')
    max_x, max_y, max_z = float('-inf'), float('-inf'), float('-inf')
    
    if len(sys.argv) < 7:
        print("Arguments needed: x_mult y_mult z_mult x_space y_space z_space files...")
        sys.exit(1)
    
    x_mult, y_mult, z_mult = map(int, sys.argv[1:4])
    x_space, y_space, z_space = map(float, sys.argv[4:7])
    file_names = sys.argv[7:]
    
    facet_list = parse_files(file_names)
    
    x_width, y_width, z_width = x_space, y_space, z_space
    
    print("solid surface")
    for x_i in range(x_mult):
        for y_i in range(y_mult):
            for z_i in range(z_mult):
                for facet in facet_list:
                    facet.print_translate(x_i * x_width, y_i * y_width, z_i * z_width)
    print("endsolid")
