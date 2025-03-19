from hipersim.mann_turbulence import MannTurbulenceField
import matplotlib.pyplot as plt
from numpy import testing as npt
from tests.test_files import tfp
import numpy as np
from numpy import newaxis as na
import pytest
import os
import shutil
import time
from hipersim.turbgen.spectral_tensor import random_generator_par, random_generator_seq, OnetimeMannSpectralTensor,\
    MannTurbulenceInput, MannSpectralTensor
import xarray as xr
from memory_utils import get_memory_usage
from hipersim.turbgen.generate_field import SpectralTensor
from hipersim.turbgen.turbgen import turb_field
from hipersim.turbgen.manntensor import manntensorcomponents
from hipersim.turbgen.trapezoidal_sum_2d import trapezoidal_sum_2d
from hipersim.turbgen.turb_utils import run_cpp
from hipersim._hipersim import TurbulenceField, Bounds
from hipersim import version
from wetb.hawc2.htc_file import HTCFile
from h2lib import H2Lib
from wetb.gtsdf import gtsdf
import warnings


@pytest.fixture(scope='module')
def mtf_medium():
    return MannTurbulenceField.generate(alphaepsilon=.5, L=40, Gamma=3,
                                        Nxyz=(4096, 16, 8), dxyz=(2, 3, 4), seed=1)


def test_version():
    assert version.__version__.startswith(".".join(map(str, version.__version_tuple__[:4])))


@pytest.mark.parametrize('hfc', [0, 1])
def test_single_field_against_reference(hfc):
    # Single field
    mtf = MannTurbulenceField.generate(alphaepsilon=.5, L=40, Gamma=3,
                                       Nxyz=(4096, 16, 8), dxyz=(2, 3, 4), seed=1, HighFreqComp=hfc)
    res = mtf.to_xarray()

    # compare with turb_gen
    st = SpectralTensor(Nx=4096, Ny=16, Nz=8, dx=2, dy=3, dz=4, alphaepsilon=.5, Gamma=3, L=40, HighFreqComp=hfc)
    uvw = st.generate_field(alphaepsilon=.5, seed=1)
    npt.assert_array_almost_equal(res.values, uvw, 5)

    ref = MannTurbulenceField.from_netcdf(
        tfp + f'hipersim_mann_l40.0_ae0.5000_g3.0_h{hfc}_4096xd16xd8_2.000x3.00x4.00_s0001.nc').to_xarray()

    # compare turbulence values with almost_equal due to numerical system-dependent differences
    npt.assert_array_almost_equal(ref, res, 5)

    # Make turbulence identical and compare everything else
    res[:] = ref[:]
    xr.testing.assert_identical(ref, res)


def test_multiple_fields(mtf_medium):
    # multiple fields
    seeds = [1, 2, 3]
    sp = MannSpectralTensor(alphaepsilon=.5, L=40, Gamma=3, Nxyz=(4096, 16, 8), dxyz=(2, 3, 4))
    # spectra variables generated on first call to generate and reused afterwards
    t = time.time()
    mtf_lst = [sp.generate(seed) for seed in seeds]
    t_generate_field = (time.time() - t) / 3
    t = time.time()
    mtf = MannTurbulenceField.generate(alphaepsilon=.5, L=40, Gamma=3, Nxyz=(4096, 16, 8), dxyz=(2, 3, 4), seed=2)
    t_all = time.time() - t

    assert mtf_lst[1].to_xarray().equals(mtf.to_xarray())

    # generating turbulence from the spectral tensor takes roughly half the time
    assert t_generate_field < (t_all * .6)


def test_cache_spectral_tensor():
    mst = MannSpectralTensor(alphaepsilon=.5, L=40, Gamma=3, Nxyz=(4096, 16, 8), dxyz=(2, 3, 4),
                             cache_spectral_tensor=True)
    omst = OnetimeMannSpectralTensor(alphaepsilon=.5, L=40, Gamma=3, Nxyz=(4096, 16, 8), dxyz=(2, 3, 4),
                                     cache_spectral_tensor=True)
    if os.path.isfile(mst.cache_name):
        os.remove(mst.cache_name)

    t = time.time()
    mst.spectral_vars
    t_generate = (time.time() - t)
    assert t_generate > 1  # spectral tensor is generated

    t = time.time()
    mst.spectral_vars
    assert (time.time() - t) < 0.1  # spectral tensor loaded from file

    t = time.time()
    omst.spectral_vars
    assert (time.time() - t) < 0.1  # spectral tensor loaded from file
    assert omst._spectral_vars is None


def test_MannTurbulenceField_cache_spectral_tensor():
    cache_name = 'mannsqrtphi_l40.0_g3.0_h0_4096xd16xd8_2.000x3.00x4.00.npy'
    if os.path.isfile(cache_name):
        os.remove(cache_name)

    t = time.time()
    mtf1 = MannTurbulenceField.generate(alphaepsilon=1, L=40, Gamma=3, Nxyz=(4096, 16, 8), dxyz=(2, 3, 4),
                                        cache_spectral_tensor=True)

    t1 = time.time() - t
    t = time.time()
    mtf2 = MannTurbulenceField.generate(alphaepsilon=2, L=40, Gamma=3, Nxyz=(4096, 16, 8), dxyz=(2, 3, 4),
                                        cache_spectral_tensor=True)
    t2 = time.time() - t
    assert t2 < t1 / 2, (t1, t2)
    npt.assert_array_almost_equal(mtf1.uvw * np.sqrt(2), mtf2.uvw)


def test_time_and_memory():
    Nxyz, time_limit, mem_limit = (8192, 64, 64), 17, 2200
    # Nxyz, time_limit, mem_limit = (4096, 32, 32), 7, 750
    try:
        import memory_profiler
    except ImportError:
        pytest.skip("memory_profiler missing")
    t = time.time()

    def run():
        MannTurbulenceField.generate(alphaepsilon=1, L=29.6, Gamma=3.9, Nxyz=Nxyz,
                                     dxyz=(1, 1, 1), HighFreqComp=0, double_xyz=(0, 0, 0))

    initial_mem_usage = get_memory_usage()
    mem_usage, res = memory_profiler.memory_usage((run), interval=.02, max_usage=True, retval=True)
    mem_usage -= initial_mem_usage
    t = time.time() - t
    print(f"test_time_and_memory: {t:.1f}s (limit: {time_limit}), {mem_usage:.0f}MB (limit: {mem_limit})")
    n = "%d,%d,%d" % Nxyz
    with open('metrics.txt', 'a') as fid:
        fid.write(f'Time({n}) {t:.1f}\n')
        fid.write(f'Memory({n}) {mem_usage:.1f}\n')
    assert t < time_limit
    assert mem_usage < mem_limit


def test_to_from_hawc2(mtf_medium):
    mtf = mtf_medium
    folder = tfp + 'tmp/'
    os.makedirs(folder, exist_ok=True)
    mtf.to_hawc2(folder, 'tmp')
    saved = MannTurbulenceField.from_hawc2([folder + f'tmp{s}.turb' for s in 'uvw'],
                                           alphaepsilon=mtf.alphaepsilon, L=mtf.L, Gamma=mtf.Gamma,
                                           Nxyz=mtf.Nxyz, dxyz=mtf.dxyz,
                                           seed=mtf.seed, HighFreqComp=mtf.HighFreqComp)
    assert saved.to_xarray().equals(mtf.to_xarray())
    attrs = mtf.to_xarray().attrs
    saved_attrs = saved.to_xarray().attrs
    assert attrs.keys() == saved_attrs.keys()
    for k in attrs.keys():
        if k == 'name':
            assert attrs[k] == saved_attrs[k].replace('Unknown', 'Hipersim')
        else:
            npt.assert_array_equal(attrs[k], saved_attrs[k])
    saved = TurbulenceField.from_hawc2([folder + f'tmp{s}.turb' for s in 'uvw'],
                                       Nxyz=mtf.Nxyz, dxyz=mtf.dxyz,
                                       seed=mtf.seed)
    assert saved.to_xarray().equals(mtf.to_xarray())

    shutil.rmtree(folder)


@pytest.mark.parametrize('box_front', ['last_plane', 'first_plane'])
def test_hawc2_box(box_front):
    ws = 9
    if box_front == 'last_plane':
        # box origo at h2 gl (0,-22.5,-16) with x=v, y=u, z=-w
        sensor_args = [1, -22.5 + 5, 0, - 16 - 25]
        advection_speed = -ws
    else:
        # box origo at h2 gl (0, 22.5, -16), with x=-v, y=u, z=-w and -16=-30+14
        sensor_args = [1, 22.5 - 5, 0, - 16 - 25]
        advection_speed = ws

    tf = MannTurbulenceField.generate(alphaepsilon=.5, L=40, Gamma=3,
                                      Nxyz=(128, 16, 8), dxyz=(2, 3, 4), seed=1)
    htc = HTCFile(modelpath='.')
    htc.output.data_format = 'gtsdf64'
    htc.wind = tf.to_hawc2(htc_dict={'wind.wsp': ws,
                                     'wind.center_pos0': (0, 0, -30)})
    assert htc.wind.mann.box_dim_u[:] == [128, 2]
    htc.wind.mann.box_front = box_front
    assert htc.wind.wsp[0] == ws
    py, pz = 5, 25
    htc.output.add_sensor('wind', 'free_wind', sensor_args)
    htc.set_name('tmp')
    htc.save()
    with H2Lib(suppress_output=1) as h2:
        h2.init(htc.filename)
        h2.run(50)
    time, data, info = gtsdf.load(htc.modelpath + htc.output_files()[0])
    da = tf.to_xarray()
    x = time * advection_speed

    da_uvw = da.interp(x=x, y=py, z=pz) + np.array([ws, 0, 0])[:, na]
    tf_uvw = (tf(x, x * 0 + py, x * 0 + pz) + np.array([ws, 0, 0])).T
    h2_uvw = data[:, 1], data[:, 0], -data[:, 2]
    if 0:
        axes = plt.subplots(3, 1)[1]
        for i, uvw in enumerate('uvw'):
            plt.sca(axes[i])
            plt.title(uvw)
            plt.plot(time, da_uvw[i], label='xarray')
            plt.plot(time, tf_uvw[i], '-', label='tf')
            plt.plot(time, h2_uvw[i], '--', label='hawc2')
            plt.legend()
        plt.show()
    npt.assert_array_almost_equal(tf_uvw, h2_uvw, 7)


def test_to_from_netcdf(mtf_medium):
    mtf = mtf_medium
    folder = tfp + 'tmp/'
    os.makedirs(folder, exist_ok=True)
    mtf.to_netcdf(folder, 'tmp.nc')
    saved = mtf.from_netcdf(folder + 'tmp.nc')
    assert saved.to_xarray().equals(mtf.to_xarray())
    shutil.rmtree(folder)


def test_to_from_bladed(mtf_medium):

    mtf = mtf_medium

    folder = tfp + 'tmp/'
    os.makedirs(folder, exist_ok=True)
    U = 8
    mtf.to_bladed(U, folder=folder, basename='tmp')
    saved = mtf.from_bladed(folder + 'tmp_1.wnd')
    saved.uvw[0] -= U
    npt.assert_allclose(saved.uvw, mtf.uvw - mtf.uvw.mean((1, 2, 3))[:, na, na, na], atol=0.05)
    shutil.rmtree(folder)


@pytest.mark.parametrize('TurbOptions', [{'ShearLaw': 'pwr', 'alpha': 0.1, 'zHub': 20},
                                         {'ShearLaw': 'pwr', 'alpha': 0.2},
                                         {'ShearLaw': 'log', 'z0': 0.2, 'zHub': 20}])
def test_to_from_bladed_shear(mtf_medium, TurbOptions):
    mtf = MannTurbulenceField.generate(alphaepsilon=.02, L=40, Gamma=3,
                                       Nxyz=(2, 2, 8), dxyz=(2, 3, 4), seed=1)
    folder = tfp + 'tmp/'
    os.makedirs(folder, exist_ok=True)
    # mtf.uvw[:] = 0
    U = 8

    zhub = TurbOptions.get('zHub', mtf.dz * (mtf.Nz - 1) / 2)
    mtf.to_bladed(U, folder=folder, basename='tmp', TurbOptions=TurbOptions)
    saved = mtf.from_bladed(folder + 'tmp_1.wnd')
    saved_da = saved.to_xarray()
    z = saved_da.z.values
    z += zhub - np.median(z)

    if TurbOptions['ShearLaw'] == 'pwr':
        shear_factor = (z / zhub)**TurbOptions['alpha']
    elif TurbOptions['ShearLaw'] == 'log':
        z0 = TurbOptions['z0']
        shear_factor = np.log(z / z0) / np.log(zhub / z0)

    ref = mtf.uvw - mtf.uvw.mean((1, 2, 3))[:, na, na, na]
    ref[0] += U * shear_factor
    if 0:
        plt.plot(saved.uvw[:, 0, 0].T, z, label='saved')
        plt.plot(ref[:, 0, 0].T, z, '--', label='org + shear + U')
        plt.legend()
        plt.show()
    npt.assert_allclose(saved.uvw, ref, atol=0.05)
    shutil.rmtree(folder)


@pytest.mark.parametrize('n_cpu', [1, 2])
def test_spectra_k_from_lut(n_cpu):
    mst = MannSpectralTensor(alphaepsilon=.1, L=33.6, Gamma=3.9, Nxyz=(8192, 64, 64), dxyz=(1, 1, 1), n_cpu=n_cpu)
    k1, phi_lut = mst.spectra_lookup()
    k_int, phi_int = mst.spectra_integrated(k1[::10], k23_resolution=200)
    if 0:
        for p_lut, p_int, l in zip(phi_lut, phi_int, ('uu', 'vv', 'ww', 'uw')):
            c = plt.semilogx(k1, k1 * p_lut, label=l)[0].get_color()
            plt.semilogx(k_int, k_int * p_int, 'x', color=c)
        plt.plot([], '-', color='gray', label='LookupTable')
        plt.plot([], 'x', color='gray', label='Integrated')
        plt.xlabel('Wave number [?]')
        plt.ylabel('? [?]')
        plt.legend()
        plt.show()

    npt.assert_allclose(k_int * phi_int, np.array(k1 * phi_lut)[:, ::10], atol=0.001)


def test_spectra_k_from_lut_alphaepsilon():

    mst_lst = [MannSpectralTensor(alphaepsilon=ae, L=33.6, Gamma=3.9, Nxyz=(8192, 64, 64), dxyz=(1, 1, 1))
               for ae in [.1, .2]]
    lut_lst = [mst.spectra_lookup() for mst in mst_lst]
    k1 = lut_lst[0][0]
    int_lst = [mst.spectra_integrated(k1[::10], k23_resolution=200) for mst in mst_lst]

    if 0:
        for (k_lut, phi_lut), (k_int, phi_int) in zip(lut_lst, int_lst):
            for p_lut, p_int, l in zip(phi_lut, phi_int, ['uu']):
                c = plt.semilogx(k_lut, k_lut * p_lut, label=l)[0].get_color()
                plt.semilogx(k_int, k_int * p_int, 'x', color=c)
            plt.plot([], '-', color='gray', label='LookupTable')
            plt.plot([], 'x', color='gray', label='Integrated')
        plt.xlabel('Wave number [?]')
        plt.ylabel('? [?]')
        plt.legend()
        plt.show()

    for (k_lut, phi_lut), (k_int, phi_int) in zip(lut_lst, int_lst):
        npt.assert_allclose(k_int * phi_int, np.array(k1 * phi_lut)[:, ::10], atol=0.007)

    npt.assert_allclose(np.array(lut_lst[0][1]) * 2, lut_lst[1][1])


def test_spectra_k_from_int():
    mst = MannSpectralTensor(alphaepsilon=.1, L=33.6, Gamma=3.9, Nxyz=(8192, 64, 64), dxyz=(1, 1, 1))
    k_int, phi_int = mst.spectra_integrated(k23_resolution=200)
    k1, phi_lut = mst.spectra_lookup(k_int)
    if 0:
        for p_lut, p_int, l in zip(phi_lut, phi_int, ('uu', 'vv', 'ww', 'uw')):
            c = plt.semilogx(k1, k1 * p_lut, label=l)[0].get_color()
            plt.semilogx(k_int, k_int * p_int, 'x', color=c)
        plt.plot([], '-', color='gray', label='LookupTable')
        plt.plot([], 'x', color='gray', label='Integrated')
        plt.xlabel('Wave number [?]')
        plt.ylabel('? [?]')
        plt.legend()
        plt.show()

    npt.assert_allclose(k_int * phi_int, np.array(k1 * phi_lut), atol=0.001)


def test_scale_TI():
    U = 10
    ae = .5
    mtf = MannTurbulenceField.generate(alphaepsilon=ae, L=40, Gamma=3, Nxyz=(4096, 16, 8), dxyz=(2, 3, 4), seed=1)
    spectrum_ti_T10 = mtf.spectrum_TI(U=U, T=100)
    spectrum_ti_co1 = mtf.spectrum_TI(U=U, cutoff_frq=1)
    spectrum_ti = mtf.spectrum_TI(U=U)
    assert spectrum_ti > spectrum_ti_T10 * 1.19
    assert spectrum_ti > spectrum_ti_co1 * 1.02
    k, S = mtf.spectra(log10_bin_size=None)
    dk = np.diff(k[:2])
    var = np.sum(S[0]) * dk * 2
    npt.assert_allclose(mtf.uvw[0].std(0).mean() / U, np.sqrt(var) / U, atol=3e-4)

    rea_ti = mtf.uvw[0].std() / U
    factor = rea_ti / spectrum_ti
    mtf.scale_TI(.1, U=U)
    npt.assert_allclose(mtf.alphaepsilon, (.1 / spectrum_ti)**2 * ae)
    npt.assert_allclose(mtf.spectrum_TI(U=U), .1)
    npt.assert_allclose(mtf.uvw[0].std() / U, .1 * factor, atol=1e-1)


def test_get_alphaepsilon():
    U = 10
    mtf = MannTurbulenceInput(alphaepsilon=1, L=40, Gamma=3, Nxyz=(4096, 16, 8), dxyz=(2, 3, 4), seed=1)
    ae = mtf.get_alpha_epsilon(.1, U)
    npt.assert_allclose(ae, 0.05680532444132224)
    mtf = MannTurbulenceInput(alphaepsilon=ae, L=40, Gamma=3, Nxyz=(4096, 16, 8), dxyz=(2, 3, 4), seed=1)
    npt.assert_allclose(mtf.spectrum_TI(U), .1)


def test_spectra(mtf_medium):
    mtf = mtf_medium
    k, S = mtf.spectra()
    phi = mtf.spectra_lookup(k)[1]
    if 0:
        for s, p in zip(S, phi):
            c = plt.semilogx(k, s * k)[0].get_color()
            plt.semilogx(k, p * k, '--', color=c)
        plt.show()
    m = k >= 0.02
    npt.assert_allclose(np.array(S * k)[:, m], np.array(phi * k)[:, m], atol=0.16)


def test_interpolation(mtf_medium):
    mtf = mtf_medium
    da = mtf.to_xarray()
    x = np.linspace(0, 100, 100)
    if 0:
        da.interp(y=5, z=17).sel(uvw='u')[:50].plot()
        da.interp(y=5, z=17, x=x).sel(uvw='u').plot()
        plt.plot(x, mtf(x, x * 0 + 5, x * 0 + 17)[:, 0])
        plt.show()

    npt.assert_array_almost_equal(da.interp(y=5, z=17, x=x).T, mtf(x, x * 0 + 5, x * 0 + 17))
    npt.assert_array_almost_equal(mtf([0], [5], [7]), mtf([-1e-14], [5], [7]))
    npt.assert_array_almost_equal(mtf([-2], [5], [7]), mtf([-2 - 1e-14], [5], [7]))


def interpolation_bounds(bounds, px, py, pz):
    Nxyz = (5, 4, 2)
    dxyz = (2, 3, 4)
    uvw = [np.zeros(Nxyz) + uvw for uvw in [np.arange(Nxyz[0])[:, na, na],
                                            np.arange(Nxyz[1])[na, :, na],
                                            np.arange(Nxyz[2])[na, na, :]]]
    mtf = MannTurbulenceField(uvw, alphaepsilon=1, L=1, Gamma=1, Nxyz=Nxyz, dxyz=dxyz,
                              bounds=bounds)
    if 0:
        plt.plot(px, mtf(px, px * 0, px * 0)[:, 0], label='x')
        print(list(mtf(px, px * 0, px * 0)[:, 0]))
        plt.plot(py, mtf(py * 0, py, py * 0)[:, 1], label='y')
        print(list(mtf(py * 0, py, py * 0)[:, 1]))
        plt.plot(pz, mtf(pz * 0, pz * 0, pz)[:, 2], label='z')
        print(list(mtf(pz * 0, pz * 0, pz)[:, 2]))
        plt.legend()

        plt.show()
    return mtf


def test_interpolation_bounds_repeat():
    px = np.arange(-2, 12, 1)
    py = np.arange(-3, 14, 1.5)
    pz = np.arange(-4, 12, 2)
    mtf = interpolation_bounds(Bounds.Repeat, px, py, pz)
    npt.assert_allclose(mtf(px, px * 0, px * 0)[:, 0],
                        [4.0, 2.0, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 2.0, 0.0, 0.5])
    npt.assert_allclose(mtf(py * 0, py, py * 0)[:, 1],
                        [3.0, 1.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 1.5, 0.0, 0.5])
    npt.assert_allclose(mtf(pz * 0, pz * 0, pz)[:, 2], [1.0, 0.5, 0.0, 0.5, 1.0, 0.5, 0.0, 0.5])


def test_interpolation_bounds_mirror():
    px = np.arange(-2, 17, .5)
    py = np.arange(-3, 19, .75)
    pz = np.arange(-4, 12, 1)
    mtf = interpolation_bounds(Bounds.Mirror, px, py, pz)
    npt.assert_allclose(mtf(px, px * 0, px * 0)[:, 0],
                        [1.0, 0.75, 0.5, 0.25, 0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0,
                         3.25, 3.5, 3.75, 4.0, 3.75, 3.5, 3.25, 3.0, 2.75, 2.5, 2.25, 2.0, 1.75, 1.5, 1.25, 1.0, 0.75,
                         0.5, 0.25, 0.0, 0.25])
    npt.assert_allclose(mtf(py * 0, py, py * 0)[:, 1],
                        [1.0, 0.75, 0.5, 0.25, 0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5, 2.75, 3.0,
                         2.75, 2.5, 2.25, 2.0, 1.75, 1.5, 1.25, 1.0, 0.75, 0.5, 0.25, 0.0, 0.25])
    npt.assert_allclose(mtf(pz * 0, pz * 0, pz)[:, 2],
                        [1.0, 0.75, 0.5, 0.25, 0.0, 0.25, 0.5, 0.75, 1.0, 0.75, 0.5, 0.25, 0.0, 0.25, 0.5, 0.75])


def test_interpolation_bounds_error():
    px = np.linspace(0, 8, 6)
    py = np.linspace(0, 9, 5)
    pz = np.linspace(0, 4, 4)
    mtf = interpolation_bounds(Bounds.Error, px, py, pz)
    for px_ in [-1, 8.1, np.array([-1, 8.1])]:
        with pytest.raises(AssertionError, match=r"out of bounds \(0 to 8\)"):
            mtf(px_, px_ * 0, px_ * 0)

    for py_ in [-1, 9.1, np.array([-1, 9.1])]:
        with pytest.raises(AssertionError, match=r"out of bounds \(0 to 9\)"):
            mtf(py_ * 0, py_, py_ * 0)

    for pz_ in [-1, 4.1, np.array([-1, 4.1])]:
        with pytest.raises(AssertionError, match=r"out of bounds \(0 to 4\)"):
            mtf(pz_ * 0, pz_ * 0, pz_)

    npt.assert_allclose(mtf(px, px * 0, px * 0)[:, 0],
                        [0.0, 0.8, 1.6, 2.4, 3.2, 4.0])
    npt.assert_allclose(mtf(py * 0, py, py * 0)[:, 1],
                        [0.0, 0.75, 1.5, 2.25, 3.0])
    npt.assert_allclose(mtf(pz * 0, pz * 0, pz)[:, 2],
                        [0.0, 0.3333333333333333, 0.6666666666666666, 1.0])


def test_interpolation_bounds_warning():
    px = np.arange(-2, 12, 1)
    py = np.arange(-3, 14, 1.5)
    pz = np.arange(-4, 12, 2)
    mtf = interpolation_bounds(Bounds.Warning, px, py, pz)
    for px_ in [-1, 8.1, np.array([-1, 8.1])]:
        with pytest.warns(Warning, match=r"out of bounds \(0 to 8\)"):
            npt.assert_array_equal(mtf(px_, px_ * 0, px_ * 0), mtf(np.clip(px_, 0, 8), px_ * 0, px_ * 0))

    for py_ in [-1, 9.1, np.array([-1, 9.1])]:
        with pytest.warns(Warning, match=r"out of bounds \(0 to 9\)"):
            npt.assert_array_equal(mtf(py_ * 0, py_, py_ * 0), mtf(py_ * 0, np.clip(py_, 0, 9), py_ * 0))

    for pz_ in [-1, 4.1, np.array([-1, 4.1])]:
        with pytest.warns(Warning, match=r"out of bounds \(0 to 4\)"):
            npt.assert_array_equal(mtf(pz_ * 0, pz_ * 0, pz_), mtf(pz_ * 0, pz_ * 0, np.clip(pz_, 0, 4)))

    with warnings.catch_warnings(action='ignore'):
        npt.assert_allclose(mtf(px, px * 0, px * 0)[:, 0],
                            [0, 0, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4, 4, 4, 4])
        npt.assert_allclose(mtf(py * 0, py, py * 0)[:, 1],
                            [0, 0, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3, 3, 3])
        npt.assert_allclose(mtf(pz * 0, pz * 0, pz)[:, 2], [0, 0, 0.0, 0.5, 1.0, 1, 1, 1])


def test_interpolation_shape(mtf_medium):
    mtf = mtf_medium

    ip_x, ip_z = np.meshgrid(np.linspace(-1000, 10000, 1000), np.linspace(-10, 100, 100))
    ip_y = ip_x * 0
    ref = mtf(ip_x.flatten(), ip_y.flatten(), ip_z.flatten()).reshape(100, 1000, 3)

    res = mtf(ip_x, ip_y, ip_z)
    if 0:
        plt.contourf(ip_x, ip_z, res[..., 0])
        plt.show()
    assert res.shape == (100, 1000, 3)
    npt.assert_array_almost_equal(res, ref)


@pytest.mark.parametrize('hfc', [0, 1])
def test_parallelization(hfc):
    kwargs = dict(alphaepsilon=.5, L=40, Gamma=3, Nxyz=(4096, 16, 8), dxyz=(2, 3, 4), HighFreqComp=hfc)
    mtf_par = MannTurbulenceField.generate(**kwargs, seed=1, n_cpu=None,
                                           random_generator=random_generator_par)
    # Single field
    n = mtf_par.random_generator(mtf_par)  # generate same random sequence as the parallel run
    mtf = MannTurbulenceField.generate(**kwargs, seed=1, random_generator=lambda self: n)
    assert mtf.to_xarray().equals(mtf_par.to_xarray())


def test_versbose():
    MannTurbulenceField.generate(alphaepsilon=.5, L=40, Gamma=3,
                                 Nxyz=(1024, 16, 8), dxyz=(2, 3, 4), seed=1, verbose=1)


# def test_constraints_big_cmp_methods():
#     if 1:
#         axes = plt.subplots(4, 1)[1]
#         from tqdm import tqdm
#         for method in tqdm([1, 2]):
#             mtf = MannTurbulenceField.generate(Nxyz=(4096, 32, 16), dxyz=(2, 3, 4), double_xyz=(0, 0, 0))
#
#             k, S_before = mtf.spectra()
#             N = 100
#             xi = np.round(np.linspace(0, 4095, N)).astype(int)
#             x = xi * mtf.dx
#             y, z = x * 0, x * 0 + 4
#             u = np.arange(N) % 5 - 2
#             v = w = u / 2
#             xi = np.round(np.linspace(0, 4095, N)).astype(int)
#             u, v, w = mtf.uvw[:, xi, 0, 4]
#             constraints = np.array([x, y, z, u, v, w]).T
#             mtf.constrain(constraints[:], method=method)
#
#             S_after = mtf.spectra()[1]
#             S_lut = mtf.spectra_lookup(k)[1]
#             for i, ax in enumerate(axes):
#                 ax.axhline(0, color='k')
#                 c = ax.semilogx(k, k * np.abs(S_before[i] - S_lut[i]), label=f'{method} before')[0].get_color()
#                 ax.semilogx(k, k * np.abs(S_after[i] - S_lut[i]), ':', label=f'{method} after')
#                 ax.set_ylabel('Diff with theoretical')
#
#         ax.legend()
#         plt.show()


@pytest.mark.parametrize('method', [1, 2])
def test_constraints_big(method):
    mtf = MannTurbulenceField.generate(Nxyz=(4096, 32, 16), dxyz=(2, 3, 4))
    plot = 0

    if plot:
        axes = plt.subplots(3, 1)[1]
        for ax, c in zip(axes, 'uvw'):
            mtf.to_xarray().sel(uvw=c, y=0, z=4).plot(ax=ax)

    k, S_before = mtf.spectra()
    N = 10
    x = np.round(np.linspace(0, 4095, N)) * mtf.dx
    x[-1] = x[-2] + 3  # last constraint too close to second last
    y, z = x * 0, x * 0 + 4
    u = np.arange(N) % 5 - 2
    v = w = u / 2
    constraints = np.array([x, x * 0, x * 0 + 4, u, v, w]).T

    mtf.constrain(constraints, method=method)

    S_after = mtf.spectra()[1]

    abs_diff = np.abs(mtf(x, y, z).T - (u, v, w))
    if plot:
        for i, (ax, c) in enumerate(zip(axes, 'uvw')):
            mtf.to_xarray().sel(uvw=c, y=0, z=4).plot(ax=ax)
            ax.axhline(0, color='k')
            ax.plot(constraints[:, 0], constraints[:, i + 3], '.k')
            ax.plot(x, abs_diff[i], label='Constraint error')
            ax.legend()
        k_lut, S_lut = mtf.spectra_lookup(k)

        for i, ax in enumerate(plt.subplots(4, 1)[1]):
            ax.axhline(0, color='k')
            ax.semilogx(k_lut, k_lut * S_lut[i])[0].get_color()
            ax.semilogx(k, k * S_before[i], label='before')
            ax.semilogx(k, k * S_after[i], label='after')
            ax.semilogx(k, k * np.abs(S_lut[i] - S_before[i]), label='abs(lut-before)')
            ax.semilogx(k, k * np.abs(S_lut[i] - S_after[i]), label='abs(lut-after)')
            ax.semilogx(k, k * np.abs(S_after[i] - S_before[i]), label='abs(after-before)')

            ax.legend()
        plt.show()

    # check constraints
    npt.assert_allclose(mtf(x, y, z).T[:, :-1], np.array([u, v, w])[:, :-1], atol=1e-10)
    m = k >= 0.01

    for i in range(4):
        npt.assert_allclose((k * S_after[i])[m], (k * S_before[i])[m], atol=0.11)


def test_coherence():

    Umean = 9.4975
    TI = 0.0549
    Nxyz = Nx, Ny, Nz = 16384, 32, 32
    Tsim = 1100
    dxyz = dx, dy, dz = Tsim * Umean / Nx, 200 / Ny, 200 / Nz
    sigmaIso = Umean * TI * 0.55
    L = 0.8 * 42
    Gamma = 3.9
    alphaepsilon = 55 / 18 * 0.4754 * sigmaIso**2 * L**(-2 / 3)

    def frq(k):
        return k * Umean / (2 * np.pi)

    # %% Coherence spacing
    dy_vect = np.array([3, 6, 1, 0, 0]) * dy
    dz_vect = np.array([0, 0, 1, 3, 6]) * dz

    mtf = MannTurbulenceField.generate(alphaepsilon, L, Gamma, Nxyz, dxyz, HighFreqComp=0, double_xyz=(0, 0, 0))
    coh_ref = [[0.941, 0.926, 0.897, 0.846, 0.757, 0.608, 0.384, 0.129, -0.028, -0.028],
               [0.845, 0.802, 0.727, 0.601, 0.405, 0.144, -0.101, -0.151, -0.023, 0.031],
               [0.986, 0.983, 0.976, 0.964, 0.94, 0.892, 0.798, 0.63, 0.379, 0.107],
               [0.97, 0.962, 0.948, 0.92, 0.864, 0.755, 0.552, 0.251, -0.02, -0.073],
               [0.924, 0.903, 0.865, 0.795, 0.667, 0.447, 0.149, -0.06, -0.032, 0.023]]

    for dy, dz, ref in zip(dy_vect, dz_vect, coh_ref):

        k1, coh = mtf.coherence_integrated(dy, dz)
        k_rea, coh_rea = mtf.coherence(dy, dz)
        f_rea = frq(k_rea)
        if 0:
            plt.figure()
            plt.plot(frq(k1), coh, label='theoretical')

            plt.plot(f_rea, coh_rea, '.-', label='realization')
            plt.plot(frq(k1[::4][:10]), ref, 'x', label='ref')

            print(list(np.round(coh[::4], 3)))
            plt.xlim([0, 0.3])
            plt.xlabel('f[Hz]')
            plt.ylabel('u co-coherence [-]')
            plt.title(r'$\Delta_y$ = %.2fm, $\Delta_z$ = %.2fm' % (dy, dz))
            plt.legend()
            plt.show()
        npt.assert_array_almost_equal(coh[::4][:10], ref, 3)
        m = f_rea < .3
        npt.assert_allclose(coh_rea[m], np.interp(k_rea[m], k1, coh), atol=0.05)


def test_coherence_components():

    mtf = MannTurbulenceField.generate(Nxyz=(16384, 32, 32), double_xyz=(0, 0, 0))
    dy, dz = 1 * mtf.dy, 2 * mtf.dz
    for comp in ['uu', 'vv', 'ww', 'uw', 'uv', 'vw'][:4]:  # for some reason the uv and vw is not working

        k1, coh = mtf.coherence_integrated(dy, dz, component=comp)
        k_rea, coh_rea = mtf.coherence(dy, dz, component=comp, bin_size=0.05)

        if 0:
            plt.figure()

            plt.plot(k1, coh)
            plt.plot(k_rea, coh_rea, '.-')

            print(list(np.round(coh[::4], 3)))
            plt.xlim([0, 0.5])
            plt.xlabel('k[$m^{-1}$]')
            plt.ylabel('co-coherence [-]')
            plt.title(r'%s ($\Delta_y$ = %.2fm, $\Delta_z$ = %.2fm)' % (comp, dy, dz))
            plt.legend()
            plt.show()

        m = k_rea < .5
        npt.assert_allclose(coh_rea[m], np.interp(k_rea[m], k1, coh), atol=0.05)


def test_coherence_n_cpu():

    mtf = MannTurbulenceField.generate(Nxyz=(1024, 32, 32), double_xyz=(0, 0, 0))
    dy, dz = 1 * mtf.dy, 2 * mtf.dz

    k1, coh_seq = mtf.coherence_integrated(dy, dz)
    mtf = MannTurbulenceField.generate(Nxyz=(1024, 32, 32), double_xyz=(0, 0, 0), n_cpu=2)
    k1, coh_par = mtf.coherence_integrated(dy, dz)
    npt.assert_array_equal(coh_seq, coh_par)


def test_hfc_spectra_coherence():
    if 0:
        ax1, ax2 = plt.subplots(1, 2)[1]
        for hfc in [0, 1, 2]:
            # t = time.time()
            mtf = MannTurbulenceField.generate(Nxyz=(1024, 32, 16), dxyz=(1, 2, 3), double_xyz=(0, 1, 1), HighFreqComp=hfc,
                                               verbose=1)
            # print(time.time() - t)
            k, S = mtf.spectra(log10_bin_size=0)
            ax1.semilogx(k, k * S[3], label=f'hipersim HighFreqComp={hfc}')

            k, C = mtf.coherence(2, 3, min_bin_count=1)
            ax2.plot(k, C, label=f'hipersim HighFreqComp={hfc}')

        k, S = mtf.spectra_lookup()
        ax1.semilogx(k, k * S[3], label='LUT')

        k, C = mtf.coherence_integrated(2, 3)
        plt.plot(k, C, label='Theoretical')

        if os.path.isfile(r'cpp\mann_turb_x64.exe'):
            for hfc in [0, 1]:
                run_cpp(name=mtf.name, ae23=mtf.alphaepsilon, L=mtf.L, G=mtf.Gamma,
                        Nx=mtf.Nx, Ny=mtf.Ny, Nz=mtf.Nz, dx=mtf.dx, dy=mtf.dy, dz=mtf.dz,
                        hfc=hfc, seed=mtf.seed, exe=r'cpp\mann_turb_x64.exe')
                filenames = [f'{mtf.name}_{uvw}.bin' for uvw in 'uvw']
                mtf = MannTurbulenceField.from_hawc2(filenames, alphaepsilon=mtf.alphaepsilon, L=mtf.L, Gamma=mtf.Gamma,
                                                     Nxyz=mtf.Nxyz, dxyz=mtf.dxyz,
                                                     seed=mtf.seed, HighFreqComp=mtf.HighFreqComp, double_xyz=mtf.double_xyz)
                k, S = mtf.spectra(log10_bin_size=0)
                ax1.semilogx(k, k * S[3], label=f'cpp HighFreqComp={hfc}')

                k, C = mtf.coherence(2, 3)
                plt.plot(k, C, label=f'cpp HighFreqComp={hfc}')

        ax1.legend()
        ax2.legend()

        plt.show()
