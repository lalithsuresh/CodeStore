import struct
import numpy
import conf
import copy
import distribute
import sys

class MetaStore:

      def __init__ (self):
          self.meta_map = {}
      
      def AddObject (self, storage_object, node_index, object_index):
          
          # If this object hasn't ever been seen before...
          if (not self.meta_map.has_key (storage_object.get_base_name())):
              self.meta_map [storage_object.get_base_name()] = {}

              for i in range(0, len(conf.DIRS)):
                  self.meta_map [storage_object.get_base_name()][i] = {}

          # Initialise list for:
          # (FileName, NodeIndex, ObjectIndex) --> []
          self.meta_map[storage_object.get_base_name()][node_index][object_index] = []

          for element in storage_object.get_indices():
              self.meta_map[storage_object.get_base_name()][node_index][object_index].append (element)
              self.meta_map[storage_object.get_base_name()][node_index][object_index].append (storage_object.get_indices()[element])


      def Print(self):
          print self.meta_map

class StorageObject:

      def __init__ (self, data, index, name):
          self.indices = {index: len (data)} # Part-indices and corresponding size
          self.data = data  # XOR-ed data
          self.base_name = name

      def get_data (self):
          return self.data

      def get_indices (self):
          return self.indices

      def get_base_name (self):
          return self.base_name

      def AddObject (self, new_so):
          self.data = numpy.bitwise_xor (self.data, new_so.get_data())

          for key in new_so.get_indices ():
              if (self.indices.has_key (key)):
                  del self.indices [key]
              else:
                  self.indices[key] = new_so.get_indices()[key]

      def Print (self):
          print self.indices, self.data

class Strip:
    """ A class that strips the file into 4 binary pieces"""
    def splitter(self,filename):
        with open(filename, "rb") as f:
            byte = f.read(1)
            data = [byte]
            while byte !="":
                byte = f.read(1)
                data.append (byte)
            #print data[:-1]
            arr = numpy.array (map(lambda x: ord(x), data[:-1]))
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
            meta.AddObject (copy.deepcopy(obj),conf.BASIS_VECTORS.index (node), node.index(vector))

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


if __name__ == "__main__":    

    global meta
    meta = MetaStore ()

    strip = Strip()
    name = sys.argv[1]
    byte_array = strip.splitter(name)
    chunks = SplitIntoChunks (byte_array)

    # Number of chunks == number of indices
    i = 0
    storage_obj_list = []
    for each in chunks:
        so = StorageObject (each, i, name)
        storage_obj_list.append (so)
        i += 1

    final_list = ApplyBasisVectors (storage_obj_list)
    meta.Print()


    # Write out data
    dist = distribute.Distributor ()
    dist.create_dirs ()
    dist.push_objects_to_stores (name, final_list)

    
    


    # TEST CASES
    """
    o1 = dist.pull_object_from_stores (name, 0, 0)
    o2 = dist.pull_object_from_stores (name, 1, 0)
    o2o3 = dist.pull_object_from_stores (name, 0, 1)
    o4 = dist.pull_object_from_stores (name, 3, 0)

    o3 = numpy.bitwise_xor (o2, o2o3)
    EATME = numpy.append(numpy.append(numpy.append (o1, o2), o3), o4)
    print EATME

    testfile = open ('thisshouldwork.mp3', 'wb')
    
    for byte in EATME:
        testfile.write (chr(byte))

    testfile.close()
    """
