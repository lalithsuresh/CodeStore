import cmd
import conf
import split
import distribute
import storage_object
import shutil
import os
import monitoring
import hashlib

class Menu(cmd.Cmd):
    def do_reconstruct (self,line):
        """ reconstruct name_of_file list_of_nodes_to_recon_from """
        list_args = line.split()
        name = list_args[0]
        list_of_nodes= map(lambda x: int(x),list_args[1:])
        if (len(list_of_nodes) == 2):
            split.Reconstruct(list_of_nodes, name)
        else:
            print "reconstruct requires name_of_file and 2 nodes sep by space"

    def do_regenerate (self, line):
       """ regenerate name_of_file node list_of_nodes 
       regenerate will crash 'failed_node' and reconstruct name_of_file using list_of_nodes"""
       list_of_args = line.split()
       name = list_of_args[0]
       failed_node = int(list_of_args[1])
       list_of_nodes= map(lambda x: int(x),list_of_args[2:])
       
       if  failed_node in list_of_nodes:
           print "Failed node should be different from list of nodes"
       else :
           reg_inst.regen_from = list_of_nodes
           reg_inst.name = name
           shutil.rmtree(str(conf.DIRS[failed_node])) #TODO  copy dir struct from do_clean
    
    def do_test (self, line):
        """ tests all possible combinations for regeneration"""
        file = line.split()[0]
        monitor.stop()
        #Testing for 3 nodes
        import itertools
        for nodes in list(itertools.permutations(range(0,len(conf.DIRS)), 4)):
                            print nodes
                            failed,node1,node2,node3 = (nodes[0], nodes[1], nodes[2], nodes[3])
                            print failed, node1,node2,node3
                            shutil.rmtree(str(conf.DIRS[failed]))
                            reg_inst.regen_from = [node1,node2,node3]
                            reg_inst.name = file
                            monitor.scan (map (lambda x: conf.DIRS[x], [node1,node2,node3]))
                            monitor.stop()
    def md5func (self,filename):
        md5 = hashlib.md5()
        with open(filename,'rb') as f:
            for chunk in iter(lambda: f.read(128*md5.block_size), ''): 
                 md5.update(chunk)
            f.close()
            return md5.hexdigest()
    
    def do_md5 (self,line):
        """ md5 filename
        Returns an md5 hash between filename and 'reconstructed-output.mp3'"""
        
        file_name = line.split()[0]
        
        print self.md5func (file_name), file_name
        print self.md5func ('reconstructed-output.mp3'),'reconstructed-output.mp3'
    
    def do_init(self,name):
        """ init name 
            Initialize the file specified by and analyze Basis Vectors.
            And place the parts into nodes"""
        if (name):
                self.initialize(name)
        else:
            print "init name_of_file"
    
    def do_exit(self,name):
        """exit"""
        monitor.stop()
        return True
    
    def do_clean(self,name):
        """ clean name 
        Clean all dirs and data"""
        for d in conf.DIRS:
            for f in os.listdir(d):
                if (f[:len(name)] == name):
                    os.remove(d + '/'+ f)
        if (os.path.isfile("reconstructed-output.mp3")):
            os.remove('reconstructed-output.mp3') 

    def do_stats (self,line):
        """ Shows status (UP/DOWN) about the diff nodes"""
        monitor.stats()

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
        monitor.start()

class Regen:
    def __init__(self):
        self.regen_from = []
        self.name = ""

if __name__ == '__main__':

    dist = distribute.Distributor()
    split_inst = split.Split()
    reg_inst = Regen()
    monitor = monitoring.Monitoring(reg_inst)
    
    Menu().cmdloop()
