import bpy
from .mirrortab import read_mirror_tab
from .utils import evaluate_side

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

    # load mirror table
    #
    mirrortab = ob.mirrortable
    mirror = read_mirror_tab(mirrortab)
    if mirror is None:
        bpy.ops.info.warningbox('INVOKE_DEFAULT', title="Cannot load mirror table, Mirror table mismatch", info=mirrortab)
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
            ngrp = vgrp.new(grp)

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
            ngrp = vgrp.new(partner)

            for index in temp:
                vn[0] = mirror[index]['m']
                ngrp.add(vn, temp[index], 'ADD')

    return {'FINISHED'}

def cleanup_vgroups (context, minweight):

    bpy.ops.object.mode_set(mode='OBJECT')
    active = context.active_object
    vgrp = active.vertex_groups
    vn = [1]    # our small array ;-)
    deletegrp = []

    # lets perform a loop on all groups
    for grp in sorted(vgrp.keys()):
        gindex = vgrp[grp].index
        cnt = 0;
        # now check all vertices of the object
        for v in active.data.vertices:

            # check all groups of a vertex
            for g in v.groups:

                # if the index of the group fits to the current group
                # get the weight of the vertex
                if g.group == gindex:
                    weight=vgrp[grp].weight(v.index)
                    if weight < minweight:
                        vn[0] = v.index
                        vgrp[grp].remove(vn)
                    else:
                        cnt += 1;

        # if no vertex is left, group can be deleted
        #
        if cnt == 0:
            deletegrp.append(vgrp[grp].name)


    for vname in deletegrp:
        vg = vgrp.get(vname)
        vgrp.remove(vg)

    return {'FINISHED'}

class MHE_MirrorVGroupsL2R(bpy.types.Operator):
    '''Mirror Vertex Groups using a table from left to right'''
    bl_idname = "mhe.mirror_vgroups_l2r"
    bl_label = 'Mirror Vertex Groups using a table from left to right'
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == "MESH" and obj.mirrortable is not None and obj.mirrortable != "" and \
            obj.vertex_groups is not None and len(obj.vertex_groups) != 0

    def execute(self, context):
        mirror_vgroups(context, "l")
        return  {'FINISHED'}

class MHE_MirrorVGroupsR2L(bpy.types.Operator):
    '''Mirror Vertex Groups using a table from right to left'''
    bl_idname = "mhe.mirror_vgroups_r2l"
    bl_label = 'Mirror Vertex Groups using a table from right to left'
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == "MESH" and obj.mirrortable is not None and obj.mirrortable != "" and \
            obj.vertex_groups is not None and len(obj.vertex_groups) != 0

    def execute(self, context):
        mirror_vgroups(context, "r")
        return  {'FINISHED'}

class MHE_CleanupVGroups(bpy.types.Operator):
    '''Cleanup Vertex Groups using a minimum value (also deletes empty groups)'''
    bl_idname = "mhe.cleanup_vgroups"
    bl_label = 'Cleanup Vertex Groups using a minimum value'
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return obj and obj.type == "MESH" and obj.vertex_groups is not None

    def execute(self, context):
        cleanup_vgroups(context, context.scene.MHE_mincleanup)
        return  {'FINISHED'}
