bl_info = {
    "name": "W_Mesh",
    "category": "Object",
    "author": "Vit Prochazka, MrDixioner",
    "version": (1, 7, 0),
    "blender": (4, 0, 0),
    "description": "Modify primitives after creation.",
}

import os
import bpy
import bpy.utils.previews
w_icons = None
import bmesh
from bpy.props import (
    EnumProperty,
    BoolProperty,
    FloatProperty,
    IntProperty,
    PointerProperty
)
from math import pi

from .W_Box import reg_wBox, unreg_wBox, update_WBox, draw_WBox_panel
from .W_Capsule import reg_wCapsule, unreg_wCapsule, update_WCapsule, draw_WCapsule_panel
from .W_Cone import reg_wCone, unreg_wCone, update_WCone, draw_WCone_panel
from .W_Plane import reg_wPlane, unreg_wPlane, update_wPlane, draw_wPlane_panel
from .W_Pyramid import reg_wPyramid, unreg_wPyramid, update_WPyramid, draw_WPyramid_panel
from .W_Ring import reg_wRing, unreg_wRing, update_WRing, draw_WRing_panel
from .W_Screw import reg_wScrew, unreg_wScrew, update_WScrew, draw_WScrew_panel
from .W_Sphere import reg_wSphere, unreg_wSphere, update_WSphere, draw_WSphere_panel
from .W_Spiral import reg_wSpiral, unreg_wSpiral, update_WSpiral, draw_WSpiral_panel
from .W_Torus import reg_wTorus, unreg_wTorus, update_WTorus, draw_WTorus_panel
from .W_Tube import reg_wTube, unreg_wTube, update_WTube, draw_WTube_panel

def WUpdate(self, context):
    if self.wType == "NONE":
        return
    
    verts = []
    edges = []
    faces = []

    if self.wType == "WBOX" : verts, edges, faces = update_WBox(self)
    if self.wType == "WCAPSULE" : verts, edges, faces = update_WCapsule(self)
    if self.wType == "WCONE" : verts, edges, faces = update_WCone(self)
    if self.wType == "WPLANE" : verts, edges, faces = update_wPlane(self)
    if self.wType == "WPYRAMID" : verts, edges, faces = update_WPyramid(self)
    if self.wType == "WRING" : verts, edges, faces = update_WRing(self)
    if self.wType == "WSCREW" : verts, edges, faces = update_WScrew(self)
    if self.wType == "WSPHERE" : verts, edges, faces = update_WSphere(self)
    if self.wType == "WSPIRAL" : verts, edges, faces = update_WSpiral(self)
    if self.wType == "WTORUS" : verts, edges, faces = update_WTorus(self)
    if self.wType == "WTUBE" : verts, edges, faces = update_WTube(self)
    
    tmpMesh = bpy.data.meshes.new("TemporaryMesh")
    tmpMesh.from_pydata(verts, edges, faces)
    tmpMesh.update()

    bm = bmesh.new()
    bm.from_mesh(tmpMesh)    
    bm.to_mesh(self.id_data)
    bm.free()
    bpy.data.meshes.remove(tmpMesh)
    self.id_data.update()

class wData(bpy.types.PropertyGroup):

    WTypes = [
        ('NONE', "None", ""),
        ('WBOX', "wBox", ""),
        ("WCAPSULE", "wCapsule", ""),
        ("WCONE", "wCone", ""),
        ('WPLANE', "wPlane", ""),
        ('WPYRAMID', "wPyramid", ""),
        ('WSCREW', "wScrew", ""),
        ('WSPHERE', "wSphere", ""),
        ("WSPIRAL", "wSpiral", ""),
        ('WRING', "wRing", ""),
        ("WTORUS", "wTorus", ""),
        ('WTUBE', "wTube", "")
    ]

    SBases = [
        ('UV', "UV", ""),
        ('TETRA', "Tetra", ""),
        ('CUBE', "Cube", ""),
        ('OCTA', "Octa", ""),
        ('ICOSA', "Icosa", "")
    ]

    wType: EnumProperty(
        items = WTypes,
        name = "wType",
        description = "Type of WMesh",
        default = 'NONE'
    )

    sBase: EnumProperty(
        items = SBases,
        name = "sBase",
        description = "Base of topology",
        default = 'UV',
        update = WUpdate
    )

    siz_x: FloatProperty(
        name="Width_X",
        description="",
        default=1.0,
        min=0.0,
        soft_min=0.0,
        step=1,
        unit='LENGTH',
        update=WUpdate
    )

    siz_y: FloatProperty(
        name="Length_Y",
        description="",
        default=1.0,
        min=0.0,
        soft_min=0.0,
        step=1,
        unit='LENGTH',
        update=WUpdate
    )

    siz_z: FloatProperty(
        name="Height_Z",
        description="",
        default=1.0,
        min=0.0,
        soft_min=0.0,
        step=1,
        unit='LENGTH',
        update=WUpdate
    )

    dia_1: FloatProperty(
        name="Diameter_1",
        description="",
        default=1.0,
        min=0.0,
        soft_min=0.0,
        step=1,
        unit='LENGTH',
        update=WUpdate
    )

    dia_2: FloatProperty(
        name="Diameter_2",
        description="",
        default=1.0,
        min=0.0,
        soft_min=0.0,
        step=1,
        unit='LENGTH',
        update=WUpdate
    )

    sec_f: FloatProperty(
        name="Sector_From",
        description="",
        default=0.0,
        min=0.0,
        max=2 * pi,
        soft_min=0.0,
        soft_max=2 * pi,
        step=10,
        unit='ROTATION',
        update=WUpdate
    )

    sec_t: FloatProperty(
        name="Sector_To",
        description="",
        default=0.0,
        min=0.0,
        max=2 * pi,
        soft_min=0.0,
        soft_max=2 * pi,
        step=10,
        unit='ROTATION',
        update=WUpdate
    )

    seg_1: IntProperty(
        name="Segmentation",
        description="",
        default=3,
        min=1,
        soft_min=1,
        step=1,
        update=WUpdate
    )

    seg_2: IntProperty(
        name="Segmentation",
        description="",
        default=3,
        min=1,
        soft_min=1,
        step=1,
        update=WUpdate
    )

    seg_3: IntProperty(
        name="Segmentation",
        description="",
        default=3,
        min=1,
        soft_min=1,
        step=1,
        update=WUpdate
    )

    cent: BoolProperty(
        name="Centered",
        description="",
        default=True,
        update=WUpdate
    )

    inn: BoolProperty(
        name="UseInner",
        description="",
        default=True,
        update=WUpdate
    )

    coeff: BoolProperty(
        name="Coefficient",
        description="Application of shrinkage coefficient",
        default=False,
        update=WUpdate
    )

    use_bounds: BoolProperty(
        name="UseBounds",
        description="Mode switch",
        default=False,
        update=WUpdate
    )

    turns: FloatProperty(
        name="Turns",
        description="Number of helical turns",
        default=3.0,
        min=0.1,
        soft_min=0.1,
        step=10,
        update=WUpdate
    )

    dia_sec: FloatProperty(
        name="Section Diameter",
        description="Diameter of the profile circle",
        default=0.1,
        min=0.001,
        soft_min=0.001,
        step=1,
        unit='LENGTH',
        update=WUpdate
    )


class WAddMenu(bpy.types.Menu):
    bl_label = "wPrimitives"
    bl_idname = "OBJECT_MT_W_Primitives_menu"

    def draw(self, context):
        lay_out = self.layout
        # Получаем доступ к коллекции иконок
        pcoll = w_icons

        lay_out.operator(operator="mesh.make_wbox", icon_value=pcoll["W_Box_64"].icon_id)
        lay_out.operator(operator="mesh.make_wcapsule", icon_value=pcoll["W_Capsule_64"].icon_id)
        lay_out.operator(operator="mesh.make_wcone", icon_value=pcoll["W_Cone_64"].icon_id)
        lay_out.operator(operator="mesh.make_wplane", icon_value=pcoll["W_Plane_64"].icon_id)
        lay_out.operator(operator="mesh.make_wpyramid", icon_value=pcoll["W_Pyramid_64"].icon_id)
        lay_out.operator(operator="mesh.make_wring", icon_value=pcoll["W_Ring_64"].icon_id)
        lay_out.operator(operator="mesh.make_wscrew", icon_value=pcoll["W_Screw_64"].icon_id)
        lay_out.operator(operator="mesh.make_wsphere", icon_value=pcoll["W_Sphere_64"].icon_id)
        lay_out.operator(operator="mesh.make_wspiral", icon_value=pcoll["W_Spiral_64"].icon_id)
        lay_out.operator(operator="mesh.make_wtorus", icon_value=pcoll["W_Torus_64"].icon_id)
        lay_out.operator(operator="mesh.make_wtube", icon_value=pcoll["W_Tube_64"].icon_id)


def draw_addMenu(self, context):
    lay_out = self.layout
    lay_out.menu(WAddMenu.bl_idname)

class ConvertWMesh(bpy.types.Operator):
    """Convert WMesh to mesh"""
    bl_idname = "mesh.convert_w_mesh"
    bl_label = "Convert to regular mesh"
    bl_options = {'UNDO', 'REGISTER'}

    def execute(self, context):
        context.object.data.wData.wType = 'NONE'        
        return {'FINISHED'}

class WEditPanel(bpy.types.Panel):
    """Creates a Panel in the data context of the properties editor"""
    bl_label = "wMesh data"
    bl_idname = "DATA_PT_Wlayout"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):
        return (context.object.type == 'MESH')

    def draw(self, context):
        lay_out = self.layout
        obj = context.object
        WType = obj.data.wData.wType

        if WType == 'NONE':
            lay_out.label(text = "This is regular Mesh")
        else:
            if WType == 'WBOX': draw_WBox_panel(self, context)
            if WType == 'WCAPSULE': draw_WCapsule_panel(self, context)
            if WType == 'WCONE': draw_WCone_panel(self, context)
            if WType == 'WPLANE': draw_wPlane_panel(self, context)
            if WType == 'WPYRAMID': draw_WPyramid_panel(self, context)
            if WType == 'WRING': draw_WRing_panel(self, context)
            if WType == 'WSCREW': draw_WScrew_panel(self, context)
            if WType == 'WSPHERE': draw_WSphere_panel(self, context)
            if WType == 'WSPIRAL': draw_WSpiral_panel(self, context)
            if WType == 'WTORUS': draw_WTorus_panel(self, context)
            if WType == 'WTUBE': draw_WTube_panel(self, context)

            lay_out.separator()
            lay_out.operator(operator="mesh.convert_w_mesh")
            lay_out.separator()

def load_w_icons():
    global w_icons
    w_icons = bpy.utils.previews.new()
    icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    
    # Загружаем файлы. Имена ключей будут соответствовать именам файлов
    # Например, к W_Box_64.png обратимся как w_icons["W_Box_64"]
    for entry in os.scandir(icons_dir):
        if entry.name.endswith(".png"):
            name = os.path.splitext(entry.name)[0]
            w_icons.load(name, entry.path, 'IMAGE')

def unload_w_icons():
    global w_icons
    bpy.utils.previews.remove(w_icons)

def register():
    load_w_icons()  # Загружаем иконки при включении аддона
    bpy.utils.register_class(wData)
    bpy.types.Mesh.wData = PointerProperty(type=wData)

    reg_wBox()
    reg_wCapsule()
    reg_wCone()
    reg_wPyramid()
    reg_wPlane()
    reg_wRing()
    reg_wScrew()
    reg_wSphere()
    reg_wSpiral()
    reg_wTorus()
    reg_wTube()

    bpy.utils.register_class(WAddMenu)
    bpy.types.VIEW3D_MT_add.prepend(draw_addMenu)
    bpy.utils.register_class(ConvertWMesh)
    bpy.utils.register_class(WEditPanel)
    
    print("Registered W_Mesh")

def unregister():
    unload_w_icons() # Очищаем память при выключении
    del bpy.types.Mesh.wData
    del bpy.types.Scene.refreshWMesh

    unreg_wBox()
    unreg_wCapsule()
    unreg_wCone()
    unreg_wPlane()
    unreg_wPyramid()
    unreg_wRing()
    unreg_wScrew()
    unreg_wSphere()
    unreg_wSpiral()
    unreg_wTorus()
    unreg_wTube()

    bpy.utils.unregister_class(WAddMenu)
    bpy.types.VIEW3D_MT_add.remove(draw_addMenu)
    bpy.utils.unregister_class(ConvertWMesh)
    bpy.utils.unregister_class(WEditPanel)
    
if __name__ == "__main__":
    register()
