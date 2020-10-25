import bpy
import re
import os
import sys
import math
import addon_utils
from bpy_extras.io_utils import (ImportHelper, ExportHelper)

def read_mirror_tab (name):
    mirror = {};
    try:
        f = open(name)
        for line in f:
            m=re.search("(\d+)\s+(\d+)\s+(\w+)", line)
            if (m is not None):
                mirror[int (m.group(1))] = { 'm': int(m.group(2)), 's': m.group(3) }
        f.close()
        return (mirror)
    except IOError:
        return (None)

def GetMirrorVNum (mirror, x, y, z, m, eps):
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
    obj = context.active_object
    verts = obj.data.vertices
    bpy.ops.object.mode_set(mode='OBJECT')
    wm = bpy.context.window_manager
    mirror = {};

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
                    mirror[i]["m"] = GetMirrorVNum (mirror,  mirror[i]["x"], mirror[i]["y"], mirror[i]["z"], i, eps)
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
        bpy.ops.info.warningbox('INVOKE_DEFAULT', title="Mesh cannot be fully mirrored",
                info=str(unmirrored) + " unmirrored vertices. Check lines with -1 in output file")
    else:
       obj.mirrortable = props.filepath
       obj.select_set(True)


class MHE_PT_PredefMirrorTab(bpy.types.Operator):
    '''Assign a predefined mirror table to a mesh, typically when maketarget is availabe and mirror tables are stored in data directory'''
    bl_idname = "mhe.predef"
    bl_label = 'Assign Predefined Mirror Table to a Mesh'
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == "MESH" and hasattr(obj, "MhMeshType")

    def execute(self, context):
        obj = context.object
        mirrorfilename =  obj.MhMeshType + ".mirror"
        for mod_name in bpy.context.preferences.addons.keys():
            if (mod_name == "maketarget"):
                mod = sys.modules[mod_name]
                mirrorfile = os.path.join(os.path.dirname(mod.__file__), "data", mirrorfilename)
                obj.mirrortable = mirrorfile
                obj.select_set(True)
                return {'FINISHED'}

        bpy.ops.info.warningbox('INVOKE_DEFAULT', title="No predefined table available", info="mesh is not known to MakeTarget2")
        return {'CANCELLED'}



class MHE_PT_AssignMirrorTab(bpy.types.Operator, ImportHelper):
    '''Assign a mirror table to a mesh'''
    bl_idname = "mhe.assign"
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
            mirrortab = obj.mirrortable
        except:
            mirrortab = "none"
        layout.label(text="Current table:")
        layout.label(text=mirrortab)


    def invoke(self, context, event):
        return super().invoke(context, event)

    def execute(self, context):
        # try directly
        obj = context.object
        obj.mirrortable = self.properties.filepath
        obj.select_set(True)
        return {'FINISHED'}



class MHE_PT_CreateMirrorTab(bpy.types.Operator, ExportHelper):
    '''Create and export a mirror table of a mesh'''
    bl_idname = "mhe.create"
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


