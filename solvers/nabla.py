#-*- encoding: utf-8
from typing import List
import numpy as np
from numba import jit
from solvers.solverbase import SolverBase, cross
from solvers.dataset import Element, Magnet


@jit("f8(f8[:], f8[:], f8[:], f8, f8)", nopython=True)
def magnetizenabla(centroid:np.ndarray, magnetpos:np.ndarray, front:np.ndarray, radius: float, magcharge:float):
    r = centroid - magnetpos
    length = np.linalg.norm(r)
    j = cross(front, r/length)
    k = cross(j, front)
    area = 2. * np.pi * radius**2
    return (np.dot(front, r) + np.dot(k, r)) / length**3 * area * magcharge
    #return np.dot(front, r) / length**3 * area * magcharge


@jit("f8(f8[:], f8[:], f8[:], f8[:], f8[:], f8, f8)", nopython=True)
def calctopbottomnabla(centroid, top, bottom, topF, bottomF, radius, magcharge):
    top = magnetizenabla(centroid, top, topF, radius, magcharge)
    bottom = magnetizenabla(centroid, bottom, bottomF, radius, magcharge)
    return top - bottom


class NablaSolver(SolverBase):
    @classmethod
    def magnetize(cls, element:Element, magnets:List[Magnet]):
        SolverBase._magnetize(element, magnets, calctopbottomnabla)

    @classmethod
    def induce(cls, elements:List[Element], magnet:Magnet):
        SolverBase._induce(elements, magnet, magnetizenabla)