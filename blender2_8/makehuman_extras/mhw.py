import bpy
import json

from bpy.props import StringProperty, IntProperty
from bpy_extras.io_utils import (ImportHelper, ExportHelper)

from .utils import v_array

def export_weights (context, props):
    bpy.ops.object.mode_set(mode='OBJECT')
    active = context.active_object

    vgrp = active.vertex_groups

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
        bpy.ops.info.warningbox('INVOKE_DEFAULT', title="Missibg assignment", info="No vertices assigned")
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

class MHE_Export_MHW(bpy.types.Operator, ExportHelper):
    '''Export an MHW File'''
    bl_idname = "mhe.export_mhw"
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
        return obj and obj.type == "MESH" and obj.vertex_groups is not None and len(obj.vertex_groups) != 0

    def invoke(self, context,event):
        self.properties.name = context.active_object.name
        self.properties.description = "generated weights for " + self.properties.name
        return super().invoke(context, event)

    def execute(self, context):
        export_weights(context, self.properties)
        return {'FINISHED'}


class MHE_Import_MHW(bpy.types.Operator, ImportHelper):
    '''Import an MHW File'''
    bl_idname = "mhe.import_mhw"
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


