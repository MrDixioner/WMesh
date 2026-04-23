# imports
import bpy
from bpy.props import (
    FloatProperty,
    IntProperty,
    BoolProperty,
    PointerProperty
)
from bpy_extras import object_utils
from mathutils import Vector, Quaternion
from math import pi
from .genFunctions import (
    circleVerts as circ_V,
    moveVerts as move_V,
    fanClose,
    coef
)

def bridgeLoops(loop1, loop2):
    faces = []

    if len(loop1) != len(loop2):
        return None

    for i in range(len(loop1) - 1):
        face = (loop1[i], loop1[i + 1], loop2[i + 1], loop2[i])
        faces.append(face)

    return faces

def getHeight(j, i, layers, height, addition, segments, layerHeight):
    if j == 0:
        return 0
    elif j == layers - 1:
        return height
    else:
        if j == 1:
            return (i * addition) / 2
        elif j == layers - 2:
            if i == 0:
                return (height - (3 * layerHeight))
            else:
                return height - (((segments - i) * addition) / 2)
        else:
            if j == 3 or j == 4:
                if i == 0:
                    return ((j - 2)*layerHeight) + (addition / 2)
                else:
                    return ((j - 2)*layerHeight) + (i * addition)
            elif j == layers - 4 or j == layers - 5:
                if i == segments - 1:
                    a = ((layers - j - 3) * layerHeight)
                    return height - a - (addition / 2)
                else:
                    return ((j - 2) * layerHeight) + (i * addition)
            else:
                return ((j - 2) * layerHeight) + (i * addition)


def getAngle(j, i, angle, layers, segments):
    if j == 1 and i == 2:
        return (angle * 2.2)
    elif j == layers - 2 and i == segments - 2:
        return ((2 * pi) - (angle * 2.2))
    elif j == 3 or j == 4:
        if i == 0:
            return (angle / 2)
        elif i == segments and layers == 8:
            return ((2 * pi) - (angle / 2))
        else:
            return (angle * i)
    elif j == layers - 4 or j == layers - 5:
        if i == segments:
            return ((2 * pi) - (angle / 2))
        else:
            return (angle * i)
    else:
        return (angle * i)


def getDiameter(j, i, layers, segments, diameter_1, diameter_2):
    if j == 0 or j == layers - 1 or j % 4 == 1 or j % 4 == 2:
        return diameter_1
    elif (
        (j == 3 or j == 4) and i == 0) or(
            (j == layers - 4 or j == layers - 5) and i == segments):
        return ((diameter_1 + diameter_2) / 2)
    else:
        return diameter_2

# generate geometry
def geoGen_WScrew (
    rounds,
    segments,
    height,
    diameter_1,
    diameter_2):

    # Перевод в диаметры
    diameter_1/=2.0
    diameter_2/=2.0
    
    if rounds < 1:
        rounds = 1
    if segments < 4:
        segments = 4
    if diameter_1 < 0:
        diameter_1 = 0
    if diameter_2 < 0:
        diameter_2 < 0

    # ...prepare empty lists
    verts = []
    edges = []
    faces = []

    loops = []
    closure1 = []
    closure2 = []

    # ...precompute some values
    layers = (rounds + 1) * 4
    layerHeight = height / (layers - 1)
    addition = (layerHeight * 4) / segments
    angle = (2 * pi) / segments

    # ...creating the layers
    for j in range(layers):
        loop = []
        for i in range(segments + 1):

            h = getHeight(
                j, i, layers, height, addition, segments, layerHeight)
            a = getAngle(j, i, angle, layers, segments)
            r = getDiameter(j, i, layers, segments, diameter_1, diameter_2)

            # ...where are vertices missing from loops
            non1 = (
                i == segments and not(j == (layers - 4) or j == (layers - 5)))
            non2 = (j == 1 or j == 2) and i < 2
            non3 = (
                j == (layers - 2) or j == (layers - 3)) and i > (segments - 2)

            if not non1 and not non2 and not non3:
                quat = Quaternion((0, 0, 1), a)
                loop.append(len(verts))
                if (j == 0 or (j > 4 and j < (layers - 1))) and i == 0:
                    closure1.append(len(verts))
                elif (i == (segments - 1) and j < (layers - 5)):
                    closure2.append(len(verts))
                verts.append(quat @ Vector((r, 0, h)))
        loops.append(loop)

    # ...creating faces
    # .......basic loops
    for i in range(len(loops) - 1):
        newFaces = bridgeLoops(loops[i], loops[i + 1])
        if newFaces:
            faces.extend(newFaces)
    # ...closure
    newFaces = bridgeLoops(closure1, closure2)
    if newFaces:
        faces.extend(newFaces)
    # ...Additional faces
    faces.append((0, loops[3][0], loops[4][0], loops[5][0]))
    faces.append((0, 1, loops[3][1], loops[3][0]))
    faces.append((1, 2, loops[1][0], loops[2][0]))
    faces.append((1, loops[2][0], loops[3][2], loops[3][1]))
    faces.append((loops[-6][-1], loops[-2][0], loops[-5][-1], loops[-5][-2]))
    faces.append((loops[-5][-1], loops[-2][0], loops[-1][0], loops[-4][-1]))
    faces.append((loops[-4][-2], loops[-4][-1], loops[-1][0], loops[-1][-1]))
    faces.append((loops[-4][-3], loops[-4][-2], loops[-1][-1], loops[-3][-1]))
    faces.append((loops[-3][-1], loops[-1][-1], loops[-1][-2], loops[-2][-1]))

    # ...shortenLoops
    loops[0].pop(0)
    loops[0].pop(0)
    newFaces = bridgeLoops(loops[0], loops[1])
    if newFaces:
        faces.extend(newFaces)
    loops[3].pop(0)
    loops[3].pop(0)
    newFaces = bridgeLoops(loops[2], loops[3])
    if newFaces:
        faces.extend(newFaces)
    loops[-5].pop(-1)
    newFaces = bridgeLoops(loops[-6], loops[-5])
    if newFaces:
        faces.extend(newFaces)
    loops[-4].pop(-1)
    loops[-4].pop(-1)
    newFaces = bridgeLoops(loops[-4], loops[-3])
    if newFaces:
        faces.extend(newFaces)
    loops[-1].pop(-1)
    newFaces = bridgeLoops(loops[-2], loops[-1])
    if newFaces:
        faces.extend(newFaces)

    return verts, edges, faces

def update_WScrew (wData):
    return geoGen_WScrew (
        rounds = wData.seg_1,
        segments = wData.seg_2,
        height = wData.siz_z,
        diameter_1 = wData.dia_1,
        diameter_2 = wData.dia_2
    )

# add object W_Plane
class Make_WScrew(bpy.types.Operator):
    """Create primitive wScrew"""
    bl_idname = "mesh.make_wscrew"
    bl_label = "wScrew"
    bl_options = {'UNDO', 'REGISTER'}

    rounds: IntProperty(
        name="Rounds",
        description="Iterations of the screw",
        default=5,
        min=1,
        soft_min=1
    )

    segments: IntProperty(
        name="Segments",
        description="Perimetr segments",
        default=12,
        min=3,
        soft_min=3
    )

    height: FloatProperty(
        name="Height",
        description="Height of the screw",
        default=1.0,
        min=0.0,
        soft_min=0.0,
        step=1,
        precision=2,
        unit='LENGTH'
    )

    diameter_1: FloatProperty(
        name="Major",
        description="Major diameter",
        default=0.5,
        min=0.0,
        soft_min=0.0,
        step=1,
        unit='LENGTH'
    )

    diameter_2: FloatProperty(
        name="Minor",
        description="Minor diameter",
        default=0.6,
        min=0.0,
        soft_min=0.0,
        step=1,
        unit='LENGTH'
    )

    def execute(self, context):

        mesh = bpy.data.meshes.new("wScrew")

        wD = mesh.wData
        wD.seg_1 = self.rounds
        wD.seg_2 = self.segments
        wD.siz_z = self.height
        wD.dia_1 = self.diameter_1
        wD.dia_2 = self.diameter_2        
        wD.wType = 'WSCREW'


        mesh.from_pydata(*update_WScrew(wD))
        mesh.update()
        
        object_utils.object_data_add(context, mesh, operator=None)
        
        return {'FINISHED'}

# create UI panel
def draw_WScrew_panel(self, context):
    lay_out = self.layout
    lay_out.use_property_split = True
    WData = context.object.data.wData

    lay_out.label(text="Type: wScrew", icon='MOD_SCREW')

    col = lay_out.column(align=True)
    col.prop(WData, "dia_1", text="Diameter 1")
    col.prop(WData, "dia_2", text="Diameter 2")

    lay_out.prop(WData, "siz_z", text="Height")
    
    col = lay_out.column(align=True)
    col.prop(WData, "seg_1", text="Rounds")
    col.prop(WData, "seg_2", text="Segments")
    
# register
def reg_wScrew():
    bpy.utils.register_class(Make_WScrew)
# unregister
def unreg_wScrew():
    bpy.utils.unregister_class(Make_WScrew)