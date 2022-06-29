import bpy

##make a new materials called 'Tex', and we use this materials for the Object with suitble texture.
def object_to_material(obj: bpy.types.Object):
  mat = bpy.data.materials.new('Tex')
  mat.use_nodes=True

  ##select the object and append with material mat
  obj.data.materials.append(mat)

#import the Texture image
def load_texture(texture_path: str):
  texImage = mat.node_tree.nodes.new('ShaderNodeTexImage')
  texImage.image = bpy.data.image.load(texture_path)
  
  #disp is path of Base color
  disp=bpy.data.materials['Tex'].node_tree.nodes["Principled BSDF"].inputs['Base Color']
      
  #connect the node between 'Base Color' of bsdf and 'Color' of texImage
  mat.node_tree.links.new(disp,texImage.outputs[0])

