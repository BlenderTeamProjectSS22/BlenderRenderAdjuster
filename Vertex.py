import bpy
 
# start in object mode
def import_vertex(material: bpy.types.Material):
  obj = bpy.data.objects[material]
  mesh = obj.data

  if not mesh.vertex_colors:
      mesh.vertex_colors.new()

  color_layer = mesh.vertex_colors["Col"]

# or you could avoid using the color_layer name
# color_layer = mesh.vertex_colors.active  

  i = 0
  for poly in mesh.polygons:
      for idx in poly.loop_indices:
          obj = bpy.data.objects[material]
          mesh = obj.data
          i += 1

# set to vertex paint mode to see the result
  bpy.ops.object.mode_set(mode='VERTEX_PAINT')