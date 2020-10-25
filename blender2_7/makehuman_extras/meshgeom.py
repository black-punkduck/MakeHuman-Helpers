import bpy
from .mirrortab import read_mirror_tab

# normal mirroring of the geometry using the table
#
def mirror_geometry (context, direction):
    bpy.ops.object.mode_set(mode='OBJECT')
    ob = context.active_object

    # load mirror table
    #
    mirrortab = ob.mirrortable
    mirror = read_mirror_tab(mirrortab)
    if mirror is None:
        bpy.ops.info.warningbox('INVOKE_DEFAULT', title="Cannot load mirror table, Mirror table mismatch", info=mirrortab)
        return {'CANCELLED'}

    for idx, vert in enumerate (ob.data.vertices):
        if mirror[idx]['s'] == direction:
            dest = mirror[idx]['m']
            ob.data.vertices[dest].co[0] = -vert.co[0]
            ob.data.vertices[dest].co[1] = vert.co[1]
            ob.data.vertices[dest].co[2] = vert.co[2]
        elif mirror[idx]['s'] == 'm':
            vert.co[0] = 0      # push middle to x = 0
    ob.data.update()

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


