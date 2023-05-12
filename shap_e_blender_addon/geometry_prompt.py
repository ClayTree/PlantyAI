bl_info = {
    "name": "Prompt Geometry Addon",
    "author": "Clay",
    "version": (1, 0),
    "blender": (3, 5, 0),
    "location": "View3D > Sidebar > Geometry Prompt",
    "description": "Dynamically generate geometry based on user input",
    "warning": "",
    "doc_url": "",
    "category": "Geometry Prompt",
}

import bpy
import requests
import socket
import json


def send_prompt(prompt: str) -> str:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 8000))
    client_socket.send(prompt.encode())
    response = client_socket.recv(1024).decode()
    client_socket.close()
    return json.loads(response)["mesh_path"]


class PromptGeometryOperator(bpy.types.Operator):
    bl_idname = "prompt.geometry_operator"
    bl_label = "Generate Geometry"

    def execute(self, context):
        prompt_text = context.scene.prompt_addon_properties.prompt_text
        self.generate_geometry(prompt_text)
        return {'FINISHED'}

    @staticmethod
    def generate_geometry(prompt_text):
        # TODO: calling generate geometry interface
        mesh_path = send_prompt(prompt_text)

        # Import the PLY file in Blender as a mesh
        bpy.ops.import_mesh.ply(filepath=mesh_path)
        
        print("FINISH!")


def prompt_text_update(self, context):
    if context.event and context.event.type == 'RET':
        bpy.ops.prompt.geometry_operator()

class PromptGeometryNodesPanel(bpy.types.Panel):
    bl_label = "Geometry Prompt"

    bl_label = "Generate Mesh from Text"
    bl_idname = "OBJECT_PT_geometry_prompt_operator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Geometry Prompt"  # Changed the category to "Geometry Nodes" instead of "Tool"

    def draw(self, context):
        layout = self.layout
        props = context.scene.prompt_addon_properties

        layout.prop(props, "prompt_text", text="")
        layout.operator(PromptGeometryOperator.bl_idname, text="Generate Geometry!")

class PromptAddonProperties(bpy.types.PropertyGroup):
    prompt_text: bpy.props.StringProperty(
        name="",
        description="Enter the text for the prompt",
        default="",
        update=prompt_text_update
    )

def register():
    bpy.utils.register_class(PromptAddonProperties)
    bpy.utils.register_class(PromptGeometryNodesPanel)
    bpy.utils.register_class(PromptGeometryOperator)
    bpy.types.Scene.prompt_addon_properties = bpy.props.PointerProperty(type=PromptAddonProperties)

def unregister():
    bpy.utils.unregister_class(PromptGeometryOperator)
    bpy.utils.unregister_class(PromptGeometryNodesPanel)
    bpy.utils.unregister_class(PromptAddonProperties)
    del bpy.types.Scene.prompt_addon_properties

if __name__ == "__main__":
    register()
