#-*- encoding: utf-8
import numpy as np
from numba import jit, prange, jitclass, f8
from inpfile import InputFile
from rptfile import ReportFile
from solvers.dataset import Element, Magnet

# 時間ごとに重心が存在する

def provideelementhistories(inp: InputFile, rpt: ReportFile):
    histories = [None for _ in range(len(rpt.times))]

    for timeid in range(len(rpt.times)):
        nodes = {nodeid: pos for nodeid, pos in inp.nodes.items()}

        # 変位を反映させる
        for nodeid, node in inp.nodes.items():
            if inp.maxnodeid < nodeid:
                continue
            nodes[nodeid] = rpt.displacements[nodeid][timeid] + node    # 絶対座標上の変位

        histories[timeid] = [Element([nodes[e] for e in elem]) for elem in inp.elements.values()]

    return histories

class ElementProvider:
    @classmethod
    def histories(cls, inp: InputFile, rpt: ReportFile):
        return provideelementhistories(inp, rpt)

def providemagnethistories(inp: InputFile, rpt: ReportFile, topid: int, topRid: int, bottomid: int, bottomRid: int, magcharge: float):
    histories = [None for _ in range(len(rpt.times))]

    for timeid in range(len(rpt.times)):
        nodes = {nodeid: pos for nodeid, pos in inp.nodes.items()}

        pos = {i: inp.nodes[i] for i in [topid, bottomid, topRid, bottomRid]}
        for i, node in pos.items():
            pos[i] = rpt.displacements[i][timeid] + node
        
        histories[timeid] = Magnet(pos, topid, bottomid, topRid, bottomRid, magcharge)
    
    return histories

class MagnetProvider:
    @classmethod
    def histories(cls, inp: InputFile, rpt: ReportFile, topid: int, topRid: int, bottomid: int, bottomRid: int, magcharge: float):
        return providemagnethistories(inp, rpt, topid, topRid, bottomid, bottomRid, magcharge)


#inp = InputFile.open("./data/magnet.inp")
#rpt = ReportFile.open("./data/magnet-2500.rpt", inp.maxnodeid)

#import time
#start = time.time()
#hist = MagnetProvider.histories(inp, rpt, 2, 3, 6, 5)
#print(time.time() - start)
#print(hist)
