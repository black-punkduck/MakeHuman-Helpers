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
Blender output, tested on 2.79

skript to get a json-like output for vertex weights for skeletons, example

  "mFootRight": [
         [4899, 1.0], [4900, 1.0], [4901, 1.0], [4902, 1.0],
         ...
         [13131, 0.002]
   ],
   "mFootLeft": [
    ...
   ]

these lines then can be merge to skeleton

the program works with the selected (active) object
at the moment we have to merge all objects into a weights file
For simplication a fixed filename is used

"""

#
# get local path of file to find the import file (as long it is not in official blender directory)

import os
import sys
import bpy
filename = os.path.basename(__file__)
localpath = os.path.dirname(bpy.data.texts[filename].filepath)
sys.path.append(localpath)

import wprint as wp

prec = 3
active = bpy.context.active_object
vgrp = active.vertex_groups

#
# we create a copy for output
#
outverts = {};
smallest = 1 / 10**prec
va = wp.v_array(prec=prec, mcol=4)

# lets perform a loop on all groups
for grp in sorted(vgrp.keys()):
    # the index of a group is referenced by a vertex
    gindex = vgrp[grp].index
    outverts[grp] = {}
    
    # now check all vertices of the object
    for v in active.data.vertices:
        
        # check all groups of a vertex
        for g in v.groups:
            
            # if the index of the group fits to the current group
            # get the weight of the vertex
            if g.group == gindex:
                weight=vgrp[grp].weight(v.index)
                if weight > smallest:
                    outverts[grp][v.index] = weight
                    
text = "{\n\"weights\": {\n" + va.appweights (outverts) + "}\n}\n"

# filename should be changed later .. also check for errors ... but I am too lazy now
fp=open('/tmp/weights_export', 'w')  

fp.write (text)
fp.close()
    

