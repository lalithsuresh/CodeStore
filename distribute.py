import os
import errno
import numpy

import conf

class Distributor:
    """Given a list of objects, this class distributes them and/or retrieves them"""

    def create_dirs(self,dirs=conf.DIRS):
        current_dir = os.getcwd()
        for path in dirs:
            try:
                os.makedirs(os.path.abspath(path))
            except OSError, e:
                if e.errno != errno.EEXIST:
                    raise

    def push_objects_to_stores(self, name, list_of_objects):
        i = 0

        # Because this is a list of tuples to be saved
        # in different nodes
        assert len(list_of_objects) == len(conf.DIRS)

        for element in map(lambda x: os.path.abspath(x), conf.DIRS):
            assert(len(list_of_objects[i])) == conf.PART_SIZE
            # For each tuple to be saved...
            for obj in list_of_objects[i]:
                outfile = open(os.path.join(element, name + '-' + str(list_of_objects[i].index (obj))), 'wb')

                # Write out each byte as in
                # original file
                for byte in obj.get_data():
                    outfile.write (chr(byte))

                outfile.close()

            i += 1

    def push_object_to_store(self, name, node_index, obj, object_index):

        path = os.path.abspath(conf.DIRS[node_index])

        # For each tuple to be saved...
        outfile = open(os.path.join(path, name + '-' + str(object_index)), 'wb')

        # Write out each byte as in
        # original file
        for byte in obj:
            outfile.write (chr(byte))

        outfile.close()

    def pull_object_from_stores(self, name, node_index, object_index):
        
        path = os.path.abspath (conf.DIRS[node_index])
        data = []

        try:
            infile = open(os.path.join(path, name + '-' + str(object_index)),'rb')
            bytes_read = infile.read (256)
            data = []
    
            while bytes_read != "":
                for b in bytes_read:
                    data.append (b)
                bytes_read = infile.read (256)

        except IOError:
            print "Error opening %s" % (os.path.join(path, name + '-' + str(object_index)))

        arr = numpy.array (map(lambda x: ord(x), data))
        return arr
