#-*- encoding: utf-8
from typing import List
import numpy as np
from numba import jit
from solvers.solverbase import SolverBase
from solvers.dataset import Element, Magnet


@jit("f8(f8[:], f8[:], f8[:], f8, f8)", nopython=True)
def magnetizedz(centroid:np.ndarray, magnetpos:np.ndarray, front:np.ndarray, radius:float, magcharge:float):
    r = centroid - magnetpos
    length = np.linalg.norm(r)
    length3 = length * length * length
    return magcharge * (np.dot(front, r) / length3)


@jit("f8(f8[:], f8[:], f8[:], f8[:], f8[:], f8, f8)", nopython=True)
def calctopbottomdz(centroid, top, bottom, topF, bottomF, radius, magcharge):
    top = magnetizedz(centroid, top, topF, radius, magcharge)
    bottom = magnetizedz(centroid, bottom, bottomF, radius, magcharge)
    return top + bottom


class HMSolver(SolverBase):
    @classmethod
    def magnetize(cls, element:Element, magnets:List[Magnet]):
        # 磁気源が強磁性体を磁化させる処理
        SolverBase._magnetize(element, magnets, calctopbottomdz)
    
    @classmethod
    def induce(cls, elements:List[Element], magnet:Magnet):
        # 強磁性体が磁気源を通過する磁束を計算
        SolverBase._induce(elements, magnet, magnetizedz)
