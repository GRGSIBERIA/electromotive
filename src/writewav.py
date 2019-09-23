#-*- encoding: utf-8
import struct
import wave
import numpy as np 
from solvers.dataset import Magnet
from typing import List


def extractinductance(i: int, timemags: List[List[Magnet]]) -> np.ndarray:
    times = [time[i].inducedvoltage for time in timemags]
    return np.array(times)


def createwav(path: str, times: List[float], samplerate: int):
    y = [int(time) for time in times / np.max(times) * 32767. * 0.8]
    data = struct.pack("h" * len(y), *y)
    with wave.open(path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(samplerate)
        w.writeframes(data)


def writewav(js, timemags: List[List[Magnet]]):
    parts = []
    for part, conf in js.items():
        if "config" not in part:
            if "magnet" in js[part]["type"]:
                parts.append(js[part])
    
    for i, part in enumerate(parts):
        if "wav" in part:
            path = part["wav"]
            times = extractinductance(i, timemags)
            createwav(path, times, js["config"]["sampling rate"])
            print("extport {}".format(path))


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