import numpy as np
import xarray as xr
from hipersim.turbgen import turbgen
import pytest
import matplotlib.pyplot as plt
import time
from hipersim.turbgen.generate_field import SpectralTensor
from numpy import testing as npt
from tests.test_files import tfp
import os


def get_memory_usage():
    import gc
    import ctypes
    import os
    import psutil
    gc.collect()
    try:
        ctypes.CDLL('libc.so.6').malloc_trim(0)
    except Exception:
        pass
    pid = os.getpid()
    python_process = psutil.Process(pid)
    return python_process.memory_info()[0] / 1024**2


@pytest.mark.parametrize('Nxyz', [(128, 16, 32),
                                  (128, 32, 16)])
def test_dimensions(Nxyz):
    T = turbgen.turb_field(Nx=Nxyz[0], Ny=Nxyz[1], Nz=Nxyz[2])
    uvw = T.generate()
    assert np.shape(uvw) == (3,) + Nxyz


@pytest.mark.parametrize('hfc', [0, 1])
def test_against_reference(hfc):
    # compared with saved reference
    Nx, Ny, Nz = 4096, 16, 8
    T = turbgen.turb_field(Nx=Nx, Ny=Ny, Nz=Nz, dx=2, dy=3, dz=4, alphaepsilon=.5, Gamma=3, L=40, HighFreqComp=hfc)

    st = SpectralTensor(Nx=Nx, Ny=Ny, Nz=Nz, dx=2, dy=3, dz=4, alphaepsilon=2, Gamma=3, L=40, HighFreqComp=hfc)
    uvw = st.generate_field(alphaepsilon=.5, seed=1)
    T.u, T.v, T.w = uvw
    # T.to_netcdf(tfp)
    res = T.to_xarray()

    ref = xr.load_dataarray(tfp + f'hipersim_mann_l40.0_ae0.5000_g3.0_h{hfc}_{Nx}xd{Ny}xd{Nz}_2.000x3.00x4.00_s0001.nc')

    # compare turbulence values with almost_equal due to numerical system-dependent differences
    if os.name == 'nt':
        npt.assert_array_equal(ref, res)
    else:
        npt.assert_array_almost_equal(ref, res, 5)

    # Make turbulence identical and compare everything else
    res[:] = ref[:]
    xr.testing.assert_identical(ref, res)


def test_save_to_file():
    # test boxes saved to file
    T = turbgen.turb_field(Nx=128, Ny=32, Nz=16, dx=2, dy=3, dz=4, alphaepsilon=.5, Gamma=3, L=40, HighFreqComp=0,
                           SaveToFile=True, BaseName=tfp + 'tmp')
    T.generate()
    for uvw in 'uvw':
        npt.assert_array_almost_equal(np.fromfile(tfp + f'tmp_1_{uvw}.bin', np.float32).reshape((128, 32, 16)),
                                      T.to_xarray().sel(uvw=uvw))
        os.remove(tfp + f'tmp_1_{uvw}.bin')


def test_spectral_tensor():
    # check 1-step vs 2-step process (generating field from pregenerated SpectralTensor should be faster)
    T = turbgen.turb_field(Nx=1024, Ny=4, Nz=64, dz=2)
    t_start = time.time()
    T.generate()
    t_all = time.time() - t_start
    ae, L, G, Nx, Ny, Nz, dx, dy, dz, hfc, s = [
        T.params[k] for k in ["alphaepsilon", "L", "Gamma", "Nx", "Ny", "Nz", "dx", "dy", "dz", "HighFreqComp", "SeedNo"]]

    st = SpectralTensor(alphaepsilon=.1, L=L, Gamma=G, Nx=Nx, Ny=Ny, Nz=Nz, dx=dx, dy=dy, dz=dz, HighFreqComp=hfc)
    t_start = time.time()
    u, v, w = st.generate_field(alphaepsilon=ae, seed=s)
    t_generate_field = time.time() - t_start

    npt.assert_array_almost_equal(u, T.u, 5)
    npt.assert_array_almost_equal(v, T.v, 5)
    npt.assert_array_almost_equal(w, T.w, 5)

    # generating turbulence from the spectral tensor takes roughly half the time
    assert t_generate_field < (t_all * .6)


def test_double():
    # check than doubling an axis removes periodicity (first and last plane should be more different
    for name, axis in [('x', 0), ('y', 1), ('z', 2)]:
        Nxyz = [64, 64, 64]

        uvw, d_uvw = [turbgen.turb_field(alphaepsilon=1, Nx=Nxyz[0], Ny=Nxyz[1], Nz=Nxyz[2], dx=1, dy=1, dz=1,
                                         TurbOptions={'double_x': False, 'double_y': False, 'double_z': False,
                                                      **{f'double_{name}': double}}).generate()
                      for double in [False, True]]

        for a in [0, 1, 2]:
            first_last_diff = np.abs(np.take(uvw[0], 0, a) - np.take(uvw[0], -1, a)).mean()
            first_last_diff_double = np.abs(np.take(d_uvw[0], 0, a) - np.take(d_uvw[0], -1, a)).mean()
            if a == axis:
                # axis with double size should have larger difference between first and last plane
                assert first_last_diff_double > 2.5
            else:
                assert first_last_diff_double < 1
            assert first_last_diff < 1


def test_to_netcdf():
    T = turbgen.turb_field(Nx=128, Ny=32, Nz=16, dx=2, dy=3, dz=4, alphaepsilon=.5, Gamma=3, L=40)
    T.generate()
    T.to_netcdf(tfp, "tmp.nc")
    ref = T.to_xarray()
    res = xr.load_dataarray(tfp + 'tmp.nc')
    os.remove(tfp + 'tmp.nc')
    assert res.identical(ref)


def test_output():
    T = turbgen.turb_field(Nx=128, Ny=32, Nz=16, dx=2, dy=3, dz=4, alphaepsilon=.5, Gamma=3, L=40,
                           TurbOptions={'alpha': .1})
    T.generate()
    T.output()


def test_output_bladed():
    T = turbgen.turb_field(Nx=128, Ny=32, Nz=16, dx=2, dy=3, dz=4, alphaepsilon=.5, Gamma=3, L=40,
                           TurbOptions={'alpha': .1, 'FileFormat': 'Bladed', 'Umean': 8})
    T.params['SaveToFile'] = 1
    T.generate()
    T.output()


def test_direction():
    T = turbgen.turb_field(Nx=1024, Ny=4, Nz=64, dz=2)
    T.generate()
    if 0:
        da = T.to_xarray()
        axes = plt.subplots(3, figsize=(12, 6))[1]
        for ax, uvw in zip(axes, 'uvw'):
            da.sel(y=0, uvw=uvw).plot(x='x', ax=ax)
            ax.plot([10, 10, 20, 20, 20], [0, 70, 70, 110, 30], 'k')
            ax.axis('scaled')
        plt.tight_layout()
        plt.show()
