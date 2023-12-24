import bpy
import bmesh
from .mirrortab import read_mirror_tab

# normal mirroring of the geometry using the table
#
def mirror_geometry (context, direction):
    bpy.ops.object.mode_set(mode='OBJECT')
    ob = context.active_object

    mesh = ob.data
    bm = bmesh.new()
    bm.from_mesh(mesh)
    v = bm.verts
    v.ensure_lookup_table()

    # load mirror table
    #
    mirrortab = ob.mirrortable
    mirror = read_mirror_tab(mirrortab)
    unmirrored = 0
    if mirror is None:
        bpy.ops.info.warningbox('INVOKE_DEFAULT', title="Cannot load mirror table, Mirror table mismatch", info=mirrortab)
        return {'CANCELLED'}


    for idx, vert in enumerate (v):
        if idx in mirror:
            if mirror[idx]['s'] == direction:
                dest = mirror[idx]['m']
                v[dest].co[0] = -vert.co[0]
                v[dest].co[1] = vert.co[1]
                v[dest].co[2] = vert.co[2]
            elif mirror[idx]['s'] == 'm':
                vert.co[0] = 0      # push middle to x = 0
        else:
            unmirrored += 1

    bm.to_mesh(mesh)
    bm.free()
    #bpy.context.view_layer.update() # seems to do nothing
    # I use that stupid way
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.object.mode_set(mode='OBJECT')

    if unmirrored > 0:
        bpy.ops.info.warningbox('INVOKE_DEFAULT', title="Cannot mirror all vertices", info= str(unmirrored) + " verts not mirrored.")


    return {'FINISHED'}

class MHE_MirrorGeomL2R(bpy.types.Operator):
    '''Mirror geometry using a table from left to right'''
    bl_idname = "mhe.mirror_geom_l2r"
    bl_label = 'Mirror Geometry using a table from left to right'
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == "MESH" and \
            obj.mirrortable is not None and obj.mirrortable != ""

    def execute(self, context):
        mirror_geometry(context, "l")
        return  {'FINISHED'}

class MHE_MirrorGeomR2L(bpy.types.Operator):
    '''Mirror geometry using a table from right to left'''
    bl_idname = "mhe.mirror_geom_r2l"
    bl_label = 'Mirror Geometry using a table from right to left'
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == "MESH" and \
            obj.mirrortable is not None and obj.mirrortable != ""

    def execute(self, context):
        mirror_geometry(context, "r")
        return  {'FINISHED'}


