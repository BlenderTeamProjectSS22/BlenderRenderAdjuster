# author: Romain Carl
# created on: 03/06/2022
# edited by: Romain Carl

# description:
# A set of fuction that allows setting an HDRI image as world texture


import bpy
from math import radians
  
# initializes the world texture nodes necessary to load an HDRI image with set_background_image()
# only needs to be called once  
def initialize_world_texture() -> None:
    world = bpy.data.worlds["World"]
    world.use_nodes = True
    node_tree = world.node_tree
    
    environment_texture_node = node_tree.nodes.new(type="ShaderNodeTexEnvironment")
        
    texture_coordinates_node = node_tree.nodes.new(type="ShaderNodeTexCoord")
    mapping_node = node_tree.nodes.new(type="ShaderNodeMapping")
    
    node_tree.links.new(texture_coordinates_node.outputs["Generated"], mapping_node.inputs["Vector"])
    node_tree.links.new(mapping_node.outputs["Vector"], environment_texture_node.inputs["Vector"])
    
# sets the background image to image specified by hdri_path    
def set_background_image(hdri_path: str) -> None:
    world = bpy.data.worlds["World"]
    environment_texture_node = world.node_tree.nodes["Environment Texture"]
    background_node = world.node_tree.nodes["Background"]
    
    world.node_tree.links.new(environment_texture_node.outputs["Color"], background_node.inputs["Color"])
    environment_texture_node.image = bpy.data.images.load(hdri_path)

# removes the background image
def remove_background_image() -> None:
    world = bpy.data.worlds["World"]
    environment_texture_node = world.node_tree.nodes["Environment Texture"]
    link = environment_texture_node.outputs["Color"].links[0]
    world.node_tree.links.remove(link)
    
    image = world.node_tree.nodes["Environment Texture"].image
    image.user_clear()
    bpy.data.images.remove(image)

# rotates background image around global Z axis
# angle: degree, image moves to the right if positive
def pan_background_horizontal(angle: float) -> None:
    world = bpy.data.worlds["World"]
    mapping_node = world.node_tree.nodes["Mapping"]
    
    mapping_node.inputs["Rotation"].default_value[2] += radians(angle)
        
# rotates background image around global Y axis
# !!Caution: This function is only practical when camera is located on X axis
# otherwise rotation will result in askew background
# angle: degree, image moves down if positive
def pan_background_vertical(angle: float) -> None:
    world = bpy.data.worlds["World"]
    mapping_node = world.node_tree.nodes["Mapping"]
    
    mapping_node.inputs["Rotation"].default_value[1] += radians(angle)

# sets the brightness of background to new_strength
# new_strength: has to be a positiv value
# new_strength < 1: background will appear darker than normal
# new_strength > 1: background will appear brighter than normal
def set_background_brightness(new_strength : float) -> None:
    assert new_strength != None and new_strength > 0
    world = bpy.data.worlds["World"]
    self.world.node_tree.nodes["Background"].inputs[1].default_value = new_strength

