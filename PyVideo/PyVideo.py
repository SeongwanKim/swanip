import numpy as np
import struct 
import matplotlib.pyplot as plt


class DataReader:
    self.szBuffer = 16384
    def __init__ (self, filename):
        self.fp = open(filename, 'rb')
        self.buf = self.fp.read(Datareader.szBuffer)


class VideoContainer:
    def __init__(self):
        pass

    def open(self, filename):
        self.filename = filename
        if filename[-4:].lower() == '.avi':
            self.open_AVI()
        pass

    def open_AVI(self):
        self.dr = DataReader(self.filename)
        pass

if __name__ == '__main__':
    print("Main function")
    # test avi
    vc = VideoContainer()
    vc.open('test.avi')

    # test mkv
