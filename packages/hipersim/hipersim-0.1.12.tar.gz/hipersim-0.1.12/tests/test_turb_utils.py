import numpy as np
import matplotlib.pyplot as plt
from hipersim.turbgen.trapezoidal_sum_2d import trapezoidal_sum_2d
from hipersim.turbgen.turb_utils import run_cpp, run_hawc2
from hipersim import MannTurbulenceField
import os
import pytest


def test_trapezoidal_sum_2d():
    x = np.linspace(-1, 1, 100)
    y = np.linspace(-1, 1, 105)
    r_sqr = x[:, None]**2 + y[None]**2
    f = np.sqrt(np.maximum(1 - r_sqr, 0))
    # plt.contourf(f)
    # plt.show()
    np.testing.assert_allclose(trapezoidal_sum_2d(f, x, y), 4 / 3 * np.pi / 2, atol=0.0005)


def test_trapezoidal_sum_2d_non_equivdistant():
    x = np.linspace(-1, 1, 100)
    y = np.linspace(-1, 1, 105)
    x[20] += 0.01

    r_sqr = x[:, None]**2 + y[None]**2
    f = np.sqrt(np.maximum(1 - r_sqr, 0))
    np.testing.assert_allclose(trapezoidal_sum_2d(f, x, y), 4 / 3 * np.pi / 2, atol=0.0005)


def test_cpp_hawc2():
    kwargs = dict(ae23=.1, L=30, G=3, Nx=1024, Ny=64, Nz=32, dx=1, dy=2, dz=3, hfc=0, seed=1)
    mtf_kwargs = dict(alphaepsilon=.1, L=30, Gamma=3, Nxyz=(1024, 64, 32), dxyz=(1, 2, 3),
                      seed=1, HighFreqComp=0, double_xyz=(0, 1, 1))
    if not os.path.isfile('cpp/mann_turb_x64.exe'):
        pytest.xfail('cpp/mann_turb_x64.exe does not exists')
    if not os.path.isfile('hawc2-win64/HAWC2MB.exe'):
        pytest.xfail('hawc2-win64/HAWC2MB.exe does not exists')

    filenames = run_cpp(name='cpp', exe='cpp/mann_turb_x64.exe', **kwargs)
    mtf_cpp = MannTurbulenceField.from_hawc2(filenames, **mtf_kwargs)

    filenames = run_hawc2(name='hawc2', hawc2_exe='hawc2-win64/HAWC2MB.exe', **kwargs)
    mtf_hawc2 = MannTurbulenceField.from_hawc2(filenames, **mtf_kwargs)
    if 0:
        cpp = mtf_cpp.to_xarray()
        h2 = mtf_hawc2.to_xarray()
        cpp.sel(uvw='u', x=0, y=0).plot()
        h2.sel(uvw='u', x=0, y=0).plot()
        plt.figure()
        cpp.sel(uvw='u', x=0).plot(x='y')
        plt.figure()
        h2.sel(uvw='u', x=0).plot(x='y')
        plt.show()
    np.testing.assert_array_equal(mtf_cpp.uvw, mtf_hawc2.uvw)
