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
Script to extract vertex weights from skeleton weight file for different parts.
"""

import re
import sys
import json
import argparse
import wprint as wp

configfilename = "data/mh_helper.json"

parser = argparse.ArgumentParser(description='Extract vertex weights from skeleton weight file for different parts.')
parser.add_argument('search', metavar='RANGE', type=str, help='name of range')
parser.add_argument('-f', default="", metavar='default_weights', help='use different default weight file (default: see configuration)')
parser.add_argument('-t', default="", metavar='transpose_file', help='an optional file to transpose groupnames')
parser.add_argument('-p', default=4, metavar='PRECISION', type=int,  help='precision of weights (default: 4)')
parser.add_argument('-c', default=4, metavar='COLUMNS', type=int,  help='number of output columns for weights (default: 4)')
args = parser.parse_args()

#
# read configuration
#
cfile = open (configfilename, "r")
config = json.load (cfile)
cfile.close()


#
# check for correct name
#
search = args.search.lower()

if search not in config["ranges"]:
    print (search + " is not existing in ranges!\n")
    rtext = 'Ranges:\n    '
    for key in config["ranges"].keys():
        rtext += (key + " ")
    print (rtext)
    exit (2)

# 
# define empty transpose dictionary
#
transpose = {}

#
# read tranpose file if needed
#
if len(args.t):
    with open(args.t) as f:
        for line in f:
            if re.search("^\s*$", line):
                continue
            elif re.search("^\s*#", line):
                continue
            m=re.search("(\S+)\s+(\S+)", line)
            if (m is not None):
                transpose[m.group(1)] = m.group(2)
        f.close()

#
# now read weight file
#
if len(args.f):
    weightfilename = args.f
else:
    weightfilename = config["default_weights"]

cfile = open (weightfilename, "r")
weights = json.load (cfile)
cfile.close()

dimens =  config["ranges"][search]
start = dimens[0]
end = dimens[1]

# create groups
# 
# system works with nested dictionaries

verts = {}

for key in weights["weights"].keys():
    group = weights["weights"][key]
    if key in transpose:
       key = transpose[key]
    if key not in verts:
        verts[key] = {}
    for comb in range (0, len(group)):
        vnum = group[comb][0]
        val  = group[comb][1]
        if start <= vnum <= end:
            if vnum not in verts[key]:
                verts[key][vnum] = val
            else:
                verts[key][vnum] += val

#
# now output pseudo JSON:
# we need a shorter form and only the vnum and weights
#
va = wp.v_array(prec=args.p, mcol=args.c)
dtext = va.appweights (verts)

print (dtext, end="")
exit (0)

