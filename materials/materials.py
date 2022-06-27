import bpy
from abc import ABC, abstractmethod

class MaterialController:

	def __init__(self, obj):
		self.material    = self.init_material(obj)
		self.bsdf	     = self.material.node_tree.nodes["Principled BSDF"]
		self.color       = self.bsdf.inputs["Base Color"].default_value
		self.metallic    = 0
		self.roughness   = 0.5
		self.tranmission = 0
		self.emissive    = False
		self.strength    = 1
	
	def init_material(self, obj) -> bpy.types.Material:
	
		# Create a simple BSDF only material
		mat  = bpy.data.materials.new("Program Material")
        mat.use_nodes = True
		tree = mat.node_tree
		for n in tree.nodes:
			tree.nodes.remove(n)
		bsdf = tree.nodes.new("ShaderNodeBsdfDiffuse")
		mat_output = tree.nodes.new("ShaderNodeOutputMaterial")
		tree.links.new(bsdf.outputs["BSDF"], mat_output.inputs["Surface"])
		return mat
	
	def glass_material(self):
        self.bsdf.set_transmission(1)
        self.bsdf.set_roughness(0.05)
	
	def stone_material(self) -> bpy.types.Material:
		self.bump_material(5, 10)
	
	# Create and return a bump material to an object, with adjustable scale and detail level of the noise
	def bump_material(self, scale: float = 5, detail: float = 2) -> bpy.types.Material:

		nodes = self.material.node_tree.nodes
		links = self.material.node_tree.links

		noise = nodes.new(type="ShaderNodeTexNoise")
		bump  = nodes.new(type="ShaderNodeBump")
		material_output = nodes.get("Material Output")
	
		links.new(noise.outputs["Color"], bump.inputs["Height"])
		links.new(bump.outputs["Normal"], self.bsdf.inputs["Normal"])
	
		# Set scale and detail properties of the noise
		noise.inputs["Scale"].default_value  = scale
		noise.inputs["Detail"].default_value = detail
	
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
	
	def set_emissive(self, emissive: bool, strength: float = 4, new_color = None):
		self.emissive = emissive
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