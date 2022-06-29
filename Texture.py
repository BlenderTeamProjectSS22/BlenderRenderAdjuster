import bpy

#import the Texture image
def load_texture(texture_path: str, material: bpy.types.Material):
  texImage = material.node_tree.nodes.new('ShaderNodeTexImage')
  texImage.image = bpy.data.images.load(texture_path)
  
  #disp is path of Base color
  disp=material.node_tree.nodes["Principled BSDF"].inputs['Base Color']
      
  #connect the node between 'Base Color' of bsdf and 'Color' of texImage
  material.node_tree.links.new(disp,texImage.outputs[0])

def delete_texture(material: bpy.types.Material):
  disp=material.node_tree.nodes["Principled BSDF"].inputs['Base Color']
  material.node_tree.links.remove(disp.links[0])
  

