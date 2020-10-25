#!/usr/bin/python
# -*- coding: utf-8 -*-

#  Authors: black-punkduck

#
# must be before(!) all imports
#
bl_info = {
    "name": "MakeHuman Extras",
    "author": "black-punkduck",
    "version": (1,1,0),
    "blender": (2,80,0),
    "location": "View3D > Properties > MakeHuman Extras",
    "description": "Extra functions to work with MakeHuman Meshes",
    'wiki_url': "http://www.makehumancommunity.org/",
    "category": "MakeHuman",
    }

import bpy
from bpy.utils import register_class, unregister_class
from bpy.props import StringProperty
from .makehumanextras import MHE_PT_MakeHumanExtrasPanel, MHE_WarningBox
from .mirrortab import MHE_PT_AssignMirrorTab, MHE_PT_CreateMirrorTab, MHE_PT_PredefMirrorTab
from .meshgeom import MHE_MirrorGeomL2R, MHE_MirrorGeomR2L
from .vertexgroups import MHE_MirrorVGroupsL2R, MHE_MirrorVGroupsR2L
from .shapekeys import MHE_MirrorShapeKeysL2R, MHE_MirrorShapeKeysR2L
from .selection import MHE_MirrorSelected
from .mhw import MHE_Export_MHW, MHE_Import_MHW

MHE_EXTRAS_CLASSES = [
    MHE_PT_MakeHumanExtrasPanel,    # from makehumanextras.py
    MHE_WarningBox,
    MHE_PT_AssignMirrorTab,         # from mirrortab.py
    MHE_PT_CreateMirrorTab, 
    MHE_PT_PredefMirrorTab,
    MHE_MirrorGeomL2R,              # from meshgeom.py
    MHE_MirrorGeomR2L,
    MHE_MirrorVGroupsL2R,           # from vertexgroups.py
    MHE_MirrorVGroupsR2L,
    MHE_MirrorShapeKeysL2R,         # from shapekeys.py
    MHE_MirrorShapeKeysR2L,
    MHE_MirrorSelected,             # from selection.py
    MHE_Export_MHW,                 # from mhw.py
    MHE_Import_MHW
]

def extraProperties():
    scn = bpy.types.Scene
    if not hasattr(bpy.types.Object, "mirrortable"):
        bpy.types.Object.mirrortable = StringProperty(name="Mirror table", description="table which contains the numbers of mirrored vertices", default="")


def register():
    extraProperties()
    for cls in MHE_EXTRAS_CLASSES:
        register_class(cls)

def unregister():

    for cls in reversed(MHE_EXTRAS_CLASSES):
        unregister_class(cls)

if __name__ == "__main__":
    register()
    print("MakeHuman extras loaded")

