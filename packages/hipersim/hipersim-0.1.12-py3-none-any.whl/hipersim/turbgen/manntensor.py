# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 09:57:06 2021

@author: nkdi
"""
import numpy as np
from hipersim.turbgen.trapezoidal_sum_2d import trapezoidal_sum_2d

from scipy.linalg import eigh


def manntensor_(k1, k2, k3, gamma_par, L, alphaepsilon, LifetimeModel):
    k1square = k1**2
    k2square = k2**2
    ksquare = k1square + k2square + k3**2
    k = np.sqrt(ksquare)
    kL = k * L

    if LifetimeModel == 2:  # efficient approximation to the hypergeometric function
        kL[kL < 0.005] = 0.005
        kLsquare = kL**2
        LifeTime = (((1 + kLsquare)**(1 / 6)) / kL) * \
            ((1.2050983316598936 - 0.04079766636961979 * kL + 1.1050803451576134 * kLsquare) /
             (1 - 0.04103886513006046 * kL + 1.1050902034670118 * kLsquare))
        Beta = gamma_par * LifeTime
    elif LifetimeModel == 1:
        Beta = gamma_par / (kL**(2 / 3))
    elif LifetimeModel == 0:  # pragma: no cover
        # Numerical evaluation of the hypergeometric function
        # NB!! Not implemented in the Python version yet
        Beta = gamma_par / ((kL**(2 / 3)) * np.sqrt(HypergeometricFunction(1 / 3, 17 / 6, 4 / 3, -(kL**(-2)), 1, 50)))

    k30 = k3 + Beta * k1
    k30square = k30**2
    k0square = k1square + k2square + k30square
    k0 = np.sqrt(k0square)
    kL0 = k0 * L

    with np.errstate(divide='ignore', invalid='ignore'):
        C1 = Beta * k1square * (k0square - 2 * k30square + Beta * k1 * k30) / ((ksquare) * (k1square + k2square))

        C2 = (k2 * (k0square) * ((k1square + k2square)**(-3 / 2))) * \
            np.arctan2(Beta * k1 * np.sqrt(k1square + k2square), ((k0square) - k30 * k1 * Beta))

        Ek0 = alphaepsilon * (L**(5 / 3)) * (kL0**4) / ((1 + kL0**2)**(17 / 6))

        zeta1 = np.asarray(C1 - (k2 / k1) * C2)
        zeta2 = np.asarray((k2 / k1) * C1 + C2)

        zeta1[k1 == 0] = -Beta[k1 == 0]
        zeta2[k1 == 0] = 0
    return k, k0, k30, ksquare, k0square, k1square, k2square, Ek0, zeta1, zeta2


def manntensorcomponents(k1, k2, k3, gamma_par, L, alphaepsilon, LifetimeModel):
    k, k0, k30, ksquare, k0square, k1square, k2square, Ek0, zeta1, zeta2 = manntensor_(
        k1, k2, k3, gamma_par, L, alphaepsilon, LifetimeModel)
    with np.errstate(divide='ignore', invalid='ignore'):

        Phi11 = np.asarray((Ek0 / (4 * np.pi * (k0**4))) * (k0square - k1square -
                           2 * k1 * k30 * zeta1 + (k1square + k2square) * (zeta1**2)))
        Phi22 = np.asarray((Ek0 / (4 * np.pi * (k0**4))) * (k0square - k2square -
                           2 * k2 * k30 * zeta2 + (k1square + k2square) * (zeta2**2)))
        Phi33 = np.asarray((Ek0 / (4 * np.pi * (k**4))) * (k1square + k2square))

        Phi12 = np.asarray((Ek0 / (4 * np.pi * (k0**4))) * (-k1 * k2 - k1 * k30 * zeta2 -
                           k2 * k30 * zeta1 + (k1square + k2square) * zeta1 * zeta2))
        Phi13 = np.asarray((Ek0 / (4 * np.pi * k0square * ksquare)) * (-k1 * k30 + (k1square + k2square) * zeta1))
        Phi23 = np.asarray((Ek0 / (4 * np.pi * k0square * ksquare)) * (-k2 * k30 + (k1square + k2square) * zeta2))

        Phi11[ksquare == 0] = 0
        Phi22[ksquare == 0] = 0
        Phi33[ksquare == 0] = 0
        Phi12[ksquare == 0] = 0
        Phi13[ksquare == 0] = 0
        Phi23[ksquare == 0] = 0

    return Phi11, Phi22, Phi33, Phi12, Phi13, Phi23


def manntensorsqrtcomponents(k1, k2, k3, gamma_par, L, alphaepsilon, LifetimeModel, VarianceRatios=[1, 1, 1]):
    k, k0, k30, ksquare, _, _, _, Ek0, zeta1, zeta2 = manntensor_(
        k1, k2, k3, gamma_par, L, alphaepsilon, LifetimeModel)
    with np.errstate(divide='ignore', invalid='ignore'):
        Ek4 = np.sqrt(Ek0 / (4 * np.pi * (k0**4)))
        kk = (k0**2) / (k**2)

        if k1 == 0:
            for i in np.where(k2[:, 0] == 0)[0]:
                for j in np.where(k3[0] == 0)[0]:
                    Ek4[i, j] = 0
                    kk[i, j] = 0

    Phi11 = Ek4 * zeta1 * k2
    Phi12 = Ek4 * (k30 * VarianceRatios[0] - zeta1 * k1)
    Phi13 = Ek4 * (-k2 * VarianceRatios[0])
    Phi21 = Ek4 * (-k30 * VarianceRatios[1] + zeta2 * k2)
    Phi22 = Ek4 * (-zeta2 * k1)
    Phi23 = Ek4 * (k1 * VarianceRatios[1])
    Phi31 = Ek4 * (k2 * kk * VarianceRatios[2])
    Phi32 = Ek4 * (-k1 * kk * VarianceRatios[2])
    Phi33 = np.zeros_like(Phi11)

    Phi = Phi11, Phi12, Phi13, Phi21, Phi22, Phi23, Phi31, Phi32, Phi33
    for P in Phi:
        P[ksquare == 0] = 0

    return [[Phi11, Phi12, Phi13], [Phi21, Phi22, Phi23], [Phi31, Phi32, Phi33]]


def matrix_sqrt(phi):
    assert np.all(phi == phi.T)  # check symmetry (requirement for eigh and x.T)
    eigval, eigvec = eigh(phi)
    assert np.all(eigval >= 0)  # requirement for np.sqrt otherwise np.lib.scimath.sqrt() is needed
    return eigvec * np.sqrt(eigval) @ eigvec.T


matrix_sqrt_vec = np.vectorize(matrix_sqrt, signature='(n,n)->(n,n)')


def HypergeometricFunction(a, b, c, z):  # pragma: no cover
    # Not implemented yet
    return 0
