#-*- encoding: utf-8
import time
import struct
import wave
import sys
import pprint
import win_unicode_console
from typing import List
import os.path
import numpy as np
import matplotlib.pyplot as plot
from config import Config
from inpfile import InputFile
from rptfile import ReportFile
#from provider import ElementProvider, MagnetProvider
#from solver import Solver
from binary import writebinary, readbinary, SequentialReportReader
from src.dataset import Element, Magnet


# デバッグ便利関数
win_unicode_console.enable()
pp = pprint.PrettyPrinter(indent=4)


def configuration(conf):
    wavpath = None
    srate = None
    if "wav" in conf:
        wavpath = conf["wav"]
        srate = conf["sampling rate"]
    return (conf["solver"], conf["output"], wavpath, srate)


def readingconfiguration(part: str, conf) -> List[float]:
    print("----- import %s" % part)

    inp = InputFile.open(conf["input"])
    print(conf["input"])

    brppath = os.path.splitext(conf["report"])[0] + ".brp"
    if not os.path.exists(brppath):
        rpt = ReportFile.open(conf["report"], inp.maxnodeid)

        if conf["type"] == "magnet":
            pp.pprint(rpt.displacements)

        writebinary(rpt, inp, brppath)
    brp = readbinary(brppath)
    print(conf["report"])

    conf["inpdata"] = inp
    conf["rptdata"] = brp

    return brp.times


def setupconfiguration(js) -> List[float]:
    times = None

    # 計算の下準備
    for part, conf in js.items():
        if part == "config":
            solvername, outputpath, wavpath, srate = configuration(conf)
            continue

        start = time.time()

        # 時間の長さが異なるかどうかチェックする
        times_temp = readingconfiguration(part, conf)
        if times != None:
            if len(times) != len(times_temp):
                raise Exception(part + "is not equal to " + str(len(times)))
        times = times_temp

        print("done import {} - {} sec".format(part, time.time() - start))

    print("--- done import all ---")
    print("--- start solving electromotive ---")

    return times


def receiveelementsandmagnetseachtime(js):
    elements = []
    magnets = []

    for part, conf in js.items():
        if part == "config":
            continue

        try:
            data = conf["rptdata"].read()
        except StopIteration:
            break

        inp = conf["inpdata"]

        if conf["type"] == "element":
            mag = conf["magnetic permeability"]
            for nid, pos in data.items():
                inp.nodes[nid] += pos
            elements += [Element(pos, mag) for _, pos in inp.nodes.items()]

        elif conf["type"] == "magnet":
            tc = conf["top"]["center"]
            tr = conf["top"]["right"]
            bc = conf["bottom"]["center"]
            br = conf["bottom"]["right"]
            mag = conf["magnetic charge"]
            tcp = data[tc] + inp.nodes[tc]
            trp = data[tr] + inp.nodes[tr]
            bcp = data[bc] + inp.nodes[bc]
            brp = data[br] + inp.nodes[br]
            
            magnets.append(Magnet(tcp, trp, bcp, brp, mag))
            # TODO: CLEAR
            # Magnetには座標ではなく変位が入っているのでゼロ除算が起きている
            # 変位から座標値を追加する方法を検討しなければならない
    return elements, magnets


def solve(path: str):
    print("--- start import ---")
    js = Config.open(path)

    times = setupconfiguration(js)
    inductance = []
    
    numtimes = len(times)
    difftimes = 1.0 / float(numtimes)

    for t in times:
        elements, magnets = receiveelementsandmagnetseachtime(js)
        print(len(elements))


def printhelp():
    print("python electromotive.py [options] [configure json file path]")
    print("[options]")
    print("    -a     analyzes the electromotive from a configure json file.")
    print("    -si    summaries an input file.")
    print("    -h     shows a help.")
    print("[configure json file path]")
    print("    This is a required option.")


from inpfile import summarizeinpfile


if __name__ == "__main__":
    # 検査
    validation = [not os.path.exists(sys.argv[-1])]
    for val in validation:
        if val:
            printhelp()
            sys.exit()

    commands = {c: 1 for c in sys.argv[1:-1]}

    if "-si" in commands:
        summarizeinpfile(sys.argv[-1])
    
    if "-h" in commands:
        printhelp()
    else:
        solve(sys.argv[-1])

    print("--- exit electromotive ---")


"""
    times, magnets, outputpath, wavpath, srate = solve(sys.argv[1])

    y = np.array([history.inducedvoltage for history in magnets[0]])
    x = np.array(times)

    with open(outputpath, "w") as f:
        for i, _ in enumerate(x):
            f.write("{},{}\n".format(x[i], y[i]))
    
    if wavpath != None:
        y = [int(datum) for datum in y / np.max(y) * 32767. * 0.8]
        data = struct.pack("h" * len(y), *y)
        w = wave.open(wavpath, "w")
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(srate)
        w.writeframes(data)
        w.close()
"""