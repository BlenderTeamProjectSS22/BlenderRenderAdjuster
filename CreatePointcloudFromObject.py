import bpy
from mathutils import Vector



def new_GeometryNodes_group():
        ''' Create a new empty node group that can be used
            in a GeometryNodes modifier.
        '''
    
        node_group = bpy.data.node_groups.new('GeometryNodes', 'GeometryNodeTree')
        node_group.name = "GeometryNodes"

        inNode = node_group.nodes.new('NodeGroupInput')
        inNode.outputs.new('NodeSocketGeometry', 'Geometry')
        outNode = node_group.nodes.new('NodeGroupOutput')
        #outNode.inputs.new('NodeSocketGeometry', 'Geometry')
        #node_group.links.new(inNode.outputs['Geometry'], outNode.inputs['Geometry'])
        inNode.location = Vector((-1.5*inNode.width, 0))
        #outNode.location = Vector((1.5*outNode.width, 0))
        return node_group

# In 3.2 Adding the modifier no longer automatically creates a node group, so it has to be created.

def geoNodeForObject(self,object):


    bpy.ops.object.modifier_add(type='NODES') 
    if object.modifiers[-1].node_group:
        node_group = object.modifiers[-1].node_group    
    else:
        node_group = new_GeometryNodes_group()
        object.modifiers[-1].node_group = node_group
    nodes = node_group.nodes
    group_scale = nodes.new("GeometryNodeScaleElements")
    group_in = nodes.get('Group Input')
    group_out = nodes.get('Group Output')
    point_node = nodes.new('GeometryNodeMeshToPoints')
    nodes.new('GeometryNodeDistributePointsOnFaces')
    object_node = nodes.new("GeometryNodeObjectInfo")
    instance_node = nodes.new ('GeometryNodeInstanceOnPoints')
    node_group.links.new(group_in.outputs[0], point_node.inputs['Mesh'])
    node_group.links.new(instance_node.inputs[0], point_node.outputs[0])
    node_group.links.new(instance_node.inputs[2], group_scale.outputs[0])
    node_group.links.new(group_scale.inputs[0], object_node.outputs[3])
    node_group.links.new(group_out.inputs[0],instance_node.outputs[0])

    
    


def switchrandom(self):
    
    node_group = self.control.model.modifiers[-1].node_group   
    nodes = node_group.nodes
    point_node =  bpy.data.node_groups["GeometryNodes"].nodes["Mesh to Points"]
    random_node =  bpy.data.node_groups["GeometryNodes"].nodes["Distribute Points on Faces"]
    instance_node =  bpy.data.node_groups["GeometryNodes"].nodes["Instance on Points"]
    group_in = nodes.get('Group Input')
    node_group.links.new(group_in.outputs[0], random_node.inputs[0])
    node_group.links.new(random_node.outputs[0],instance_node.inputs[0])


def switchvertex(self):
    
    node_group = self.control.model.modifiers[-1].node_group   
    nodes = node_group.nodes
    point_node =  bpy.data.node_groups["GeometryNodes"].nodes["Mesh to Points"]
    random_node =  bpy.data.node_groups["GeometryNodes"].nodes["Distribute Points on Faces"]
    instance_node =  bpy.data.node_groups["GeometryNodes"].nodes["Instance on Points"]
    group_in = nodes.get('Group Input')
    node_group.links.new(group_in.outputs[0], point_node.inputs[0])
    node_group.links.new(point_node.outputs[0],instance_node.inputs[0])
    

def convert(self):
        
        self.selectMainObject()
        if self.hasconverted:
            
            if self.pointcloud.get():
                bpy.context.object.modifiers["GeometryNodes"].show_render = True
                bpy.context.object.modifiers["GeometryNodes"].show_viewport = True
            else:
                bpy.context.object.modifiers["GeometryNodes"].show_render = False
                bpy.context.object.modifiers["GeometryNodes"].show_viewport = False
            
        else:
            if(not self.control.model == None):
                self.control.model.select_set(True)
                geoNodeForObject(self,bpy.context.active_object)
                self.hasconverted = True
                self.set_object
                self.obj_selected.set("sphere")
                bpy.data.node_groups["GeometryNodes"].nodes["Object Info"].inputs[0].default_value = self.sphere
                setRightAfterImport(self)
                



        self.control.re_render()


def setRightAfterImport(self):
    if (self.vertices.get()):
        switchvertex(self)
    else:
        switchrandom(self)




def setSphere(self):
    bpy.data.node_groups["GeometryNodes"].nodes["Object Info"].inputs[0].default_value = self.sphere


def setCube(self):
    bpy.data.node_groups["GeometryNodes"].nodes["Object Info"].inputs[0].default_value = self.cube

def setDisk(self):
    bpy.data.node_groups["GeometryNodes"].nodes["Object Info"].inputs[0].default_value = self.disk

        