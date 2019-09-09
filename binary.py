#-*- encoding: utf-8
import struct
import sys
import os.path
from rptfile import ReportFile
from inpfile import InputFile
from config import Config

"""書き込みフォーマット
4 byte int 時刻数, t
8*t byte double 時刻

4 byte int ノード数, n
8*3*n byte double 変位
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
                    pk = struct.pack("=3d", *pos)
                    f.write(pk)

if __name__ == "__main__":
    if not os.path.isfile(sys.argv[1]):
        print("python binary.py [config path]")
        sys.exit()

    js = Config.open(sys.argv[1])
    for key, val in js.items():
        if key == "config":
            continue
        if val["type"] == "element":
            if not os.path.isfile(val["input"]) and not os.path.isfile(val["report"]):
                continue
            inp = InputFile.open(val["input"])
            rep = ReportFile.open(val["report"], inp.maxnodeid)
            path = os.path.splitext(val["report"])[0] + ".brp"
            writebinary(rep, inp, path)
            print("converted: " + path)
