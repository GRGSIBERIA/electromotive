#-*- encoding: utf-8
from typing import List
import numpy as np 
from numba import jit
from solvers.dataset import Element, Magnet



@jit("f8[:](f8[:], f8[:])", nopython=True)
def cross(a, b):
    return np.array([
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0]])


@jit("f8(f8, f8, f8)", nopython=True)
def inducevoltage(phiA:float, phiB:float, deltatime:float):
    dphi = phiB - phiA
    return dphi / deltatime


def calcdirection(epos: np.ndarray, magnets: List[Magnet]):
    direction = np.zeros(3)
    for magnet in magnets:
        direction += magnet.center - epos
    return direction / np.linalg.norm(direction)


class SolverBase:
    """ソルバーのベースクラス，誘導起電力を求める式は共通
    """
    @classmethod
    def voltage(cls, magnetA:Magnet, magnetB:Magnet, deltatime:float):
        # 通過する磁束の時刻歴をもとに誘導起電力を計算
        # ファラデーだと符号が逆になっているのでそのとおりにする
        magnetA.inducedvoltage -= inducevoltage(
            magnetA.inducedmagnetized, magnetB.inducedmagnetized, deltatime)


    @classmethod
    def _magnetize(cls, element:Element, magnets:List[Magnet], func):
        total = 0.0
        for magnet in magnets:
            total += func(
                element.centroid, magnet.top, magnet.bottom, 
                magnet.topF, magnet.bottomF, magnet.radius, magnet.magcharge)
        element.magnetized = total * element.volume
        element.direction = calcdirection(element.centroid, magnets)


    @classmethod
    def _induce(cls, elements:List[Element], magnet:Magnet, func):
        total = 0.0
        for element in elements:
            total += func(
                magnet.top, element.centroid, element.direction, 
                magnet.radius, element.magnetized)
        magnet.inducedmagnetized = total


    @classmethod
    def magnetize(cls, element, magnets):
        raise NotImplementedError()


    @classmethod
    def induce(cls, elements, magnet):
        raise NotImplementedError()
