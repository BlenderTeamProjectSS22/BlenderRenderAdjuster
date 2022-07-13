import bpy

#import the Texture image
def load_texture(texture_path: str, material: bpy.types.Material):
  if(material.node_tree.nodes.find('ShaderNodeTexImage') == -1):
    texImage = material.node_tree.nodes.new('ShaderNodeTexImage')
  else:
    texImage = material.node_tree.nodes['Image Texture']
    
  texImage.image = bpy.data.images.load(bpy.path.relpath(texture_path))
  
  #disp is path of Base color
  disp=material.node_tree.nodes["Principled BSDF"].inputs['Base Color']
      
  #connect the node between 'Base Color' of bsdf and 'Color' of texImage
  material.node_tree.links.new(disp,texImage.outputs[0])

def delete_texture(material: bpy.types.Material):
  if(material.node_tree.nodes.find('ShaderNodeTexImage') != -1):
    node_to_delete =  material.node_tree.nodes['Image Texture']
    material.node_tree.nodes.remove[node_to_delete]
    
  disp=material.node_tree.nodes["Principled BSDF"].inputs['Base Color']
  material.node_tree.links.remove(disp.links[0])