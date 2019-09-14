#-*- encoding: utf-8
import time
import struct
import wave
import sys
from typing import List
import os.path
import numpy as np
import matplotlib.pyplot as plot
from config import Config
from inpfile import InputFile
from rptfile import ReportFile
from provider import ElementProvider, MagnetProvider
from solver import Solver
from binary import writebinary, readbinary, SequentialReportReader


def configuration(conf):
    wavpath = None
    srate = None
    if "wav" in conf:
        wavpath = conf["wav"]
        srate = conf["sampling rate"]
    return (conf["solver"], conf["output"], wavpath, srate)


def readingconfiguration(part: str, conf) -> List[float]:
    print("import %s" % part)

    inp = InputFile.open(conf["input"])
    print(conf["input"])

    brppath = os.path.splitext(conf["report"])[0] + ".brp"
    if not os.path.exists(brppath):
        rpt = ReportFile.open(conf["report"], inp.maxnodeid)
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

    for part, conf in js.items():
        if part == "config":
            solvername, outputpath, wavpath, srate = configuration(conf)
            continue

        start = time.time()

        times = readingconfiguration(part, conf)

        print("done import {} - {} sec".format(part, time.time() - start))

    print("--- done import all ---")

    #del js["config"]
    #elements = [elem["history"] for elem in js.values() if elem["type"] == "element"]
    #magnets = [mag["history"] for mag in js.values() if mag["type"] == "magnet"]

    #Solver.solve(solvername, elements, magnets, times)

    #return times, magnets, outputpath, wavpath, srate


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("python electromotive.py [configure json file path]")
    if not os.path.exists(sys.argv[1]):
        print("python electromotive.py [configure json file path]")

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