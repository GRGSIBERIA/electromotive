#-*- encoding: utf-8
from typing import List
import numpy as np
from numba import jit, prange, jitclass, f8

class Element:
    def __init__(self, ns: List[np.ndarray], mag: float):
        self.volume = calcvolume(ns[0], ns[1], ns[2], ns[3])
        self.centroid = calccentroid(ns[0], ns[1], ns[2], ns[3])
        self.direction = np.zeros(3)

        self.magnetic_permeability = mag    # 比例定数
        self.magnetized = 0.0               # 磁性体が磁化する磁束密度

#@jit("f8(f8[:], f8[:], f8[:], f8[:])")
def calcvolume(n0, n1, n2, n3):
    v = np.array([n1-n0, n2-n0, n3-n0])
    return 1./6. * np.abs(np.linalg.det(v))

#@jit("f8[:](f8[:], f8[:], f8[:], f8[:])", nopython=True)
def calccentroid(n0, n1, n2, n3):
    #centroid = np.zeros(3)
    centroid = n0 + n1 + n2 + n3
    return centroid * 0.25

    
#@jit("f8[:](f8[:], f8[:])", nopython=True)
def calcforward(a, b):
    c = -(b - a)
    return c / np.linalg.norm(c)

class Magnet:
    def __init__(self, tcp: np.ndarray, trp: np.ndarray, bcp: np.ndarray, brp: np.ndarray, magcharge: float):
        #self.top = pos[topid]
        #self.bottom = pos[bottomid]
        #self.topR = pos[topRid]
        #self.bottomR = pos[bottomRid]

        self.top = tcp
        self.topR = trp
        self.bottom = bcp
        self.bottomR = brp

        self.center = (self.top + self.bottom) * 0.5
        self.topF = calcforward(self.top, self.bottom)
        self.bottomF = -self.topF
        self.radius = np.linalg.norm(self.topR - self.top)
        self.magcharge = magcharge

        self.inducedmagnetized = 0.0    # 鎖交磁場の誘導起電力
        self.inducedvoltage = 0.0       # 誘導起電力
