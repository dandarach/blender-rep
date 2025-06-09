'''Teamatical Addon'''

import bpy
from bpy.utils import (register_class, unregister_class)
from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )
from .teamatical.blender_addon import *


# ------------------------------------------------------------------------
#    Store properties in the active scene
# ------------------------------------------------------------------------

class TeamaticalPanelSettings(PropertyGroup):
    '''Teamatical Panel settings'''
    sandwich_selector:BoolProperty(
        name = 'Sandwich pattern',
        description = 'Sandwich pattern selector',
        default = False
        )

    baking_sampling:IntProperty(
        name = 'Sampling',
        description = 'Baking sampling',
        default = 1500,
        min = 1,
        max = 10000
        )

    baking_margins:IntProperty(
        name = 'Margins',
        description = 'Baking margins',
        default = 5,
        min = 0,
        max = 100
        )

    crunch_threshold:IntProperty(
        name = 'Threshold angle',
        description = 'Preserve normals threshold angle',
        default = 10,
        min = 0,
        max = 90
        )

    crunch_vertexes:IntProperty(
        name = 'Vertexes',
        description = 'Crunch vertexes',
        default = 70000,
        min = 1000,
        max = 100000
        )
        
    last_operator: bpy.props.StringProperty(default="")

    
# ------------------------------------------------------------------------
#    Teamatical Tools
# ------------------------------------------------------------------------

class TeamaticalPanel(bpy.types.Panel):
    '''Teamatical Panel Main Class'''
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    #bl_space_type  = 'PROPERTIES'
    bl_category = 'Teamatical'
    bl_idname = 'TEAMATICAL_PT_TOOLS'
    bl_label = 'Teamatical Tools'
    #use_pin = True
    #bl_context = 'objectmode'
    #bl_options = {'HIDE_HEADER'}
    #bl_order = 0
    #bl_description = 'sdafsdafsaddsfa'

    # this is needed to check if the operator can be executed/invoked
    # in the current context, useful for some but not for this example    
    # @classmethod
    # def poll(cls, context):
    #     #check the context here
    #     return context.object is not None

    def draw(self, context):
        layout = self.layout
        #scene = context.scene
        tmtool = context.scene.tm_tool
        tm = 'TEAMATICAL_OT_'
        
        #print(f"Current last_operator: {tmtool.last_operator}")

        def draw_operator(layout, operator_id, icon, align = None, is_enabled = True):
            row = layout.row(align = True) if align else layout.row()
            if align:
                row.alignment = align
            row.enabled = is_enabled;
            row.operator(tm + operator_id, icon = icon, depress = tmtool.last_operator == tm + operator_id)

        draw_operator(layout, 'clean_scene', 'TRASH')
        draw_operator(layout, 'import_obj', 'IMPORT')
        draw_operator(layout, 'reset_obj_position', 'EMPTY_DATA')
        draw_operator(layout, 'move_vertices_to_groups', 'MESH_DATA')        

        row = layout.row()
        split = row.split(factor = 0.5)
        left_col  = split.column(align = True)
        right_col = split.column(align = True)
        left_col.alignment  = 'RIGHT'
        right_col.alignment = 'CENTER'
        draw_operator(left_col, 'move_uvs', 'MESH_GRID', align='RIGHT')
        right_col.prop(tmtool, 'sandwich_selector', text = 'Sandwich')

        draw_operator(layout, 'create_shadows_image', 'FILE_IMAGE')
        draw_operator(layout, 'create_material', 'NODE_TEXTURE')
        draw_operator(layout, 'setup_scene', 'SHADING_TEXTURE')
        draw_operator(layout, 'save_blend_file', 'BLENDER')

        row = layout.split()
        row = layout.split()

        row = layout.row()
        split = row.split(factor = 0.6)
        left_col  = split.column(align = True)
        right_col = split.column(align = True)
        left_col.alignment  = 'RIGHT'
        right_col.alignment = 'CENTER'
        left_col.label(text = 'Sampling')
        right_col.prop(tmtool, 'baking_sampling', text = '')

        row = layout.row()
        split = row.split(factor = 0.6)
        left_col  = split.column(align = True)
        right_col = split.column(align = True)
        left_col.alignment  = 'RIGHT'
        right_col.alignment = 'CENTER'
        left_col.label(text = "Margins")
        right_col.prop(tmtool, 'baking_margins', text = '')

        draw_operator(layout, 'bake_and_save_shadows', 'RESTRICT_RENDER_OFF')
        draw_operator(layout, 'save_obj', 'MATCLOTH')

        row = layout.split()
        row = layout.split()

        row = layout.row()
        split = row.split(factor = 0.6)
        left_col  = split.column(align = True)
        right_col = split.column(align = True)
        left_col.alignment  = 'RIGHT'
        right_col.alignment = 'CENTER'
        left_col.label(text = "Threshold angle")
        right_col.prop(tmtool, 'crunch_threshold', text = '')
        row.enabled = False
        
        row = layout.row()
        split = row.split(factor = 0.6)
        left_col  = split.column(align = True)
        right_col = split.column(align = True)
        left_col.alignment  = 'RIGHT'
        right_col.alignment = 'CENTER'
        left_col.label(text = "Vertexes")
        right_col.prop(tmtool, 'crunch_vertexes', text = '')
        row.enabled = False

        draw_operator(layout, 'crunch_obj', 'SHADERFX', None, False)


# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------

#register, unregister = bpy.utils.register_classes_factory(classes)

classes = ( TeamaticalPanelSettings,
            TeamaticalPanel,
            CleanScene,
            ImportOBJ,
            ResetObjectPosition,
            MoveVertexesToGroupsByMaterial,
            MoveUVs,
            CreateShadowsImage,
            CreateMaterial,
            SetupScene,
            SaveBlendFile,
            BakeAndSaveShadows,
            CrunchOBJ,
            SaveOBJ
        )

def activate_addon_tab():
    #bpy.context.space_data.context = "Teamatical"
    #bpy.context.area.ui_type = "Teamatical"
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            with bpy.context.temp_override(area=area):
                bpy.ops.wm.context_toggle(data_path="space_data.show_region_ui")
            break


def register():
    '''Register classes'''
    print('=== Teamatical Addon ===')
    for clss in classes:
        register_class(clss)

    bpy.types.Scene.tm_tool = PointerProperty(type = TeamaticalPanelSettings)
    #activate_addon_tab()


def unregister():
    '''Unregister classes'''
    for clss in reversed(classes):
        unregister_class(clss)

    del bpy.types.Scene.tm_tool

if __name__ == '__main__':
    register()
