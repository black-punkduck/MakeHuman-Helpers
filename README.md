# MakeHuman-Helpers
Helpers used for manipulating objects in MakeHuman Environment

All programs use a common json-file for configuration, called:

    data/mh_helper.json

It contains filenames of basemesh, mirror table and standard weights.

There are options to use different filenames in the program.
All output is written to standard output so that no existing file is overwritten.

The configuration also contains the start vertices of the helpers.

*I don't like JSON files with millions of lines for the weights. So the output of vertex/weights combinations is shortened to a 4 column table with 4 digits precision. You can change this by using -p and -c options.*

---

## Create mirror table

A small skript to create a mirror table of vertices from a symmetric (y-axis) wavefront (.obj) file. This table is used for symmetrizing objects. Normally a deviation (MAXDIST) of 0.0 is allowed. If you edit your mesh in mirror mode set deviation to e.g. 0.001.

    create_mirror_tab.py [-h] [-b base_object] [-m MAXDIST]

The table contains all vertex numbers, mirror vertex numbers and orientations (l = left, r = right, m = mid)

*Example:*

```
..
18707 18690 l
18708 18708 m
18709 18691 l
..
19154 19157 r
19155 19156 r
19156 19155 l
19157 19154 l
```

---
## Extract weights from weights file

A script which extracts groups from a given .mhw weight file

    extract_weights.py [-h] [-f default_weights] [-t transpose_file][-p PRECISION][-c COLUMNS] RANGE

This skript extracts weight groups from a weight file, it is also able to transpose names according to a table. The transpose file then should contain lines of containing source group and destination group.

*Example:*

Consider the transpose file is called

    data/default_bento.transpose

and looks like
```
#
# transpose file for default to bento
#
clavicle.L      mCollarLeft
clavicle.R      mCollarRight
eye.L   mFaceEyeAltLeft
eye.R   mFaceEyeAltRight
finger1-1.L     mHandThumb1Left
finger1-1.R     mHandThumb1Right
finger1-2.L     mHandThumb2Left
finger1-2.R     mHandThumb2Right
...
```
now use

    extract_weights.py -t data/default_bento.transpose skirt

you will get

```
"mTorso": [
        [18002, 0.4441], [18003, 0.6071], [18004, 0.8432], [18005, 0.6358],
        ...
],

"mPelvis": [
]
```

---
## Creation of symmetric weight groups

A script which creates a symmetric group or symmetrizes an existing one according to the name.

    symmetrize_weights.py [-h] [-f default_weights] [-p PRECISION] [-c COLUMNS] GROUP [ORIENTATION]

If GROUP contains *.l*, *.L*, *left*, *Left*, *LEFT* or *.r*, *.R*, *right*, *Right*, *RIGHT* the mirrored and the original groups are created.

All other groups are made symmetrical depending on a second parameter l or r to tell the program which side is preferred.

The GROUP "=all=" can be used to create identical weights on left and right side. Without ORIENTATION given the left side is copied to the right.
In case of GROUP "=all=" also the rest of the original JSON file is copyied.

For calculation the program uses the file created by create_mirror_tab.py
which should be copied to destination specified in the json-configfile.

---
## Merging weights

When a new file was created it should be merged with the default weights file.

    merge_weights.py [-h] [-f default_weights] [-p PRECISION] [-c COLUMNS] [-r] WEIGHTS

The skript merges the weights of a second file to the default weights. It can be used to replace groups or to add new weights to existing groups.

Add: e.g. a helper to the base mesh.

Replace: e.g. a beautified symmetrical version for the hair helper

Merging with an empty WEIGHTS file results in a version of the default weights using e.g. different PRECISION or COLUMNS values

---
## Checking the weights in a weights file

To check if the weights will result to a normalized value of 1, the script weights_sum can be used

    weights_sum.py [-h] [-f default_weights] [-L LOWEST] [-H HIGHEST][-s MINWEIGHTNUM] [-m MAXWEIGHTNUM]

All vertex numbers having smaller weights than LOWEST or bigger ones than HIGHEST will be printed. If only part of the file should be checked, the check may be reduced to a specific range of vertex number by using *-s* and *-m* option.

---
## Normalizing weights

To get normalized weights of "bad" weights the skript normalize.py is used:

    normalize.py [-h] [-f default_weights] [-s MINWEIGHTNUM][-m MAXWEIGHTNUM] [-p PRECISION] [-c COLUMNS] [-D DIFFERENCE]

Instead of writing only the incorrect lines this command creates the normalized values. At least one weight should be set for each vertex before, vertices with a weight of zero (yet *undefined* when you use the command *weights_sum.py*) are not processed.

Best to be used with a higher DIFFERENCE e.g. 0.005

---
## Blender exporter in .mhw format

The Blender plugin mhw_export.py should be copied to standard addons directory of Blender.
It will appear in the preferences, category MakeHuman. Tested in 2.79

To test it, select e.g. the skin (body) of a MakeHuman character (must be supplied with a skeleton)
and use file / export / MakeHuman Weight (.mhw)

This plugin works with all meshes with at least one vertex group and at least a vertex assigned.

Consider this as beta-version. An ASCII file is generated.

---

## Workflow: normalize a mesh

Normalizing a mesh. Just do a copy of the start mesh in a form we can compare with *diff* after processing. In this case we work with *default_weights*, the standard weight file of MakeHuman.

        merge_weights.py '' >/tmp/original_weights

Now let's do the normalization, the output only contains new weights:

    normalize.py -D 0.005 >/tmp/normalized

Next merge the weights, replace mode is not used, because all weights not touched by normalization should stay as they are

    merge_weights.py /tmp/normalized >/tmp/merged


Just to see what is processed, check the result by comparing with *diff*:

        diff /tmp/original_weights /tmp/merged

---

## Workflow: create a new weight-file for a proxy

This workflow only works, if create_mirror_tab.py is able to create a table, where each vertex has a mirrored vertex. The base.obj in Makehuman fulfills this demand. For an own proxy best is to use a mirror operator in Blender when creating it. If that is not possible you have to correct the weights on both sides ... but then the output of the Blender exporter can be used directly in MakeHuman.

 * Export a MakeHuman default character (male, female) with a proxy and the default skeleton supplied in mhx2 format, no subdivision used.
 * Import character into Blender, do not add or delete vertices (order is still original)
 * Now fix e.g. the area of the left kneecap by changing weights (e.g. by reducing the impact of upperleg on the lower part of the kneecap).
 * select the mesh and export with Blender exporter for .mhw format
 * change .proxy file so it refers to this mesh 
 * create mirror table (use the .obj file of your proxy)
 * use symmetrize_weights on the .mhw file. Use "=all=" for the GROUP and if you changed the left side Blender, no further parameter is needed. The output should be written into a new file.
 * copy this file to the destinaton directory.

---

## Append meshes to the basemesh

A command to append additional meshes to the base mesh. Designed for a base mesh in future editions. 

	append_base_mesh.py [-h] [-b default_base] [-p PRECISION] MESH

MESH (must be a wavefront .obj file) is concatenated to the base mesh (or default_base) to generate a new base mesh.
