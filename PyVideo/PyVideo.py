import numpy as np
import struct 
import matplotlib.pyplot as plt


class DataReader:
    szBuffer = 16384
    def __init__ (self, filename):
        self.fp = open(filename, 'rb')
        self.buf = self.fp.read(DataReader.szBuffer)
        self.pos = 0
        pass

    def GetBytes(self, n):
        ret = self.buf[self.pos:(self.pos+n)]
        self.pos += n
        print(self.pos, ret)
        return ret
    
    def Int32(self):
        ret = self.GetBytes(4)
        return int.from_bytes(ret, 'little')



class VideoContainer:
    def __init__(self):
        pass

    def open(self, filename):
        self.filename = filename
        if filename[-4:].lower() == '.avi':
            self.open_AVI()
        pass

    def Parse_unit(self, name = ''):
        if name == '':
            name = self.dr.GetBytes(4)
        if type(name) == bytes:
            name = name.decode('utf-8')
        try:
            eval('self.Parse_' + name + '()')
        except Exception as e:
            print(f'Exception occurred with parse_{name} : {e}')

    def open_AVI(self):
        self.dr = DataReader(self.filename)
        self.Parse_unit()
        pass

    def Parse_RIFF(self):
        print('parse RIFF unit - size: ', self.dr.Int32())
        self.Parse_unit()
        pass

    def Parse_AVI(self):
        self.Parse_unit()
        pass

    def Parse_LIST(self):
        sz = self.dr.Int32()
        print(sz)
        self.Parse_unit()
        pass

    def Parse_hdrl(self):
        self.Parse_unit()
        pass

    def Parse_avih(self):
        parm1 = self.dr.Int32()
        parm2 = self.dr.Int32()
        parm3 = self.dr.Int32()
        parm4 = self.dr.Int32()

        print('---')
        pass

if __name__ == '__main__':
    print("Main function")
    # test avi
    vc = VideoContainer()
    vc.open('test.avi')
    pass

    # test mkv
