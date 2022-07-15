import bpy

#import the Texture image
def load_texture(texture_path: str, material: bpy.types.Material):
  if material.node_tree.nodes.get("Image Texture") is None:
    texImage = material.node_tree.nodes.new(type = "ShaderNodeTexImage")
  else:
    texImage = material.node_tree.nodes.get("Image Texture")
  texImage.image = bpy.data.images.load(bpy.path.relpath(texture_path))
  
  #disp is path of Base color
  disp=material.node_tree.nodes["Principled BSDF"].inputs["Base Color"]
      
  #connect the node between 'Base Color' of bsdf and 'Color' of texImage
  material.node_tree.links.new(disp,texImage.outputs[0])
  
def control_scale(material: bpy.types.Material, gross: int):
    Mapping = material.node_tree.nodes.new('ShaderNodeTexImage')
    Coord = material.node_tree.nodes.new('ShaderNodeTexCoord')
    
    material.node_tree.links.new(Mapping.inputs['Vector'], Coord.outputs['UV'])
        
    disp=material.node_tree.nodes["ShaderNodeTexImage"].inputs['Vector'] 
    material.node_tree.links.new(disp,Mapping.outputs['Vector'])
    
    
    #control the scale of Texture image
    bpy.data.materials["Material"].node_tree.nodes["Mapping"].inputs[3].default_value[0] = gross
    bpy.data.materials["Material"].node_tree.nodes["Mapping"].inputs[3].default_value[1] = gross
    bpy.data.materials["Material"].node_tree.nodes["Mapping"].inputs[3].default_value[2] = gross
  

  

def delete_texture(material: bpy.types.Material):
  disp=material.node_tree.nodes["Principled BSDF"].inputs["Base Color"]
  material.node_tree.links.remove(disp.links[0])