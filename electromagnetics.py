#-*- encoding: utf-8
import time
import struct
import wave
import numpy as np
import matplotlib.pyplot as plot
from config import Config
from inpfile import InputFile
from rptfile import ReportFile
from provider import ElementProvider, MagnetProvider
from solver import Solver

def configuration(conf):
    wavpath = None
    srate = None
    if "wav" in conf:
        wavpath = conf["wav"]
        srate = conf["sampling rate"]
    return (conf["solver"], conf["output"], wavpath, srate)

def solve(path):
    print("--- start import ---")
    js = Config.open(path)
    numoftimes = 0

    for part, conf in js.items():
        if part == "config":
            solvername, outputpath, wavpath, srate = configuration(conf)
            continue

        start = time.time()
        print("import %s" % part)
        inp = InputFile.open(conf["input"])
        print(conf["input"])
        rpt = ReportFile.open(conf["report"], inp.maxnodeid)
        print(conf["report"])
        conf["inpdata"] = inp
        conf["rptdata"] = rpt
        times = rpt.times
        numoftimes = len(rpt.times)

        if conf["type"] == "element":
            conf["history"] = ElementProvider.histories(inp, rpt)
        elif conf["type"] == "magnet":
            conf["history"] = MagnetProvider.histories(inp, rpt, 
                conf["top"]["point"], conf["top"]["right"], 
                conf["bottom"]["point"], conf["bottom"]["right"], conf["magnetic charge"])
        
        print("done import {} - {} sec".format(part, time.time() - start))

    print("--- done import all ---")

    del js["config"]
    elements = [elem["history"] for elem in js.values() if elem["type"] == "element"]
    magnets = [mag["history"] for mag in js.values() if mag["type"] == "magnet"]

    Solver.solve(solvername, elements, magnets, times)

    return times, magnets, outputpath, wavpath, srate

#plot.figure(figsize=(8,4))
#plot.plot(js["tine"]["rptdata"].times, [hist[885].centroid[1] for hist in js["tine"]["history"]])
#plot.plot(js["tonebar"]["rptdata"].times, [hist[1476].centroid[1] for hist in js["tonebar"]["history"]])
#plot.xlabel("Time [sec]")
#plot.ylabel("Displacement [mm]")

#plot.tight_layout()
#plot.show()

if __name__ == "__main__":
    times, magnets, outputpath, wavpath, srate = solve("./data/config.json")

    #plot.figure()
    y = np.array([history.inducedvoltage for history in magnets[0]])
    x = np.array(times)
    #plot.plot(x, y)
    #plot.show()

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
