#-*- encoding: utf-8
import struct
from rptfile import ReportFile
from inpfile import InputFile

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
                pos = displacement[timeid] + inp.nodes[nodeid]
                pk = struct.pack("=3d", pos)
                f.write(pk)