# imports
import bpy
from bpy.props import (
    FloatProperty,
    IntProperty,
    BoolProperty,
    PointerProperty
)
from mathutils import Vector, Quaternion
from math import pi as PI
from .genFunctions import (
    circleVerts as circ_V,
    moveVerts as move_V,
    fanClose,
    bridgeLoops,
    create_mesh_object,
    coef
)

# generate geometry
def geoGen_WCapsule (
    diameter,
    height,
    seg_perimeter,
    seg_height,
    seg_caps,
    centered,
    coefficient):
    
    # Prepare empty lists
    verts = []
    edges = []
    faces = []

    loops = []

    # Coefficient
    coeff_mult=1.0

    # Make diameter (01.08.2024)
    diameter/=2.0

    # Set minimums
    if seg_perimeter < 3:
        seg_perimeter = 3
    if seg_height < 1:
        seg_height = 1
    if seg_caps < 1:
        seg_caps = 1
    if diameter > height:
        diameter = height
    
    # Coefficient
    if coefficient:
        coeff_mult=coef(seg_perimeter)
        diameter*=coeff_mult

    # Add top and bottom center vertices
    verts.append(Vector((0, 0, 0)))
    verts.append(Vector((0, 0, height)))

    # Create bootom cap segmentation loops
    if seg_caps > 1:
        angleStep = PI / (2 * seg_caps)
        for i in range(1, seg_caps):
            # find the radius and height
            quat = Quaternion((0, -1, 0), i * angleStep)
            helperVect = quat @ Vector((0, 0, -diameter))
            segmentRadius = helperVect.x
            segmentHeight = diameter + helperVect.z
            # create the ring
            newVerts, loop = circ_V(segmentRadius, seg_perimeter, len(verts))
            move_V(newVerts, Vector((0, 0, segmentHeight)))
            verts.extend(newVerts)
            loops.append(loop)

    # Create the base corner circle
    newVerts, loop = circ_V(diameter, seg_perimeter, len(verts))
    move_V(newVerts, Vector((0, 0, diameter)))
    verts.extend(newVerts)
    loops.append(loop)

    # Create the side segmentation loops
    if height > 2 * diameter:
        if seg_height > 1:
            heightStep = (height - (2 * diameter)) / seg_height
            for i in range(1, seg_height):
                newHeight = (i * heightStep) + diameter
                newVerts, loop = circ_V(diameter, seg_perimeter, len(verts))
                move_V(newVerts, Vector((0, 0, newHeight)))
                verts.extend(newVerts)
                loops.append(loop)

    # Create top corner circle
        newVerts, loop = circ_V(diameter, seg_perimeter, len(verts))
        move_V(newVerts, Vector((0, 0, height - diameter)))
        verts.extend(newVerts)
        loops.append(loop)

    # Create top cap segmentation loops
    if seg_caps > 1:
        angleStep = PI / (2 * seg_caps)
        for i in range(1, seg_caps):
            # find the radius and height
            quat = Quaternion((0, -1, 0), i * angleStep)
            helperVect = quat @ Vector((diameter, 0, 0))
            segmentRadius = helperVect.x
            segmentHeight = height - diameter + helperVect.z
            # create the ring
            newVerts, loop = circ_V(segmentRadius, seg_perimeter, len(verts))
            move_V(newVerts, Vector((0, 0, segmentHeight)))
            verts.extend(newVerts)
            loops.append(loop)

    # Close caps
    faces.extend(fanClose(loops[0], 0, flipped = True))
    faces.extend(fanClose(loops[-1], 1))

    # Bridge all loops
    for i in range(1, len(loops)):
        faces.extend(bridgeLoops(loops[i - 1], loops[i], True))

    if centered:
        move_V(verts, Vector((0, 0, -height / 2)))

    return verts, edges, faces

def update_WCapsule (wData):
    return geoGen_WCapsule (
        diameter = wData.dia_1,
        height = wData.siz_z,
        seg_perimeter = wData.seg_1,
        seg_height = wData.seg_2,
        seg_caps = wData.seg_3,
        centered = wData.cent,
        coefficient = wData.coeff
    )

# add object W_Capsule
class Make_WCapsule(bpy.types.Operator):
    """Create primitive wCapsule"""
    bl_idname = "mesh.make_wcapsule"
    bl_label = "wCapsule"
    bl_options = {'UNDO', 'REGISTER'}

    diameter: FloatProperty(
        name = "Diameter",
        description = "Diameter",
        default = 0.5,
        min = 0.0,
        soft_min = 0.0,
        step = 1,
        unit = "LENGTH"
    )

    height: FloatProperty(
        name = "Height",
        description = "Height of the capsule",
        default = 1.0,
        min = 0.0,
        soft_min = 0.0,
        step = 1,
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

    seg_caps: IntProperty(
        name = "Caps Segments",
        description = "Subdivision of the caps",
        default = 6,
        min = 1,
        soft_min = 1,
        step = 1,
        subtype = 'NONE'
    )

    centered: BoolProperty(
        name = "Centered",
        description = "Set origin of the cone",
        default = False
    )

    coefficient: BoolProperty(
        name="Coef",
        description="Применение коэффициента усадки",
        default=False
    )

    def execute(self, context):

        verts, edges, faces = geoGen_WCapsule(
            diameter = self.diameter,
            height = self.height,
            seg_perimeter = self.seg_perimeter,
            seg_height = self.seg_height,
            seg_caps = self.seg_caps,
            centered = self.centered,
            coefficient = self.coefficient
        )
        create_mesh_object(context, verts, edges, faces, "wCapsule")

        wD = context.object.data.wData
        wD.dia_1 = self.diameter
        wD.siz_z = self.height
        wD.seg_1 = self.seg_perimeter
        wD.seg_2 = self.seg_height
        wD.seg_3 = self.seg_caps
        wD.cent = self.centered
        wD.coeff = self.coefficient
        wD.wType = 'WCAPSULE'

        return {'FINISHED'}

# create UI panel
def draw_WCapsule_panel(self, context):
    lay_out = self.layout

    from . import w_icons

    lay_out.use_property_split = True
    WData = context.object.data.wData

    if w_icons and "W_Capsule_64" in w_icons:
        icon_id = w_icons["W_Capsule_64"].icon_id
        lay_out.label(text="Type: wCapsule", icon_value=icon_id)
    else:
        lay_out.label(text="Type: wCapsule", icon='MESH_CAPSULE')
    
    col = lay_out.column(align=True)
    col.prop(WData, "dia_1", text="Diameter")
    col.prop(WData, "siz_z", text="Height")
    
    col = lay_out.column(align=True)
    col.prop(WData, "seg_1", text="Segmentation Main")
    col.prop(WData, "seg_2", text="Vertical")
    col.prop(WData, "seg_3", text="Caps")

    lay_out.prop(WData, "cent", text="Centered")
    
    lay_out.prop(WData, "coeff", text="Coef")    

# register
def reg_wCapsule():
    bpy.utils.register_class(Make_WCapsule)
# unregister
def unreg_wCapsule():
    bpy.utils.unregister_class(Make_WCapsule)