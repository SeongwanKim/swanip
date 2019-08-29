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
        sz = int.from_bytes(ret, 'little')
        print('int32: ', sz)
        return sz



class VideoContainer:
    def __init__(self):
        pass

    def open(self, filename):
        self.filename = filename
        if filename[-4:].lower() == '.avi':
            self.open_AVI()
        pass

    def parse_unit(self, name = ''):
        list_names = ['LIST', 'RIFF', 'hdrl']
        if name == '':
            name = self.dr.GetBytes(4)
        if type(name) == bytes:
            name = name.decode('utf-8')
        sz = self.dr.Int32()
        tsz = sz
        if name in list_names:
            #parse list
            print('fourcc', end='')
            fourcc = self.dr.GetBytes(4)
            pass
        while tsz > 0:
            psd = self.parse_fourcc(name)
            tsz -= psd
            print(f'parsed {name}, parsed: {psd}, remain unit: {tsz}, all: {sz}')
        return sz

    def parse_RIFF(self):
        return self.parse_unit()

    def parse_LIST(self):
        return self.parse_unit()

    def parse_AVI(self):
        return self.parse_unit()

    def parse_hdrl(self):
        return self.parse_unit()

    def parse_avih(self): # avi header 
        self.msec_per_frame = self.dr.Int32()
        self.Bytes_per_sec = self.dr.Int32()
        self.padd_gran = self.dr.Int32()
        self.flags = self.dr.Int32()
        self.num_frames = self.dr.Int32()
        self.init_frames = self.dr.Int32()
        self.streams = self.dr.Int32()
        self.szBuffer = self.dr.Int32()
        self.width = self.dr.Int32()
        self.height = self.dr.Int32()
        self.reserved0 = self.dr.GetBytes(4)
        self.reserved1 = self.dr.GetBytes(4)
        self.reserved2 = self.dr.GetBytes(4)
        self.reserved3 = self.dr.GetBytes(4)
        return 56

    def parse_fourcc(self, cc = ''):
        if len(cc) == 0:
            cc = self.dr.GetBytes(4)
        if type(cc) == bytes:
            cc = cc.decode('utf-8')
        try:
            sz = eval('self.parse_' + cc + '()')
        except Exception as e:
            print(f'error is occurred in fourcc parsing: {e}')
        return sz

    def open_AVI(self):
        self.dr = DataReader(self.filename)
        self.parse_unit()
        pass


if __name__ == '__main__':
    print("Main function")
    # test avi
    vc = VideoContainer()
    vc.open('test.avi')
    pass

    # test mkv
