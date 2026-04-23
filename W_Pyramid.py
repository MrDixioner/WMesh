import bpy
import math
from bpy.props import FloatProperty, IntProperty
from mathutils import Vector
from .genFunctions import bridgeLoops, create_mesh_object

def geoGen_WPyramid(sides, steps, step_h, step_w, diameter):
    if sides < 3: sides = 3
    if steps < 1: steps = 1

    verts = []
    faces = []
    loops = []

    angle_step = (math.pi * 2) / sides
    current_z = 0.0
    current_dia = diameter 

    for i in range(steps):
        # 1. Bottom ring of the step
        loop_bottom = []
        for s in range(sides):
            # Divide the diameter by 2 for trigonometry only
            x = math.cos(s * angle_step) * (current_dia / 2)
            y = math.sin(s * angle_step) * (current_dia / 2)
            loop_bottom.append(len(verts))
            verts.append(Vector((x, y, current_z)))
        loops.append(loop_bottom)

        # 2. The top ring of the same step
        current_z += step_h
        loop_top = []
        for s in range(sides):
            x = math.cos(s * angle_step) * (current_dia / 2)
            y = math.sin(s * angle_step) * (current_dia / 2)
            loop_top.append(len(verts))
            verts.append(Vector((x, y, current_z)))
        loops.append(loop_top)

        # 3. Reduce the diameter for the next step
        # The diameter is reduced by two step widths (on both sides)
        current_dia -= (step_w * 2)
        if current_dia < 0: current_dia = 0

    # Create faces
    faces.append(list(reversed(loops[0]))) # Bottom
    
    for i in range(len(loops) - 1):
        # Connecting the rings (vertical walls and horizontal platforms)
        faces.extend(bridgeLoops(loops[i], loops[i+1], True))
        
    faces.append(loops[-1]) # Top cap

    return verts, [], faces

def update_WPyramid(wData):
    # Protection: the width of a step cannot be more than half the diameter / number of steps
    max_w = (wData.siz_y / 2) / wData.seg_2 if wData.seg_2 > 0 else 0
    safe_step_w = min(wData.siz_x, max_w)
    
    return geoGen_WPyramid(
        sides=wData.seg_1, 
        steps=wData.seg_2, 
        step_h=wData.siz_z, 
        step_w=safe_step_w, 
        diameter=wData.siz_y
    )

class Make_WPyramid(bpy.types.Operator):
    """Create Step Pyramid"""
    bl_idname = "mesh.make_wpyramid"
    bl_label = "wPyramid"
    bl_options = {'UNDO', 'REGISTER'}

    sides: IntProperty(name="Sides", default=4, min=3)
    steps: IntProperty(name="Steps", default=5, min=1)
    step_h: FloatProperty(name="Step Height", default=.05, min=0.0)
    step_w: FloatProperty(name="Step Width", default=.05, min=0.0)
    diameter: FloatProperty(name="Diameter", default=1.0, min=0.01)

    def execute(self, context):
        # Calculating the safe width for the first creation
        safe_w = min(self.step_w, (self.diameter / 2) / self.steps)
        
        verts, edges, faces = geoGen_WPyramid(
            self.sides, self.steps, self.step_h, safe_w, self.diameter
        )
        create_mesh_object(context, verts, edges, faces, "wPyramid")
        
        wD = context.object.data.wData
        wD.seg_1 = self.sides
        wD.seg_2 = self.steps
        wD.siz_z = self.step_h # Height
        wD.siz_x = self.step_w # Width
        wD.siz_y = self.diameter # Base diameter
        wD.wType = 'WPYRAMID'
        return {'FINISHED'}

def draw_WPyramid_panel(self, context):
    lay_out = self.layout

    from . import w_icons

    lay_out.use_property_split = True
    wD = context.object.data.wData
    
    if w_icons and "W_Pyramid_64" in w_icons:
        icon_id = w_icons["W_Pyramid_64"].icon_id
        lay_out.label(text="Type: wPyramid", icon_value=icon_id)
    else:
        lay_out.label(text="Type: wPyramid", icon='OUTLINER_DATA_MESH')
    
    col = lay_out.column(align=True)
    col.prop(wD, "siz_y", text="Diameter")
    col.prop(wD, "seg_1", text="Sides")
    
    col = lay_out.column(align=True)
    col.prop(wD, "seg_2", text="Steps Count")
    col.prop(wD, "siz_z", text="Step Height")
    col.prop(wD, "siz_x", text="Step Width")

def reg_wPyramid():
    bpy.utils.register_class(Make_WPyramid)

def unreg_wPyramid():
    bpy.utils.unregister_class(Make_WPyramid)
