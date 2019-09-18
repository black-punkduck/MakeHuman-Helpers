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
to test export, select e.g. the skin (body) of a MakeHuman character with skeleton
and use file / export / MakeHuman Weight (.mhw)

export works with all meshes with at least one vertex group and at least a vertex assigned

to test import throw vertices away and import it on the same mesh.
"""

bl_info = {
    "name": "Import/Export MHW",
    "author": "black-punkduck",
    "version": (2019, 9, 18),
    "blender": (2, 79, 0),
    "location": "File > Export > MakeHuman Weightfile",
    "description": "Import and Export a MakeHuman weightfile (.mhw) based on vertex groups",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "MakeHuman"}

import re, os, struct, math
import mathutils
import bpy
import bmesh
import json
from bpy_extras.io_utils import (ImportHelper, ExportHelper)

mirror = {};

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

def read_mirror_tab (name):
    try:
        f = open(name)
        for line in f:
            m=re.search("(\d+)\s+(\d+)\s+(\w+)", line)
            if (m is not None):
                mirror[int (m.group(1))] = { 'm': int(m.group(2)), 's': m.group(3) }
        f.close()
        return True
    except IOError:
        return False

def export_weights (context, props):
    bpy.ops.object.mode_set(mode='OBJECT')
    active = context.active_object

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

    fp=open(props.filepath, 'w')
    fp.write (text)
    fp.close()

def import_weights (context, props):
    bpy.ops.object.mode_set(mode='OBJECT')

    fp = open(props.filepath, "r")
    weights = json.load(fp)
    fp.close

    ob = context.active_object
    ogroups = ob.vertex_groups

    groups = weights["weights"]

    vn = [1]
    for group in groups.keys():
        if group in ogroups:
            if props.replace:
                ogroups.remove(ogroups[group])
        vgrp = ogroups.new(group)
        for val in groups[group]:
            # print ("Vertexnum: " + str(val[0]) + " Value: " + str(val[1]))
            vn[0] = val[0]
            vgrp.add(vn, val[1], 'ADD')
    return

def mirror_weights (context, props):
    pass

class ExportMHW(bpy.types.Operator, ExportHelper):
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

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == "MESH"

    def invoke(self, context,event):
        self.properties.name = context.active_object.name
        self.properties.description = "generated weights for " + self.properties.name
        return super().invoke(context, event)

    def execute(self, context):
        export_weights(context, self.properties)
        return {'FINISHED'}

class ImportMHW(bpy.types.Operator, ImportHelper):
    '''Import an MHW File'''
    bl_idname = "import.mhw"
    bl_label = 'Import MHW'
    filename_ext = ".mhw"

    replace   = bpy.props.BoolProperty(name="Replace Groups", description="Replace or append vertex group", default=True)

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == "MESH"

    def invoke(self, context,event):
        return super().invoke(context, event)

    def draw (self, context):
        layout = self.layout
        layout.label("Create weights on: " + context.active_object.name)
        layout.prop(self, "replace")

    def execute(self, context):
        import_weights(context, self.properties)
        return {'FINISHED'}

class MIRRORMESH_OT_mesh_by_table(bpy.types.Operator):
    '''Mirror a mesh using a table'''
    bl_idname = "mirror.mesh_by_table"
    bl_label = 'Mirror Mesh using a table'
    bl_options = {'REGISTER'}

    filename = bpy.props.StringProperty(name="Filename", description="Name of the mirror table", maxlen=256, default="")

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == "MESH"

    def draw(self, context):
        obj = context.object
        layout = self.layout
        try: 
            mirrortab = obj['mirrortable']
        except:
            layout.prop(self, "filename")
        else:
            layout.label("Using table: " + mirrortab)
            

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        print ("Select the other side")
        obj = context.object
        try: 
            mirrortab = obj['mirrortable']
        except:
            mirrortab = self.properties.filename
            obj['mirrortable'] = mirrortab
        if read_mirror_tab (mirrortab) is False:
            ShowMessageBox("Cannot load " + mirrortab, "Mirror Table Mismatch", 'ERROR')
            return {'CANCELLED'}

        bpy.ops.mesh.select_mode(type="VERT")
        me = obj.data
        bm = bmesh.from_edit_mesh(me)

        # we need to remember the values
        for vert in bm.verts:
            if vert.index in mirror:
                mirror[vert.index]['o'] = vert.select
            else:
                ShowMessageBox("mirrortable too short", "Mirror Table Mismatch", 'ERROR')
                return {'CAŃCELLED'}


        # now select the mirrored ones
        for vert in bm.verts:
            try:
                vert.select = mirror[mirror[vert.index]['m']]['o']
            except:
                ShowMessageBox("mirrortable does not fit", "Mirror Table Mismatch", 'ERROR')
                return {'CANCELLED'}

        # recalculate edges
        for edge in bm.edges:
            if edge.verts[0].select and edge.verts[1].select:
                edge.select = True

        # recalculate faces
        for face in bm.faces:
            b = True
            for edges in face.edges:
                b &= edges.select
            if b:
                face.select = b
        bmesh.update_edit_mesh(me, True)
        return {'FINISHED'}

def export_func(self, context):
    self.layout.operator(ExportMHW.bl_idname, text="MakeHuman Weights (.mhw)")

def import_func(self, context):
    self.layout.operator(ImportMHW.bl_idname, text="MakeHuman Weights (.mhw)")

def mirror_func(self, context):
    self.layout.operator("mirror.mesh_by_table", text="Mirror Mesh by table")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_export.append(export_func)
    bpy.types.INFO_MT_file_import.append(import_func)
    #bpy.utils.register_class(MIRRORMESH_OT_mesh_by_table)
    bpy.types.VIEW3D_MT_select_edit_mesh.prepend(mirror_func)

def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_export.remove(export_func)
    bpy.types.INFO_MT_file_import.remove(import_func)
    #bpy.utils.unregister_class(MIRRORMESH_OT_mesh_by_table)
    bpy.types.VIEW3D_MT_select_edit_mesh.remove(mirror_func)


if __name__ == "__main__":
    register()

