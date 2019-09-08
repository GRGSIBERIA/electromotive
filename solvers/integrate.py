#-*- encoding: utf-8
from typing import List
import numpy as np
from numba import jit
from solvers.solverbase import SolverBase, cross
from solvers.dataset import Element, Magnet


@jit("f8[:](f8[:], f8, f8[:])", nopython=True)
def rotation(axis:np.ndarray, theta:float, vec:np.ndarray):
    rot = axis * np.sin(theta/2.)
    rotv = -axis * np.cos(theta/2.)
    vv = cross(rot, vec)
    vw = -np.dot(rot, vec)
    rv = cross(vv, -rot) + rotv * vv - rot * vw
    return rv


@jit("f8(f8, f8, f8, f8[:], f8[:], f8[:], f8, f8[:], f8[:])", nopython=True)
def quadfunction(drho:float, dphi:float, 
    magcharge:float, r:np.ndarray, front:np.ndarray, right:np.ndarray, radius:float,
    centroid:np.ndarray, magpos:np.ndarray):
    top = magcharge * np.dot(front, r) * drho
    # x' + x + theta
    rotate = rotation(front, dphi, right) * radius
    bottom = centroid - (magpos + rotate)
    return top / np.linalg.norm(bottom)**2. * drho * dphi


def magnetizeintegrate(centroid:np.ndarray, magnetpos:np.ndarray, front:np.ndarray, radius: float, magcharge:float):
    r = centroid - magnetpos
    length = np.linalg.norm(r)
    j = cross(front, r/length)
    right = cross(j, front)
    args = (magcharge, r, front, right, radius, centroid, magnetpos)
    return dblquad(quadfunction, 0., 2.*np.pi, lambda x: 0, lambda x: radius, args=args)[0]


def calctopbottomintegrate(centroid, top, bottom, topF, bottomF, radius, magcharge):
    a = magnetizeintegrate(centroid, top, topF, radius, magcharge)
    b = magnetizeintegrate(centroid, bottom, bottomF, radius, magcharge)
    return a - b


class IntegrateSolver(SolverBase):
    @classmethod
    def magnetize(cls, element:Element, magnets:List[Magnet]):
        SolverBase._magnetize(element, magnets, calctopbottomintegrate)
    
    @classmethod
    def induce(cls, elements:List[Element], magnet:Magnet):
        SolverBase._induce(elements, magnet, magnetizeintegrate)

