import bpy


#bpy.ops.mesh.primitive_cube_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))

#object = bpy.context.active_object


def createBasicPointcloud(object, type):
    
    selectRightObject(object)
    # add GeometryNodes modifier
    bpy.ops.object.modifier_add(type='NODES')

    # access active object node_group
    bpy.ops.node.new_geometry_node_group_assign()
    node_group = bpy.context.object.modifiers[0].node_group
    # add socket
    inputs = node_group.inputs
    inputs.new(type = "NodeSocketFloat", name = "cube_size")
    # remove first socket
    #inputs.remove(inputs[0])

    inputs.new(type = "NodeSocketFloat", name = "size_x")
    inputs.new(type = "NodeSocketFloat", name = "size_y")

    # add node
    nodes = node_group.nodes
    
    meshpoint = nodes.new(type="GeometryNodeMeshToPoints")
    meshpoint.location.x += 400
    meshpoint.location.y -= 50

    nodes["Group Output"].location.x += 850

    # connect
    links = node_group.links
    links.new(nodes["Group Input"].outputs["Geometry"],     meshpoint.inputs["Mesh"])
    links.new(meshpoint.outputs["Points"],                  nodes["Group Output"].inputs["Geometry"])
    

def selectRightObject(object):
    bpy.ops.object.select_all(action = "DESELECT")
    objectname = bpy.context.object.data.name
    for ob in bpy.data.objects:
         print(objectname)
         print(ob.data.name)
         if ob.data.name == objectname:
            ob.select_set(True)
    
    
createBasicPointcloud(object)


