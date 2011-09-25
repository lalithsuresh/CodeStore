import numpy

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
