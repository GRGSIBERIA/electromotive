#-*- encoding: utf-8
from typing import List
import numpy as np
from numba import jit
from solvers.solverbase import SolverBase
from solvers.dataset import Element, Magnet


#@jit("f8(f8[:], f8[:], f8[:], f8, f8)", nopython=True)
def magnetizecone(centroid:np.ndarray, magnetpos:np.ndarray, front:np.ndarray, radius:float, magcharge:float):
    r = centroid - magnetpos
    upper = np.dot(front, r)
    length = np.linalg.norm(r)
    under = length**3.
    area = 1./3. * np.pi * radius**2. * length
    return upper / under * area * magcharge

    
#@jit("f8(f8[:], f8[:], f8[:], f8[:], f8[:], f8, f8)", nopython=True)
def calctopbottomcone(centroid, top, bottom, topF, bottomF, radius, magcharge):
    top = magnetizecone(centroid, top, topF, radius, magcharge)
    bottom = magnetizecone(centroid, bottom, bottomF, radius, magcharge)
    return top + bottom


class ConeSolver(SolverBase):
    @classmethod
    def magnetize(cls, element:Element, magnets:List[Magnet]):
        # 磁気源が強磁性体を磁化させる処理
        SolverBase._magnetize(element, magnets, calctopbottomcone)
    
    @classmethod
    def induce(cls, elements:List[Element], magnet:Magnet):
        # 強磁性体が磁気源を通過する磁束を計算
        SolverBase._induce(elements, magnet, magnetizecone)
