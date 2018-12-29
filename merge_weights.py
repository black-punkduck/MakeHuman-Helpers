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
Skript to merge weights of default weight file with additional weight file to stdout
"""

import re
import sys
import json
import argparse
import wprint as wp

configfilename = "data/mh_helper.json"

parser = argparse.ArgumentParser(
        description='Merge weights of default weight file with additional weight file to stdout',
        epilog="an empty filename for WEIGHTS can be used for beautifying")
parser.add_argument('file', metavar='WEIGHTS', type=str, help='name of additional weight file')
parser.add_argument('-f', default="", metavar='default_weights', help='use different default weight file (default: see configuration)')
parser.add_argument('-p', default=4, metavar='PRECISION', type=int,  help='precision of weights (default: 4)')
parser.add_argument('-c', default=4, metavar='COLUMNS', type=int,  help='number of output columns for weights (default: 4)')
parser.add_argument('-r', action="store_true", help='use replace instead of merge, non-existing weights in default weight file will not appear for groups used in WEIGHTS (default: merge)')

args = parser.parse_args()

def RecalcWeights (weights, verts, replace=False):
    groups =  weights["weights"]
    for key in groups.keys():
        group = groups[key]
        if (key not in verts) or replace:
            verts[key] = {}
        for comb in range (0, len(group)):
            vnum = group[comb][0]
            val  = group[comb][1]
            verts[key][vnum] = val

#
# read configuration
#
cfile = open (configfilename, "r")
config = json.load (cfile)
cfile.close()

#
# read primary weight-file
#
if len(args.f):
    weightfilename = args.f
else:
    weightfilename = config["default_weights"]

cfile = open (weightfilename, "r")
weights = json.load (cfile)
cfile.close()

#
# recalculate weights to key form
#
verts = {}
RecalcWeights (weights, verts)

# we don't need this double in memory
weights["weights"] = {}

#
# now load second file, made it proper json
#
if args.file != '':
    secondjson = "{\"weights\":{ "
    with open(args.file) as f:
        secondjson += f.read()
        f.close()
    secondjson += "}}"

    secondweights = json.loads(secondjson)

    #
    # and add or replace
    #
    RecalcWeights (secondweights, verts, args.r)

#
# now output pseudo JSON:
# we need a shorter form and only the vnum and weights
#

dtext = "{\n"
of = 0
va = wp.v_array(prec=args.p, mcol=args.c)

for info in sorted(weights):
    if of != 0:
        dtext += ",\n"
    of = 1
    dtext += "\"" + info + "\": "
    if info != "weights":
        if (type(weights[info]) is str):
            dtext += "\"" + weights[info] + "\""
        elif (type(weights[info]) is int):
            dtext += str(weights[info]) 
    else:
        dtext += "{\n"
        dtext += va.appweights (verts)
        dtext += "}"

dtext += "\n}"
print (dtext)

exit (0)
