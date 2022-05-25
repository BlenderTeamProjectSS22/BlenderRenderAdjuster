# Sets the roughness of the active material
# Assertion: Object has at least one material
# Assertion: Roughness is a value between 0 and 1
# Assertion: Material is BDSF (because not every material has roughness property)
def set_roughness(obj: object, roughness : int) -> None:
    obj.active_material.roughness = roughness
    obj.active_material.node_tree.nodes["Principled BSDF"].inputs[7].default_value=roughness
	
# Sets the metallic value of the active material
# Assertion: Object has at least one material
# Assertion: Metallic is a value between 0 and 1
def set_metallic(obj: object, metallic : int) -> None:
    obj.active_material.metallic = metallic
	obj.active_material.node_tree.nodes["Principled BSDF"].inputs[4].default_value = metallic
	
# Apply a transparent glass material to an object
def apply_glass(obj) -> None:
	glass = bpy.data.materials.new("Glass")
	glass.use_nodes = True
	nodes = glass.node_treetree.nodes
	bsdf  = nodes.get("Principled BSDF")
	
	set_roughness(obj, 0)
	bsdf.inputs["Transmission"].default_value = 1
	glass.use_screen_refraction = True
	
	# Enable transparent rendering in "Render properties" (EVEE specific)
	bpy.context.scene.eevee.use_ssr = True 			  # Screen Space Reflections
	bpy.context.scene.eevee.use_ssr_refraction = True # Refraction
	
	obj.data.materials.append(glass)
	obj.active_material = glass

# Applys a glow effect to the object (adds emissive material and enables bloom)
def apply_emissive(obj, strength: float = 5) -> None:
	bpy.context.scene.evee.use_bloom = True
	obj.active_material.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = strength
	
	# The following will set the emission color, but somehow I need to get the current color set in the UI
	#obj.active_material.node_tree.nodes["Principled BSDF"].inputs["Emission"].default_value = 
	



	