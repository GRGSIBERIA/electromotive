#-*- encoding: utf-8
import struct
import sys
import io
import os.path
from typing import Dict, List
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
8*3 byte double 位置
以下，nだけ繰り返し

---------

以下，tだけ繰り返し
"""
def writebinary(report: ReportFile, inp: InputFile,  path: str):
    with open(path, "wb") as f:
        print("number of times: " + str(len(report.times)))
        pk = struct.pack("<L", len(report.times))
        f.write(pk)

        for time in report.times:
            pk = struct.pack("<d", time)
            f.write(pk)
        
        print("number of displacements: " + str(len(report.displacements.keys())))
        pk = struct.pack("<L", len(report.displacements.keys()))
        f.write(pk)

        ba = bytes()
        for timeid, _ in enumerate(report.times):
            for nodeid, displacement in report.displacements.items():
                if nodeid in inp.nodes:
                    pos = displacement[timeid] + inp.nodes[nodeid]
                    ba += struct.pack("<L3d", nodeid, *pos)
        f.write(ba)


def readtimes(f: io.BufferedIOBase) -> List[float]:
    b = f.read(4)
    numof_times = struct.unpack_from("<L", b, 0)[0]
    times = [0.0 for _ in range(numof_times)]
    bs = f.read(8 * numof_times)
    for i, _ in enumerate(times):
        times[i] = struct.unpack_from("<d", bs, 8 * i)
    return times


def readnumnode(f: io.BufferedIOBase):
    b = f.read(4)
    return struct.unpack_from("<L", b, 0)[0]


class SequentialReportReader:
    def __init__(self, f: io.BufferedIOBase):
        self.file = f
        self.times = readtimes(self.file)
        self.numnodes = readnumnode(self.file)
        self.count = 1
        print("number of nodes: " + str(self.numnodes))
        print("number of times: " + str(len(self.times)))


    def __del__(self):
        self.file.close()
    

    def read(self) -> Dict[int, np.ndarray]:
        if len(self.times) < self.count:
            raise StopIteration()

        chunksize = 8 * 3 + 4

        pos = {}
        for i in range(self.numnodes):
            bs = self.file.read(chunksize)
            unp = struct.unpack("<L3d", bs)
            nodeid = unp[0]
            disp = np.array(unp[1:])
            pos[nodeid] = disp

        self.count += 1

        return pos


def readbinary(path: str) -> SequentialReportReader:
    if not os.path.isfile(path):
        print("File not exists: " + path)
        sys.exit()
    
    f = open(path, "rb")
    return SequentialReportReader(f)


def printhelp():
    print("python binary.py [flag] [config path]")
    print("flag is")
    print("       -s summarize report")
    print("       -w write binary")
    sys.exit()


def validitem(key, val) -> bool:
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

    js = Config.open(path)

    for key, val in js.items():
        if not validitem(key, val):
            continue

        inp = InputFile.open(val["input"])
        rep = ReportFile.open(val["report"], inp.maxnodeid)

        if flag == "-w":
            path = os.path.splitext(val["report"])[0] + ".brp"
            writebinary(rep, inp, path)
            print("converted: " + path)
        elif flag == "-s":
            print(key)
            print("maximum nodeid: ", inp.maxnodeid)
            print("number of times: ", len(rep.times))
