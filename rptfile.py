#-*- encoding: utf-8
import numpy as np

def readfile(path):
    with open(path, "r") as f:
        lines = f.readlines()
    return lines

def makeheaders(lines):
    headers = {}
    for i in range(len(lines)):
        if "  X  " in lines[i]:
            cnt = 1
            header = lines[i].split("  X  ")[-1].strip()
            while len(lines[i-cnt]) > 2 and i-cnt >= 0:
                header = lines[i-cnt].strip() + header
                cnt += 1
            headers[i+2] = header   # 実際に読み込み始める行数を挿入
    return headers

def getenablenodes(headers, maxnodeid):
    nodeaxis = {}
    for lineid, header in headers.items():
        nodeid = int(header.split(" N:")[1])
        if nodeid <= maxnodeid:
            axisid = int(header[3:4]) - 1
            nodeaxis[lineid] = {"nodeid": nodeid, "axisid": axisid}
    return nodeaxis

def gettimes(nodeaxis, lines):
    firstline = list(nodeaxis)[0]

    cnt = 0
    while len(lines[firstline + cnt]) > 4:
        cnt += 1
    times = np.zeros(cnt)

    cnt = 0
    while len(lines[firstline + cnt]) > 4:
        times[cnt] = float(lines[firstline + cnt].strip().split(" ")[0])
        cnt += 1
    return times

def setupdisplacements(nodeaxis, maxnodeid, positions, times, lines):

    for lineid, data in nodeaxis.items():
        
        axisid = data["axisid"]
        nodeid = data["nodeid"]

        if nodeid > maxnodeid:
            continue
        
        node = positions[nodeid]

        for timeid in range(len(times)):
            value = float(lines[lineid + timeid].strip().split(" ")[-1])
            node[timeid][axisid] = value


class ReportFile:
    def __init__(self, lines, maxnodeid, nodeaxis):
        self.times = gettimes(nodeaxis, lines)
        self.displacements = {i: [np.zeros(3) for _ in range(len(self.times))] for i in range(maxnodeid+1)}
        setupdisplacements(nodeaxis, maxnodeid, self.displacements, self.times, lines)
    
    @classmethod
    def open(cls, path, maxnodeid):
        lines = readfile(path)
        headers = makeheaders(lines)
        nodeaxis = getenablenodes(headers, maxnodeid)   # lineid => {nodeid, axisid}

        return ReportFile(lines, maxnodeid, nodeaxis)



import sys
import time
import os.path
from inpfile import InputFile

def printhelp():
    print("python report.py [input path] [report path]")
    sys.exit()


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        if "-h" == arg or "--help" == arg:
            printhelp()

    reportpath = sys.argv[2]
    inputpath = sys.argv[1]

    # ファイル検査
    if not os.path.isfile(reportpath) and not os.path.isfile(inputptah):
        printhelp()
    
    binpath = os.path.splitext(reportpath)[0] + ".bin"

    # 拡張子検査
    if not os.path.splitext(reportpath)[1] == ".rpt" and not os.path.splitext(inputpath)[1] == ".inp":
        printhelp()
    
    inpfile = InputFile.open(inputpath)
    maxnodeid = inpfile.maxnodeid

    start = time.time()
    repfile = ReportFile.open(reportpath, maxnodeid)
    print("report file reading time: " + str(time.time() - start) + " sec")
