bl_info = {
    "name": "Maya based pie selection menu",
    "author": "Rév",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Right Click",
    "description": "Pie menu for switching between edit modes loosely based on Maya's behavior. Please remove the default shortcut for VIEW3D_MT_edit_mesh_context_menu and VIEW3D_MT_object_context_menu, which is the right click press.",
    "category": "3D View",
}

import bpy
from bpy.types import Menu, Operator
from bpy.props import StringProperty

def set_edit_mode(context, mode):
    if context.active_object:
        bpy.ops.object.mode_set(mode='EDIT')
        context.tool_settings.mesh_select_mode = (
            mode == 'VERT',
            mode == 'EDGE',
            mode == 'FACE'
        )

def has_mesh_object(context):
    return any(obj for obj in context.scene.objects if obj.type == 'MESH')

class VIEW3D_OT_edit_mode_set(Operator):
    bl_idname = "view3d.edit_mode_set"
    bl_label = "Set Edit Mode"
    bl_options = {'REGISTER', 'UNDO'}
    
    mode: StringProperty()
    
    @classmethod
    def description(cls, context, properties):
        if properties.mode == 'VERT':
            return "Opens the vertex mode"
        elif properties.mode == 'EDGE':
            return "Opens the edge mode"
        elif properties.mode == 'FACE':
            return "Opens the face mode"
        elif properties.mode == 'OBJECT':
            return "Opens object mode"
        return ""
    
    def execute(self, context):
        if self.mode == 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        else:
            set_edit_mode(context, self.mode)
        return {'FINISHED'}

class VIEW3D_OT_context_menu_caller(Operator):
    bl_idname = "view3d.context_menu_caller"
    bl_label = "Call Context Menu"
    bl_options = {'REGISTER'}
    bl_description = "Opens the context sensitive right click menu"
    
    def execute(self, context):
        # Close the pie menu
        bpy.ops.wm.tool_set_by_id(name="builtin.select")
        
        # Call appropriate context menu
        if context.mode == 'EDIT_MESH':
            bpy.ops.wm.call_menu(name="VIEW3D_MT_edit_mesh_context_menu")
        else:
            bpy.ops.wm.call_menu(name="VIEW3D_MT_object_context_menu")
        return {'FINISHED'}

class VIEW3D_OT_close_pie_menu(Operator):
    bl_idname = "view3d.close_pie_menu"
    bl_label = "Close Pie Menu"
    bl_options = {'REGISTER'}
    bl_description = "Close this pie menu"
    
    def execute(self, context):
        bpy.ops.wm.tool_set_by_id(name="builtin.select")
        return {'FINISHED'}

class VIEW3D_MT_mode_pie(Menu):
    bl_idname = "VIEW3D_MT_mode_pie"
    bl_label = "Select Mode"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        
        # Check if there's a mesh object in the scene
        if has_mesh_object(context):
            # Left
            op = pie.operator("view3d.edit_mode_set", text="Vertex", icon='VERTEXSEL')
            op.mode = 'VERT'
            #Right
            pie.operator("view3d.close_pie_menu", text="Close", icon='PANEL_CLOSE')
            #Bottom
            box = pie.box()
            col = box.column()
            
            # Dynamic context menu based on mode
            if context.mode == 'EDIT_MESH':
                col.operator("view3d.context_menu_caller", text="Edit Mode Context Menu")
            else:
                col.operator("view3d.context_menu_caller", text="Object Mode Context Menu")
              
            #Top
            op = pie.operator("view3d.edit_mode_set", text="Object Mode", icon='OBJECT_DATA')
            op.mode = 'OBJECT'
            # Top-Left
            op = pie.operator("view3d.edit_mode_set", text="Edge", icon='EDGESEL')
            op.mode = 'EDGE'
            #Top-Right
            pie.separator()
            # Bottom-Left
            op = pie.operator("view3d.edit_mode_set", text="Face", icon='FACESEL')
            op.mode = 'FACE'
            #  Bottom-Right
            pie.separator()
        else:
            # Simplified menu when no mesh objects present
            # Left
            pie.separator()
            # Right
            pie.operator("view3d.close_pie_menu", text="Close", icon='PANEL_CLOSE')
            # Bottom
            box = pie.box()
            col = box.column()
            col.operator("view3d.context_menu_caller", text="Context Menu")
            # Top
            pie.separator()
            # Top-Left
            pie.separator()
            # Top-Right
            pie.separator()
            # Bottom-Left
            pie.separator()
            # Bottom-Right
            pie.separator()

addon_keymaps = []

def register():
    bpy.utils.register_class(VIEW3D_OT_edit_mode_set)
    bpy.utils.register_class(VIEW3D_OT_context_menu_caller)
    bpy.utils.register_class(VIEW3D_OT_close_pie_menu)
    bpy.utils.register_class(VIEW3D_MT_mode_pie)
    
    # Adding the keymap
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new('wm.call_menu_pie', 'RIGHTMOUSE', 'PRESS')
        kmi.properties.name = "VIEW3D_MT_mode_pie"
        kmi.active = True
        addon_keymaps.append((km, kmi))

def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    
    bpy.utils.unregister_class(VIEW3D_MT_mode_pie)
    bpy.utils.unregister_class(VIEW3D_OT_close_pie_menu)
    bpy.utils.unregister_class(VIEW3D_OT_context_menu_caller)
    bpy.utils.unregister_class(VIEW3D_OT_edit_mode_set)

if __name__ == "__main__":
    register()