#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""

**Project Name:**      MakeHuman Support Tools

**Authors:**           Black Punkduck

**Code Home Page:**    https://github.com

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
Skript to create a symmetrical group from right to left or left to right.
"""

import re
import sys
import json
import argparse
import wprint as wp

configfilename = "data/mh_helper.json"

parser = argparse.ArgumentParser(description='Create a symmetrical group from right to left or left to right.')
parser.add_argument('group', metavar='GROUP', type=str, help='name of group')
parser.add_argument('direction', metavar='DIR', type=str, default='r', nargs='?', choices=['l','r'],
        help='left or right in case of no indication in group name')
parser.add_argument('-f', default="", metavar='default_weights', help='use different default weight file (default: see configuration)')
parser.add_argument('-p', default=4, metavar='PRECISION', type=int,  help='precision of weights (default: 4)')
parser.add_argument('-c', default=4, metavar='COLUMNS', type=int,  help='number of output columns for weights (default: 4)')
args = parser.parse_args()

dest = ""

#
# Get symmetrical group in case of pattern name
#
dirbyname = ''

m = re.search ("(\S+)(left)$", args.group, re.IGNORECASE)
if (m is not None):
    if m.group(2) == "left":
        dest = m.group(1) + "right"
    elif m.group(2) == "Left":
        dest = m.group(1) + "Right"
    elif m.group(2) == "LEFT":
        dest = m.group(1) + "RIGHT"
    else:
        print ("unknown pattern " + m.group(2))
        exit (-1)
    dirbyname = 'l'

if dest == "":
    m = re.search ("(\S+)(right)$", args.group, re.IGNORECASE)
    if (m is not None):
        if m.group(2) == "right":
            dest = m.group(1) + "left"
        elif m.group(2) == "Right":
            dest = m.group(1) + "Left"
        elif m.group(2) == "RIGHT":
            dest = m.group(1) + "LEFT"
        else:
            print ("unknown pattern " + m.group(2))
            exit (-1)
        dirbyname = 'r'

if dest == "":
    m = re.search ("(\S+)(\.[Ll])$", args.group)
    if (m is not None):
        if m.group(2) == ".l":
            dest = m.group(1) + ".r"
        if m.group(2) == ".L":
            dest = m.group(1) + ".R"
        dirbyname = 'l'

if dest == "":
    m = re.search ("(\S+)(\.[rR])$", args.group)
    if (m is not None):
        if m.group(2) == ".r":
            dest = m.group(1) + ".l"
        if m.group(2) == ".R":
            dest = m.group(1) + ".L"
        dirbyname = 'r'

#
# read configuration
#
cfile = open (configfilename, "r")
config = json.load (cfile)
cfile.close()

mirror = {}
#
# read mirror vertices
#
with open(config["mirror_vertices"]) as f:
    for line in f:
        m=re.search("(\d+)\s+(\d+)\s+(\w+)", line)
        if (m is not None):
            mirror[int (m.group(1))] = { 'm': int(m.group(2)), 's': m.group(3) }
    f.close()

#
# read weight-file
#
if len(args.f):
    weightfilename = args.f
else:
    weightfilename = config["default_weights"]

cfile = open (weightfilename, "r")
weights = json.load (cfile)
cfile.close()

groups =  weights["weights"]
newgroups = {args.group: {}, dest: {}}

if args.group not in groups.keys():
    print ("Weightfile does not contain " + args.group)
    exit(2)

# print (dest + " dirbyname " + dirbyname)

#
# create same and second group when name is given
#
if dirbyname != "":
    for vnum in groups[args.group]:
        m = mirror[vnum[0]]['m']
        newgroups[dest][m] =  vnum[1]
        newgroups[args.group][vnum[0]] =  vnum[1]
#
# symmetrize group otherwise
#
else:
    for vnum in groups[args.group]:
        if mirror[vnum[0]]['s'] == args.direction:
            m = mirror[vnum[0]]['m']
            newgroups[args.group][vnum[0]] =  vnum[1]
            newgroups[args.group][m] =  vnum[1]
        elif mirror[vnum[0]]['s'] == "m":
            newgroups[args.group][vnum[0]] =  vnum[1]

#
# now output pseudo JSON:
# we need a shorter form and only the vnum and weights
#
va = wp.v_array(prec=args.p, mcol=args.c)
dtext = va.appweights (newgroups)

print (dtext, end="")
exit (0)
