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
this plugin should be copied to standard addons directory of blender.
to test it, select e.g. the skin (body) of a MakeHuman character with skeleton
and use file / export / MakeHuman Weight (.mhw)

this program works with all meshes with at least one vertex group and at least a vertex assigned
"""

bl_info = {
    "name": "Export MHW",
    "author": "black-punkduck",
    "version": (2019, 4, 27),
    "blender": (2, 79, 0),
    "location": "File > Export > MakeHuman Weightfile",
    "description": "Export a MakeHuman weightfile (.mhw) based on vertex groups",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "MakeHuman"}

import os, struct, math
import mathutils
import bpy
import bpy_extras.io_utils

class v_array:
    def __init__(self, prec=4, mcol=4):
        self.prec = prec
        self.mcol = mcol
        self.col = -1

    def new(self):
        self.col = -1
    
    def appval(self, num, val):
        x = round(val, self.prec)
        if x ==  0.0:
            return ("")
        t = ""
        if self.col == 0:
            t += ",\n\t\t"
        elif self.col < 0:
            self.col = 0
            t += "\t\t"
        else:
            t += ", "

        t += "[" + str(num) + ", " + str(x) + "]"
        self.col +=1
        if self.col == self.mcol:
            self.col = 0
        return t

    def appgroup (self, verts, key):
        self.new()
        t = "\t\"" + key + "\": [\n"
        for vnum in sorted(verts[key]):
            t += self.appval (vnum, verts[key][vnum])
        t += "\n\t]"
        return t

    def appweights (self, verts):
        t = ""
        for key in sorted(verts):
            elems = len (verts[key])
            if elems > 0:
                if t != "":
                    t += ",\n"
                t += self.appgroup (verts, key)
        t += "\n"
        return t

def ShowMessageBox(message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)

def exportMHW(context, file, props):
    bpy.ops.object.mode_set(mode='OBJECT')
    active = context.active_object
    #print (active.name)
    if active == None:
        ShowMessageBox("No object selected", "Invalid selection", 'ERROR')
        return

    if active.type != "MESH":
        ShowMessageBox("object is not a mesh", "Invalid selection", 'ERROR')
        return

    vgrp = active.vertex_groups

    if vgrp == None or len(vgrp) == 0:
        ShowMessageBox("object has no vertex groups", "Missing attributes", 'ERROR')
        return

    outverts = {};
    smallest = 1 / 10**props.precision
    cnt = 0
    va = v_array(prec=props.precision, mcol=props.columns)

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
                        cnt += 1

    if cnt == 0:
        ShowMessageBox("No vertices assigned", "Missing assignment", 'ERROR')
        return

    text = "{\n\"copyright\": \"" + props.author + "\",\n" + \
        "\"description\": \"" + props.description + "\",\n" + \
        "\"license\": \"" + props.license + "\",\n" + \
        "\"name\": \"" + props.name + "\",\n" + \
        "\"version\": " + props.version + ",\n" + \
        "\"weights\": {\n" + va.appweights (outverts) + "}\n}\n"

    fp=open(file, 'w')
    fp.write (text)
    fp.close()

class ExportMHW(bpy.types.Operator, bpy_extras.io_utils.ExportHelper):
    '''Export an MHW File'''
    bl_idname = "export.mhw"
    bl_label = 'Export MHW'
    filename_ext = ".mhw"

    author      = bpy.props.StringProperty(name="Author", description="Name of author", maxlen=64, default="unknown")
    name        = bpy.props.StringProperty(name="Name", description="Name of weightfile", maxlen=64, default="unknown")
    description = bpy.props.StringProperty(name="Description", description="Description of weightfile", maxlen=1024, default="")
    license     = bpy.props.StringProperty(name="License", description="Type of license", maxlen=64, default="CC BY 4.0")
    precision   = bpy.props.IntProperty(name="Precision", min=2, max=5, description="Precision of weights", default=3)
    columns     = bpy.props.IntProperty(name="Columns", min=1, max=16, description="Columns in weightfile", default=4)
    version     = bpy.props.StringProperty(name="Version", description="MakeHuman version", maxlen=20, default="110")

    def invoke (self, context,event):
        active = None

        if hasattr(context, 'active_object'):
            active = context.active_object

        name = ""
        desc = ""
        if active != None:
            name   = active.name
            desc   = "generated weights for " + name
        self.properties.name = name
        self.properties.description = desc
        return bpy_extras.io_utils.ExportHelper.invoke(self, context, event)


    def execute(self, context):

        active = None

        if hasattr(context, 'active_object'):
            active = context.active_object

        name = ""
        desc = ""
        if active != None:
            name   = active.name
            desc   = "generated weights for " + name

        self.properties.name = name
        self.properties.description = desc

        exportMHW(context, self.properties.filepath, self.properties)
        return {'FINISHED'}

def menu_func(self, context):
    self.layout.operator(ExportMHW.bl_idname, text="MakeHuman Weights (.mhw)")


def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(menu_func)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(menu_func)


if __name__ == "__main__":
    register()

