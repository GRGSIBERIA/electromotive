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
    @classmethod
    def computemagnetize(cls, solvername: str, elements: List[Element], magnets: List[Magnet]):
        solver = detectsolver(solvername)
        
        for element in elements:
            solver.magnetize(element, magnets)


    @classmethod
    def solve(cls, solvername: str, elements: List[Element], magnets: List[Magnet]):
        numoftimes = len(times)
        detectdirection(parts, magnets, numoftimes)

        
        
        # 磁性体を磁化させるときの計算
        start = time.time()
        for timeid in range(numoftimes):
            for part in parts:
                mags = [mag[timeid] for mag in magnets]
                for element in part[timeid]:
                    solver.magnetize(element, mags)
        print("done magnetization - {} sec".format(time.time() - start))
        
        # 磁極表面を通る磁束を計算
        start = time.time()
        for timeid in range(numoftimes):
            elements = []
            for element_history in parts:
                elements.extend(element_history[timeid])

            for magnet_history in magnets:
                mag = magnet_history[timeid]
                solver.induce(elements, mag)
        print("done magnetic induction - {} sec".format(time.time() - start))

        # 誘導起電力の計算
        start = time.time()
        for timeid in range(numoftimes-1):
            deltatime = times[timeid+1] - times[timeid]
            for element_history in parts:
                ea = element_history[timeid]
                eb = element_history[timeid + 1]
                for magnet_history in magnets:
                    ma = magnet_history[timeid]
                    mb = magnet_history[timeid + 1]
                    solver.voltage(ea, eb, ma, mb, deltatime)
        print("done induced electromotive - {} sec".format(time.time() - start))
