import conf
import os
import errno
import struct

class Distributor:
    """Given a list of objects, this class distributes them and/or retrieves them"""

    def create_dirs(self):
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

            for obj in list_of_objects[i]:
                for key in obj.get_data_map():
                    outfile.write (struct.pack ('II'+str(len(obj.get_data_map[key]))+'s', [key, len(obj.get_data_map[key]), obj.get_data_map[key]]))

            outfile.close()
            i += 1

    def pull_objects_from_stores(self, name, num):
        list_of_objects=[]
        i = 0
        success = 0
        for element in map(lambda x: os.path.abspath(x), conf.DIRS):
            try:
                infile = open(os.path.join(element, name + str(i)), 'rb')
            except IOError:
                print "Error opening %s" % (infile.name)
                continue
            finally:
                i += 1
            line = infile.readlines()
            list_of_objects.append(list(struct.unpack('I' * conf.PART_SIZE, line[0].strip())))
            success += 1
            if (success == num):
                break

        if (num > len(list_of_objects)):
            print 'Could not retrieve objects from %s nodes' % (num)
            raise Exception (num)
        return list_of_objects

if __name__ == "__main__":
    dist = Distributer()
    #dist.create_dirs() 
    #dist.push_objects_to_stores('objectA', [[1,2],[3,4],[5,6],[7,8]])
    #dist.push_objects_to_stores('objectB', [[2,1],[4,3],[6,5],[8,7]])
    try:
        print dist.pull_objects_from_stores('objectB', 3)
    except Exception as inst:
        print inst.args

    print dist.pull_objects_from_stores('objectA', 2)
