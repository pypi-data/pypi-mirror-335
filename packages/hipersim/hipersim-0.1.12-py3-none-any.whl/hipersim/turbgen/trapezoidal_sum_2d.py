# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 14:05:42 2021

@author: nkdi
"""
import numpy as np


def trapezoidal_sum_2d(f, x, y):
    fa = f[:-1, :-1]
    fb = f[:-1, 1:]
    fc = f[1:, :-1]
    fd = f[1:, 1:]
    f = (fa + fb + fc + fd) / 4

    dx, dy = np.diff(x), np.diff(y)
    if np.all(np.abs(dx - dx[0]) < 1e-15) and np.all(np.abs(dy - dy[0]) < 1e-15):
        return dx[0] * dy[0] * np.sum(f)
    else:
        return np.sum(dx[:, None] * dy[None] * f)
