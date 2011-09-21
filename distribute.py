import conf
import os
import errno
import struct

class Distributer:
    """Given a list of objects, this class distributes them and/or retrieves them"""

    def __init__(self):
        current_dir = os.getcwd()
        for path in conf.DIRS:
            try:
                os.makedirs(os.path.abspath(path))
            except OSError, e:
                if e.errno != errno.EEXIST:
                    raise

    def push_objects_to_stores(self, name, list_of_objects):
        i = 0
        assert len(list_of_objects) == len(conf.DIRS)
        for element in map(lambda x: os.path.abspath(x), conf.DIRS):
            assert(len(list_of_objects[i])) == conf.PART_SIZE
            outfile = open(os.path.join(element, name + str(i)), 'wb')
            outfile.write(struct.pack('I'*len(list_of_objects[i]),*list_of_objects[i]))
            outfile.close()
            i += 1

    def pull_objects_from_stores(self, name):
        list_of_objects=[]
        i = 0
        for element in map(lambda x: os.path.abspath(x), conf.DIRS):
            infile = open(os.path.join(element, name + str(i)), 'rb')
            line = infile.readlines()
            list_of_objects.append(list(struct.unpack('I' * conf.PART_SIZE, line[0].strip())))
            i += 1

        return list_of_objects

if __name__ == "__main__":
    dist = Distributer()
    dist.push_objects_to_stores('objectA', [[1,2],[3,4],[5,6],[7,8]])
    dist.push_objects_to_stores('objectB', [[2,1],[4,3],[6,5],[8,7]])
    print dist.pull_objects_from_stores('objectB')
    print dist.pull_objects_from_stores('objectA')
