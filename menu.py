import cmd
import split
import distribute
import storage_object
class Menu(cmd.Cmd):
        
    def do_reconstruct (self,line):
        """ reconstruct name_of_file list_of_nodes_to_recon_from """
        list_args = line.split()
        name = list_args[0]
        list_of_nodes= map(lambda x: int(x),list_args[1:])
        print list_of_nodes
        if (len(list_of_nodes) == 2):
            split.Reconstruct(list_of_nodes, name)
        else:
            print "reconstruct requires name_of_file and 2 nodes sep by space"

    def do_regenerate (self ,failed_node, list_of_nodes,name):
       """ regenerate failed_node list_of_nodes name_of_file"""
       if ( failed_node and list_of_nodes):
           split.Regenerate (failed_node, list_of_nodes, name)
       else:
           print "regenerate requires  failed_node  list_of_nodes name_of_file"

    def do_create_dirs (self):
        """ create dirs for the specified file """
        create_dirs()


    def do_init(self,name):
        """ init name 
        Initialize the file specified by and analyze Basis Vectors.
        And place the parts into nodes"""
        if (name):
                self.initialize(name)
        else:
            print "init name"
    
    def emptyline(self):
            pass
    
    def initialize(self,name):
        byte_array = split_inst.splitter(name)
        chunks = split.SplitIntoChunks (byte_array)

        # Number of chunks == number of indices
        i = 0
        storage_obj_list = []
        for each in chunks:
            so = storage_object.StorageObject (each, i, name)
            storage_obj_list.append (so)
            i += 1

        final_list = split.ApplyBasisVectors (storage_obj_list)
        dist.create_dirs()
        dist.push_objects_to_stores(name, final_list)

if __name__ == '__main__':

    dist = distribute.Distributor()
    split_inst = split.Split()
    Menu().cmdloop()
