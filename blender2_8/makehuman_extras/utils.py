import re

# check orientation of name and calculate partner name
#
def evaluate_side(name):
    orientation = 'm'
    partner = ""
    m = re.search ("(\S+)(left)$", name, re.IGNORECASE)
    if (m is not None):
        if m.group(2) == "left":
            partner = m.group(1) + "right"
            orientation = 'l'
        elif m.group(2) == "Left":
            partner = m.group(1) + "Right"
            orientation = 'l'
        elif m.group(2) == "LEFT":
            partner = m.group(1) + "RIGHT"
            orientation = 'l'
        else:
            partner = name

    if partner == "":
        m = re.search ("(\S+)(right)$", name, re.IGNORECASE)
        if (m is not None):
            if m.group(2) == "right":
                partner = m.group(1) + "left"
                orientation = 'r'
            elif m.group(2) == "Right":
                partner = m.group(1) + "Left"
                orientation = 'r'
            elif m.group(2) == "RIGHT":
                partner = m.group(1) + "LEFT"
                orientation = 'r'
            else:
                partner = name

    if partner == "":
        m = re.search ("(\S+)(\.[Ll])$", name)
        if (m is not None):
            if m.group(2) == ".l":
                partner = m.group(1) + ".r"
            if m.group(2) == ".L":
                partner = m.group(1) + ".R"
            orientation = 'l'

    if partner == "":
        m = re.search ("(\S+)(\.[rR])$", name)
        if (m is not None):
            if m.group(2) == ".r":
                partner = m.group(1) + ".l"
            if m.group(2) == ".R":
                partner = m.group(1) + ".L"
            orientation = 'r'

    if orientation == 'm':
        partner = name
    return (orientation, partner)

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


