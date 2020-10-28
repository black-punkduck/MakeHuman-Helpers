import bpy

def create_uv_reference_table(mesh):
    uvlayer  = mesh.uv_layers.active.data
    reftab = [None]*len(mesh.vertices)
    for polygon in mesh.polygons:
        for uvindex in range(polygon.loop_start, polygon.loop_start + polygon.loop_total):
            vn = mesh.loops[uvindex].vertex_index
            uv = uvlayer[uvindex].uv

            if reftab[vn] is None:
                reftab[vn] = uv
            else:
                if reftab[vn][0] < uv[0]:
                    reftab[vn] = uv
                elif  reftab[vn][0] == uv[0]:
                    if reftab[vn][1] < uv[1]:
                        reftab[vn] = uv
    return (reftab)

def create_comparison_tab(s_ref, t_ref):
    ctab = [None]*len(t_ref)
    for i, s_elem in enumerate(s_ref):
        found = False
        for j, d_elem in enumerate(t_ref):
            if d_elem is not None:
                #vec = s_elem - d_elem
                    #if vec.length < 1e-8:
                if s_elem[0] == d_elem[0] and s_elem[1] == d_elem[1]:
                    ctab[i] = j
                    t_ref[j] = None
                    found = True
                    break
        # second try
        if found is False:
            for j, d_elem in enumerate(t_ref):
                if d_elem is not None:
                    vec = s_elem - d_elem
                    if vec.length < 1e-3:
                        ctab[i] = j
                        t_ref[j] = None
                        print (str(i) + " matches with " + str(j))
                        found = True
                        break
        
        if found is False:
            print (str(i) + " not found")
    return (ctab)

def cloneweights (obj_from, obj_to, UV, eps):
    #
    # first calculate source UV entries, since a vertex normally is member of more than one polygon take allways smallest UV entry
    s_mesh = obj_from.data
    t_mesh = obj_to.data
    uvlayer  = s_mesh.uv_layers.active
    ctab = []
    if UV is True:
        # list of Vectors
        s_ref = create_uv_reference_table(s_mesh)
        t_ref  = create_uv_reference_table(t_mesh)

        ctab = create_comparison_tab(s_ref, t_ref)
    else:
        ctab = [i for i in range (len(t_mesh.vertices))]       # creates identity array

    #for i,elem in enumerate(ctab):
       #print (i, elem)

    s_vgrp = obj_from.vertex_groups
    t_vgrp = obj_to.vertex_groups

    # delete all groups from target
    #
    if len(t_vgrp) > 0:
        for grp in t_vgrp:
            t_vgrp.remove(grp)

    # copy vertex groups from source
    #

    # add vertex groups
    vgroups_IndexName = {}

    for i in range(0, len(s_vgrp)):
        groups = s_vgrp[i]
        vgroups_IndexName[groups.index] = groups.name
        t_vgrp.new(groups.name)

    data = {}  # vert_indices, [(vgroup_index, weights)]
    for v in s_mesh.vertices:
        vg = v.groups
        vi = v.index
        if len(vg) > 0:
            vgroup_collect = []
            for i in range(0, len(vg)):
                if vg[i].weight > eps:
                    vgroup_collect.append((vg[i].group, vg[i].weight))
            data[vi] = vgroup_collect

    # write weights
    for v in t_mesh.vertices:
        t_index = ctab[v.index]
        vgroupIndex_weight = data[t_index]

        for i in range(0, len(vgroupIndex_weight)):
            groupName = vgroups_IndexName[vgroupIndex_weight[i][0]]
            vg = t_vgrp.get(groupName)
            vg.add((t_index,), vgroupIndex_weight[i][1], "REPLACE")

def cloneshapekeys (obj_from, obj_to, UV):
    s_mesh = obj_from.data
    t_mesh = obj_to.data

    # TODO don't consider UV atm

    ctab = [i for i in range (len(t_mesh.vertices))]       # creates identity array

    # delete all shape keys of target
    #
    if t_mesh.shape_keys is not None:
        for shape in t_mesh.shape_keys.key_blocks:
            obj_to.shape_key_remove(shape)

    # get original object once
    nshapeKey = obj_to.shape_key_add()
    nshapeKey.name = "Basis"
    s_basis = s_mesh.shape_keys.key_blocks["Basis"].data
    t_basis = t_mesh.shape_keys.key_blocks["Basis"].data

    for shape in s_mesh.shape_keys.key_blocks:
        if shape.name != "Basis":
            nshapeKey = obj_to.shape_key_add(from_mix=False)
            nshapeKey.name = shape.name
            nshapeKey.slider_min = shape.slider_min
            nshapeKey.slider_max = shape.slider_max

            source = s_mesh.shape_keys.key_blocks[shape.name].data

            for idx, vert in enumerate (source):
                x = s_basis[idx].co[0] - vert.co[0]
                y = s_basis[idx].co[1] - vert.co[1]
                z = s_basis[idx].co[2] - vert.co[2]
                n_idx = ctab[idx]
                nshapeKey.data[n_idx].co = [t_basis[n_idx].co[0] -x , t_basis[n_idx].co[1] - y, t_basis[n_idx].co[2] -z]



class MHE_WeightsCopy(bpy.types.Operator):
    '''Copy weights'''
    bl_idname = "mhe.weights_copy"
    bl_label = 'Copy weights'
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        # check if source and target are available and not the same
        obj_to = context.object
        obj_from = context.scene.MHE_clone_from
        return obj_to is not None and obj_from is not None and obj_from is not obj_to and obj_from.type == "MESH"

    def execute(self, context):
        scn = context.scene
        obj_to = context.object
        obj_from = scn.MHE_clone_from
        UV = False
        if UV is True:
            #
            # now test UV layers, this will be done here otherwise nobody understands while objects are
            # not selectable!
            #
            if obj_from.data.uv_layers is None or len(obj_from.data.uv_layers) < 1:
                bpy.ops.info.warningbox('INVOKE_DEFAULT', info="Cannot copy weights", title="Source object has no UVMAP")
                return {'CANCELLED'}
            if obj_to.data.uv_layers is None or len(obj_to.data.uv_layers) < 1:
                bpy.ops.info.warningbox('INVOKE_DEFAULT', info="Cannot copy weights", title="Target object has no UVMAP")
                return {'CANCELLED'}
            if len(obj_from.data.uv_layers) > 1:
                bpy.ops.info.warningbox('INVOKE_DEFAULT', info="Cannot copy weights", title="Source object has more than 1 UVMAP")
                return {'CANCELLED'}
            if len(obj_to.data.uv_layers) > 1:
                bpy.ops.info.warningbox('INVOKE_DEFAULT', info="Cannot copy weights", title="Target object has more than 1 UVMAP")
                return {'CANCELLED'}
            print ("Source" + str(obj_from.data.uv_layers[0]))
            print ("Dest" + str(obj_to.data.uv_layers[0]))
        #
        # minimum condition for target mesh: it must contain at least same number of vertices
        #
        if len(obj_to.data.vertices) < len(obj_from.data.vertices):
            bpy.ops.info.warningbox('INVOKE_DEFAULT', info="Cannot copy weights", title="Target object has less vertices than source object")
            return {'CANCELLED'}
            
        cloneweights(obj_from, obj_to, UV, scn.MHE_minweight)
        return  {'FINISHED'}

class MHE_ShapeKeyCopy(bpy.types.Operator):
    '''Copy shape keys'''
    bl_idname = "mhe.shapekey_copy"
    bl_label = 'Copy shape keys'
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        # check if source and target are available and not the same
        obj_to = context.object
        obj_from = context.scene.MHE_clone_from
        return obj_to is not None and obj_from is not None and obj_from is not obj_to and obj_from.type == "MESH" and obj_from.data.shape_keys is not None

    def execute(self, context):
        scn = context.scene
        obj_to = context.object
        obj_from = scn.MHE_clone_from
        UV = False
        if UV is True:
            #
            # now test UV layers, this will be done here otherwise nobody understands while objects are
            # not selectable!
            #
            if obj_from.data.uv_layers is None or len(obj_from.data.uv_layers) < 1:
                bpy.ops.info.warningbox('INVOKE_DEFAULT', info="Cannot copy weights", title="Source object has no UVMAP")
                return {'CANCELLED'}
            if obj_to.data.uv_layers is None or len(obj_to.data.uv_layers) < 1:
                bpy.ops.info.warningbox('INVOKE_DEFAULT', info="Cannot copy weights", title="Target object has no UVMAP")
                return {'CANCELLED'}
            if len(obj_from.data.uv_layers) > 1:
                bpy.ops.info.warningbox('INVOKE_DEFAULT', info="Cannot copy weights", title="Source object has more than 1 UVMAP")
                return {'CANCELLED'}
            if len(obj_to.data.uv_layers) > 1:
                bpy.ops.info.warningbox('INVOKE_DEFAULT', info="Cannot copy weights", title="Target object has more than 1 UVMAP")
                return {'CANCELLED'}
            print ("Source" + str(obj_from.data.uv_layers[0]))
            print ("Dest" + str(obj_to.data.uv_layers[0]))
        #
        # minimum condition for target mesh: it must contain at least same number of vertices
        #
        if len(obj_to.data.vertices) < len(obj_from.data.vertices):
            bpy.ops.info.warningbox('INVOKE_DEFAULT', info="Cannot copy weights", title="Target object has less vertices than source object")
            return {'CANCELLED'}
            
        cloneshapekeys(obj_from, obj_to, UV)
        return  {'FINISHED'}

