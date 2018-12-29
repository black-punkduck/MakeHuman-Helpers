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
Skript to normalize weights of a weights file so sum up to 1
"""

import re
import sys
import json
import argparse
import wprint as wp

configfilename = "data/mh_helper.json"

parser = argparse.ArgumentParser(description='Normalize weights of a weights file so sum up to 1.')
parser.add_argument('-f', default="", metavar='default_weights', help='use different default weight file (default: see configuration)')

parser.add_argument('-s', default=0, metavar='MINWEIGHTNUM', type=int,  help='lowest vertex number to check (default: 0)')
parser.add_argument('-m', default=0, metavar='MAXWEIGHTNUM', type=int,  help='highest vertex to check (default: see configuration ranges/_end_)')
parser.add_argument('-p', default=4, metavar='PRECISION', type=int,  help='precision of weights (default: 4)')
parser.add_argument('-c', default=4, metavar='COLUMNS', type=int,  help='number of output columns for weights (default: 4)')
parser.add_argument('-D', default=0.002, metavar='DIFFERENCE', type=float,  help='smallest discrepancy to recalculate default: 0.002)')
args = parser.parse_args()

#
# read configuration
#
cfile = open (configfilename, "r")
config = json.load (cfile)
cfile.close()

minweights = args.s
if args.m == 0:
    maxweights = config['ranges']['_end_']
else:
    maxweights = args.m

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

verts = {}
for key in weights["weights"].keys():
    group = weights["weights"][key]

    for comb in range (0, len(group)):
        vnum = int(group[comb][0])
        val  = group[comb][1]
        if vnum not in verts:
            verts[vnum] = { '_sum' : val, key: val}
        else:
            verts[vnum][key] = val
            verts[vnum]['_sum'] += val


#
# create weights to merge (replace mode)
#
new_g = {}

for vnum in range (minweights, maxweights):
    if vnum not in verts:
        continue
    else:
        r = 1.0 - verts[vnum]['_sum']
        if (r > args.D or r < -args.D):
            f = 1.0 / (1.0 - r)
            for group in verts[vnum].keys():
                if group != '_sum':
                    if group not in new_g:
                        new_g[group] = {}
                    new_g[group][vnum] = round(verts[vnum][group] * f,args.p)

va = wp.v_array(prec=args.p, mcol=args.c)
dtext = va.appweights (new_g)
print (dtext, end="")

