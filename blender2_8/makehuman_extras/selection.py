import bpy
import bmesh
from .mirrortab import read_mirror_tab

class MHE_MirrorSelected(bpy.types.Operator):
    '''Select mirrored vertices using a table'''
    bl_idname = "mhe.mirror_selected"
    bl_label = 'Mirror Mesh using a table'
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == "MESH" and \
                obj.mirrortable is not None and obj.mirrortable != "" 


    def execute(self, context):
        obj = context.object
        # load mirror table
        #
        mirrortab = obj.mirrortable
        mirror = read_mirror_tab(mirrortab)
        if mirror is None:
            bpy.ops.info.warningbox('INVOKE_DEFAULT', title="Cannot load mirror table, Mirror table mismatch", info=mirrortab)
            return {'CANCELLED'}

        bpy.ops.mesh.select_mode(type="VERT")
        me = obj.data
        bm = bmesh.from_edit_mesh(me)

        # we need to remember the values
        for vert in bm.verts:
            if vert.index in mirror:
                mirror[vert.index]['o'] = vert.select
            else:
                bpy.ops.info.warningbox('INVOKE_DEFAULT', title="Mirror table mismatch", info="Mirrortable too short")
                return {'CANCELLED'}


        # now select the mirrored ones
        for vert in bm.verts:
            try:
                vert.select = mirror[mirror[vert.index]['m']]['o']
            except:
                bpy.ops.info.warningbox('INVOKE_DEFAULT', title="Mirror table mismatch", info="Mirrortable does not fit")
                return {'CANCELLED'}

        bm.select_flush(True)
        bm.select_flush(False)

        bmesh.update_edit_mesh(me, True)
        return {'FINISHED'}

