import struct
import numpy
import conf
import copy
import distribute

class MetaStore:
      meta_map = {}
      

class StorageObject:

      def __init__ (self, data, index):
          self.data_map = {}
          self.data_map[index] = data

      def get_data_map (self):
          return self.data_map

      # This method follows XOR semantics
      def AddObject (self, new_obj):
          for x in new_obj.data_map:
              # Assumes that both values held by the key
              # are the same
              if (self.data_map.has_key (x)):
                  del self.data_map[x]
              else:
                  self.data_map[x] = new_obj.data_map[x]


class Strip:
        """ A class that strips the file into 4 binary pieces"""
        def splitter(self,filename):
                    with open(filename, "rb") as f:
                                otherfd = open("other.mp3",'wb')                                
                                byte = f.read(1)
                                s=byte
                                while byte !="":
                                    byte = f.read(1)
                                    s = s + str(byte)

                                #Not considering having less char in s than NUM_PIECES
                                chunks_size = int(len(s) /conf.NUM_PIECES)
                                chunks_list = [ ]
                                modulo = len(s) % conf.NUM_PIECES
                                if modulo != 0:
                                    for x in range(0,conf.NUM_PIECES):
                                        if x == 0: 
                                            chunks_list.append( s[x: chunks_size + modulo])
                                            p=chunks_size+modulo
                                        else:
                                            chunks_list.append( s[p:p+chunks_size])
                                            p=p+chunks_size
                                else:
                                    for x in range(0, conf.NUM_PIECES):
                                        chunks_list.append( s[x:x+chunks_size])
                                f.close()
                                otherfd.close()
                                return chunks_list                                


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
            del obj
        final_list.append (obj_list)

    return final_list

if __name__ == "__main__":    

    meta = MetaStore ()

    strip = Strip()
    myfile="myfile"
    li = strip.splitter("Test.mp3")

    i = 0
    storage_obj_list = []
    for each in li:
        so = StorageObject (each, i)
        storage_obj_list.append (so)
        i += 1

    final_list = ApplyBasisVectors (storage_obj_list)
