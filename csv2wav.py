#-*- encoding: utf-8
import sys
import wave
import struct

def printhelp():
    print("python csv2wav.py [sampling rate] [csv path] [wav path]")
    print("[summary]")
    print("    csv2wav.py makes a wav file based on a csv file.")
    print("    A csv file printed electromotive force from magnets.")
    print("[sampling rate]")
    print("    *Required parameter*")
    print("    It is the sampling rate for a wav file.")
    print("    The sampling rate is number of times")
    print("        obtained by dividing 1 second.")
    print("    For example, 44.1kHz is 44100.")
    print("[csv path]")
    print("    *Required parameter*")
    print("    electromotive.py ables to export a csv file.")
    print("    It is exported the electromotive force of the magnets")
    print("        described in multiple columns into a csv file.")
    print("    This parameter is it's the path.")
    print("[wav path]")
    print("    *Required parameter*")
    print("    csv2wav.py exports a wav file.")
    print("    A wav file is multiple track")
    print("        from the electromotive force of the magnets.")

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        printhelp()

    csvpath = sys.argv[-2]
    sampling_rate = int(sys.argv[-3])

    with open(csvpath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    data = []
    for line in lines[1:-1]:
        data.append([float(datum.strip()) for datum in line.split(",")[1:]])
    
    write = []
    write_append = write.append
    for did, _ in enumerate(data):
        for cid, _ in enumerate(data[did]):
            write_append(data[did][cid])
    
    wmax = max(write)
    wmin = min(write)
    if wmax < -wmin:
        wmax = -wmin

    for wid, _ in enumerate(write):
        write[wid] = write[wid] / wmax

    for wid, _ in enumerate(write):
        write[wid] = int(write[wid] * 32767.)

    record = bytes()
    for wid, _ in enumerate(write):
        record += struct.pack("<h", write[wid])

    wavpath = sys.argv[-1]
    with wave.open(wavpath, "wb") as wav:
        nchannel = len(lines[0].split(",")) - 1
        wav.setparams((
            nchannel, 2, sampling_rate, len(data), "NONE", "NONE"
        ))
        wav.writeframes(record)
        
