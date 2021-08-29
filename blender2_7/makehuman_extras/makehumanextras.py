# -*- coding: utf-8 -*-
#
# main panel

import bpy
from . import bl_info   # to get information about version

class MHE_PT_MakeHumanExtrasPanel(bpy.types.Panel):
    bl_label = bl_info["name"] + " v %d.%d.%d" % bl_info["version"]
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "MakeHuman Extras"

    def draw(self, context):
        layout = self.layout
        scn = context.scene
        obj = context.active_object
        sett = layout.box()
        if obj is None or obj.type != "MESH":
            sett.label(text="- select a visible mesh object -")
        else:
            sett.label(text="Mirror table", icon="PREFERENCES")

            sett.label(text="Current table:")
            if obj.mirrortable != "":
                sett.label(text=obj.mirrortable)
            else:
                sett.label(text="- none created or assigned -")

            sett.operator("mhe.create", text="Create mirror table")
            sett.operator("mhe.assign", text="Assign existent table")

            select = layout.box()
            select.label(text="Selection", icon="BBOX")
            select.operator("mhe.mirror_selected", text="Select mirrored")

            geom = layout.box()
            geom.label(text="Geometry", icon="MESH_DATA")
            geom.operator("mhe.mirror_geom_l2r", text="Symmetrize L > R")
            geom.operator("mhe.mirror_geom_r2l", text="Symmetrize R > L")

            weights = layout.box()
            weights.label(text="Vertex Groups / Weights", icon="GROUP_VERTEX")
            weights.operator("mhe.mirror_vgroups_l2r", text="Symmetrize L > R")
            weights.operator("mhe.mirror_vgroups_r2l", text="Symmetrize R > L")
            weights.operator("mhe.cleanup_vgroups", text="Clean up")
            weights.prop(scn, "MHE_mincleanup", text="Minimum Value")
            weights.operator("mhe.export_mhw", text="Export as MHW")
            weights.operator("mhe.import_mhw", text="Import from MHW")

            shapek = layout.box()
            shapek.label(text="Shape Keys", icon="SHAPEKEY_DATA")
            shapek.operator("mhe.mirror_shapekeys_l2r", text="Symmetrize L > R")
            shapek.operator("mhe.mirror_shapekeys_r2l", text="Symmetrize R > L")
            shapek.operator("mhe.norm_shapekeys", text="Normalize to [-1, 1 ]")

            clonew = layout.box()
            clonew.label(text="Copy", icon="MESH_DATA")
            clonew.operator("mhe.weights_copy", text="Weights")
            clonew.operator("mhe.shapekey_copy", text="Shape Keys")
            clonew.prop(scn,"MHE_clone_from", text="Source")
            clonew.prop(scn, "MHE_minweight", text="Minimum Weight")

            debug = layout.box()
            debug.label(text="Debug", icon="MESH_DATA")
            debug.prop(scn, "MHE_find_vertex", text="Number(s)")
            debug.operator("mhe.selectbynum", text="Find Vertex Number")

class MHE_WarningBox(bpy.types.Operator):
    bl_idname = "info.warningbox"
    bl_label = ""

    info= bpy.props.StringProperty( name = "info", description = "information", default = '')
    title= bpy.props.StringProperty( name = "title", description = "title", default = '')

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=500)

    def draw(self, context):
        box = self.layout.box()
        box.label(text=self.info)
        box.label(icon="ERROR", text=self.title)
