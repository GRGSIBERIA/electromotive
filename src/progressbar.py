#-*- encoding: utf-8

class ProgressBar:
    def __init__(self, num: int, width=72):
        self.num = num
        self.percentile = 0.0
        self._widthpercentile = 0.0
        self._dp = 100.0 / float(num)
        self._dw = float(width) / float(num)
        self._width = width
    
    def incrementasprint(self):
        self.percentile += self._dp
        self._widthpercentile += self._dw
        
        fill = int(self._widthpercentile)
        space = self._width - fill
        string = ""
        for i in range(fill):
            string += "%"
        for i in range(space):
            string += " "
        print("\r[{:}] {: >6.2f} / {:>3.2f}".format(string, self.percentile, 100.00), end="")


if __name__ == "__main__":
    num = 100000
    ps = ProgressBar(num)
    for _ in range(num):
        ps.incrementasprint()
    