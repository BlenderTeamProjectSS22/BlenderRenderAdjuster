import bpy
from abc import ABC, abstractmethod

class CompositeNodes:
    def __init__(self):
        bpy.context.scene.use_nodes = True
        self.tree = bpy.context.scene.node_tree

        for node in self.tree.nodes:
            self.tree.nodes.remove(node)

        self.rlayer = self.tree.nodes.new("CompositorNodeRLayers")   
        self.output = self.tree.nodes.new("CompositorNodeComposite")
        self.glare  = self.tree.nodes.new("CompositorNodeGlare")
        self.tree.links.new(self.rlayer.outputs["Image"], self.output.inputs["Image"])
        
        # Glare properties
        self.glare.glare_type = 'FOG_GLOW'
        self.glare.threshold = 0.5
        self.glare.size = 10
    
    def set_glow(self, is_glowing: bool):
        if is_glowing:
            self.tree.links.new(self.rlayer.outputs["Image"], self.glare.inputs["Image"])
            self.tree.links.new(self.glare.outputs["Image"], self.output.inputs["Image"])
        else:
            self.tree.links.new(self.rlayer.outputs["Image"], self.output.inputs["Image"])

class MaterialController:

    def __init__(self):
        self.material    = self.init_material()
        nodes            = self.material.node_tree.nodes
        self.bsdf        = nodes.get("Principled BSDF")
        self.noise       = nodes.new(type="ShaderNodeTexNoise")
        self.bump        = nodes.new(type="ShaderNodeBump")
        self.color       = self.bsdf.inputs["Base Color"].default_value
        self.metallic    = 0
        self.roughness   = 0.5
        self.tranmission = 0
        self.emissive    = False
        self.strength    = 1
        self.compositing = CompositeNodes()
        
    
    def init_material(self) -> bpy.types.Material:
    
        # Create a simple BSDF only material
        mat  = bpy.data.materials.new("Program Material")
        mat.use_nodes = True
        tree = mat.node_tree
        for n in tree.nodes:
            tree.nodes.remove(n)
        bsdf = tree.nodes.new("ShaderNodeBsdfPrincipled")
        mat_output = tree.nodes.new("ShaderNodeOutputMaterial")
        tree.links.new(bsdf.outputs["BSDF"], mat_output.inputs["Surface"])
        return mat
    
    def apply_material(self, obj):
        obj.active_material = self.material
        obj.active_material_index = 0
    
    def glass_material(self):
        self.set_emissive(False)
        self.set_transmission(1)
        self.set_roughness(0.05)
        self.set_metallic(0.1)
    
    def stone_material(self) -> bpy.types.Material:
        self.set_emissive(False)
        self.bump_material(5, 10)
    
    # Create and return a bump material to an object, with adjustable scale and detail level of the noise
    def bump_material(self, scale: float = 5, detail: float = 2) -> bpy.types.Material:

        links = self.material.node_tree.links
        self.noisel = links.new(self.noise.outputs["Color"], self.bump.inputs["Height"])
        self.bumpl  = links.new(self.bump.outputs["Normal"], self.bsdf.inputs["Normal"])
    
        # Set scale and detail properties of the noise
        self.noise.inputs["Scale"].default_value  = scale
        self.noise.inputs["Detail"].default_value = detail
    
    def disable_bump(self):
        links = self.material.node_tree.links
        print(str(self.bump.inputs["Height"].links))
        if self.bump.inputs["Height"].links:
            links.remove(self.noisel)
        if self.bsdf.inputs["Normal"].links:
            links.remove(self.bumpl)
    
    def set_color(self, color):
        self.color = color
        self.bsdf.inputs["Base Color"].default_value = color
    
    def set_roughness(self, roughness):
        self.roughness = roughness
        self.bsdf.inputs["Roughness"].default_value = roughness
    
    def set_metallic(self, metallic):
        self.metallic = metallic
        self.bsdf.inputs["Metallic"].default_value = metallic
    
    def set_transmission(self, transmission):
        self.transmission = transmission
        self.bsdf.inputs["Transmission"].default_value = transmission
    
    def set_emissive(self, emissive: bool, strength: float = 4, new_color = None):
        self.emissive = emissive
        if not emissive:
            self.bsdf.inputs["Emission Strength"].default_value = 0
        else:
            self.bsdf.inputs["Emission Strength"].default_value = strength
        
        if new_color is None:
            self.bsdf.inputs["Emission"].default_value = self.color
        else:
            self.bsdf.inputs["Emission"].default_value = new_color
    
    def change_preset(self, obj, material: bpy.types.Material, keep_color):
        
        obj.active_material = self.material
        obj.active_material_index = 0
        
        # Keep settings unaffected by the preset
        if keep_color:
            self.set_color(self.color)
        self.set_emissive(self.emissive)
        self.restore_previous(self.bsdf)

    def restore_previous(self, bsdf):
        self.bsdf = bsdf
        self.set_color(self.color)
        self.set_roughness(self.roughness)
        self.set_metallic(self.metallic)
        self.set_transmission(self.tranmission)
        self.set_emissive(self.emissive, self.strength)


"""
# Minimal example
obj = bpy.context.active_object
m = MaterialController(obj)
m.glass_material()
m.change_preset(obj)
"""