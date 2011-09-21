class Strip:
        """ A class that strips the file into 4 binary pieces"""
        num_pieces = 4 #TODO change to not hardcoded

        def splitter(self,filename):
                    with open(filename, "rb") as f:
                                otherfd = open("other.mp3",'w')                                
                                byte = f.read(1)
                                while byte !="":
                                    part = f.read(1)
                                    otherfd.write(part)
                    f.close()
                    otherfd.close()
if __name__ == "__main__":    
    strip = Strip()
    myfile="myfile"
    strip.splitter("Test.mp3")     
