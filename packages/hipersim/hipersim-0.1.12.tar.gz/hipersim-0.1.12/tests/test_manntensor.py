import numpy as np
from hipersim.turbgen.manntensor import manntensorcomponents, manntensorsqrtcomponents
from tests.test_files import tfp


def test_manntensor():

    N1, N2, N3 = 8, 10, 12
    dx, dy, dz = 2, 3, 4
    Gamma = 3
    L = 40
    alphaepsilon = .4

    L1 = N1 * dx
    L2 = N2 * dy
    L3 = N3 * dz

    m1 = np.concatenate([np.arange(0, N1 / 2), np.arange(-N1 / 2, 0)])
    m2 = np.concatenate([np.arange(0, N2 / 2), np.arange(-N2 / 2, 0)])
    m3 = np.concatenate([np.arange(0, N3 / 2), np.arange(-N3 / 2, 0)])

    k1 = m1 * 2 * np.pi / L1
    k2 = m2 * 2 * np.pi / L2
    k3 = m3 * 2 * np.pi / L3

    k3grid, k2grid = np.meshgrid(k3, k2)

    SqrtPhi = np.array([[manntensorsqrtcomponents(k1[5], k2grid, k3grid, Gamma, L, alphaepsilon, LifetimeModel,
                                                  VarianceRatios=VarianceRatios)
                         for LifetimeModel in [1, 2]]
                        for VarianceRatios in [[1, 1, 1], [2, 3, 4]]])
    # np.save(tfp + 'manntensorsqrt_ref.npy', SqrtPhi)
    np.testing.assert_array_almost_equal(SqrtPhi, np.load(tfp + 'manntensorsqrt_ref.npy').reshape(SqrtPhi.shape), 15)

    Phi = np.array([[manntensorcomponents(k1[5] * np.ones(k2grid.shape), k2grid, k3grid, Gamma, L, alphaepsilon, LifetimeModel)
                     for LifetimeModel in [1, 2]]])
    # np.save(tfp + 'manntensor_ref.npy', Phi)
    np.testing.assert_array_almost_equal(Phi, np.load(tfp + 'manntensor_ref.npy').reshape(Phi.shape), 15)
