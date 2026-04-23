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
from math import pi as PI
from .genFunctions import (
    circleVerts as circ_V,
    moveVerts as move_V,
    rotateVerts as rot_V,
    fanClose,
    bridgeLoops,
    create_mesh_object,
    coef
)

# generate geometry
def geoGen_WTorus (
    diameter_main,
    diameter_minor,
    seg_main,
    seg_minor,
    sec_from,
    sec_to,
    coefficient=False,
    use_bounds=False):
    
    # Prepare empty lists
    verts = []
    edges = []
    faces = []
    loops = []

    # Расчёт диаметров
    if use_bounds:
        # Внешний и внутренний диаметры
        dia_main=(diameter_main+diameter_minor)/4.0
        dia_minor=(diameter_main-diameter_minor)/4.0
    else:
        # Основной диаметр и диаметр сечения
        dia_main=diameter_main/2.0
        dia_minor=diameter_minor/2.0
    
    # Применение коэффициентов
    if coefficient:
        dia_main*=coef(seg_main)
        dia_minor*=coef(seg_minor)

    # Set minimums
    if seg_main < 3:
        seg_main = 3
    if seg_minor < 3:
        seg_minor = 3
    if sec_from > sec_to:
        sec_from, sec_to = sec_to, sec_from

    # Create the loops
    seg_angle = (sec_to - sec_from) / seg_main
    quatRight = Quaternion((-1, 0, 0), PI / 2)
    vecOffset = Vector((dia_main, 0, 0))
    for i in range(seg_main):
        quat = Quaternion((0, 0, 1), (i * seg_angle) + sec_from)
        newVerts, loop = circ_V(dia_minor, seg_minor, len(verts))
        rot_V(newVerts, quatRight)
        move_V(newVerts, vecOffset)
        rot_V(newVerts, quat)
        verts.extend(newVerts)
        loops.append(loop)

    # Close the shape
    if sec_to - sec_from < 2 * PI:
        quat = Quaternion((0, 0, 1), sec_to)
        newVerts, loop = circ_V(dia_minor, seg_minor, len(verts))
        rot_V(newVerts, quatRight)
        move_V(newVerts, vecOffset)
        rot_V(newVerts, quat)
        verts.extend(newVerts)
        loops.append(loop)

        verts.append(quat @ vecOffset)
        quat = Quaternion((0, 0, 1), sec_from)
        verts.append(quat @ vecOffset)

        # Close caps
        faces.extend(fanClose(loops[0], len(verts) - 1, flipped = True))
        faces.extend(fanClose(loops[-1], len(verts) - 2))
    else:
        faces.extend(bridgeLoops(loops[-1], loops[0], True))

    # Bridge all loops
    for i in range(1, len(loops)):
        faces.extend(bridgeLoops(loops[i - 1], loops[i], True))

    return verts, edges, faces

def update_WTorus (wData):
    return geoGen_WTorus (
        diameter_main = wData.dia_1,
        diameter_minor = wData.dia_2,
        seg_main = wData.seg_1,
        seg_minor = wData.seg_2,
        sec_from = wData.sec_f,
        sec_to = wData.sec_t,
        use_bounds=wData.use_bounds,
        coefficient=wData.coeff
    )

# add object W_Plane
class Make_WTorus(bpy.types.Operator):
    """Create primitive wTorus"""
    bl_idname = "mesh.make_wtorus"
    bl_label = "wTorus"
    bl_options = {'UNDO', 'REGISTER'}

    diameter_main: FloatProperty(
        name = "Main Diameter",
        description = "Main Diameter",
        default = 1.0,
        min = 0.0,
        soft_min = 0.0,
        step = 1,
        unit = "LENGTH"
    )

    diameter_minor: FloatProperty(
        name = "Minor Diameter",
        description = "Minor Diameter",
        default = 0.5,
        min = 0.0,
        soft_min = 0.0,
        step = 1,
        unit = "LENGTH"
    )

    use_bounds: BoolProperty(
        name = "Use Bounds",
        description="Switch between Main/Minor and Outer/Inner diameters",
        default = False
    )

    seg_main: IntProperty(
        name = "Main",
        description = "Segmentation on main perimeter",
        default = 24,
        min = 3,
        soft_min = 3,
        step = 1,
        subtype = 'NONE'
    )

    seg_minor: IntProperty(
        name = "Minor",
        description = "Segmentation of the minor perimeter",
        default = 12,
        min = 3,
        soft_min = 3,
        step = 1,
        subtype = 'NONE'
    )

    sec_from: FloatProperty(
        name = "From",
        description = "Start angle of the section",
        default = 0.0,
        min = 0.0,
        max = 2 * PI,
        soft_min = 0.0,
        soft_max = 2 * PI,
        step = 10,
        unit = "ROTATION"
    )

    sec_to: FloatProperty(
        name = "To",
        description = "End angle of the section",
        default = 2 * PI,
        min = 0.0,
        max = 2 * PI,
        soft_min = 0.0,
        soft_max = 2 * PI,
        step = 10,
        unit = "ROTATION"
    )

    coefficient: BoolProperty(
        name="Coef",
        description="Применение коэффициента усадки",
        default=False
    )

    def execute(self, context):

        mesh = bpy.data.meshes.new("wTorus")

        wD = mesh.wData
        wD.dia_1 = self.diameter_main
        wD.dia_2 = self.diameter_minor
        wD.seg_1 = self.seg_main
        wD.seg_2 = self.seg_minor
        wD.sec_f = self.sec_from
        wD.sec_t = self.sec_to
        wD.use_bounds = self.use_bounds
        wD.coeff = self.coefficient
        wD.wType = 'WTORUS'


        mesh.from_pydata(*update_WTorus(wD))
        mesh.update()
        
        object_utils.object_data_add(context, mesh, operator=None)
        
        return {'FINISHED'}

# create UI panel
def draw_WTorus_panel(self, context):
    lay_out = self.layout
    lay_out.use_property_split = True
    WData = context.object.data.wData

    lay_out.label(text="Type: wTorus", icon='MESH_TORUS')

    col = lay_out.column(align=True)
    if not WData.use_bounds:
        col.prop(WData, "dia_1", text="Diameter Main")
        col.prop(WData, "dia_2", text="Diameter Minor")
    else:
        col.prop(WData, "dia_1", text="Outer Diameter")
        col.prop(WData, "dia_2", text="Inner Diameter")

    # Переключатель режима
    lay_out.prop(WData, "use_bounds", text="Use Outer/Inner")

    col = lay_out.column(align=True)
    col.prop(WData, "sec_f", text="Section From")
    col.prop(WData, "sec_t", text="Section To")
    
    col = lay_out.column(align=True)
    col.prop(WData, "seg_1", text="Segmentation Main")
    col.prop(WData, "seg_2", text="Minor")

    lay_out.prop(WData, "coeff", text="Coef")
    
# register
def reg_wTorus():
    bpy.utils.register_class(Make_WTorus)
# unregister
def unreg_wTorus():
    bpy.utils.unregister_class(Make_WTorus)