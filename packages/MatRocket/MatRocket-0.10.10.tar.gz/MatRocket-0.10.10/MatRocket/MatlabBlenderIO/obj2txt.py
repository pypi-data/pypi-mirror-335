import bpy, mathutils, numpy, os, shutil, time



def obj2txt(obj, path, *args, **kwargs):
    
    filename = kwargs.get('filename', None)
    address  = kwargs.get('address',  None)
    
    if filename == None:
        if not os.path.exists(path):
            os.makedirs(path)
        filename = path+"\\"+obj.name+".txt"
        if os.path.isfile(filename):
            os.remove(filename)

    if address == None:
        address = obj.name


    with open(filename, 'a') as file:
        obj.rotation_mode = 'QUATERNION'
        position            = numpy.array(obj.location)
        attitude            = numpy.array(obj.rotation_quaternion.to_matrix())
        
        file.write(address+'.position\n')
        numpy.savetxt(file, position, delimiter=',')
        file.write(address+'.attitude\n')
        numpy.savetxt(file, attitude, delimiter=',')
        
        if obj.type == 'MESH':
            file.write(address+'.mesh\n')
            file.write(obj.name   +'.stl\n')
            stl_path = path+'\\'+obj.name+'.stl'
            
            
            # Un-parenting and saving logic
            if not obj.parent is None:
                matrix_world_obj    = obj.matrix_world.copy()
                matrix_world_parent = obj.parent.matrix_world.copy()
                matrix_world_parent.invert()
                matrix_local = matrix_world_parent @ matrix_world_obj
                obj.matrix_world = matrix_local
            
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
            
                bpy.ops.export_mesh.stl(
                                        filepath=stl_path,
                                        use_selection=True)

                obj.matrix_world = matrix_world_obj
                obj.select_set(False)

            else:
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
            
                bpy.ops.export_mesh.stl(
                                        filepath=stl_path,
                                        use_selection=True)

                obj.select_set(False)

    
    for child in obj.children:
        obj2txt(child, path, filename=filename, address = address + '.' + child.name)
