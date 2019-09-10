#-*- encoding: utf-8
import struct
import sys
import io
import os.path
import numpy as np
from rptfile import ReportFile
from inpfile import InputFile
from config import Config

"""書き込みフォーマット
4 byte int 時刻数, t
8*t byte double 時刻

---------

4 byte int ノード数, n

---------

4 byte int ノード番号
24 byte double 位置
以下，nだけ繰り返し

---------

以下，tだけ繰り返し
"""
def writebinary(report: ReportFile, inp: InputFile,  path: str):
    with open(path, "wb") as f:
        pk = struct.pack("L", len(report.times))
        f.write(pk)

        for time in report.times:
            pk = struct.pack("d", time)
            f.write(pk)
        
        pk = struct.pack("L", len(report.displacements.keys()))
        for timeid, _ in enumerate(report.times):
            for nodeid, displacement in report.displacements.items():
                if nodeid in inp.nodes:
                    pos = displacement[timeid] + inp.nodes[nodeid]
                    pk = struct.pack("L3d", nodeid, *pos)
                    f.write(pk)

def readbinary(path: str):
    if not os.path.isfile(path):
        print("File not exists: " + path)
        sys.exit()
    
    f = open(path, "rb")
    return SequentialReportReader(f)


def readtimes(f: io.BufferedIOBase):
    b = f.read(4)
    numof_times = struct.unpack_from("L", b, 0)
    times = [0.0 for _ in range(numof_times)]
    bs = f.read(8 * numof_times)
    for i, _ in enumerate(times):
        times[i] = struct.unpack_from("d", bs, 8 * i)
    return times


def readnumnode(f: io.BufferedIOBase):
    b = f.read(4)
    return struct.unpack_from("L", b, 0)


class SequentialReportReader:
    def __init__(self, f: io.BufferedIOBase):
        self.file = f
        self.times = readtimes(self.file)
        self.numnodes = readnumnode(self.file)
        self.count = 0
    
    def __del__(self):
        self.file.close()
    
    """[summary]

    Raises:
        StopIteration: イテレーションを終了させる
    """
    def iter_read(self):
        if self.numnodes <= self.count:
            raise StopIteration()
        
        self.count += 1

        try:
            bs = self.file.read(8 * 3 + 4)
        except:
            raise StopIteration()
        
        pos = {}
        for i, _ in enumerate(self.numnodes):
            unp = struct.unpack_from("L3d", bs, (4 + 8) * i)
            nodeid = unp[0]
            disp = np.array(unp[1:])
            pos[nodeid] = disp

        yield pos

def printhelp():
    print("python binary.py [flag] [config path]")
    print("flag is")
    print("       -s summarize binary")
    print("       -w write binary")
    sys.exit()


def validitem(key, val):
    if key == "config":
        return False
    if not os.path.isfile(val["input"]) and not os.path.isfile(val["report"]):
        return False
    return True

if __name__ == "__main__":
    if len(sys.argv) != 3:
        printhelp()
    flag = sys.argv[1]
    path = sys.argv[2]
    if not os.path.isfile(path) and ("-s" == flag or "-w" == flag):
        printhelp()

    if flag == "-w":
        js = Config.open(path)
        for key, val in js.items():
            if validitem(key, val):
                continue
            
            inp = InputFile.open(val["input"])
            rep = ReportFile.open(val["report"], inp.maxnodeid)
            path = os.path.splitext(val["report"])[0] + ".brp"
            writebinary(rep, inp, path)
            print("converted: " + path)
    elif flag == "-s":
        js = Config.open(path)
