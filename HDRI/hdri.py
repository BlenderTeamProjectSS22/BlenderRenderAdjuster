import bpy
from math import radians

class Background:    
    def __init__(self, 
                 hdri_path: str):
        self.world = bpy.data.worlds["World"]
        self.world.use_nodes = True
        node_tree = self.world.node_tree
    
        environment_texture_node = node_tree.nodes.new(type="ShaderNodeTexEnvironment")
        
        texture_coordinates_node = node_tree.nodes.new(type="ShaderNodeTexCoord")
        mapping_node = node_tree.nodes.new(type="ShaderNodeMapping")
    
        node_tree.links.new(texture_coordinates_node.outputs["Generated"], mapping_node.inputs["Vector"])
        node_tree.links.new(mapping_node.outputs["Vector"], environment_texture_node.inputs["Vector"])
        node_tree.links.new(environment_texture_node.outputs["Color"], node_tree.nodes["Background"].inputs["Color"])
        
        self.environment_texture_node = environment_texture_node
        self.mapping_node = mapping_node
        
        self.set_image(hdri_path)
        
    def set_image(self, hdri_path: str) -> None:
        self.environment_texture_node.image = bpy.data.images.load(hdri_path)
        
    #degree, + -> image goes to the right
    def pan_horizontal(self, angle: float) -> None:
        self.mapping_node.inputs["Rotation"].default_value[2] += radians(angle)
        
    #rotates around global Y axis
    #can only be sensibly used when camera is on X axis
    #degree, + -> image goes down
    def pan_vertical(self, angle: float) -> None:
        self.mapping_node.inputs["Rotation"].default_value[1] += radians(angle)
