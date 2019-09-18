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
        norm = np.linalg.norm(top - btm)
        self.topnrm = -(top-btm) / norm if norm > 0.0 else 0.0

        self.btm = btm
        self.btmright = btmright
        norm = np.linalg.norm(btm - top)
        self.btmnorm = -(btm-top) / norm if norm > 0.0 else 0.0

        self.sigma = sigma
        self.inductance = 0.0
        