import bpy

def DoNothing(self):
        return

def selectMainObject(self):
    #bpy.ops.object.select_all(action = "DESELECT")
    # self.objectname = self.control.model.name
    #bpy.data.objects[self.objectname].select_set(True)
    bpy.context.view_layer.objects.active = self.control.model

def new_GeometryNodes_group(self):
    ''' Create a new empty node group that can be used
        in a GeometryNodes modifier.
    '''
    
    node_group = bpy.data.node_groups.new('GeometryNodes', 'GeometryNodeTree')
    inNode = node_group.nodes.new('NodeGroupInput')
    inNode.outputs.new('NodeSocketGeometry', 'Geometry')
    outNode = node_group.nodes.new('NodeGroupOutput')
    #outNode.inputs.new('NodeSocketGeometry', 'Geometry')
    #node_group.links.new(inNode.outputs['Geometry'], outNode.inputs['Geometry'])
    inNode.location = Vector((-1.5*inNode.width, 0))
    #outNode.location = Vector((1.5*outNode.width, 0))
    return node_group

# In 3.2 Adding the modifier no longer automatically creates a node group.
# This test could be done with versioning, but this approach is more general
# in case a later version of Blender goes back to including a node group.

def geoNodeForObject(self,object):

    self.selectMainObject()
    bpy.ops.object.modifier_add(type='NODES') 
    
    if object.modifiers[-1].node_group:
        node_group = object.modifiers[-1].node_group    
    else:
        node_group = self.new_GeometryNodes_group()
        object.modifiers[-1].node_group = node_group
    nodes = node_group.nodes
    group_in = nodes.get('Group Input')
    group_out = nodes.get('Group Output')
    new_node = nodes.new('GeometryNodeMeshToPoints')
    node_group.links.new(group_in.outputs[0], new_node.inputs['Mesh'])
    node_group.links.new(group_out.inputs[0], new_node.outputs[0])

def convert(self):
    print(self.hasconverted)
    if self.hasconverted:
            bpy.context.object.modifiers["GeometryNodes"].show_render = False
            bpy.context.object.modifiers["GeometryNodes"].show_viewport = False
            self.hasconverted = False
            self.control.re_render()
    else:
        if(not self.control.model == None):
            self.control.model.select_set(True)
            self.geoNodeForObject(bpy.context.active_object)
            self.hasconverted = True
            self.control.re_render()

def changesize(self):
    bpy.data.node_groups["GeometryNodes"].nodes["Mesh to Points"].inputs[3].default_value = 8.75




