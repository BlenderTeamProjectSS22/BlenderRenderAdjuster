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

# Change the color of an object
# Requires a float array with length 4, (r,g,b,alpha)
def set_base_color(obj: object, color: Vector) -> None:
    obj.active_material.node_tree.nodes["Principled BSDF"].inputs[0].default_value = color
	
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
	
# Create and return a bump material to an object, with adjustable scale and detail level of the noise
def bump_material(scale: float = 5, detail: float = 2) -> bpy.types.Material:
	bump_mat = bpy.data.materials.new(name="BumpMaterial")
	bump_mat.use_nodes = True

	nodes = bump_mat.node_tree.nodes
	links = bump_mat.node_tree.links

	noise = nodes.new(type="ShaderNodeTexNoise")
	bump = nodes.new(type="ShaderNodeBump")
	bsdf = nodes.get("Principled BSDF")
	material_output = nodes.get("Material Output")
	
	links.new(noise.outputs[1], bump.inputs[2]) # Connect Noise Color output to Bump Height input
	links.new(bump.outputs[0], bsdf.inputs[20]) # Connect Bump Normal output to Normal input of BDSF
	
	# Set scale and detail properties of the noise
	noise.inputs[2].default_value = scale	# Scale
	noise.inputs[3].default_value = detail	# Detail
	
	return bump_mat


# Apply a stone like material to an object
def apply_stone(obj):
	stone = bump_material(5, 10)

	obj.data.materials.append(stone)
	obj.active_material = stone
	
	set_base_color(obj, (0.345151, 0.345151, 0.345151, 1) )  # Set color to light gray
	