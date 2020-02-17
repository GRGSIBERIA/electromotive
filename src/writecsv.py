#-*- encoding: utf-8

def writecsv(js, timemagnets):
    header = "time"

    for part, conf in js.items():
        if "config" in part:
            continue

        if "magnet" in conf["type"]:
            header += "," + part
    
    with open(js["config"]["csv"], "w") as f:
        f.write(header + "\n")

        times = js["config"]["times"]

        for ti, magnets in enumerate(timemagnets):
            rs = str(times[ti])
            for mag in magnets:
                rs += "," + str(mag.inducedvoltage)
            f.write(rs + "\n")
    print("export {}".format(js["config"]["csv"]))
    
    # 磁石の磁束密度を求める，プラス極とマイナス極を考慮した値
    if "magnetic field csv" in js["config"]:
        with open(js["config"]["magnetic field csv"], "w") as f:
            f.write(header + "\n")
            times = js["config"]["times"]

            for ti, magnets in enumerate(timemagnets):
                rs = str(times[ti])
                for mag in magnets:
                    rs += "," + str(mag.inducedmagnetized)
                f.write(rs + "\n")
        print("export {}".format(js["config"]["magnetic field csv"]))