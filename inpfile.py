#-*- encoding: utf-8
import time
import sys
import numpy as np
from config import Config

def readlines(path):
    with open(path, "r") as f:
        lines = f.readlines()
    if len(lines[-1]) < 4:
        return lines[0:-1]
    return lines

def isNode(line):
    return True if "*Node" in line else False

def isElement(line):
    return True if "*Element" in line else False

def isTranslate(lines, transid):
    if len(lines) <= transid:
        return False
    return True if "*Translate" in lines[transid] else False

#@jit("i8(u1[:], i8)")
def numofSize(lines, start):
    count = 0
    while start + count < len(lines):
        if "*" in lines[start + count]:
            break
        count += 1
    return count

def extractNode(lines, nodeCount, translate):
    data = [line.split(",") for line in lines[1:nodeCount+1]]
    return {int(datum[0]): np.array([float(x) for x in datum[1:4]]) + translate for datum in data}

def extractElement(lines, start, elemCount):
    data = [line.split(",") for line in lines[start:start+elemCount]]
    return {int(datum[0]): [int(x) for x in datum[1:5]] for datum in data}

def getmaxnodeid(elements):
    maxid = 0
    for elem in elements.values():
        for nid in elem:
            if maxid < nid:
                maxid = nid
    return maxid

class InputFile:
    def __init__(self, nodeCount: int, elemCount: int, maxnodeid: int, nodes, elements):
        self.nodeCount = nodeCount
        self.elemCount = elemCount
        self.maxnodeid = maxnodeid
        self.nodes = nodes
        self.elements = elements
    
    @classmethod
    def open(cls, path):
        lines = readlines(path)

        translate = np.zeros(3)

        if isNode(lines[0]):
            nodeCount = numofSize(lines, 1)
        else:
            raise Exception("Syntax Error: undefined *Node, lineno=" + str(1))
        
        if isElement(lines[1 + nodeCount]):
            elemCount = numofSize(lines, 2 + nodeCount)
        else:
            raise Exception("Syntax Error: undefined *Element, lineno=" + str(2 + nodeCount))

        transid = nodeCount + elemCount + 2
        if isTranslate(lines, transid):
            translate = np.array([float(e) for e in lines[transid+1].split(",")])

        nodes = extractNode(lines, nodeCount, translate)
        elements = extractElement(lines, 2 + nodeCount, elemCount)
        maxnodeid = getmaxnodeid(elements)

        return InputFile(nodeCount, elemCount, maxnodeid, nodes, elements)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("python inpfile.py [config file path]")
        sys.exit()

    confpath = sys.argv[1]
    js = Config.open(confpath)
    print("element name: number of valid 1-dim node")
    for name, value in js.items():
        if name == "config":
            continue
        
        if value["type"] == "element":
            inp = InputFile.open(value["input"])
            print("{0}: {1}".format(name, inp.maxnodeid))
            