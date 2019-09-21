#-*- encoding: utf-8
from typing import List
import numpy as np
from numba import jit
from solvers.solverbase import SolverBase, cross
from solvers.dataset import Element, Magnet


def magnetizerect(centroid:np.ndarray, magnetpos:np.ndarray, front:np.ndarray, radius: float, magcharge:float):
    area = 2. * np.pi * radius**2
    r = centroid - magnetpos
    length = np.linalg.norm(r)

    Z = np.dot(front, r)
    Xj = cross(front, r/length)
    Yk = cross(Xj, front)

    a = b = np.sqrt(area)
    S = [np.dot(Xj, centroid) - a, np.dot(Xj, centroid) + a]
    T = [np.dot(Yk, centroid) - b, np.dot(Yk, centroid) + b]
    z2 = Z**2
    #R = [[np.sqrt(S[0]**2 + T[0]**2 + z2), np.sqrt(S[0]**2 + T[1]**2 + z2)], [np.sqrt(S[1]**2 + T[0]**2 + z2), np.sqrt(S[1]**2 + T[1]**2 + z2)]]
    R = [[np.sqrt(S[j]**2 + T[i]**2 + z2) for i in range(2)] for j in range(2)]
    total = 0.0
    for i in range(2):
        for j in range(2):
            total += (-1)**(i+j) * np.math.atan((S[j] * T[i]) / (R[j][i] * Z))
    return total * magcharge


def calctopbottomrect(centroid, top, bottom, topF, bottomF, radius, magcharge):
    a = magnetizerect(centroid, top, topF, radius, magcharge)
    b = magnetizerect(centroid, bottom, bottomF, radius, magcharge)
    return a - b


class RectSolver(SolverBase):
    @classmethod
    def magnetize(cls, element:Element, magnets:List[Magnet]):
        SolverBase._magnetize(element, magnets, calctopbottomrect)

    @classmethod
    def induce(cls, elements:List[Element], magnet:Magnet):
        SolverBase._induce(elements, magnet, magnetizerect)
