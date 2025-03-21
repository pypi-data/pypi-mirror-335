import bpy, mathutils, numpy, os, shutil, time


def query_txt(filepath, key):
    file               = open(filepath, 'r')
    data               = file.read()
    data               = data.split('\n')
    data_length        = len(data)
    is_number          = ['0','1','2','3','4','5','6','7','8','9']

    key_index      = sum(i*(key == data[i]) for i in range(0,len(data)))

    outdata_length = 1
    length_found   = False

    while not length_found:
        out_of_index = (data_length < key_index + outdata_length)

        if not out_of_index: is_outdata     = any( is_number[i] in data[key_index + outdata_length] for i in range(0,10) )
        else:                is_outdata     = False
        
        if not is_outdata: length_found     = True
        else:              outdata_length  += 1


    outdata = data[key_index+1:key_index+outdata_length]
    for index in range(0, len(outdata)):
        outdata[index] = outdata[index].split(',')
    outdata = numpy.array(outdata, dtype = float)
    
    return outdata
