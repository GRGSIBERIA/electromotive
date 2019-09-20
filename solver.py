#-*- encoding: utf-8
from typing import List
import time
import numpy as np 
from scipy.integrate import dblquad
from numba import jit, prange
from provider import Element, Magnet

from solvers.solverbase import SolverBase
from solvers.cone import ConeSolver
from solvers.nabla import NablaSolver
from solvers.rect import RectSolver


def detectdirection(elements, magnets, numoftimes):
    start = time.time()
    for timeid in range(numoftimes):
        for element_history in elements:
            for element in element_history[timeid]:
                direction = np.zeros(3)
                for magnet_history in magnets:
                    direction += magnet_history[timeid].center - element.centroid
                try:
                    direction /= float(len(magnets))
                    element.direction = direction / np.linalg.norm(direction)
                except ZeroDivisionError:
                    element.direction = np.zeros(3)
    print("detect direction -- {} sec".format(time.time() - start))


def detectsolver(solvername: str) -> SolverBase:
    solver = None
    if solvername == "cone":
        solver = ConeSolver
    elif solvername == "nabla":
        solver = NablaSolver
    elif solvername == "integrate":
        solver = IntegrateSolver
    elif solvername == "rect":
        solver = RectSolver
    else:
        raise Exception("Can't use solver name ({}).".format(solvername))
    return solver


class Solver:
    def __init__(self, solvername: str):
        self.solver = detectsolver(solvername)


    def computemagnetize(self, elements: List[Element], magnets: List[Magnet]):
        for element in elements:
            self.solver.magnetize(element, magnets)


    def computeinduce(self, elements: List[Element], magnets: List[Magnet]):
        for magnet in magnets:
            self.solver.induce(elements, magnet)


    def computeinductance(self, magnets: List[List[Magnet]], times: List[float]):
        for i, t in enumerate(times[:-1]):
            deltatime = times[i+1] - times[i]
            magA = magnets[i]
            magB = magnets[i+1]
            for mi, _ in enumerate(magA):
                self.solver.voltage(magA[mi], magB[mi], deltatime)
