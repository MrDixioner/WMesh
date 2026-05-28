# imports
import bpy
from bpy.props import (
    FloatProperty,
    IntProperty,
    BoolProperty
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
    coef
)

# generate geometry
def geoGen_WSpring(
    dia_bottom,
    dia_top,
    dia_section,
    turns,
    height,
    seg_main,
    seg_minor,
    coefficient=False,
    centered=True):
    
    verts = []
    edges = []
    faces = []
    loops = []

    # Радиусы траектории и сечения
    r_bottom = dia_bottom / 2.0
    r_top = dia_top / 2.0
    r_sec = dia_section / 2.0
    
    if coefficient:
        r_bottom *= coef(seg_main)
        r_top *= coef(seg_main)
        r_sec *= coef(seg_minor)

    # Ограничения минимумов
    if seg_main < 3:
        seg_main = 3
    if seg_minor < 3:
        seg_minor = 3
    if turns <= 0:
        turns = 0.1

    # Общее количество шагов по всей длине спирали
    # seg_main задает количество сегментов НА ОДИН ВИТОК
    total_steps = int(seg_main * turns)
    if total_steps < 3:
        total_steps = 3

    total_angle = 2 * PI * turns
    angle_step = total_angle / total_steps
    height_step = height / total_steps

    # Смещение по Z, если спираль центрирована
    z_start = -height / 2.0 if centered else 0.0

    for i in range(total_steps + 1):
        angle = i * angle_step
        
        # Линейная интерполяция радиуса от нижнего к верхнему
        factor = i / total_steps
        current_r_mesh = r_bottom + (r_top - r_bottom) * factor
        
        # Текущая точка на центральной оси пружины
        pos_x = current_r_mesh * (Quaternion((0, 0, 1), angle) @ Vector((1.0, 0.0, 0.0))).x
        pos_y = current_r_mesh * (Quaternion((0, 0, 1), angle) @ Vector((1.0, 0.0, 0.0))).y
        pos_z = z_start + (i * height_step)
        center_point = Vector((pos_x, pos_y, pos_z))

        # Вычисление наклона витка (касательная и нормаль для разворота профиля)
        # Нам нужно развернуть окружность сечения так, чтобы она смотрела вдоль витка
        quat_rot = Quaternion((0, 0, 1), angle)
        
        # Дополнительный наклон профиля по оси X из-за подъема витка
        pitch_angle = 0.0
        if height > 0:
            # Длина окружности текущего витка ориентировочно
            pitch_angle = (height / turns) / (2 * PI * current_r_mesh)
            
        quat_pitch = Quaternion((1, 0, 0), pitch_angle)
        quat_final = quat_rot @ Quaternion((-1, 0, 0), PI / 2) @ quat_pitch

        # Генерируем окружность сечения пружины
        newVerts, loop = circ_V(r_sec, seg_minor, len(verts))
        
        # Ориентируем и перемещаем кольцо сечения в пространстве
        rot_V(newVerts, quat_final)
        move_V(newVerts, center_point)
        
        verts.extend(newVerts)
        loops.append(loop)

    # Закрываем торцы пружины (заглушки на концах)
    # Вычисляем центральные точки торцов
    center_bottom = Vector((r_bottom, 0.0, z_start))
    quat_end = Quaternion((0, 0, 1), total_angle)
    center_top = quat_end @ Vector((r_top, 0.0, z_start + height))

    verts.append(center_bottom)
    verts.append(center_top)

    faces.extend(fanClose(loops[0], len(verts) - 2, flipped=True))
    faces.extend(fanClose(loops[-1], len(verts) - 1, flipped=False))

    # Соединяем последовательно все кольца сечений между собой
    for i in range(1, len(loops)):
        faces.extend(bridgeLoops(loops[i - 1], loops[i], True))

    return verts, edges, faces

def update_WSpring(wData):
    return geoGen_WSpring(
        dia_bottom=wData.dia_1,
        dia_top=wData.dia_2,
        dia_section=wData.dia_sec,
        turns=wData.turns,
        height=wData.siz_z,
        seg_main=wData.seg_1,
        seg_minor=wData.seg_2,
        coefficient=wData.coeff,
        centered=wData.cent
    )

# Operator to create object
class Make_WSpring(bpy.types.Operator):
    """Create primitive wSpring"""
    bl_idname = "mesh.make_wspring"
    bl_label = "wSpring"
    bl_options = {'UNDO', 'REGISTER'}

    dia_1: FloatProperty(name="Bottom Diameter", default=1.0, min=0.0, unit="LENGTH")
    dia_2: FloatProperty(name="Top Diameter", default=1.0, min=0.0, unit="LENGTH")
    dia_sec: FloatProperty(name="Section Diameter", default=0.1, min=0.001, unit="LENGTH")
    turns: FloatProperty(name="Turns", default=3.0, min=0.1, step=10)
    height: FloatProperty(name="Height", default=1.0, min=0.0, unit="LENGTH")
    seg_1: IntProperty(name="Segmentation Main", default=24, min=3)
    seg_2: IntProperty(name="Segmentation Minor", default=12, min=3)
    centered: BoolProperty(name="Centered", default=True)
    coefficient: BoolProperty(name="Coef", default=False)

    def execute(self, context):
        mesh = bpy.data.meshes.new("wSpring")

        wD = mesh.wData
        wD.dia_1 = self.dia_1
        wD.dia_2 = self.dia_2
        wD.dia_sec = self.dia_sec
        wD.turns = self.turns
        wD.siz_z = self.height
        wD.seg_1 = self.seg_1
        wD.seg_2 = self.seg_2
        wD.cent = self.centered
        wD.coeff = self.coefficient
        wD.wType = 'WSPRING'

        mesh.from_pydata(*update_WSpring(wD))
        mesh.update()
        
        object_utils.object_data_add(context, mesh, operator=None)
        return {'FINISHED'}

# UI panel draw function
def draw_WSpring_panel(self, context):
    lay_out = self.layout
    from . import w_icons

    lay_out.use_property_split = True
    WData = context.object.data.wData

    if w_icons and "WSpring" in w_icons:
        icon_id = w_icons["WSpring"].icon_id
        lay_out.label(text="Type: wSpring", icon_value=icon_id)
    else:
        lay_out.label(text="Type: wScrew", icon='MOD_SCREW')

    col = lay_out.column(align=True)
    col.prop(WData, "dia_1", text="Bottom Diameter")
    col.prop(WData, "dia_2", text="Top Diameter")
    col.prop(WData, "dia_sec", text="Section Diameter")
    
    col = lay_out.column(align=True)
    col.prop(WData, "siz_z", text="Height")
    col.prop(WData, "turns", text="Turns")
    
    col = lay_out.column(align=True)
    col.prop(WData, "seg_1", text="Seg. Main")
    col.prop(WData, "seg_2", text="Seg. Section")

    lay_out.prop(WData, "cent", text="Centered")
    lay_out.prop(WData, "coeff", text="Coef")

def reg_wSpring():
    bpy.utils.register_class(Make_WSpring)

def unreg_wSpring():
    bpy.utils.unregister_class(Make_WSpring)
