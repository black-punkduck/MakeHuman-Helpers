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
Skript to create a symmetrical object from right to left or left to right.
Can also be used to create a complete symmetrical geometry based on the mirror table
"""

import re
import sys
import argparse


configfilename = "data/mh_helper.json"

parser = argparse.ArgumentParser(description='Create a symmetrical wavefront-file')
parser.add_argument('objfile', metavar='OBJFILE', type=str, help='wavefront .obj file')
parser.add_argument('orientation', metavar='ORIENT', type=str, default='l', nargs='?', choices=['l','r'],
        help='use left or right side to be mirrored (default: l)')
parser.add_argument('-m', default="", metavar='mirror_table', help='use different mirror_table (default: see configuration)')
args = parser.parse_args()


def printerror(linenum, message):
    if linenum == 0:
        print ("post check: " + message)
    else:
        print ("line " + str(linenum) + ": " + message)

#
# read configuration
#
if len(args.m):
    mirrorfilename = args.m
else:
    cfile = open (configfilename, "r")
    config = json.load (cfile)
    cfile.close()
    mirrorfilename = config["mirror_vertices"]

mirror = {} # for mirroring
vcnt   = {} # for counting only to figure out completeness

#
# read mirror vertices and check
#       n1, n2 equal => 'm'
#       n1, n2 = 'l' => n2, n1 = 'r'
#       each value must occur 2 times (vcnt used, maximum value evaluated)

linenum = 0
maxc = 0
errcnt = 0
with open(mirrorfilename) as f:
    for line in f:
        linenum += 1
        m=re.search("(\d+)\s+(\d+)\s+([lrm])", line)
        if (m is not None):
            n1 = int(m.group(1))
            n2 = int(m.group(2))
            di = m.group(3)

            if n1 in vcnt:
                vcnt[n1] += 1
            else:
                vcnt[n1] = 1

            if n2 in vcnt:
                vcnt[n2] += 1
            else:
                vcnt[n2] = 1

            if n1 > maxc:
                maxc = n1
            if n2 > maxc:
                maxc = n2

            if n1 == n2 and di != "m":
                printerror(linenum, "direction for identical values must be 'm'")
                errcnt += 1
            elif n2 in mirror:
                if di == mirror[n2]['s']:
                    printerror(linenum, "peer " + str(n1) + " " + str(n2) + " both on same side")
                    errcnt += 1
            mirror[n1] = { 'm': n2, 's': di }
    f.close()

for ind in range (0, maxc):
    if ind not in vcnt:
        printerror (0, "Vertex " + str(ind) + " is missing.")
        errcnt += 1
    elif vcnt[ind] != 2:
        printerror (0, "Vertex " + str(ind) + " has " + str(vcnt[ind]) + " instead of 2 occurences.")
        errcnt += 1

if errcnt > 0:
    print ("Fix mirror-table '" + mirrorfilename + "'. Program aborted.")
    exit (10)

coords = {}

# now read obj file
with open(args.objfile) as f:
    vtnum = 0
    for line in f:
        m=re.search("^v (\S+)\s+(\S+)\s+(\S+)", line)
        if (m is not None):
            coords[vtnum] = {'x': float(m.group(1)), 'y': float(m.group(2)), 'z': float(m.group(3))}
            vtnum += 1

    # read second time
    f.seek(0)
    vtnum = 0
    for line in f:
        m=re.search("^v (\S+)\s+(\S+)\s+(\S+)", line)
        if (m is not None):
            if mirror[vtnum]['s'] == 'm' or mirror[vtnum]['s'] == args.orientation:
                print (line, end='')
            else:
                m = mirror[vtnum]['m'];
                print ("v " + str(-coords[m]['x']) + " " + str(coords[m]['y']) + " " + str(coords[m]['z']))
            vtnum += 1
        else:
            print (line, end='')

    f.close()

exit (0)
