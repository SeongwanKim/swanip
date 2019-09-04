import numpy as np
import struct 
import matplotlib.pyplot as plt


class DataReader:
    szBuffer = 32768
    log = True
    def __init__ (self, filename):
        self.fp = open(filename, 'rb')
        self.buf = self.fp.read(DataReader.szBuffer)
        self.pos = 0
        self.cur_unit = 0
        self.prev_pos = 0
        pass

    def szHelper(self):
        sz = self.pos - self.cur_unit
        self.cur_unit = self.pos
        return sz

    def GetBytes(self, n):
        if n > DataReader.szBuffer:
            print('ERROR. buffersize is too small.', n, DataReader.szBuffer)
            DataReader.szBuffer = n * 2;
        tpos = self.pos - self.prev_pos
        if (self.pos + n - self.prev_pos) > len(self.buf):
            self.prev_pos = self.pos
            buf2 = self.buf[tpos:] + self.fp.read(DataReader.szBuffer)
            self.buf = buf2
        ret = self.buf[tpos:(tpos+n)]
        self.pos += n
        if DataReader.log:
            print(hex(self.pos), ret[:8])
        return ret
    
    def Int32(self):
        return self.DWORD()
    
    def fourcc(self):
        return self.GetBytes(4).decode()

    def WORD(self):
        ret = self.GetBytes(2)
        sz = int.from_bytes(ret, 'little')
        if DataReader.log:
            print('WORD: ', sz)
        return sz
        
    def DWORD(self):
        ret = self.GetBytes(4)
        sz = int.from_bytes(ret, 'little')
        if DataReader.log:
            print('DWORD: ', sz)
        return sz

    def LONG(self):
        ret = self.GetBytes(4)
        sz = int.from_bytes(ret, 'little')
        if DataReader.log:
            print('DWORD: ', sz)
        return sz

    def RECT(self):
        sz = []
        sz.append(self.WORD())
        sz.append(self.WORD())
        sz.append(self.WORD())
        sz.append(self.WORD())
        return sz

class VideoContainer:
    def __init__(self):
        self.stream_headers = []
        self.stream_info = {}
        self.avih = {}
        pass

    def open(self, filename):
        self.filename = filename
        if filename[-4:].lower() == '.avi':
            self.open_AVI()
        pass

    def parse_unit(self, name = ''):
        empty_names = ['AVI ', 'hdrl', 'strl', 'INFO']
        if name == '':
            name = self.dr.GetBytes(4)
        if type(name) == bytes:
            name = name.decode('utf-8')
        if name in empty_names:
            sz = self.parse_unit()
            return sz
        sz = self.dr.Int32()
        tsz = sz
        psd = self.parse_fourcc(name, sz)
        tsz -= psd
        print(f'parsed {name}, parsed: {psd}, remain unit: {tsz}, all: {sz}')
        #while (tsz > 0):
            #self.parse_unit()
        return sz - tsz

    def fourcc_ISFT(self, sz):
        print(f'parsing ISFT, all: {sz}')
        self.stream_info['ISFT'] = self.dr.GetBytes(sz)
        return sz

    def fourcc_RIFF(self, sz):
        tsz = sz
        while (tsz > 0):
            psd = self.parse_unit()
            tsz -= psd
            print(f'parsing RIFF, parsed: {psd}, remain unit: {tsz}, all: {sz}')
        return sz

    def fourcc_LIST(self, sz):
        tsz = sz
        self.latest_tsz = tsz
        while (tsz > 0):
            psd = self.parse_unit()
            tsz -= psd
            self.latest_tsz = tsz
            print(f'parsed LIST, parsed: {psd}, remain unit: {tsz}, all: {sz}')
        return sz - tsz

    def fourcc_AVI(self, sz):
        tsz = sz
        while (tsz > 0):
            psd = self.parse_unit()
            tsz -= psd
            print(f'parsed AVI, parsed: {psd}, remain unit: {tsz}, all: {sz}')
        return sz

    def fourcc_hdrl(self, sz):
        tsz = sz
        while (tsz > 0):
            psd = self.parse_unit()
            tsz -= psd
            print(f'parsed hdrl, parsed: {psd}, remain unit: {tsz}, all: {sz}')
        return sz

    def fourcc_strn(self, sz):
        self.dr.szHelper()
        sz = (sz + 1 ) & 0xFFFFFFFE
        self.stream_headers[-1]['name'] = self.dr.GetBytes(sz).decode()
        return self.dr.szHelper()

    def fourcc_JUNK(self,sz):
        self.dr.szHelper()
        sz = (sz + 1 ) & 0xFFFFFFFE
        #sz = (sz + 15 ) & 0xFFFFFFF0
        self.stream_headers[-1]['junk'] = self.dr.GetBytes(sz)
        return self.dr.szHelper()

    def fourcc_movi(self,sz):
        #TODO: fill it. 
        # refer to 
        tsz = self.latest_tsz
        psd = tsz
        first = True
        while psd > 0:
            self.dr.szHelper()
            if first:
                tag = sz.to_bytes(4,'little').decode()
                first = False
            else:
                tag = self.dr.fourcc()
            print('movi', tag, int(tag[:2]), tag[2:], psd)

            if tag[2:] == 'wb': # audio
                headers = self.stream_headers[self.audio_idx]
                real_size = headers['SampleSize']
                real_size = self.dr.Int32()
                real_size = (real_size + 1 ) & 0xFFFFFFFE
                buffer = self.dr.GetBytes(real_size)
                psd -= self.dr.szHelper()
                pass
            elif tag[2:] == 'dc': # video 
                real_size = self.dr.Int32()
                real_size = (real_size + 1 ) & 0xFFFFFFFE
                buffer = self.dr.GetBytes(real_size)
                psd -= self.dr.szHelper()
                pass
            else: 
                print('Unknown type???:')
        return tsz - psd





    def fourcc_avih(self, sz): # avi header 
        self.dr.szHelper()
        self.avih['msec_per_frame'] = self.dr.DWORD()
        self.avih['Bytes_per_sec'] = self.dr.DWORD()
        self.avih['padd_gran'] = self.dr.DWORD()
        self.avih['flags'] = self.dr.DWORD()
        self.avih['num_frames'] = self.dr.DWORD()
        self.avih['init_frames'] = self.dr.DWORD()
        self.avih['streams'] = self.dr.DWORD()
        self.avih['szBuffer'] = self.dr.DWORD()
        self.avih['width'] = self.dr.DWORD()
        self.avih['height'] = self.dr.DWORD()
        self.avih['reserved0'] = self.dr.GetBytes(4)
        self.avih['reserved1'] = self.dr.GetBytes(4)
        self.avih['reserved2'] = self.dr.GetBytes(4)
        self.avih['reserved3'] = self.dr.GetBytes(4)
        return self.dr.szHelper()

    def fourcc_strh(self, sz):
        self.dr.szHelper()
        strh = {}
        strh['fccType'] = self.dr.fourcc()
        strh['fccHandler'] = self.dr.fourcc()
        strh['dwFlags'] = self.dr.DWORD()
        strh['Priority'] = self.dr.WORD()
        strh['Language'] = self.dr.WORD()
        strh['InitialFrames'] = self.dr.DWORD()
        strh['Scale'] = self.dr.DWORD()
        strh['Rate'] = self.dr.DWORD()
        strh['Start'] = self.dr.DWORD()
        strh['Length'] = self.dr.DWORD()
        strh['BufferSize'] = self.dr.DWORD()
        strh['Quality'] = self.dr.DWORD()
        strh['SampleSize'] = self.dr.DWORD()
        strh['rectFrame'] = self.dr.RECT()
        if strh['fccType'] == 'vids':
            self.video_idx = len(self.stream_headers)
        elif strh['fccType'] == 'auds':
            self.audio_idx = len(self.stream_headers)
        self.stream_headers.append(strh)
        return self.dr.szHelper()

    def fourcc_strf(self, sz):
        self.dr.szHelper()
        type = self.stream_headers[-1]['fccType']
        if  type == 'vids':
            self.stream_headers[-1]['Size'] = self.dr.DWORD()
            self.stream_headers[-1]['Width'] = self.dr.LONG()
            self.stream_headers[-1]['Height'] = self.dr.LONG()
            self.stream_headers[-1]['Planes'] = self.dr.WORD()
            self.stream_headers[-1]['BitCount'] = self.dr.WORD()
            self.stream_headers[-1]['Compression'] = self.dr.DWORD()
            self.stream_headers[-1]['SizeImage'] = self.dr.DWORD()
            self.stream_headers[-1]['XPelsPerMeter'] = self.dr.LONG()
            self.stream_headers[-1]['YPelsPerMeter'] = self.dr.LONG()
            self.stream_headers[-1]['ClrUsed'] = self.dr.DWORD()
            self.stream_headers[-1]['ClrImportant'] = self.dr.DWORD()
            if sz > 40:
                print(f'parse remain data: {sz}')
                self.stream_headers[-1]['Remains'] = self.dr.GetBytes(sz - 40)
            pass
        elif type == 'auds': # https://docs.microsoft.com/en-us/previous-versions/dd757713(v%3dvs.85)
            self.stream_headers[-1]['FormatTag'] = self.dr.WORD()
            self.stream_headers[-1]['Channels'] = self.dr.WORD()
            self.stream_headers[-1]['SamplesPerSec'] = self.dr.DWORD()
            self.stream_headers[-1]['AvgBytesPerSec'] = self.dr.DWORD()
            self.stream_headers[-1]['BlockAlign'] = self.dr.WORD()
            self.stream_headers[-1]['BitsPerSample'] = self.dr.WORD()
            self.stream_headers[-1]['bSize'] = self.dr.WORD()
            if sz > 18:
                print(f'parse remain data: {sz}')
                self.stream_headers[-1]['Remains'] = self.dr.GetBytes(sz - 18)
            pass
        else:
            print(f'unknown type stream format {type}, {sz}')
            pass
        return self.dr.szHelper()

    def parse_fourcc(self, cc = '', sz = 0):
        if len(cc) == 0:
            cc = self.dr.GetBytes(4)
        if type(cc) == bytes:
            cc = cc.decode('utf-8')
        try:
            sz = eval(f'self.fourcc_{cc}({sz})')
        except Exception as e:
            r = input(f'error is occurred in fourcc parsing: {e}')
            pass
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
