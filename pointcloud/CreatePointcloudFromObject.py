"""
author: Jason Pywell
created on: 20/05/2022
description:
All the functions needed to create a pointcloud from a object,
also includes the addplane function, which adds a plane into the scene.
"""

import bpy
from mathutils import Vector

# creates a new geometry node group
def new_GeometryNodes_group():
        ''' Create a new empty node group that can be used
            in a GeometryNodes modifier.
        '''
    
        node_group = bpy.data.node_groups.new('GeometryNodes', 'GeometryNodeTree')
        node_group.name = "GeometryNodes"

        inNode = node_group.nodes.new('NodeGroupInput')
        inNode.outputs.new('NodeSocketGeometry', 'Geometry')
        outNode = node_group.nodes.new('NodeGroupOutput')
        inNode.location = Vector((-1.5*inNode.width, 0))
        return node_group

# In 3.2 and after Adding the modifier no longer automatically creates a node group, so it has to be created.
# this function creates the nodes in the node tree and links them up.

def geoNodeForObject(self,object):

    bpy.ops.object.modifier_add(type='NODES') 
    if object.modifiers[-1].node_group:
        node_group = object.modifiers[-1].node_group    
    else:
        node_group = new_GeometryNodes_group()
        object.modifiers[-1].node_group = node_group
    nodes = node_group.nodes
    group_scale = nodes.new("GeometryNodeScaleElements")
    bpy.data.node_groups["GeometryNodes"].nodes["Scale Elements"].inputs[2].default_value = 0.1
    group_in = nodes.get('Group Input')
    group_out = nodes.get('Group Output')
    point_node = nodes.new('GeometryNodeMeshToPoints')
    nodes.new('GeometryNodeDistributePointsOnFaces')
    object_node = nodes.new("GeometryNodeObjectInfo")
    instance_node = nodes.new ('GeometryNodeInstanceOnPoints')
    bpy.data.node_groups["GeometryNodes"].nodes["Instance on Points"].inputs[5].default_value[0] = -1.570796
    bpy.data.node_groups["GeometryNodes"].nodes["Instance on Points"].inputs[5].default_value[1] = 1.5708
    node_group.links.new(group_in.outputs[0], point_node.inputs['Mesh'])
    node_group.links.new(instance_node.inputs[0], point_node.outputs[0])
    node_group.links.new(instance_node.inputs[2], group_scale.outputs[0])
    node_group.links.new(group_scale.inputs[0], object_node.outputs[3])
    node_group.links.new(group_out.inputs[0],instance_node.outputs[0])

    
    

# links up the "Distribute Points on Faces" node with the node tree (unlinks the "Mesh to Points" node).
def switch_random(self):
    
    node_group = self.control.model.modifiers[-1].node_group   
    nodes = node_group.nodes
    random_node =  bpy.data.node_groups["GeometryNodes"].nodes["Distribute Points on Faces"]
    instance_node =  bpy.data.node_groups["GeometryNodes"].nodes["Instance on Points"]
    group_in = nodes.get('Group Input')
    node_group.links.new(group_in.outputs[0], random_node.inputs[0])
    node_group.links.new(random_node.outputs[0],instance_node.inputs[0])


# links up the "Mesh to Points" node with the node tree (unlinks the "Distribute Points on Faces" node).
def switch_vertex(self):
    
    node_group = self.control.model.modifiers[-1].node_group   
    nodes = node_group.nodes
    point_node =  bpy.data.node_groups["GeometryNodes"].nodes["Mesh to Points"]
    instance_node =  bpy.data.node_groups["GeometryNodes"].nodes["Instance on Points"]
    group_in = nodes.get('Group Input')
    node_group.links.new(group_in.outputs[0], point_node.inputs[0])
    node_group.links.new(point_node.outputs[0],instance_node.inputs[0])
    

# converts the selected object in a scene into a pointcloud using geometry nodes
def convert_active_to_pointcloud(self):
        
        select_main_object(self)
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


# switches the pointcloud into the right setting after importing a new model.
def setRightAfterImport(self):
    if (self.vertices.get()):
        switch_vertex(self)
    else:
        switch_random(self)


#changes the instanced object to be a sphere
def set_sphere(self):
    bpy.data.node_groups["GeometryNodes"].nodes["Object Info"].inputs[0].default_value = self.sphere

#changes the instanced object to be a cube
def set_cube(self):
    bpy.data.node_groups["GeometryNodes"].nodes["Object Info"].inputs[0].default_value = self.cube

#changes the instanced object to be a disk
def set_disk(self):
    bpy.data.node_groups["GeometryNodes"].nodes["Object Info"].inputs[0].default_value = self.disk

def set_monkey(self):
    bpy.data.node_groups["GeometryNodes"].nodes["Object Info"].inputs[0].default_value = self.monkey

# changes the size of the instanced objects from the pointcloud
def set_size(self,value):
    bpy.data.node_groups["GeometryNodes"].nodes["Scale Elements"].inputs[2].default_value = (float(value) + 0.1) / 10


# creates default objects that are instanced to create the pointcloud (are hidden in viewport and render).      
def create_point_objects(self):
    bpy.ops.mesh.primitive_cube_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    self.cube = bpy.context.object
    bpy.context.object.hide_render = True
    bpy.context.object.hide_viewport = True
    so = bpy.context.active_object
    self.control.material.apply_material(so)

    bpy.ops.mesh.primitive_uv_sphere_add(radius=1, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    self.sphere = bpy.context.object
    bpy.context.object.hide_render = True
    bpy.context.object.hide_viewport = True
    so = bpy.context.active_object
    self.control.material.apply_material(so)
    
    bpy.ops.mesh.primitive_circle_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.edge_face_add()
    bpy.ops.object.editmode_toggle()
    self.disk = bpy.context.object
    bpy.context.object.hide_render = True
    bpy.context.object.hide_viewport = True
    so = bpy.context.active_object
    self.control.material.apply_material(so)


    bpy.ops.mesh.primitive_monkey_add(size=2, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 1, 1))
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.separate(type='LOOSE')
    bpy.ops.object.editmode_toggle()
    bpy.ops.object.select_all(action = "DESELECT")
    for obj in bpy.context.scene.objects:
        if  obj.name == "Suzanne.001" or obj.name == "Suzanne":
            bpy.data.objects[obj.name].select_set(True)
            bpy.ops.object.delete()  
    
    for obj in bpy.context.scene.objects:
      
        if  obj.name == "Suzanne.002":
            bpy.context.view_layer.objects.active = obj
            
    self.monkey = bpy.context.object
    bpy.context.object.hide_render = True
    bpy.context.object.hide_viewport = True
    so = bpy.context.active_object
    self.control.material.apply_material(so)
    


# adds a plane into the scene or deletes it if a plane is present.
def add_plane(self):
    self.has_plane = False
    for obj in bpy.context.scene.objects:
        if obj.name == "Plane":
            self.has_plane = True
        
    if self.has_plane:
        bpy.ops.object.select_all(action = "DESELECT")
        bpy.data.objects["Plane"].select_set(True) 
        bpy.ops.object.delete()   
        
    else:
        bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=(0, 0, -1), scale=(1, 1, 1))
        bpy.ops.transform.resize(value=(15, 15, 15))
    
    bpy.ops.object.select_all(action = "DESELECT")
    bpy.data.objects[self.control.model.name].select_set(True) 
    self.control.re_render()

# selects the self.control.model object in the scene 
def select_main_object(self):
    bpy.context.view_layer.objects.active = self.control.model

# removes the geometry node modifier from the active object
def remove_mod():
    bpy.ops.object.modifier_remove(modifier="GeometryNodes")
