import conf

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
