import numpy as np
import struct 
import matplotlib.pyplot as plt

class VideoContainer:
    def __init__(self):
        pass

    def __init__(self, filename):
        self.__init__()
        self.open(filename)

    def open(self, filename):
        self.filename = filename
        if filename[-4:].lower() == '.avi':
            self.open_AVI()
        pass

    def open_AVI(self):
        pass

if __name__ == '__main__':
    print("Main function")
