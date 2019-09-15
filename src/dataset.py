#-*- encoding: utf-8
import numpy as np 


class Element:
    def __init__(self, position: np.ndarray, gamma: float):
        self.pos = position
        self.gamma = gamma
        self.magnetize = 0.0


class Magnet:
    def __init__(self, top: np.ndarray, topright: np.ndarray, btm: np.ndarray, btmright: np.ndarray, sigma: float):
        self.top = top
        self.topright = topright
        self.topnrm = -(top-btm) / np.linalg.norm(top-btm)

        self.btm = btm
        self.btmright = btmright
        self.btmnorm = -(btm-top) / np.linalg.norm(top-btm)

        self.sigma = sigma
        self.inductance = 0.0