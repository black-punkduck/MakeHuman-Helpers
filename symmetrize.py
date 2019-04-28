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
Skript to create a symmetrical group from right to left or left to right.
Can also be used to create a complete symmetrical character based on the mirror table
"""

import re
import sys
import json
import argparse
import wprint as wp

# check orientation of name and calculate partner name
#
def evaluate_side(name):
    orientation = 'm'
    partner = ""
    m = re.search ("(\S+)(left)$", name, re.IGNORECASE)
    if (m is not None):
        if m.group(2) == "left":
            partner = m.group(1) + "right"
        elif m.group(2) == "Left":
            partner = m.group(1) + "Right"
        elif m.group(2) == "LEFT":
            partner = m.group(1) + "RIGHT"
        else:
            print ("unknown pattern " + m.group(2))
            exit (-1)
        orientation = 'l'

    if partner == "":
        m = re.search ("(\S+)(right)$", name, re.IGNORECASE)
        if (m is not None):
            if m.group(2) == "right":
                partner = m.group(1) + "left"
            elif m.group(2) == "Right":
                partner = m.group(1) + "Left"
            elif m.group(2) == "RIGHT":
                partner = m.group(1) + "LEFT"
            else:
                print ("unknown pattern " + m.group(2))
                exit (-1)
            orientation = 'r'

    if partner == "":
        m = re.search ("(\S+)(\.[Ll])$", name)
        if (m is not None):
            if m.group(2) == ".l":
                partner = m.group(1) + ".r"
            if m.group(2) == ".L":
                partner = m.group(1) + ".R"
            orientation = 'l'

    if partner == "":
        m = re.search ("(\S+)(\.[rR])$", name)
        if (m is not None):
            if m.group(2) == ".r":
                partner = m.group(1) + ".l"
            if m.group(2) == ".R":
                partner = m.group(1) + ".L"
            orientation = 'r'

    if orientation == 'm':
        partner = name
    return (orientation, partner)


configfilename = "data/mh_helper.json"

parser = argparse.ArgumentParser(description='Create a symmetrical group from right to left or left to right.')
parser.add_argument('group', metavar='GROUP', type=str, help='name of group or use "=all=" for all groups')
parser.add_argument('orientation', metavar='ORIENT', type=str, default='l', nargs='?', choices=['l','r'],
        help='left or right in case of no indication in group name, use this for "=all=" especially (default: l)')
parser.add_argument('-f', default="", metavar='default_weights', help='use different default weight file (default: see configuration)')
parser.add_argument('-p', default=4, metavar='PRECISION', type=int,  help='precision of weights (default: 4)')
parser.add_argument('-c', default=4, metavar='COLUMNS', type=int,  help='number of output columns for weights (default: 4)')
args = parser.parse_args()



#
# Get symmetrical group in case of pattern name, "=all=" does not contain this pattern
#
(orientation, partner) = evaluate_side(args.group)

if orientation == "m":
    orientation = args.orientation

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

#
# generate an array with all groups to be mirrored in case of '=all='
# else check if weightfile has the desired group and create only
# one task
#
tasks = {}
taskcount = 0

if args.group == '=all=':
    for group in groups.keys():
        (o, partner) = evaluate_side(group)
        if o == orientation or o == 'm':
            tasks[taskcount] = {'group': group, 'orient': o, 'partner': partner}
            taskcount += 1
else:
    if args.group not in groups.keys():
        print ("Weightfile does not contain " + args.group)
        exit(2)
    (o, partner) = evaluate_side(args.group)
    tasks[0] = {'group': args.group, 'orient': o, 'partner': partner}


newgroups = {}

for task in tasks:
    group = tasks[task]["group"]
    partner = tasks[task]["partner"]
    group_orientation = tasks[task]["orient"]
    if group_orientation == 'm':
        newgroups[group] = {}
        for vnum in groups[group]:
            if mirror[vnum[0]]['s'] == orientation:
                m = mirror[vnum[0]]['m']
                newgroups[group][vnum[0]] =  vnum[1]
                newgroups[group][m] =  vnum[1]
            elif mirror[vnum[0]]['s'] == "m":
                newgroups[group][vnum[0]] =  vnum[1]
    else:
        newgroups[group] = {}
        newgroups[partner] = {}
        for vnum in groups[group]:
            m = mirror[vnum[0]]['m']
            newgroups[partner][m] =  vnum[1]
            newgroups[group][vnum[0]] =  vnum[1]
#
# now output pseudo JSON:
# we need a shorter form and only the vnum and weights
#
va = wp.v_array(prec=args.p, mcol=args.c)
dtext = va.appweights (newgroups)

print (dtext, end="")
exit (0)
