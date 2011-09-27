import struct
import numpy
import copy
import sys
import os

import conf
import meta_store
import distribute
import storage_object
import monitoring

global dist
dist = distribute.Distributor()

class Split:
    """ A class that strips the file into 4 binary pieces"""
    def splitter(self,filename):
        with open(filename, "rb") as f:
            bytes_read = f.read(256)
            data = []
            while bytes_read !="":
                for b in bytes_read:
                    data.append (ord(b))
                bytes_read = f.read(256)
            arr = numpy.array (data)
            return arr

def ApplyBasisVectors (storage_obj_list):
    final_list = []
    for node in conf.BASIS_VECTORS:
        obj_list = []
        for vector in node:
             
            flag = 0
            obj = ''
            for i in range(0,len(vector)):
                if (vector[i] == 1):
                    if (flag == 0):
                        obj = copy.deepcopy (storage_obj_list [i])

                        flag = 1
                    else:
                        obj.AddObject (copy.deepcopy (storage_obj_list [i]))
                        
            obj_list.append (obj)
            
            # Store (Object, NodeIndex, ObjectPartIndex) to MetaMap
            #meta.AddObject (copy.deepcopy(obj),conf.BASIS_VECTORS.index (node), node.index(vector))

            del obj
        final_list.append (obj_list)

    return final_list

    
# TODO: Do padding
def SplitIntoChunks (narray):
    
    size = len (narray)

    chunk_size = size/conf.NUM_PIECES
    assert size % conf.NUM_PIECES == 0

    chunks = []

    for i in range (0, conf.NUM_PIECES):
        chunks.append (copy.deepcopy(narray[i*chunk_size:(i+1)*chunk_size]))

    return chunks


# TODO: Should probably check if nodes are up
# before computing inverse
def Reconstruct (list_of_nodes, name):
    """ Reconstruct the object from the
        list of nodes provided. Requires
        at least two nodes.
    """
    
    list_of_vects = []
    # Find inverse
    for node_index in list_of_nodes:
        list_of_vects = list_of_vects + (map(lambda x: list(x), list(conf.BASIS_VECTORS [node_index])))

    inverted_matrix = numpy.linalg.inv (list_of_vects)
    
    # Assuming reconstruction from 2 nodes, we
    # fetch all objects, and then go through
    # the inverted matrix and put them together
    obj_list = []

    for node_index in list_of_nodes:
        for object_index in range(0,conf.PART_SIZE):
           obj_list.append (dist.pull_object_from_stores (name, node_index, object_index))

    outfile = open ('reconstructed-output.mp3', 'wb')

    for row in inverted_matrix:
        pack = []
        for i in range(0,len(row)):
            if (row[i] != 0):
                pack.append (copy.deepcopy (obj_list[i]))
        for byte in reduce (numpy.bitwise_xor, pack):
            outfile.write (chr(byte))
    
    outfile.close()


def RegenerateWith2Nodes (failed_node, list_of_nodes, name):
    """Regenerate a node using parts obtained from 2 nodes"""
    
    list_of_vects = []

    for node_index in list_of_nodes:
        list_of_vects = list_of_vects + (map(lambda x: list(x), list(conf.BASIS_VECTORS [node_index])))

    array_A = numpy.array(list_of_vects).transpose()
    arrays_B = []

    arrays_B = map(lambda x: list(x), list(conf.BASIS_VECTORS [failed_node]))

    obj_list = []

    for node_index in list_of_nodes:
        for object_index in range(0,conf.PART_SIZE):
           obj_list.append (dist.pull_object_from_stores (name, node_index, object_index))

    for each in arrays_B:
        parts_to_pull = numpy.linalg.solve (array_A, numpy.array(each).transpose())
        pack = []
        
        for i in range(0,len(parts_to_pull)):
            if (parts_to_pull[i] != 0):
                pack.append (copy.deepcopy (obj_list[i]))

        dist.push_object_to_store (name, failed_node, reduce (numpy.bitwise_xor, pack), arrays_B.index (each))



def RegenerateWith3Nodes (failed_node, list_of_nodes, name):
    """ Regenerate a node using parts obtained from 3 nodes.
        This method works only if:
          - The failed node is missing one object part.
          - The nodes to be used for repairing collectively have at least
            three basis vectors that do not include the missing part.
    """
    # Obtain index of an object which isn't
    # required to repair the failed node
    basis_vectors_of_failed_node = conf.BASIS_VECTORS [failed_node]
    ored_vect = reduce (numpy.bitwise_or, basis_vectors_of_failed_node)
    if (list(ored_vect).count (0) == 1):
        pos = list(ored_vect).index (0)
    else:
        # fallback
        raise

    #
    # Store basis vectors indexed by nodeId and objectId.
    # We eliminate basis vectors which have a bit set for
    # an object which isn't required to repair the failed_node.
    #
    list_of_basis_vectors = {}
    for node_index in list_of_nodes:
        bv_of_node = map(lambda x: list(x), list(conf.BASIS_VECTORS [node_index]))
        list_of_basis_vectors [node_index] = {}
        for bv in bv_of_node:
            if (bv[pos] != 1):
                list_of_basis_vectors [node_index][bv_of_node.index(bv)] = bv

    array_A = []
    # Remove rows which have 0 at 'pos' position
    # If not, raise exception
    for node_index in list_of_basis_vectors:
        for object_index in list_of_basis_vectors[node_index]:
            obj_vect = list_of_basis_vectors[node_index][object_index]
            if (obj_vect[pos] == 0):
                list_of_basis_vectors[node_index][object_index] = obj_vect[:pos] + obj_vect[pos+1:]
                array_A.append (list_of_basis_vectors[node_index][object_index])
            else:
                # fallback
                raise

    list_of_objects = []
    # Pull from repository
    for node_index in list_of_basis_vectors:
        for object_index in list_of_basis_vectors[node_index]:
            list_of_objects.append (dist.pull_object_from_stores (name, node_index, object_index))
    
    # Now we have the reduced matrix (3x3 for this case)
    # Solve the linear equations!
    for tup in basis_vectors_of_failed_node:
        each = tup[:pos] + tup[pos+1:]
        res = numpy.linalg.solve (numpy.array(array_A).transpose(), numpy.array(each).transpose())

        # Select the object-parts that need to
        # be XOR-ed together to reconstruct
        # the corresponding part
        pack = []
        for i in range (0, len(res)):
            if (res[i] != 0):
                pack.append (copy.deepcopy (list_of_objects[i]))

        # XOR the parts together
        # and push to repository
        dist.push_object_to_store (name, failed_node, reduce (numpy.bitwise_xor, pack), basis_vectors_of_failed_node.index (tup))



def Regenerate (failed_node, list_of_nodes, name):
    """ If the 3-node-repair doesn't include
        the special case of the missing bit, then
        fallback to 2-node repair
    """
    if (len(list_of_nodes) == 2):
        RegenerateWith2Nodes (failed_node, list_of_nodes, name)
    elif (len(list_of_nodes) == 3):
        try:
            RegenerateWith3Nodes (failed_node, list_of_nodes, name)
        except:
            print "Falling back to 2 nodes, failed_node: %s, list_of_nodes: %s" % (failed_node, list_of_nodes)
            RegenerateWith2Nodes (failed_node, list_of_nodes[:-1], name)
