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


def solve(path: str):
    print("--- start import ---")
    js = Config.open(path)

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

    inductance = []
    numtimes = len(times)
    difftimes = 1.0 / float(numtimes)

    for t in times:
        elements = []
        magnets = []

        for part, conf in js.items():
            if part == "config":
                continue

            try:
                data = conf["rptdata"].read()
            except StopIteration:
                break

            if conf["type"] == "element":
                mag = conf["magnetic permeability"]
                elements += [Element(pos, mag) for _, pos in data.items()]
            elif conf["type"] == "magnet":
                tc = conf["top"]["center"]
                tr = conf["top"]["right"]
                bc = conf["bottom"]["center"]
                br = conf["bottom"]["right"]
                mag = conf["magnetic charge"]
                magnets.append(Magnet(data[tc], data[tr], data[bc], data[br], mag))


def printhelp():
    print("python electromotive.py [options] [configure json file path]")
    print("[options]")
    print("    -a     analyzes the electromotive from a configure json file.")
    print("    -si    summarizes an input file.")
    print("    -h     shows a help.")
    print("[configure json file path]")
    print("    This is a required option.")


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        printhelp()
    if not os.path.exists(sys.argv[-1]):
        printhelp()

    commands = {c: 1 for c in sys.argv[1:-1]}

    if "-si" in commands:
        pass
    elif "-h" in commands:
        printhelp()

    solve(sys.argv[1])

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