import numpy as np
import matplotlib.pyplot as plt
from hipersim.turbgen.mannspectrum import MannSpectrum_TableLookup
from hipersim.turbgen.generate_field import SpectralTensor
import os
from hipersim.turbgen.turb_utils import spectra
from hipersim.turbgen.manntensor import manntensorcomponents
from hipersim.turbgen.trapezoidal_sum_2d import trapezoidal_sum_2d
import pytest
from hipersim.turbgen.spectral_tensor import MannSpectralTensor

kwargs = dict(alphaepsilon=0.5, L=33.6, Gamma=3.9, HighFreqComp=False,)


@pytest.mark.parametrize('tensor,spectra_function', [
    (SpectralTensor(**kwargs, Nx=1024, Ny=64, Nz=32, dx=1, dy=1, dz=1,
                    double_x=False, double_y=False, double_z=False), 'spectra'),
    (MannSpectralTensor(**kwargs, Nxyz=(1024, 64, 32), double_xyz=(0, 0, 0)), 'spectra_integrated')])
def test_spectra(tensor, spectra_function):
    ae, L, G = .5, 33.6, 3.9
    k = 10**np.linspace(-3, 3, 1000) / L
    _, phi_lut = MannSpectrum_TableLookup(Gamma=G, L=L, alphaepsilon=ae, kinput=k)

    k1, phi = getattr(tensor, spectra_function)(k[::100], 200)
    if 0:
        for p_lut, p in zip(phi_lut, phi):
            c = plt.semilogx(k, k * p_lut)[0].get_color()
            plt.semilogx(k[::100], (k * p_lut)[::100], '.', color=c)

            plt.semilogx(k1, k1 * p)

        # for now use wetb spectra as reference
        from wetb.wind.turbulence.mann_parameters import get_mann_model_spectra
        for s in get_mann_model_spectra(ae=ae, L=L, G=G, k1=k[::100]):
            plt.semilogx(k[::100], (k[::100] * s), 'x')
            print(list(np.round(s, 2)))

        plt.show()

    # compare integrated spectrum with LUT
    np.testing.assert_allclose(k1 * phi, k1 * np.array(phi_lut)[:, ::100], atol=0.004)
    # Compare LUT with reference values
    np.testing.assert_array_almost_equal(np.array(phi_lut)[:, ::100],
                                         [[1327.31, 1219.92, 944.69, 531.16, 163.3, 25.24, 2.76, 0.28, 0.03, 0.0],
                                          [167.55, 170.77, 142.88, 99.08, 54.82, 23.19, 3.7, 0.38, 0.04, 0.0],
                                          [28.81, 29.48, 29.58, 28.95, 21.65, 10.23, 2.58, 0.35, 0.04, 0.0],
                                          [-121.51, -126.98, -121.64, -98.27, -47.63, -9.99, -0.62, -0.02, -0.0, -0.0]], 2)


def test_spectra_default_k():
    ae, L, G = .5, 33.6, 3.9
    k, phi = MannSpectrum_TableLookup(Gamma=G, L=L, alphaepsilon=ae)
    if 0:
        for p in phi:
            c = plt.semilogx(k, k * p)[0].get_color()
            plt.semilogx(k[::10], (k * p)[::10], '.', color=c)

        # for now use wetb spectra as reference
        from wetb.wind.turbulence.mann_parameters import get_mann_model_spectra
        for s in get_mann_model_spectra(ae=ae, L=L, G=G, k1=k[::10]):
            plt.semilogx(k[::10], (k[::10] * s), 'x')
            print(list(np.round(s, 2)))

        plt.show()

    np.testing.assert_array_almost_equal(np.array(phi)[:, ::10],
                                         [[1327.31, 1053.09, 388.79, 25.51, 0.61, 0.01, 0.0],
                                          [167.55, 154.26, 83.43, 23.33, 0.82, 0.02, 0.0],
                                          [28.81, 29.43, 27.49, 10.29, 0.72, 0.02, 0.0],
                                          [-121.51, -124.29, -83.23, -10.1, -0.07, -0.0, -0.0]], 2)


def test_spectra_dx():
    Nx = 1024
    Ny = 64
    Nz = 64
    dy = 6
    dz = 6
    L = 30
    G = 3.0
    ae23 = 0.1

    for dx in [1, 2, 4]:
        hs_uvw = SpectralTensor(alphaepsilon=ae23, L=L, Gamma=G, Nx=Nx, Ny=Ny, Nz=Nz, dx=dx, dy=dy, dz=dz,
                                HighFreqComp=False, double_x=False, double_y=False, double_z=False).generate_field(1)
        k, hs_SUVW = spectra(hs_uvw, Nx, dx)

        if os.path.isfile("cpp/mann_turb_x64.exe"):
            seed = 1001
            exe = r"cpp\mann_turb_x64.exe"

            os.system(f'cmd /c {exe} turb_dx{dx}_s{seed} {ae23} {L} {G} {seed} {Nx} {Ny} {Nz} {dx} {dy} {dz} false')
            cpp_uvw = [np.fromfile(f'turb_dx{dx}_s1001_{uvw}.bin', dtype=np.float32).reshape((Nx, Ny, Nz))
                       for uvw in 'uvw']
            _, cpp_SUVW = spectra(cpp_uvw, Nx, dx)
        else:
            cpp_SUVW = None

        kref, Psiref = MannSpectrum_TableLookup(G, L, ae23, k)

        if 0:
            fig, axes = plt.subplots(2, 2, figsize=(10, 6), dpi=200)
            for i, (ax, uvw) in enumerate(zip(axes.flatten(), ['UU', 'VV', 'WW', 'UW'])):
                ax.semilogx(kref, kref * Psiref[i], label='Theoretical')
                ax.semilogx(k, k * hs_SUVW[i], label='Hipersim')
                if cpp_SUVW:
                    ax.semilogx(k, k * cpp_SUVW[i], label='Mann C++')
                    ax.axvline(0.01)
                    ax.axvline(0.1)
                ax.set_title(uvw)
                ax.legend()
            fig.suptitle(f'dx = {dx}')
            plt.show()

        m = (np.log10(k) > -2) & (np.log10(k) < -1)
        for i, uvw in enumerate(['UU', 'VV', 'WW']):
            #print(uvw, np.abs(np.log10((k * hs_SUVW[i])[m]) - np.log10((k * Psiref[i])[m])).max())
            np.testing.assert_allclose(np.log10((k * hs_SUVW[i])[m]), np.log10((k * Psiref[i])[m]), atol=.16)
            if cpp_SUVW:
                # print(uvw, np.abs(np.log10((k * hs_SUVW[i])[m]) - np.log10((k * cpp_SUVW[i])[m])).max())
                np.testing.assert_allclose(np.log10((k * hs_SUVW[i])[m]), np.log10((k * cpp_SUVW[i])[m]), atol=.2)

        # print('UW', np.abs((k * hs_SUVW[3])[m] - (k * Psiref[3])[m]).max())
        np.testing.assert_allclose((k * hs_SUVW[3])[m], (k * Psiref[3])[m], atol=.025)
        if cpp_SUVW:
            # print('UW', np.abs((k * hs_SUVW[3])[m] - (k * cpp_SUVW[3])[m]).max())
            np.testing.assert_allclose((k * hs_SUVW[3])[m], (k * cpp_SUVW[3])[m], atol=.017)


def test_spectra_dx_new():
    Nx = 1024
    Ny = 64
    Nz = 64
    dy = 6
    dz = 6
    L = 30
    G = 3.0
    ae23 = 0.1

    for dx in [1, 2, 4]:
        mtf = MannSpectralTensor(alphaepsilon=ae23, L=L, Gamma=G, Nxyz=(Nx, Ny, Nz), dxyz=(dx, dy, dz),
                                 HighFreqComp=False, double_xyz=(0, 0, 0)).generate(1)
        k, hs_SUVW = mtf.spectra(log10_bin_size=0)

        if os.path.isfile("cpp/mann_turb_x64.exe"):
            seed = 1001
            exe = r"cpp\mann_turb_x64.exe"

            os.system(f'cmd /c {exe} turb_dx{dx}_s{seed} {ae23} {L} {G} {seed} {Nx} {Ny} {Nz} {dx} {dy} {dz} false')
            cpp_uvw = [np.fromfile(f'turb_dx{dx}_s1001_{uvw}.bin', dtype=np.float32).reshape((Nx, Ny, Nz))
                       for uvw in 'uvw']
            _, cpp_SUVW = spectra(cpp_uvw, Nx, dx)
        else:
            cpp_SUVW = None

        kref, Psiref = mtf.spectra_lookup(k)

        if 0:
            fig, axes = plt.subplots(2, 2, figsize=(10, 6), dpi=200)
            for i, (ax, uvw) in enumerate(zip(axes.flatten(), ['UU', 'VV', 'WW', 'UW'])):
                ax.semilogx(kref, kref * Psiref[i], label='Theoretical')
                ax.semilogx(k, k * hs_SUVW[i], label='Hipersim')
                if cpp_SUVW:
                    ax.semilogx(k, k * cpp_SUVW[i], label='Mann C++')
                    ax.axvline(0.01)
                    ax.axvline(0.1)
                ax.set_title(uvw)
                ax.legend()
            fig.suptitle(f'dx = {dx}')
            plt.show()

        m = (np.log10(k) > -2) & (np.log10(k) < -1)
        for i, uvw in enumerate(['UU', 'VV', 'WW']):
            #print(uvw, np.abs(np.log10((k * hs_SUVW[i])[m]) - np.log10((k * Psiref[i])[m])).max())
            np.testing.assert_allclose(np.log10((k * hs_SUVW[i])[m]), np.log10((k * Psiref[i])[m]), atol=.16)
            if cpp_SUVW:
                # print(uvw, np.abs(np.log10((k * hs_SUVW[i])[m]) - np.log10((k * cpp_SUVW[i])[m])).max())
                np.testing.assert_allclose(np.log10((k * hs_SUVW[i])[m]), np.log10((k * cpp_SUVW[i])[m]), atol=.2)

        # print('UW', np.abs((k * hs_SUVW[3])[m] - (k * Psiref[3])[m]).max())
        np.testing.assert_allclose((k * hs_SUVW[3])[m], (k * Psiref[3])[m], atol=.025)
        if cpp_SUVW:
            # print('UW', np.abs((k * hs_SUVW[3])[m] - (k * cpp_SUVW[3])[m]).max())
            np.testing.assert_allclose((k * hs_SUVW[3])[m], (k * cpp_SUVW[3])[m], atol=.017)


@pytest.mark.parametrize('tensor', [SpectralTensor, MannSpectralTensor])
def test_coherence(tensor):

    Umean = 9.4975
    TI = 0.0549
    Nx = 16384
    # Nx = 8192
    Ny = 32
    Nz = 32
    Tsim = 1100
    dx = Tsim * Umean / Nx
    dy = 200 / Ny
    dz = 200 / Nz
    sigmaIso = Umean * TI * 0.55
    L = 0.8 * 42
    Gamma = 3.9
    alphaepsilon = 55 / 18 * 0.4754 * sigmaIso**2 * L**(-2 / 3)

    # %% Generate the turbulence boxes
    if tensor is SpectralTensor:
        u = SpectralTensor(alphaepsilon, L, Gamma, Nx, Ny, Nz, dx, dy, dz, HighFreqComp=0,
                           double_x=False, double_y=False, double_z=False).generate_field(1001)[0]
    else:
        u = MannSpectralTensor(alphaepsilon, L, Gamma,
                               Nxyz=(Nx, Ny, Nz), dxyz=(dx, dy, dz), HighFreqComp=0,
                               double_xyz=(0, 0, 0)).generate_uvw(seed=1001)[0]

    N1int = Nx
    L1 = N1int * dx
    m1 = np.concatenate([np.arange(0, N1int / 2), np.arange(-N1int / 2, 0)])
    k1 = m1 * 2 * np.pi / L1
    klogrange = np.linspace(-6, 2, 100)
    k1shift = 10**np.linspace(np.log10(np.min(k1[k1 > 0])), np.log10(np.max(k1)), 60)
    f1shift = k1shift * Umean / (2 * np.pi)
    k1shift, f1shift = k1shift[f1shift < 0.4], f1shift[f1shift < 0.4]

    k23shift = np.concatenate([-np.flip(10**klogrange), 10**klogrange])

    # %% Coherence spacing
    deltak2_vect = [3, 6, 1, 0, 0]
    deltak3_vect = [0, 0, 1, 3, 6]

    # %% Compute  coherence
    for deltak2, deltak3 in zip(deltak2_vect, deltak3_vect):

        # THEORETICAL COHERENCE
        PsiCrossij = np.zeros(len(k1shift), dtype='csingle')
        PsiPointi = np.zeros(len(k1shift))
        PsiPointj = np.zeros(len(k1shift))

        [k3i, k2i] = np.meshgrid(k23shift, k23shift)

        for i in range(len(k1shift)):
            k1i = np.ones(k2i.shape) * k1shift[i]
            Phiij = manntensorcomponents(k1i, k2i, k3i, Gamma, L, alphaepsilon, 2)[0]
            PhiDeltaij = Phiij * np.exp(1j * (k2i * deltak2 * dy + k3i * deltak3 * dz))
            PsiCrossij[i] = trapezoidal_sum_2d(PhiDeltaij, k23shift, k23shift)
            PsiPointi[i] = trapezoidal_sum_2d(Phiij, k23shift, k23shift)
            PsiPointj[i] = PsiPointi[i]

        Coherence_ref = np.real(PsiCrossij) / PsiPointi

        # Coherence from time series
        ui, uj = u, u
        if deltak2:
            ui, uj = ui[:, :-deltak2], uj[:, deltak2:]
        if deltak3:
            ui, uj = ui[:, :, :-deltak3], uj[:, :, deltak3:]
        _, (SUPiens2, _, _, SUPijens2) = spectra([ui, ui[:8, :8, :8], uj], Nx, dx, exclude_zero=True)
        SUPiens, SUPijens = [SUP / (dx / (2 * np.pi * Nx)) * (1 / (np.sqrt(2) * Nx * dx))
                             for SUP in [SUPiens2, SUPijens2]]

        CoherenceP = (np.real(SUPijens) / SUPiens)[:8192]

        k1plot = np.arange(0, int(Nx / 2)) * 2 * np.pi / L1
        f1plot = k1plot * Umean / (2 * np.pi)
        f1plot_mean = f1plot.reshape((1024, 8)).mean(1)
        CoherenceP_mean = CoherenceP.reshape((1024, 8)).mean(1)
        m = (f1shift > 0.02) & (f1shift < 0.3)

        if 0:
            plt.figure()
            plt.plot(f1plot, CoherenceP, label='Hipersim')
            plt.plot(f1plot_mean, CoherenceP_mean, label='Hipersim_mean')
            f1plot.reshape((8, 1024)).mean(0)
            plt.plot(f1shift, Coherence_ref, '-b', label='Mann model')

            plt.xlim([0, 0.3])
            plt.xlabel('f[Hz]')
            plt.ylabel('u co-coherence [-]')
            plt.title(r'$\Delta_y$ = %.2fm, $\Delta_z$ = %.2fm' % (deltak2 * dy, deltak3 * dz))
            plt.legend()
            print(np.abs(np.interp(f1shift[m], f1plot_mean, CoherenceP_mean[:]) - Coherence_ref[m]).max())
            plt.show()
        np.testing.assert_allclose(np.interp(f1shift[m], f1plot_mean,
                                   CoherenceP_mean[:]), Coherence_ref[m], atol=0.06)
