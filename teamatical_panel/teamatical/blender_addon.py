'''Teamatical Addon'''

import os
import bpy
import addon_utils
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator


ADDON_NAME = 'Teamatical Tools'
DEFAULT_SHADOWS_NAME = 'shadows'
DEFAULT_MATERIAL_NAME = 'ProductMaterial'
DEFAULT_MESH_NAME = 'TeamaticalProduct'
LIGHTING_NAME = 'LightningScene.blend'
blend_file_name = 'sadsad'


def set_object_mode():
    '''Set object mode'''
    print('----- set object mode')
    if bpy.ops.object.mode_set.poll():
        bpy.ops.object.mode_set(mode = 'OBJECT')


def get_active_object(self, context):
    '''Get active object'''
    print('--- get active object')
    set_object_mode()
    obj = context.active_object

    if (obj is None) or (obj.type != 'MESH'):
        self.report({'WARNING'}, 'Select mesh object first, please')
        obj = None
    elif obj.name != DEFAULT_MESH_NAME:
        obj.name = DEFAULT_MESH_NAME

    return obj


def get_shadows():
    '''Get shadows image'''
    print('--- get shadows image')
    shadows_img = None
    i = bpy.data.images.find(DEFAULT_SHADOWS_NAME)
    if i == -1:
        shadows_img = None
    else:
        shadows_img = bpy.data.images[i]
    print('----- shadows_image =', shadows_img)
    return shadows_img


def get_material():
    '''Get product material'''
    print('--- get material')
    mat = None
    i = bpy.data.materials.find(DEFAULT_MATERIAL_NAME)
    if i == -1:
        mat = None
    else:
        mat = bpy.data.materials[i]
    print('----- product material =', mat)
    return mat


def get_file_path(self, context):
    '''Get BLEND file path'''
    print('--- get file path')
    fname = os.path.splitext(bpy.data.filepath)[0]
    if fname == '':
        self.report({'ERROR'}, 'You must save BLEND file first')
    return fname


class CleanScene(bpy.types.Operator):
    '''Remove unnecessary objects in the scene'''
    bl_idname = 'teamatical.clean_scene'
    bl_label = 'Clean scene'
    bl_description = 'Remove unnecessary objects in the scene'
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        print('--- clean scene')
        set_object_mode()
        for obj in bpy.data.objects:
            obj.select_set(True)
            bpy.data.objects.remove(obj, do_unlink = True)
        self.report({'INFO'}, 'Scene cleaned')
        context.scene.tm_tool.last_operator = self.bl_idname
        return {'FINISHED'}


class ImportOBJ(bpy.types.Operator):
    '''Import OBJ file'''
    bl_idname = 'teamatical.import_obj'
    bl_label = 'Import OBJ'
    bl_description = 'Import OBJ file'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print('********1')
        print('--- import obj')
        bpy.ops.wm.obj_import('INVOKE_AREA')
        self.report({'INFO'}, 'OBJ imported')
        context.scene.tm_tool.last_operator = self.bl_idname
        return {'FINISHED'}

'''
class ImportOBJ(bpy.types.Operator, ImportHelper):
    # NEW VERSION for Blender 4
    bl_idname = 'teamatical.import_obj'
    bl_label = 'Import OBJ'
    bl_description = 'Import OBJ file'
    bl_options = {'REGISTER', 'UNDO'}

    filter_glob: bpy.props.StringProperty(default="*.obj", options={'HIDDEN'})

    def execute(self, context):
        print("--- test1")
        print("--- selected file:", self.filepath)
        bpy.ops.wm.obj_import('EXEC_DEFAULT', filepath=self.filepath)
        self.report({'INFO'}, 'OBJ imported')
        context.scene.tm_tool.last_operator = self.bl_idname
        return {'FINISHED'}
'''

class ResetObjectPosition(bpy.types.Operator):
    '''Set mesh coordinates to (0, 0, 0)'''
    bl_idname = 'teamatical.reset_obj_position'
    bl_label = 'Reset position'
    bl_description = 'Set mesh coordinates to (0, 0, 0)'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print('--- reset position')
        obj = get_active_object(self, context)
        if not obj:
            return {'CANCELLED'}
        bpy.ops.object.origin_set(type = 'ORIGIN_GEOMETRY', center = 'BOUNDS')
        obj.location.x = obj.location.y = obj.location.z = 0

        #bpy.ops.screen.area_split(direction = 'VERTICAL', factor = 0.5)
        #bpy.context.area.ui_type = 'UV'
        #bpy.ops.object.mode_set(mode = 'EDIT')

        self.report({'INFO'}, 'OBJ position is (0, 0, 0)')
        context.scene.tm_tool.last_operator = self.bl_idname
        return {'FINISHED'}


class MoveVertexesToGroupsByMaterial(bpy.types.Operator):
    '''Move vertexes to groups by material'''
    bl_idname = 'teamatical.move_vertices_to_groups'
    bl_label = 'Setup vertexes groups'
    bl_description = 'Move vertexes to groups by material'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print('--- setup vertexes groups')
        obj = get_active_object(self, context)
        if not obj:
            return {'CANCELLED'}

        if len(obj.material_slots) == 0:
            self.report({'ERROR'}, 'There is no material slots')
            return {'CANCELLED'}

        for index, slot in enumerate(obj.material_slots):
            # select the verts from faces with material index
            if not slot.material:
                # empty slot
                continue
            verts = [v for f in obj.data.polygons
                    if f.material_index == index for v in f.vertices]
            if len(verts):
                vert_groups = obj.vertex_groups.get(slot.material.name)
                if vert_groups is None:
                    vert_groups = obj.vertex_groups.new(name = slot.material.name)
                vert_groups.add(verts, 1.0, 'ADD')
        self.report({'INFO'}, 'Vertexes groups created')
        context.scene.tm_tool.last_operator = self.bl_idname
        return {'FINISHED'}


class MoveUVs(bpy.types.Operator):
    '''Move the inside of the fabric UVs'''
    bl_idname = 'teamatical.move_uvs'
    bl_label = 'Move UVs'
    bl_description = 'Move the inside of the fabric UVs'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print('--- move background UVs')

        #bpy.ops.wm.call_panel(name = 'TEAMATICAL_PT_TOOLS', keep_open = True)

        sandwich = context.scene.tm_tool.sandwich_selector
        print('----- sandwich selector is', sandwich)
        obj = get_active_object(self, context)
        if not obj:
            return {'CANCELLED'}


        # select back side of the fabric by material name
        # cool python expression
        slots = [id for id, mat in enumerate(obj.data.materials) if "_BACK_" in mat.name]
        if len(slots) == 0:
            self.report({'ERROR'}, 'There is no _BACK_ material')
            return {'CANCELLED'}

        uv_data = obj.data.uv_layers.active.data

        for face in obj.data.polygons:
            for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                uv_data[loop_idx].uv.x *= 0.5
                if face.material_index in slots:
                    if sandwich is False:
                        # UVs - move and scale inside part
                        uv_data[loop_idx].uv.x += 0.5
                    else:
                        # UVs - scale, mirror and move inside part
                        uv_data[loop_idx].uv.x *= -1
                        uv_data[loop_idx].uv.x += 1
        self.report({'INFO'}, 'UVs moved')
        context.scene.tm_tool.last_operator = self.bl_idname
        return {'FINISHED'}

    # old version by Ivan
    # def execute(self, context):
    #     obj = context.active_object
    #     vMax = obj.data.vertices[0].co
    #     outsideMaterialIdx = -1
    #     print(vMax)
    #     print(obj.data.vertices)
    #     verts = obj.data.vertices
    #     for face in obj.data.polygons:
    #         for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
    #             vert = verts[vert_idx].co
    #             if vMax<vert:
    #                 vMax = vert
    #                 outsideMaterialIdx = face.material_index
    #             obj.data.uv_layers.active.data[loop_idx].uv.x *= 0.5
    #
    #     print('outsideMaterialIdx: ', outsideMaterialIdx)
    #     print('Max Vertex: ', vMax)
    #
    #     for face in obj.data.polygons:
    #         for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
    #             if face.material_index != outsideMaterialIdx:
    #                 obj.data.uv_layers.active.data[loop_idx].uv.x += 0.5
    #     return {'FINISHED'}


class CreateShadowsImage(bpy.types.Operator):
    '''Create an empty image for baking shadows'''
    bl_idname = 'teamatical.create_shadows_image'
    bl_label = 'Create shadows image'
    bl_description = 'Create an empty image for baking shadows'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print('--- create shadows image')
        if not DEFAULT_SHADOWS_NAME in bpy.data.images:
            bpy.ops.image.new(name = DEFAULT_SHADOWS_NAME,
                              width = 1024 * 4,
                              height = 1024 * 2,
                              color = (1.0, 1.0, 1.0, 1.0),
                              alpha = True,
                              float = False
                             )
        else: self.report({'WARNING'}, 'Shadows image already exists')

        shadows_image = get_shadows()
        for area in bpy.context.screen.areas:
            if area.type == 'IMAGE_EDITOR':
                print('----- setting active shadows image')
                area.spaces.active.image = shadows_image
        self.report({'INFO'}, 'Shadows image created')
        context.scene.tm_tool.last_operator = self.bl_idname
        return {'FINISHED'}


class CreateMaterial(bpy.types.Operator):
    '''Combine all materials into one'''
    bl_idname = 'teamatical.create_material'
    bl_label = 'Create material'
    bl_description = 'Combine all materials into one'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print('--- create material')
        obj = get_active_object(self, context)
        if not obj:
            return {'CANCELLED'}

        shadows_image = get_shadows()
        if not shadows_image:
            self.report({'ERROR'}, 'You must create a shadows image first')
            return {'CANCELLED'}

        bpy.context.scene.render.engine = 'CYCLES'
        bpy.context.scene.cycles.device = 'GPU'
        obj.data.materials.clear()
        mat = bpy.data.materials.new(name = DEFAULT_MATERIAL_NAME)
        mat.use_nodes = True
        mat_nodes = mat.node_tree.nodes

        tex_node = mat_nodes.new(type = 'ShaderNodeTexImage')
        tex_node.location = -300, 300
        tex_node.image = shadows_image

        # for mat in bpy.data.materials:
        #     print(mat)

        obj.data.materials.append(mat)

        # for mat in obj.data.materials:
        #     print('-----materials in object', mat)

        for material in bpy.data.materials:
            if material.users == 0 and material != mat:
                bpy.data.materials.remove(material)

        index = obj.data.materials.find(mat.name)

        for face in obj.data.polygons:
            for vert_idx, loop_idx in zip(face.vertices, face.loop_indices):
                face.material_index = index
        self.report({'INFO'}, 'Product material created')
        context.scene.tm_tool.last_operator = self.bl_idname
        return {'FINISHED'}


class SetupScene(bpy.types.Operator):
    '''Load BLEND file with lighting'''
    bl_idname = 'teamatical.setup_scene'
    bl_label = 'Setup scene'
    bl_description = 'Load BLEND file with lighting'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print('--- setup lighting scene')
        addon_file = os.path.realpath(__file__)
        addon_dir = os.path.dirname(addon_file)
        lighting_file = addon_dir +'\\' + LIGHTING_NAME
        print('addon_dir = ', addon_dir)
        print('lighting_file = ', lighting_file)

        try:
            with bpy.data.libraries.load(lighting_file) as (data_from, data_to):
                #data_to.objects = [name for name in data_from.objects if True]
                data_to.objects = [name for name in data_from.objects]
        except:
            self.report({'ERROR'}, 'Something went wrong. Can not load lighting file')
            return {'CANCELLED'}
        else:
            for obj in data_to.objects:
                if obj is not None:
                    bpy.context.collection.objects.link(obj)
            self.report({'INFO'}, 'Lighting created')

        context.scene.tm_tool.last_operator = self.bl_idname
        return {'FINISHED'}


class SaveBlendFile(bpy.types.Operator):
    '''Save BLEND file'''
    bl_idname = 'teamatical.save_blend_file'
    bl_label = 'Save BLEND file'
    bl_description = 'Save BLEND file'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print('--- save BLEND file')
        #if not bpy.data.filepath:
        bpy.ops.wm.save_as_mainfile('INVOKE_AREA')
        self.report({'INFO'}, 'BLEND file saved')
        context.scene.tm_tool.last_operator = self.bl_idname
        return {'FINISHED'}


class BakeAndSaveShadows(bpy.types.Operator):
    '''Bake shadows and save the image'''
    bl_idname = 'teamatical.bake_and_save_shadows'
    bl_label = 'Bake and save shadows'
    bl_description = 'Bake shadows and save the image'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print('--- bake and save shadows')
        obj = get_active_object(self, context)
        if not obj:
            return {'CANCELLED'}
        obj.select_set(True)

        shadows_image = get_shadows()
        if not shadows_image:
            self.report({'ERROR'}, 'You must create a shadows image first')
            return {'CANCELLED'}

        product_material = get_material()
        if not product_material:
            self.report({'ERROR'}, 'You must create a material first')
            return {'CANCELLED'}

        file_name = get_file_path(self, context)
        if file_name == '':
            return {'CANCELLED'}

        self.report({'INFO'}, 'Baking shadows...')
        # baking settings
        cycls = bpy.data.scenes['Scene'].cycles
        cycls.device = 'GPU'
        cycls.samples = context.scene.tm_tool.baking_sampling
        #scn.cycles.aa_samples = 512 # default = 128
        bakk = bpy.data.scenes['Scene'].render.bake
        bakk.use_pass_glossy = False
        bakk.use_pass_transmission = False
        bakk.margin = context.scene.tm_tool.baking_margins
        #bakk.margin_type = 'EXTEND'

        # bake shadows
        shadows_image.source = 'GENERATED'
        bpy.ops.object.bake(type = 'COMBINED')
        # save shadows image
        shadows_image.file_format = 'PNG'
        shadows_image.filepath_raw = file_name + '.shadows.png'
        shadows_image.save()
        self.report({'INFO'}, 'Shadows image saved')
        context.scene.tm_tool.last_operator = self.bl_idname
        return {'FINISHED'}


class CrunchOBJ(bpy.types.Operator):
    '''Crunch OBJ'''
    bl_idname = 'teamatical.crunch_obj'
    bl_label = 'Crunch OBJ'
    bl_description = 'Crunch OBJ with Polygon Cruncher'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print('--- crunch OBJ')
        self.report({'INFO'}, 'OBJ has been crunched')
        context.scene.tm_tool.last_operator = self.bl_idname
        return {'FINISHED'}


class SaveOBJ(bpy.types.Operator):
    '''Save OBJ file'''
    bl_idname = 'teamatical.save_obj'
    bl_label = 'Save OBJ'
    bl_description = 'Save OBJ file (Y-forward, Z-up)'
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        print('--- save OBJ')
        file_name = get_file_path(self, context)
        if file_name == '':
            return {'CANCELLED'}

        file_name += '.obj'
        bpy.ops.wm.obj_export(filepath=file_name,
                            check_existing=True,
                            filter_blender=False,
                            filter_backup=False,
                            filter_image=False,
                            filter_movie=False,
                            filter_python=False,
                            filter_font=False,
                            filter_sound=False,
                            filter_text=False,
                            filter_archive=False,
                            filter_btx=False,
                            filter_collada=False,
                            filter_alembic=False,
                            filter_usd=False,
                            filter_obj=False,
                            filter_volume=False,
                            filter_folder=True,
                            filter_blenlib=False,
                            filemode=8,
                            display_type='DEFAULT',
                            sort_method='DEFAULT',
                            forward_axis='Y',
                            up_axis='Z',
                            filter_glob='*.obj',
                            export_selected_objects=True,
                            export_animation=False,
                            apply_modifiers=True,
                            export_uv=True,
                            export_normals=True,
                            export_colors=False,
                            export_materials=True,
                            export_pbr_extensions=False,
                            global_scale=1.0,
                            export_eval_mode='DAG_EVAL_VIEWPORT',
                            path_mode='AUTO',
                            export_triangulated_mesh=False,
                            export_curves_as_nurbs=False,
                            export_object_groups=False,
                            export_material_groups=False,
                            export_vertex_groups=False,
                            export_smooth_groups=False,
                            smooth_group_bitflags=False
                            )
        self.report({'INFO'}, 'OBJ file saved')
        context.scene.tm_tool.last_operator = self.bl_idname
        return {'FINISHED'}
