import bpy

#ture the engine to 'CYCLES', when the node_tree is been used
bpy.context.scene.render.engine='CYCLES'

#make a new materials called 'Tex', and we use this materials for the Object with suitble texture.
mat = bpy.data.materials.new('Tex')
mat.use_nodes=True

#Default:model is already imported, and we know the path to material.
#connect object 'Eiffel_tower'
Eiffel = bpy.context.collection.objects['Eiffel_tower']
Eiffel.data.materials.append(mat)
Eiffel = bpy.context.active_object

#import the Texture image
texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
texImage.image = bpy.data.images.load("/Users/xiaochenli/Documents/Semester5/Teamprojekt/blender/Texutre/abstract-gf253dd991_1920.jpg")

#disp is path of Base color
disp=bpy.data.materials['Tex'].node_tree.nodes["Principled BSDF"].inputs['Base Color']

#connect the node between 'Base Color' of bsdf and 'Color' of texImage
mat.node_tree.links.new(disp,texImage.outputs[0])