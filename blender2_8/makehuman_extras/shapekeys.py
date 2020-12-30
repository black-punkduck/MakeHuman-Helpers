import bpy
from .mirrortab import read_mirror_tab
from .utils import evaluate_side

def mirror_shapekeys (context, direction):
    bpy.ops.object.mode_set(mode='OBJECT')
    ob = context.active_object

    # load mirror table
    #
    mirrortab = ob.mirrortable
    mirror = read_mirror_tab(mirrortab)
    if mirror is None:
        bpy.ops.info.warningbox('INVOKE_DEFAULT', title="Cannot load mirror table, Mirror table mismatch", info=mirrortab)
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

def norm_shapekeys (context):
    bpy.ops.object.mode_set(mode='OBJECT')
    ob = context.active_object

    # get original object once
    basis = ob.data.shape_keys.key_blocks["Basis"].data

    for shape in ob.data.shape_keys.key_blocks:
        name = shape.name
        if shape.slider_max > 1 or shape.slider_min < -1:
            factor = shape.slider_max
            if -shape.slider_min > shape.slider_max:
                factor =  -shape.slider_min
            source = ob.data.shape_keys.key_blocks[name].data
            for idx, vert in enumerate (source):
                vert.co = (vert.co - basis[idx].co) * factor + basis[idx].co
            shape.slider_max /= factor
            shape.slider_min /= factor

    return {'FINISHED'}

class MHE_MirrorShapeKeysL2R(bpy.types.Operator):
    '''Mirror Shape Keys using a table from left to right'''
    bl_idname = "mhe.mirror_shapekeys_l2r"
    bl_label = 'Mirror Shape Keys using a table from left to right'
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == "MESH" and \
            obj.mirrortable is not None and obj.mirrortable != "" and \
            obj.data.shape_keys is not None 

    def execute(self, context):
        mirror_shapekeys(context, "l")
        return  {'FINISHED'}

class MHE_MirrorShapeKeysR2L(bpy.types.Operator):
    '''Mirror Shape Keys using a table from right to left'''
    bl_idname = "mhe.mirror_shapekeys_r2l"
    bl_label = 'Mirror Shape Keys using a table from right to left'
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == "MESH" and \
            obj.mirrortable is not None and obj.mirrortable != "" and \
            obj.data.shape_keys is not None 

    def execute(self, context):
        mirror_shapekeys(context, "r")
        return  {'FINISHED'}

class MHE_NormShapeKeys(bpy.types.Operator):
    '''Normalize Shape Keys from -1 to 1 (useful for fbx export) '''
    bl_idname = "mhe.norm_shapekeys"
    bl_label = 'Normalize Shape Keys'
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == "MESH" and  obj.data.shape_keys is not None 

    def execute(self, context):
        norm_shapekeys(context)
        return  {'FINISHED'}

