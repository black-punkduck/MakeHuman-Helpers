#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""

**Project Name:**      MakeHuman-Helpers

**Authors:**           Black Punkduck

**Code Home Page:**    https://github.com/black-punkduck/MakeHuman-Helpers

**Copyright(c):**      Black Punkduck

**Licensing:**         AGPL3

    This file is part of the MakeHuman Support Tools

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

Abstract
--------
Script to merge additional parts to base mesh
"""

import re
import sys
import json
import argparse

configfilename = "data/mh_helper.json"

parser = argparse.ArgumentParser(description='Appends additional meshes to the base mesh.')
parser.add_argument('-b', default="", metavar='default_weights', help='use different base mesh file (default: see configuration)')
parser.add_argument('-p', default=4, metavar='PRECISION', type=int,  help='precision of weights (default: 4)')
parser.add_argument('file', metavar='WEIGHTS', type=str, help='name of additional mesh file')
args = parser.parse_args()

#
# read configuration
#
cfile = open (configfilename, "r")
config = json.load (cfile)
cfile.close()

if len(args.b):
    meshfile = args.b
else:
    meshfile = config["base_object"]

# read the object file
#
vnum = 0
vtnum = 0
linebuf = []
with open(meshfile) as f:
    for line in f:
        linebuf.append(line)
        if (re.search("^\s*v\s+", line) is not None):
            vnum += 1
            continue
        if (re.search("^\s*vt\s+", line) is not None):
            vtnum += 1
            continue
    f.close()

print (str(vnum) + " vertices, " + str(vtnum) + " UVs detected", file=sys.stderr)

# read file to append, create lines.
#
flinebuf = []
vlinebuf = []
vtlinebuf = []
groupnames = False
with open(args.file) as f:
    for line in f:
        # v - lines to add
        m=re.search("^\s*v\s+(\S+)\s+(\S+)\s+(\S+)", line)
        if (m is not None):
            vlinebuf.append ("v " +
                    str (round (float(m.group(1)), args.p)) + " " +
                    str (round (float(m.group(2)), args.p)) + " " +
                    str (round (float(m.group(3)), args.p)) + "\n")
            continue

        # vt - lines to add
        m=re.search("^\s*vt\s+", line)
        if (m is not None):
            vtlinebuf.append (line)
            groupnames = True
            continue

        # f - lines to add
        m=re.search("^\s*f\s+(\d+)/(\d+)\s+(\d+)/(\d+)\s+(\d+)/(\d+)\s+(\d+)/(\d+)", line)
        if (m is not None):
            flinebuf.append ("f "+ 
                    str(int(m.group(1)) + vnum) + "/" + str(int(m.group(2)) + vtnum) + " " +
                    str(int(m.group(3)) + vnum) + "/" + str(int(m.group(4)) + vtnum) + " " +
                    str(int(m.group(5)) + vnum) + "/" + str(int(m.group(6)) + vtnum) + " " +
                    str(int(m.group(7)) + vnum) + "/" + str(int(m.group(8)) + vtnum) + "\n")
            continue

        # g will be added to f-line buf, after vt section
        m=re.search("^\s*g\s+", line)
        if (m is not None):
            if groupnames is True:
                flinebuf.append (line)

    f.close()


#
# output of new mesh
#
# put new vertices before vt (step = 0)
# put new vertex-UV before group (step = 1)

step = 0
for line in linebuf:
    if step == 0:
        m=re.search("^\s*vt\s+", line)
        if (m is not None):
            step = 1
            print ("".join (vlinebuf), end="")
    if step == 1:
        m=re.search("^\s*g\s+", line)
        if (m is not None):
            step = 2
            print ("".join (vtlinebuf), end="")
    print (line, end="")

if step == 2:
    print ("".join (flinebuf), end="")
else:
    print ("Problems to find positions in file")
    exit (2)
exit (0)

