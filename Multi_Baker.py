import bpy
import os

# Define a function to get the UV maps
def get_uv_maps(self, context):
    obj = context.object
    if obj and obj.type == 'MESH':
        return [(uv.name, uv.name, "") for uv in obj.data.uv_layers]
    return []

# Define a property group to hold the UV map selection and the Smart UV map toggle
class MyProperties(bpy.types.PropertyGroup):
    uv_map: bpy.props.EnumProperty(
        name="UV Map",
        description="Choose a UV map",
        items=get_uv_maps
    )
    smart_uv: bpy.props.BoolProperty(
        name="Smart UV Map",
        description="Enable Smart UV Mapping",
        default=False  # Set to untoggled by default
    )
    bake_type: bpy.props.EnumProperty(
        name="Type",
        description="Choose the type of bake",
        items=[
            ('DIFFUSE', 'Diffuse', ''),
            ('METALLIC', 'Metalness', ''),
            ('ROUGHNESS', 'Roughness', ''),
            ('EMIT', 'Emit', ''),
            ('POSITION', 'Position', ''),
            ('NORMAL', 'Normal', ''),
            ('UV', 'UV', ''),
            ('AO', 'Ambient Occlusion', ''),
            ('ENVIRONMENT', 'Environment', ''),
            ('GLOSSY', 'Glossy', ''),
            ('TRANSMISSION', 'Transmission', '')
        ]
    )
    image: bpy.props.PointerProperty(
        name="Image",
        type=bpy.types.Image,
        description="Image to be used for baking"
    )
    bake_done: bpy.props.BoolProperty(
        name="Bake Done",
        description="Indicates if the baking process has been completed",
        default=False
    )

# Define an operator to apply Smart UV mapping
class ApplySmartUVOperator(bpy.types.Operator):
    bl_idname = "object.apply_smart_uv"
    bl_label = "Apply Smart UV Map"

    def execute(self, context):
        obj = context.object
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project()
        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}

# Define an operator to bake the texture
class BakeTextureOperator(bpy.types.Operator):
    bl_idname = "object.bake_texture"
    bl_label = "Bake Texture"

    def execute(self, context):
        obj = context.object
        scene = context.scene
        mytool = scene.my_tool

        # Ensure the object is selected
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj

        # Apply UV map and set up nodes for each material
        uv_map_name = mytool.uv_map if not mytool.smart_uv else "Smart UV Project"
        if mytool.smart_uv:
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.smart_project()
            bpy.ops.object.mode_set(mode='OBJECT')

        for mat in obj.data.materials:
            if mat.use_nodes:
                nodes = mat.node_tree.nodes
                links = mat.node_tree.links

                # Clear selection of all nodes
                for node in nodes:
                    node.select = False

                # Create or get UV Map node
                uv_node = nodes.get("UV Map")
                if not uv_node:
                    uv_node = nodes.new(type='ShaderNodeUVMap')
                    uv_node.uv_map = uv_map_name

                # Create or get Image Texture node
                image_node = nodes.get("Image Texture")
                if not image_node:
                    image_node = nodes.new(type='ShaderNodeTexImage')
                    image_node.image = mytool.image

                # Link UV Map node to Image Texture node
                if not any(link.to_node == image_node and link.from_node == uv_node for link in links):
                    links.new(uv_node.outputs['UV'], image_node.inputs['Vector'])

                # Select the Image Texture node
                image_node.select = True
                nodes.active = image_node

        # Set bake type
        bpy.context.scene.cycles.bake_type = mytool.bake_type

        # Toggle off Direct and Indirect light influence
        bpy.context.scene.render.bake.use_pass_direct = False
        bpy.context.scene.render.bake.use_pass_indirect = False

        # Perform baking
        bpy.ops.object.bake(type=mytool.bake_type)

        # Mark bake as done
        mytool.bake_done = True

        return {'FINISHED'}

# Define an operator to save the baked image
class SaveBakedImageOperator(bpy.types.Operator):
    bl_idname = "object.save_baked_image"
    bl_label = "Save Image"

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        mytool = context.scene.my_tool
        if mytool.image:
            # Save the image directly
            mytool.image.filepath_raw = self.filepath
            mytool.image.file_format = 'PNG'
            mytool.image.save()

            self.report({'INFO'}, f"Image saved at: {self.filepath}")
        return {'FINISHED'}

    def invoke(self, context, event):
        mytool = context.scene.my_tool
        obj_name = context.object.name
        bake_method = mytool.bake_type.capitalize()  # Replace with the actual bake method if needed

        # Set the default file path
        self.filepath = os.path.join(bpy.path.abspath("//"), f"{obj_name}_{bake_method}.png")

        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

# Define a panel to display the dropdown menu and the checkbox
class MyAddonPanel(bpy.types.Panel):
    bl_label = "Multi Baker"
    bl_idname = "OBJECT_PT_texture_baking_helper"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Multi Baker'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool
        obj = context.object####

        if bpy.context.selected_objects:
            layout.label(text="Active object is: " + obj.name, icon='CUBE')
        else:
            layout.label(text="Select an object to set it up")
        
        layout.prop(mytool, "smart_uv")

        if mytool.smart_uv:
            layout.operator("object.apply_smart_uv")
        else:
            layout.prop(mytool, "uv_map")

        layout.prop(mytool, "bake_type")

        if mytool.bake_done:
            row = layout.row(align=True)
            layout.template_ID_preview(mytool, "image", new="image.new", open="image.open")
            layout.operator("object.save_baked_image")
        else:
            row = layout.row(align=True)
            row.template_ID(mytool, "image", new="image.new", open="image.open")

        layout.operator("object.bake_texture")

# Register the classes
def register():
    bpy.utils.register_class(MyProperties)
    bpy.utils.register_class(ApplySmartUVOperator)
    bpy.utils.register_class(BakeTextureOperator)
    bpy.utils.register_class(SaveBakedImageOperator)
    bpy.utils.register_class(MyAddonPanel)
    bpy.types.Scene.my_tool = bpy.props.PointerProperty(type=MyProperties)

def unregister():
    bpy.utils.unregister_class(MyProperties)
    bpy.utils.unregister_class(ApplySmartUVOperator)
    bpy.utils.unregister_class(BakeTextureOperator)
    bpy.utils.unregister_class(SaveBakedImageOperator)
    bpy.utils.unregister_class(MyAddonPanel)
    del bpy.types.Scene.my_tool

if __name__ == "__main__":
    register()