import bpy
from abc import ABC, abstractmethod

class CompositeNodes:
    def __init__(self):
        bpy.context.scene.use_nodes = True
        self.tree = bpy.context.scene.node_tree
        self.glow = False

        for node in self.tree.nodes:
            self.tree.nodes.remove(node)

        self.rlayer = self.tree.nodes.new("CompositorNodeRLayers")   
        self.output = self.tree.nodes.new("CompositorNodeComposite")
        self.glare  = self.tree.nodes.new("CompositorNodeGlare")
        self.tree.links.new(self.rlayer.outputs["Image"], self.output.inputs["Image"])
        
        # Glare properties
        self.glare.glare_type = "FOG_GLOW"
        self.glare.threshold = 0.5
        self.glare.size = 10
    
    def set_glow(self, is_glowing: bool):
        if is_glowing:
            self.glow = True
            self.tree.links.new(self.rlayer.outputs["Image"], self.glare.inputs["Image"])
            self.tree.links.new(self.glare.outputs["Image"], self.output.inputs["Image"])
        else:
            self.glow = False
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
    
    # If a value is not set, it will not be changed
    def material_preset(self, **opts):
        self.set_metallic(opts.get("metallic", self.metallic))
        self.set_roughness(opts.get("roughness", self.roughness))
        self.set_transmission(opts.get("transmission", self.transmission))
        self.set_emissive(opts.get("emissive", self.emissive))
        self.set_emissive_strength(opts.get("strength", self.strength))
        self.compositing.set_glow(opts.get("glow", self.compositing.glow))
        if not opts.get("bump", False):
            self.disable_bump()
    
    def glass_material(self):
        self.material_preset(
            transmission = 1,
            roughness     = 0.05,
            emissive     = False)
    
    def stone_material(self):
        self.material_preset(
            transmission = 0,
            emissive     = False,
            roughness    = 0.5,
            metallic     = 0.2,
            glow         = False,
            bump         = True)
        self.bump_material(10, 5)
    
    def emissive_material(self):
        self.material_preset(
            emissive = True,
            strength = 1,
            transmission = 0.5,
            glow     = True)
    
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
    
    def set_emissive(self, emissive: bool, new_color = None):
        print("SET emissive to " + str(emissive))
        self.emissive = emissive
        
        if emissive:
            self.bsdf.inputs["Emission Strength"].default_value = self.strength
        else:
            self.bsdf.inputs["Emission Strength"].default_value = 0
        
        if new_color is None:
            self.bsdf.inputs["Emission"].default_value = self.color
        else:
            self.bsdf.inputs["Emission"].default_value = new_color
    
    def set_emissive_strength(self, strength: float = 4):
        self.strength = strength
        if self.emissive:
            self.bsdf.inputs["Emission Strength"].default_value = strength