#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

**Project Name:**      MakeHuman-Helpers

**Authors:**           Black Punkduck

**Code Home Page:**    https://github.com/black-punkduck/MakeHuman-Helpers

**Copyright(c):**      Black Punkduck

**Licensing:**         AGPL3

    This file is part of the MakeHuman Support Tools

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

Abstract
--------
Output class for support tools
"""

class v_array:
    def __init__(self, prec=4, mcol=4):
        self.prec = prec
        self.mcol = mcol
        self.col = -1

    def new(self):
        self.col = -1
    
    def appval(self, num, val):
        x = round(val, self.prec)
        if x ==  0.0:
            return ("")
        t = ""
        if self.col == 0:
            t += ",\n\t\t"
        elif self.col < 0:
            self.col = 0
            t += "\t\t"
        else:
            t += ", "

        t += "[" + str(num) + ", " + str(x) + "]"
        self.col +=1
        if self.col == self.mcol:
            self.col = 0
        return t

    def appgroup (self, verts, key):
        self.new()
        t = "\t\"" + key + "\": [\n"
        for vnum in sorted(verts[key]):
            t += self.appval (vnum, verts[key][vnum])
        t += "\n\t]"
        return t

    def appweights (self, verts):
        t = ""
        for key in sorted(verts):
            elems = len (verts[key])
            if elems > 0:
                if t != "":
                    t += ",\n"
                t += self.appgroup (verts, key)
        t += "\n"
        return t

