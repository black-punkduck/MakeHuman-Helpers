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
and use file > export > MakeHuman Weights (.mhw)

export works with all meshes with at least one vertex group and at least a vertex assigned

to test import throw vertices away and import it on the same mesh.

to test the mirror function you have to assign a mirror table to the object

use edit mode
    mesh > vertices > assign mirror table

mirror selection in edit mode
    select > Mirror Mesh by Table

mirror vertex groups (edit mode .. switches to object mode)
    mesh > mirror > Mirror Vertex Groups by Table (L>R)
    mesh > mirror > Mirror Vertex Groups by Table (R>L)

mirror shape keys (edit mode .. switches to object mode)
    mesh > mirror > Mirror Shape Keys by Table (L>R)
    mesh > mirror > Mirror Shape Keys by Table (R>L)
"""

bl_info = {
    "name": "MakeHuman Weighting",
    "author": "black-punkduck",
    "version": (2019, 9, 22),
    "blender": (2, 80, 0),
    "location": "File > Export > MakeHuman Weightfile",
    "description": "Import and Export a MakeHuman weightfile (.mhw), Mirroring using a mirror-table",
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

# check orientation of name and calculate partner name
#
def evaluate_side(name):
    orientation = 'm'
    partner = ""
    m = re.search ("(\S+)(left)$", name, re.IGNORECASE)
    if (m is not None):
        if m.group(2) == "left":
            partner = m.group(1) + "right"
            orientation = 'l'
        elif m.group(2) == "Left":
            partner = m.group(1) + "Right"
            orientation = 'l'
        elif m.group(2) == "LEFT":
            partner = m.group(1) + "RIGHT"
            orientation = 'l'
        else:
            partner = name

    if partner == "":
        m = re.search ("(\S+)(right)$", name, re.IGNORECASE)
        if (m is not None):
            if m.group(2) == "right":
                partner = m.group(1) + "left"
                orientation = 'r'
            elif m.group(2) == "Right":
                partner = m.group(1) + "Left"
                orientation = 'r'
            elif m.group(2) == "RIGHT":
                partner = m.group(1) + "LEFT"
                orientation = 'r'
            else:
                partner = name

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
        self.layout.label(text=message)

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

def GetMirrorVNum (x, y, z, m, eps):
    if (eps == 0):
        for vnum in mirror.keys():
            if mirror[vnum]["m"] == -1 and mirror[vnum]["x"] == -x and mirror[vnum]["y"] == y and mirror[vnum]["z"] ==  z:
                mirror[vnum]["m"] = m
                return (vnum)
    else:
        for vnum in mirror.keys():
            if mirror[vnum]["m"] == -1:
                dx = abs(mirror[vnum]["x"] + x)
                dy = abs(mirror[vnum]["y"] - y)
                dz = abs(mirror[vnum]["z"] - z)
                dist = math.sqrt (dx * dx + dy * dy + dz * dz)
                if dist <= eps:
                    mirror[vnum]["m"] = m
                    return (vnum)

    return (-1);

def export_mirrortab(context, props):
    verts = context.active_object.data.vertices
    bpy.ops.object.mode_set(mode='OBJECT')
    wm = bpy.context.window_manager

    # create the table without the mirroring

    nvnum = 0
    for vnum, vrt in enumerate(verts):
        mirror[vnum] = { 'x': vrt.co[0], 'y': vrt.co[1], 'z': vrt.co[2], 'm': -1 }
        nvnum += 1

    # now calculate mirror
    wm.progress_begin(0,10)
    progress = 1

    still_unmirrored = True
    unmirrored = 0
    for eps in [0, 0.0001, 0.0002, 0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05]:
        if still_unmirrored and eps <= props.eps:
            wm.progress_update(progress)
            # print ("epsilon " + str(eps) + ": ")

            unmirrored = 0
            for i in range (0, nvnum):
                if mirror[i]["m"] == -1:
                    mirror[i]["m"] = GetMirrorVNum ( mirror[i]["x"], mirror[i]["y"], mirror[i]["z"], i, eps)
                    if ( mirror[i]["m"]  == -1):
                        unmirrored +=1
            # print (str(unmirrored) + " unmirrored vertices")
            if unmirrored == 0:
                still_unmirrored = False
            progress += 1

    wm.progress_end()

    with open(props.filepath, 'w') as fp:
        for i in range (0, nvnum):
            pos = 'l'
            if mirror[i]["m"] == i:
                pos = 'm'
            elif mirror[i]["x"] < 0:
                pos = 'r'
            fp.write (str(i) + " " + str(mirror[i]["m"]) + " " + pos + "\n")
        fp.close()

    if still_unmirrored:
        ShowMessageBox(str(unmirrored) + " Vertices. Check lines with -1 in file", "Mesh cannot be fully mirrored", 'ERROR')

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
        vgrp = ogroups.new(name=group)
        for val in groups[group]:
            # print ("Vertexnum: " + str(val[0]) + " Value: " + str(val[1]))
            vn[0] = val[0]
            vgrp.add(vn, val[1], 'ADD')
    return

#
# mirror the vertex groups
#
# direction will be 'l' or 'r' which is the source-side
#
def mirror_vgroups (context, direction):
    # print ("in mirror vgroups " + direction)
    bpy.ops.object.mode_set(mode='OBJECT')
    ob = context.active_object
    vgrp = ob.vertex_groups

    # load mirrored table
    #
    mirrortab = ob['mirrortable']
    if read_mirror_tab (mirrortab) is False:
        ShowMessageBox("Cannot load " + mirrortab, "Mirror Table Mismatch", 'ERROR')
        return {'CANCELLED'}

    # delete all groups of destination side
    #   
    for grp in sorted(vgrp.keys()):
        (orientation, partner) = evaluate_side(grp)
        if orientation != 'm' and orientation != direction:
            # print ("delete group " + grp)
            vg = ob.vertex_groups.get(grp)
            ob.vertex_groups.remove(vg)

    # now create mirrored groups and symmetrize mid ones
    #
    vn = [1]    # our small array ;-)

    for grp in sorted(vgrp.keys()):
        #
        # read the group in temporary dictionary
        #
        temp={}
        dgrp = ob.vertex_groups
        gindex = dgrp[grp].index
        for v in ob.data.vertices:
            for g in v.groups:

                # if the index of the group fits to the current group
                # get the weight of the vertex
                if g.group == gindex:
                    temp[v.index] = dgrp[grp].weight(v.index)

        # now check what to do
        #
        (orientation, partner) = evaluate_side(grp)
        if orientation == 'm':

            # this is a group which need to be mirrored on the x-axis
            # delete and recreate it (did not find an "empty") function
            #
            # print ("Symmetrize " + grp)
            vg = ob.vertex_groups.get(grp)
            ob.vertex_groups.remove(vg)
            ngrp = vgrp.new(name=grp)

            # now create the symmetric group use the same weight for both
            # values in case of the table has the same direction, if it is on
            # mid line use it once
            #
            for index in temp:
                if mirror[index]['s'] == direction:
                    vn[0] = index
                    ngrp.add(vn, temp[index], 'ADD')
                    vn[0] = mirror[index]['m']
                    ngrp.add(vn, temp[index], 'ADD')
                elif mirror[index]['s'] == 'm':
                    vn[0] = index
                    ngrp.add(vn, temp[index], 'ADD')
        else:
            # in case of a left or right group create the identical partner
            # using identical weights
            #
            #print ("Creating Partner " + partner)
            ngrp = vgrp.new(name=partner)

            for index in temp:
                vn[0] = mirror[index]['m']
                ngrp.add(vn, temp[index], 'ADD')

    return {'FINISHED'}

def mirror_shapekeys (context, direction):
    bpy.ops.object.mode_set(mode='OBJECT')
    ob = context.active_object

    # load mirrored table
    #
    mirrortab = ob['mirrortable']
    if read_mirror_tab (mirrortab) is False:
        ShowMessageBox("Cannot load " + mirrortab, "Mirror Table Mismatch", 'ERROR')
        return {'CANCELLED'}

    # delete all shapekeys of destination side
    # keep those in an array we want to change
    #   

    names = []

    for shape in ob.data.shape_keys.key_blocks:
        (orientation, partner) = evaluate_side(shape.name)
        if orientation != 'm' and orientation != direction:
            print ("delete shape key " + shape.name)
            ob.shape_key_remove(shape)
        else:
            # in case of "Basis", skip
            if shape.name != "Basis":
                names.append(shape.name)
            

    # get original object once
    basis = ob.data.shape_keys.key_blocks["Basis"].data

    # now create mirrored groups and symmetrize mid ones
    #
    for name in names:
        # now check what to do
        #
        (orientation, partner) = evaluate_side(name)

        if orientation == 'm':
            # create internal group symmetry
            # print ("Symmetrize " + name)
            source = ob.data.shape_keys.key_blocks[name].data
            for idx, vert in enumerate (source):
                if mirror[idx]['s'] == direction:
                    destvert = mirror[idx]['m']
                    x = basis[idx].co[0] - vert.co[0]
                    y = basis[idx].co[1] - vert.co[1]
                    z = basis[idx].co[2] - vert.co[2]
                    source[destvert].co = [basis[destvert].co[0] +x , basis[destvert].co[1] - y, basis[destvert].co[2] -z]
        else:
            # create symmetric group
            # print ("Creating Partner of " + name + ": " + partner)

            nshapeKey = ob.shape_key_add(from_mix=False)
            nshapeKey.name = partner
            source = ob.data.shape_keys.key_blocks[name].data

            for idx, vert in enumerate (source):
                destvert = mirror[idx]['m']
                x = basis[idx].co[0] - vert.co[0]
                y = basis[idx].co[1] - vert.co[1]
                z = basis[idx].co[2] - vert.co[2]
                nshapeKey.data[destvert].co = [basis[destvert].co[0] +x , basis[destvert].co[1] - y, basis[destvert].co[2] -z]

    return {'FINISHED'}

class ExportMHW(bpy.types.Operator, ExportHelper):
    '''Export an MHW File'''
    bl_idname = "export.mhw"
    bl_label = 'Export MHW'
    filename_ext = ".mhw"

    author      : bpy.props.StringProperty(name="Author", description="Name of author", maxlen=64, default="unknown")
    name        : bpy.props.StringProperty(name="Name", description="Name of weightfile", maxlen=64, default="unknown")
    description : bpy.props.StringProperty(name="Description", description="Description of weightfile", maxlen=1024, default="")
    license     : bpy.props.StringProperty(name="License", description="Type of license", maxlen=64, default="CC BY 4.0")
    precision   : bpy.props.IntProperty(name="Precision", min=2, max=5, description="Precision of weights", default=3)
    columns     : bpy.props.IntProperty(name="Columns", min=1, max=16, description="Columns in weightfile", default=4)
    version     : bpy.props.StringProperty(name="Version", description="MakeHuman version", maxlen=20, default="110")

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

    replace   : bpy.props.BoolProperty(name="Replace Groups", description="Replace or append vertex group", default=True)

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == "MESH"

    def invoke(self, context,event):
        return super().invoke(context, event)

    def draw (self, context):
        layout = self.layout
        layout.label(text="Create weights on: " + context.active_object.name)
        layout.prop(self, "replace")

    def execute(self, context):
        import_weights(context, self.properties)
        return {'FINISHED'}

class MIRRORMESH_assign_mirrortab(bpy.types.Operator, ImportHelper):
    '''Assign a mirror table to a mesh'''
    bl_idname = "mirror.assign_tab"
    bl_label = 'Assign a Mirror Table to a Mesh'
    bl_options = {'REGISTER'}

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
            mirrortab = "none"
        layout.label(text="Current table:")
        layout.label(text=mirrortab)
            

    def invoke(self, context, event):
        return super().invoke(context, event)

    def execute(self, context):
        obj = context.object
        obj['mirrortable'] = self.properties.filepath
        return {'FINISHED'}

class MIRRORMESH_create_mirrortab(bpy.types.Operator, ExportHelper):
    '''Create and export a mirror table of a mesh'''
    bl_idname = "mirror.create_tab"
    bl_label = 'Create and Export a Mirror Table of a Mesh'
    bl_options = {'REGISTER'}
    filename_ext = ".txt"

    eps   : bpy.props.FloatProperty(name="Epsilon", min=0, max=0.05, description="Deviation of the mirrored vertex", default= 0.05)

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == "MESH"

    def execute(self, context):
        export_mirrortab(context, self.properties)
        return {'FINISHED'}

class MIRRORMESH_vgroups_by_table_lr(bpy.types.Operator):
    '''Mirror Vertex Groups using a table from left to right'''
    bl_idname = "mirror.vgroups_by_table_lr"
    bl_label = 'Mirror Vertex Groups using a table from left to right'
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == "MESH" and 'mirrortable' in obj

    def execute(self, context):
        mirror_vgroups(context, "l")
        return  {'FINISHED'}

class MIRRORMESH_vgroups_by_table_rl(bpy.types.Operator):
    '''Mirror Vertex Groups using a table from right to left'''
    bl_idname = "mirror.vgroups_by_table_rl"
    bl_label = 'Mirror Vertex Groups using a table from right to left'
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == "MESH" and 'mirrortable' in obj

    def execute(self, context):
        mirror_vgroups(context, "r")
        return  {'FINISHED'}

class MIRRORMESH_shapekeys_by_table_lr(bpy.types.Operator):
    '''Mirror Shape Keys using a table from left to right'''
    bl_idname = "mirror.shapekeys_by_table_lr"
    bl_label = 'Mirror Shape Keys using a table from left to right'
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == "MESH" and obj.data.shape_keys is not None and 'mirrortable' in obj

    def execute(self, context):
        mirror_shapekeys(context, "l")
        return  {'FINISHED'}

class MIRRORMESH_shapekeys_by_table_rl(bpy.types.Operator):
    '''Mirror Shape Keys using a table from right to left'''
    bl_idname = "mirror.shapekeys_by_table_rl"
    bl_label = 'Mirror Shape Keys using a table from right to left'
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == "MESH" and obj.data.shape_keys is not None and 'mirrortable' in obj

    def execute(self, context):
        mirror_shapekeys(context, "r")
        return  {'FINISHED'}

class MIRRORMESH_mesh_by_table(bpy.types.Operator):
    '''Mirror a mesh using a table'''
    bl_idname = "mirror.mesh_by_table"
    bl_label = 'Mirror Mesh using a table'
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == "MESH" and 'mirrortable' in obj

    def execute(self, context):
        obj = context.object
        mirrortab = obj['mirrortable']
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

        bm.select_flush(True)
        bm.select_flush(False)

        bmesh.update_edit_mesh(me, True)
        return {'FINISHED'}

def export_func(self, context):
    self.layout.operator(ExportMHW.bl_idname, text="MakeHuman Weights (.mhw)")

def import_func(self, context):
    self.layout.operator(ImportMHW.bl_idname, text="MakeHuman Weights (.mhw)")

def assign_mirrortab_func(self, context):
    self.layout.operator("mirror.assign_tab", text="Assign Mirror Table")

def create_mirrortab_func(self, context):
    self.layout.operator("mirror.create_tab", text="Create and Export Mirror Table")

def mirror_select_func(self, context):
    self.layout.operator("mirror.mesh_by_table", text="Mirror Mesh by Table")

def mirror_vgroups_left2right_func(self, context):
    self.layout.operator("mirror.vgroups_by_table_lr", text="Mirror Vertex Groups by Table (L>R)")

def mirror_vgroups_right2left_func(self, context):
    self.layout.operator("mirror.vgroups_by_table_rl", text="Mirror Vertex Groups by Table (R>L)")

def mirror_shapekeys_left2right_func(self, context):
    self.layout.operator("mirror.shapekeys_by_table_lr", text="Mirror Shape Keys by Table (L>R)")

def mirror_shapekeys_right2left_func(self, context):
    self.layout.operator("mirror.shapekeys_by_table_rl", text="Mirror Shape Keys by Table (R>L)")

def register():
    bpy.utils.register_class(ExportMHW)
    bpy.utils.register_class(ImportMHW)
    bpy.utils.register_class (MIRRORMESH_mesh_by_table)
    bpy.utils.register_class (MIRRORMESH_assign_mirrortab)
    bpy.utils.register_class (MIRRORMESH_create_mirrortab)
    bpy.utils.register_class (MIRRORMESH_vgroups_by_table_rl)
    bpy.utils.register_class (MIRRORMESH_vgroups_by_table_lr)
    bpy.utils.register_class (MIRRORMESH_shapekeys_by_table_rl)
    bpy.utils.register_class (MIRRORMESH_shapekeys_by_table_lr)
    bpy.types.TOPBAR_MT_file_export.append(export_func)
    bpy.types.TOPBAR_MT_file_import.append(import_func)
    bpy.types.TOPBAR_MT_file_export.append(create_mirrortab_func)
    bpy.types.VIEW3D_MT_edit_mesh_vertices.append(assign_mirrortab_func)
    bpy.types.VIEW3D_MT_select_edit_mesh.prepend(mirror_select_func)
    bpy.types.VIEW3D_MT_mirror.append(mirror_vgroups_left2right_func)
    bpy.types.VIEW3D_MT_mirror.append(mirror_vgroups_right2left_func)
    bpy.types.VIEW3D_MT_mirror.append(mirror_shapekeys_left2right_func)
    bpy.types.VIEW3D_MT_mirror.append(mirror_shapekeys_right2left_func)

def unregister():
    bpy.utils.unregister_class(ExportMHW)
    bpy.utils.unregister_class(ImportMHW)
    bpy.utils.unregister_class (MIRRORMESH_mesh_by_table)
    bpy.utils.unregister_class (MIRRORMESH_assign_mirrortab)
    bpy.utils.unregister_class (MIRRORMESH_create_mirrortab)
    bpy.utils.unregister_class (MIRRORMESH_vgroups_by_table_rl)
    bpy.utils.unregister_class (MIRRORMESH_vgroups_by_table_lr)
    bpy.utils.unregister_class (MIRRORMESH_shapekeys_by_table_rl)
    bpy.utils.unregister_class (MIRRORMESH_shapekeys_by_table_lr)
    bpy.types.TOPBAR_MT_file_export.remove(export_func)
    bpy.types.TOPBAR_MT_file_import.remove(import_func)
    bpy.types.TOPBAR_MT_file_export.remove(create_mirrortab_func)
    bpy.types.VIEW3D_MT_edit_mesh_vertices.remove(assign_mirrortab_func)
    bpy.types.VIEW3D_MT_select_edit_mesh.remove(mirror_select_func)
    bpy.types.VIEW3D_MT_mirror.remove(mirror_vgroups_left2right_func)
    bpy.types.VIEW3D_MT_mirror.remove(mirror_vgroups_right2left_func)
    bpy.types.VIEW3D_MT_mirror.remove(mirror_shapekeys_left2right_func)
    bpy.types.VIEW3D_MT_mirror.remove(mirror_shapekeys_right2left_func)


if __name__ == "__main__":
    register()

