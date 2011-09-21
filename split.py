import struct
import numpy
import conf
GLOBAL DEBUG=1
class Strip:
        """ A class that strips the file into 4 binary pieces"""
        def splitter(self,filename):
                    with open(filename, "rb") as f:
                                otherfd = open("other.mp3",'wb')                                
                                byte = f.read(1)
                                s=""
                                while byte !="":
                                    byte = f.read(1)
                                    s = s + str(byte)
                                if DEBUG:
                                    s="12345"
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
        def xorer(self, chunks_list):
            for x in chunks_list:
                


if __name__ == "__main__":    
    strip = Strip()
    myfile="myfile"
    strip.splitter("Test.mp3")     
