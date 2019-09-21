#-*- encoding: utf-8
import time
import struct
import wave
import sys
import pprint
import win_unicode_console
from typing import List
import os.path
from concurrent import futures
import numpy as np
import matplotlib.pyplot as plot
from config import Config
from inpfile import InputFile
from rptfile import ReportFile
from solver import Solver
from binary import writebinary, readbinary, SequentialReportReader
from solvers.dataset import Element, Magnet
from src.progressbar import ProgressBar


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
    append_element = elements.append
    append_magnet = magnets.append

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
            
            for eid, elem in inp.elements.items():
                enode = [inp.nodes[nid] for nid in elem]
                append_element(Element(enode, mag))

            # TODO: CLEAR
            # Elementはsrc/dataset.pyを使っているので，solvers/dataset.pyのものを使う
            # いくつか修正する必要があるらしい

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
            
            append_magnet(Magnet(tcp, trp, bcp, brp, mag))

            # TODO: CLEAR
            # Magnetには座標ではなく変位が入っているのでゼロ除算が起きている
            # 変位から座標値を追加する方法を検討しなければならない

    return elements, magnets


def computemagneticfield(js, solver, i, result_magnets):
    elements, magnets = receiveelementsandmagnetseachtime(js)
        
    solver.computemagnetize(elements, magnets)
    solver.computeinduce(elements, magnets)
    
    result_magnets[i] = magnets


def solve(path: str) -> List[List[Magnet]]:
    print("--- start import ---")
    js = Config.open(path)
    
    times = setupconfiguration(js)

    result_magnets = [None for _ in times] # 誘導起電力を算出するのに必要
    
    solver = Solver(js["config"]["solver"])

    print("----- start solving magnetic field ---")

    progress = ProgressBar(len(times))

    # マルチスレッドで実行
    with futures.ThreadPoolExecutor() as executor:
        fs = []
        for i, _ in enumerate(times):
            fs.append(executor.submit(computemagneticfield, js, solver, i, result_magnets))

        for f in futures.as_completed(fs):
            progress.incrementasprint()
            # TODO: CLEAR
            # 残り時間を表示する部分を作る

        print("")   # 改行して再開する必要がある
    solver.computeinductance(result_magnets, times)

    return result_magnets


def printhelp():
    print("python electromotive.py [options] [config json file path]")
    print("[summary]")
    print("    electromotive.py computes the inductance from each magnets.")
    print("    It works to require a config json file.")
    print("    Default options -c (enabled to write .csv files).")
    print("[options]")
    print("    -a     analyzes the inductance from a config json file.")
    print("    -s     summaries input files each parts.")
    print("    -w     bakes the inductance in .wav files each magnets.")
    print("    -c     bakes the inductance in .csv files each magnets.")
    print("    -h     shows a help.")
    print("[config json file path]")
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

    if "-s" in commands:
        summarizeinpfile(sys.argv[-1])
    
    if "-h" in commands:
        printhelp()
    else:
        magnets = solve(sys.argv[-1])

        if "-w" in commands:
            # TODO: UNCOMPLETE
            # magnetsの結果をファイルに出力する
            pass
        
        if "-c" in commands:
            pass

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