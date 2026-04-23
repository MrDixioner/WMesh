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
    bridgeLoops,
    create_mesh_object,
    coef
)

# generate geometry
def geoGen_WCone (
    diameter_main,
    diameter_top,
    height,
    seg_perimeter,
    seg_height,
    seg_diameter,
    centered,
    coefficient):
    
    # Prepare empty lists
    verts = []
    edges = []
    faces = []

    loops = []

    # Коэффициенты
    coeff_mult=1.0

    # Перевод в диаметры
    diameter_main/=2;
    diameter_top/=2;

    # Set minimums
    if seg_perimeter < 3:
        seg_perimeter = 3
    if seg_height < 1:
        seg_height = 1
    if seg_diameter < 1:
        seg_diameter = 1
    
    # Коэффициент
    if coefficient:
        coeff_mult=coef(seg_perimeter)
        diameter_main*=coeff_mult
        diameter_top*=coeff_mult

    # Add top and bottom center vertices
    verts.append(Vector((0, 0, 0)))
    verts.append(Vector((0, 0, height)))

    if diameter_top == 0 and diameter_main == 0:
        edges.append((0, 1))
        return verts, edges, faces

    # Create base segmentation loops
    if diameter_main > 0:
        if seg_diameter > 1:
            step = diameter_main / seg_diameter
            for i in range(1, seg_diameter):
                newVerts, loop = circ_V(i * step, seg_perimeter, len(verts))
                verts.extend(newVerts)
                loops.append(loop)

        # Create the base corner circle
        newVerts, loop = circ_V(diameter_main, seg_perimeter, len(verts))
        verts.extend(newVerts)
        loops.append(loop)

    # Create the side segmentation loops
    if seg_height > 1:
        heightStep = height / seg_height
        diameterStep = (diameter_top - diameter_main) / seg_height
        for i in range(1, seg_height):
            newDiameter = diameter_main + (i * diameterStep)
            newVerts, loop = circ_V(newDiameter, seg_perimeter, len(verts))
            move_V(newVerts, Vector((0, 0, heightStep * i)))
            verts.extend(newVerts)
            loops.append(loop)

    # Create top corner circle
    if diameter_top > 0:
        newVerts, loop = circ_V(diameter_top, seg_perimeter, len(verts))
        move_V(newVerts, Vector((0, 0, height)))
        verts.extend(newVerts)
        loops.append(loop)

        # Create the top segmentation loops
        if seg_diameter > 1:
            step = diameter_top / seg_diameter
            for i in range(1, seg_diameter):
                newDiameter = diameter_top - (i * step)
                newVerts, loop = circ_V(newDiameter, seg_perimeter, len(verts))
                move_V(newVerts, Vector((0, 0, height)))
                verts.extend(newVerts)
                loops.append(loop)

    # Close caps
    faces.extend(fanClose(loops[0], 0, closed = True, flipped = True))
    faces.extend(fanClose(loops[-1], 1))

    # Bridge all loops
    for i in range(1, len(loops)):
        faces.extend(bridgeLoops(loops[i - 1], loops[i], True))

    if centered:
        move_V(verts, Vector((0, 0, -height / 2)))

    return verts, edges, faces

def update_WCone (wData):
    return geoGen_WCone (
        diameter_main = wData.dia_1,
        diameter_top = wData.dia_2,
        height = wData.siz_z,
        seg_perimeter = wData.seg_1,
        seg_height = wData.seg_2,
        seg_diameter = wData.seg_3,
        centered = wData.cent,
        coefficient=wData.coeff
    )

# add object W_Plane
class Make_WCone(bpy.types.Operator):
    """Create primitive wCone"""
    bl_idname = "mesh.make_wcone"
    bl_label = "wCone"
    bl_options = {'UNDO', 'REGISTER'}

    diameter_top: FloatProperty(
        name = "Diameter top",
        description = "Top Diameter",
        default = 0.0,
        min = 0.0,
        soft_min = 0.0,
        step = 1,
        precision = 2,
        unit = "LENGTH"
    )

    diameter_main: FloatProperty(
        name = "Diameter bottom",
        description = "Bottom Diameter",
        default = 1.0,
        min = 0.0,
        soft_min = 0.0,
        step = 1,
        precision = 2,
        unit = "LENGTH"
    )

    height: FloatProperty(
        name = "Height",
        description = "Height of the cone",
        default = 1.0,
        min = 0.0,
        soft_min = 0.0,
        step = 1,
        precision = 2,
        unit = "LENGTH"
    )

    seg_perimeter: IntProperty(
        name = "Perim Segments",
        description = "Subdivision on perimeter",
        default = 24,
        min = 3,
        soft_min = 3,
        step = 1,
        subtype = 'NONE'
    )

    seg_height: IntProperty(
        name = "Height Segments",
        description = "Subdivision of the height",
        default = 1,
        min = 1,
        soft_min = 1,
        step = 1,
        subtype = 'NONE'
    )

    seg_diameter: IntProperty(
        name = "Diameter Segments",
        description = "Subdivision of the diameters",
        default = 1,
        min = 1,
        soft_min = 1,
        step = 1,
        subtype = 'NONE'
    )

    coefficient: BoolProperty(
        name="Coef",
        description="Применение коэффициента усадки",
        default=False
    )

    centered: BoolProperty(
        name = "Centered",
        description = "Set origin of the cone",
        default = False
    )

    def execute(self, context):

        mesh = bpy.data.meshes.new("wCone")

        wD = mesh.wData
        wD.dia_1 = self.diameter_main
        wD.dia_2 = self.diameter_top
        wD.siz_z = self.height
        wD.seg_1 = self.seg_perimeter
        wD.seg_2 = self.seg_height
        wD.seg_3 = self.seg_diameter
        wD.coeff = self.coefficient
        wD.cent = self.centered
        wD.smo = True
        wD.wType = 'WCONE'


        mesh.from_pydata(*update_WCone(wD))
        mesh.update()
        
        object_utils.object_data_add(context, mesh, operator=None)
        
        return {'FINISHED'}

# create UI panel
def draw_WCone_panel(self, context):
    lay_out = self.layout
    lay_out.use_property_split = True
    WData = context.object.data.wData

    lay_out.label(text="Type: wCone", icon='MESH_CONE')

    col = lay_out.column(align=True)
    col.prop(WData, "dia_2", text="Diameter Top")
    col.prop(WData, "dia_1", text="Diameter Main")
    col.prop(WData, "siz_z", text="Height")
    
    col = lay_out.column(align=True)
    col.prop(WData, "seg_1", text="Segmentation Main")
    col.prop(WData, "seg_2", text="Vertical")
    col.prop(WData, "seg_3", text="Caps")

    lay_out.prop(WData, "cent", text="Centered") 
    lay_out.prop(WData, "coeff", text="Coef")   

# register
def reg_wCone():
    bpy.utils.register_class(Make_WCone)
# unregister
def unreg_wCone():
    bpy.utils.unregister_class(Make_WCone)