# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 12:23:07 2021

@author: nkdi, mmpe, astah
"""
import numpy as np
from hipersim.turbgen.manntensor import manntensorsqrtcomponents, manntensorcomponents, matrix_sqrt_vec, matrix_sqrt
from hipersim.turbgen.trapezoidal_sum_2d import trapezoidal_sum_2d


import multiprocessing
from tqdm import tqdm
from numpy import newaxis as na
import itertools
import os
from hipersim.turbgen.turb_utils import get_k
from hipersim._hipersim import TurbulenceInput
from hipersim.mann_turbulence import MannTurbulenceInput
pool_dict = {}


def init_worker(*args):
    pass


def get_pool(n_cpu):
    n_cpu = n_cpu or multiprocessing.cpu_count()
    if n_cpu not in pool_dict:
        print(f"initialize pool with {n_cpu} cpus")
        pool_dict[n_cpu] = multiprocessing.Pool(n_cpu)
        pool_dict[n_cpu].map(init_worker, range(n_cpu))
    return pool_dict[n_cpu]


def random_generator_seq(self):

    from numpy.random import Generator, PCG64
    rg = Generator(PCG64(self.seed))
    return (random_standard_normal(rg, (self.N1r, self.N2, self.N3)) for _ in range(3))


def random_generator_par(self):
    from numpy.random import SeedSequence
    ss = SeedSequence(self.seed)

    for _ in range(3):
        n1 = np.diff(np.linspace(0, self.N1r, min(self.N1r, self.n_cpu * 4)).astype(int))
        args_lst = [(s, (n, self.N2, self.N3)) for s, n in zip(ss.spawn(len(n1)), n1)]
        n = np.array([e for lst in get_pool(self.n_cpu).starmap(random_standard_normal, args_lst) for e in lst])
        imap = get_pool(self.n_cpu).imap
        n = np.fromiter(itertools.chain.from_iterable(imap(random_standard_normal_args, args_lst)),
                        dtype=(np.complex64, (self.N2, self.N3)))
        yield n


def random_standard_normal_args(args):
    generator, shape = args
    return random_standard_normal(generator, shape)


def random_standard_normal(generator, shape):
    from numpy.random import Generator, PCG64
    if not isinstance(generator, Generator):
        generator = Generator(PCG64(generator))
    return (generator.standard_normal(shape, dtype='float32') +
            generator.standard_normal(shape, dtype='float32') * 1j)


class MannSpectralTensor(MannTurbulenceInput):
    _spectral_vars = None

    def __init__(self, alphaepsilon=1, L=33.6, Gamma=3.9, Nxyz=(8192, 64, 64), dxyz=(1, 1, 1), HighFreqComp=0,
                 double_xyz=(False, True, True), n_cpu=1, verbose=0, seed=1,
                 cache_spectral_tensor=False):
        """Generate a MannSpectralTensor

        Parameters
        ----------
        alphaepsilon : float, optional
            Mann model turbulence parameter $(\\alpha \\varepsilon)^{2/3}$ (Mann, 1994), default is 1.
        L : float, optional
            Mann model turbulence length scale parameter $L$ (Mann, 1994), default is 33.6
        Gamma : float, optional
            Mann model turbulence anisotropy parameter $\\Gamma$ (Mann, 1994), default is 3.9
        Nxyz: (int,int,int)
            Dimension of the turbulence box in x (longitudinal), y (transveral) and z (vertical) direction.
            Default is (8192,64,64)
        dxyz : (float, float, float), optional
            Spacing in meters between data points along the x,y,z coordinates. Default is (1,1,1)
        HighFreqComp : bool, optional
            Defines whether high-frequency compensation is applied. There are three options
            0 or False (default): No high-frequency compensation applied
            1 or True: A fast high-Frequency compensation method is applied. This method differs from the method in Mann (1998)
            2: The high-Frequency compensation method from the C++ version is applied.
            The method corresponds to Eq. A.6 in Mann (1998) except that the convolution is only applied in the (k2,k3),
            i.e. -2<=n_l<=2, l=(2,3)
        double_xyz : (bool,bool,bool)
            Defines whether doubling is enabled along the x, y and z direction.
            When doubling is applied, a box with the double size is generated and the first half is returned. In this
            way periodicity is avoided.
            Default is False in the x direction and True in the y and z direction
        n_cpu : int or None, optional
            Number of CPUs to use for the turbulence generation. Default is 1 (no parallelization).
            If None, all available CPUs are used.
        verbose : bool
            If true, status messages and progress bars are printed
        seed : int, optional
            Seed number for random generator. Default is 1
        cache_spectral_tensor : boolean, optional
            If True, the spectral tensor is loaded from file if exists otherwise it is calculated and saved to file
            If False, the spectral tensor is always recalculated

        """
        MannTurbulenceInput.__init__(self, alphaepsilon, L, Gamma, Nxyz, dxyz, seed=seed, HighFreqComp=HighFreqComp,
                                     double_xyz=double_xyz,
                                     n_cpu=n_cpu, generator='hipersim')
        self.verbose = verbose
        self.cache_spectral_tensor = cache_spectral_tensor

    def generate_spectral_tensor(self):
        self.log('Generate spectral tensor')

        N1 = self.N1
        k1_lst = self.k1

        var_ratio = self._HighFreqCompVarRatio(k1_lst)

        args_lst = [(k1, ik1, N1, ratio)
                    for ik1, (k1, ratio) in enumerate(zip(k1_lst, var_ratio))]
        it = self._imap_iter(self._generate_spectral_tensor_k1, args_lst,
                             desc='Generate spectral tensor', N=len(k1_lst))
        SqrtPhi = np.fromiter(it, np.dtype((np.float32, (3, 3, self.N2, self.N3))))

        SqrtPhi = np.moveaxis(SqrtPhi, 0, 2)
        return SqrtPhi

    def _generate_spectral_tensor_k1(self, args):
        # I have tried to vectorize on k1 also, but
        # manntensor_(k1[:,na,na], k2[na,:,na], k3[na,na,:] was significantly slower than
        # [manntensor_(np.full(k2grid.shape,k1_),k2grid,k3grid for k1_ in k1_lst]

        k1, ik1, N1, VarRatio = args

        pi = np.pi
        N2, N3 = self.N2, self.N3
        dx, dy, dz = self.dx, self.dy, self.dz
        alphaepsilon = 1
        L, Gamma = self.L, self.Gamma
        HighFreqComp = self.HighFreqComp
        '''
        -----------------------------------------
        Settings for low frequency correction.
        -----------------------------------------'''
        # knormlim = [np.inf, np.inf, np.inf]  # Apply low-freq correction to all wavenumbers
        # knormlim = np.array([0, 0, 0]) # No low-freq correction
        knormlim = np.array([3 / L, 4 * pi / (N2 * dy), 4 * pi / (N3 * dz)])  # Recommendation from Mann 1998

        '''
        ===========================================
         Define wave number vectors
        ==========================================='''
        L1 = N1 * dx
        L2 = N2 * dy
        L3 = N3 * dz

        k2, k3 = self.k23

        VolumeCoef = np.sqrt((8 * (pi**3) / (L1 * L2 * L3)))

        '''
        ==================================================================
         Prepare numerical integration for accurate low-frequency spectra
        ==================================================================
        '''
        SincCorrectionFactors = np.array([1.22686, 1.10817, 1.07072, 1.05248, 1.04171])
        Nsinc = 1
        SincCorrection = SincCorrectionFactors[Nsinc - 1]
        k2local = np.linspace(- Nsinc * 2 * pi / L2, Nsinc * 2 * pi / L2, N2)
        k3local = np.linspace(- Nsinc * 2 * pi / L3, Nsinc * 2 * pi / L3, N3)
        S2 = k2local[:, na] * L2 / 2
        Sinc2 = (np.sin(S2) / S2)**2
        Sinc2[S2 == 0] = 1
        S3 = k3local[na, :] * L3 / 2
        Sinc3 = (np.sin(S3) / S3)**2
        Sinc3[S3 == 0] = 1
        SincProd = Sinc2 * Sinc3

        '''
        ======================================================================
         Pre-generate arrays with the Mann Tensor square-root matrices
        ======================================================================'''

        ik2grid, ik3grid = np.arange(N2)[:, na], np.arange(N3)[na, :]
        ComputeRange = (((ik1 + 1) / N1 + (ik2grid + 1) / N2 +
                         (ik3grid + 1) / N3 - 3 / 2 - 1 / N3) <= 0)

        InVolLists = np.where(((abs(k1) < knormlim[0]) & (abs(k2[ik2grid]) < knormlim[1]) &
                               (abs(k3[ik3grid]) < knormlim[2])) & ComputeRange)

        del ComputeRange

        '''
        ==============================================================================
        Implementation of eq. 46 in Mann (1998) over all wave numbers.
        The square root of the Mann tensor is computed, however without multiplying
        with random complex standard normal coefficients yet.

        Some of the values for low wave numbers will later be overwritten by the
        implementation of eq. 47 in Mann (1998), but this is normally less than 0.1%
        of the total number of coefficients, so it is not convenient to exclude
        these wave number ranges.

        If no high-frequency compensation is required, just the Mann tensor square root
        over all wave numbers is computed. It is done in a loop over k1, as a
        compromise between computational speed requirements (best avoiding all loops)
        and memory requirements (making a full 3-D grid of k1, k2 and k3 values will
        require many megabytes of extra memory).
        =============================================================================='''

        if HighFreqComp:
            if HighFreqComp == 2:

                # const int Order=2;  /* Max "n" in eq A.6 */
                order = 2

                # /* The main part of the spectra tensor: */
                SPhi = np.array(manntensorsqrtcomponents(k1, k2[:, na], k3[na, :], Gamma, L, alphaepsilon, 2),
                                dtype=np.float32)
                # SPhi @ SPhi.T for all k2, k3
                Phi = np.einsum('ij...,kj...->ik...', SPhi, SPhi)
                HiFPhi = np.zeros_like(Phi)

                # /* The extra high frequency part of the spectral tensor modelled as isotropic turbulnce: */
                # /*  Anisotrpic implementation with "deconvolution" in the x-direction dropped.
                HiFPhi = np.zeros_like(Phi)
                jk_lst = [(j, k) for j in range(-order, order + 1) for k in range(-order, order + 1)
                          if not ((j == 0) & (k == 0))]
                for j, k in jk_lst:
                    sphi = manntensorsqrtcomponents(k1, k2[:, na] + 2 * np.pi * j / self.dy,
                                                    k3[na, :] + 2 * np.pi * k / self.dz,
                                                    0, self.L, self.alphaepsilon, 2)

                    HiFPhi += np.einsum('ij...,kj...->ik...', sphi, sphi)
                Phi += HiFPhi

                SqrtPhi = matrix_sqrt_vec(np.moveaxis(Phi.reshape((3, 3, -1)), -1, 0))
                SqrtPhi = np.moveaxis(SqrtPhi, 0, -1).reshape(Phi.shape)

            else:
                '''
                -------------------------------------------------------------------------
                High-frequency compensation is done by directly applying the compensation
                terms to the main diagonal of the "sheared tensor" matrix given in eq.13
                in Mann (1998). May not be ideal as it also introduces variance increase
                in the off-diagonal terms in the full Mann tensor - but it allows to
                directly assemble the square-root Mann tensor, avoiding the need for
                computing a matrix square root. This is especially important for the
                Python implementation of the code, because the np.linalg.eig() and
                np.lib.scimath.sqrt() functions are extremely slow, increasing the
                computation time 20-fold.
                ----------------------------------------------------------------------'''
                SqrtPhi = np.array(manntensorsqrtcomponents(k1, k2[:, na], k3[na, :], Gamma, L, alphaepsilon, 2,
                                                            VarianceRatios=np.sqrt(VarRatio)),
                                   dtype=np.float32)
        else:
            '''
            ----------------------------------------------------------------------------
            Implementation of eq. 46 in Mann (1998) over all wave numbers without
            high-frequency compensation.
            ----------------------------------------------------------------------------'''

            SqrtPhi = np.array(manntensorsqrtcomponents(
                k1, k2[:, na], k3[na, :], Gamma, L, alphaepsilon, 2), dtype=np.float32)

        SqrtPhi *= VolumeCoef

        '''
            ==============================================================================
             Implementation of eq. 47 in Mann (1998) for low wave numbers where the sinc
             function is not delta-function like.
            =============================================================================='''

        for ik2, ik3 in zip(*InVolLists):

            k2primei = k2[ik2] - k2local
            k3primei = k3[ik3] - k3local
            PhiInt11ij, PhiInt22ij, PhiInt33ij, PhiInt12ij, PhiInt13ij, PhiInt23ij = manntensorcomponents(
                k1, k2primei[:, na], k3primei[na, :], Gamma, L, alphaepsilon, 2)

            C11i = trapezoidal_sum_2d(PhiInt11ij * SincProd, k2primei, k3primei)
            C22i = trapezoidal_sum_2d(PhiInt22ij * SincProd, k2primei, k3primei)
            C33i = trapezoidal_sum_2d(PhiInt33ij * SincProd, k2primei, k3primei)
            C12i = trapezoidal_sum_2d(PhiInt12ij * SincProd, k2primei, k3primei)
            C13i = trapezoidal_sum_2d(PhiInt13ij * SincProd, k2primei, k3primei)
            C23i = trapezoidal_sum_2d(PhiInt23ij * SincProd, k2primei, k3primei)

            Cij = (SincCorrection * 2 * pi / L1) * \
                np.array([[C11i, C12i, C13i], [C12i, C22i, C23i], [C13i, C23i, C33i]])
            if HighFreqComp:
                '''
                ----------------------------------------
                  Apply eq. A6 in Mann (1998).
                ----------------------------------------'''
                Cij[np.diag_indices(3)] *= VarRatio
            SqrtCij = matrix_sqrt(Cij)
            SqrtPhi[:, :, ik2, ik3] = SqrtCij

        return SqrtPhi

    def _HighFreqCompVarRatio(self, k1):
        if self.HighFreqComp:
            '''
            ---------------------------------------------------------------------
            Implementation of high-frequency compensation based on computing the
            variance loss due to aliasing. Significantly faster than implementing
            eq. A6 in Mann (1998). The variance loss ratio is computed by integrating
            the u, v, w components of the Mann spectrum over two k2-k3 planes with
            different spans: one with the k2-k3 span of the desired turbulence box,
            the other one with much bigger span to approximate the range of k's from
            -Inf to Inf.
            ---------------------------------------------------------------------'''
            p2delta = 4
            p3delta = 4
            N1, N2, N3 = self.N1, self.N2, self.N3
            pi = np.pi
            dx, dy, dz = self.dx, self.dy, self.dz
            alphaepsilon, L, Gamma = self.alphaepsilon, self.L, self.Gamma

            L1 = N1 * dx
            L2 = N2 * dy
            L3 = N3 * dz

            k2, k3 = self.k23

            nk2deltapoints = N2
            nk3deltapoints = N3

            k2deltaint0 = np.concatenate([k2[int(N2 / 2):], k2[0:int(N2 / 2)]])
            k3deltaint0 = np.concatenate([k3[int(N3 / 2):], k3[0:int(N3 / 2)]])

            k2deltarange1 = [N2 * pi / L2, (p2delta + 1) * N2 * pi / L2]
            k3deltarange1 = [N3 * pi / L3, (p3delta + 1) * N3 * pi / L3]
            k21p = 10**(np.linspace(np.log10(k2deltarange1[0]),
                        np.log10(k2deltarange1[1]), int(np.floor(nk2deltapoints / 2))))
            k31p = 10**(np.linspace(np.log10(k3deltarange1[0]),
                        np.log10(k3deltarange1[1]), int(np.floor(nk3deltapoints / 2))))
            k2deltaint1 = np.concatenate([-np.flip(k21p[1:]), k2deltaint0, k21p])
            k3deltaint1 = np.concatenate([-np.flip(k31p[1:]), k3deltaint0, k31p])

            VarRatio = np.ones((len(k1), 3))
            k1p = np.linspace(0, N1 * pi / L1, int(np.floor(np.max([(N1 / 32 + 1), 33]))))
            k1interp = np.concatenate([-np.flip(k1p[1:]), k1p])
            VarRatioInterp = np.ones((k1interp.shape[0], 3))

            for ik1p in range(k1interp.shape[0]):
                PhiHiFreq11ij, PhiHiFreq22ij, PhiHiFreq33ij, __, __, __ = manntensorcomponents(k1interp[ik1p],
                                                                                               k2deltaint1[:, na], k3deltaint1[na, :], Gamma, L, alphaepsilon, 2)
                VarHigh11 = trapezoidal_sum_2d(PhiHiFreq11ij, k2deltaint1, k3deltaint1)
                VarHigh22 = trapezoidal_sum_2d(PhiHiFreq22ij, k2deltaint1, k3deltaint1)
                VarHigh33 = trapezoidal_sum_2d(PhiHiFreq33ij, k2deltaint1, k3deltaint1)
                PhiLowFreq11ij, PhiLowFreq22ij, PhiLowFreq33ij, __, __, __ = manntensorcomponents(k1interp[ik1p],
                                                                                                  k2deltaint0[:, na], k3deltaint0[na, :], Gamma, L, alphaepsilon, 2)
                VarLow11 = trapezoidal_sum_2d(PhiLowFreq11ij, k2deltaint0, k3deltaint0)
                VarLow22 = trapezoidal_sum_2d(PhiLowFreq22ij, k2deltaint0, k3deltaint0)
                VarLow33 = trapezoidal_sum_2d(PhiLowFreq33ij, k2deltaint0, k3deltaint0)
                VarRatioInterp[ik1p, 0] = VarHigh11 / VarLow11
                VarRatioInterp[ik1p, 1] = VarHigh22 / VarLow22
                VarRatioInterp[ik1p, 2] = VarHigh33 / VarLow33

            VarRatio[:, 0] = np.interp(k1, k1interp, VarRatioInterp[:, 0])
            VarRatio[:, 1] = np.interp(k1, k1interp, VarRatioInterp[:, 1])
            VarRatio[:, 2] = np.interp(k1, k1interp, VarRatioInterp[:, 2])
            return VarRatio
        else:
            return np.ones((len(k1), 3))

    def generate_uvw(self, seed, alphaepsilon=None, random_generator=None):
        self.seed = seed
        self.random_generator = random_generator or [random_generator_par, random_generator_seq][self.n_cpu == 1]
        SqrtPhi = self.spectral_vars

        alphaepsilon = alphaepsilon or self.alphaepsilon
        N1, N2, N3 = self.N1, self.N2, self.N3
        Nx, Ny, Nz = self.Nx, self.Ny, self.Nz
        N1r = N1 // 2 + 1

        '''
        ===================================================================================
        The rest of the code multiplies the Mann tensor square root values with
        random complex Gaussian coefficients and inverse Fourier-transforms to obtain
        the final turbulence box. This is done over a loop to allow quicker generation
        of multiple turbulence boxes with identical spectral properties but different seeds.
        ==================================================================================='''

        # use Generator, MT19937 to match the (SeedNo,'twister') behavior in Matlab

        '''
        ===========================================================================
         Initialize random number generator with the seed number requested
        ==========================================================================='''

        Cxyz = np.zeros((3, N1r, N2, N3), dtype=np.complex64)

        for i, n in enumerate(tqdm(self.random_generator(self), total=3,
                                   desc='Generate random numbers', disable=not self.verbose)):

            for j in range(3):  # slightly slower, but reduces memory usage
                Cxyz[j] += SqrtPhi[j, i] * n

        Cxyz /= np.sqrt(2)
        del n
        del SqrtPhi

        '''
        ============================================================================================
         Adjust coefficients to enforce symmetry (only about half of the coefficients are filled in)
        ============================================================================================
                    Symmetry by astah
        -------------------------------------------------------------------------------------------'''

        # # Symmetry in 3D around the plane x = N1/2 and excluding the zero edge plane and the centerplane:
        # Cind = np.where((ik1grid > 0) & (ik1grid < N1 / 2))
        # Cxyz[:, -Cind[0], -Cind[1], -Cind[2]] = np.conj(Cxyz[:, Cind[0], Cind[1], Cind[2]])
        # Symmetry in the two 2d planes:
        ik1grid = np.arange(self.N1r)[:, na, na]
        ik2grid = np.arange(self.N2)[na, :, na]
        ik3grid = np.arange(self.N3)[na, na, :]
        Cind = np.where(((ik1grid == 0) | (ik1grid == N1 / 2)) &
                        ((ik2grid > 0) & (ik2grid < N2 / 2)) &
                        (ik3grid >= 0))

        Cxyz[:, Cind[0], -Cind[1], -Cind[2]] = np.conj(Cxyz[:, Cind[0], Cind[1], Cind[2]])

        # Symmetry along the edges in the planes:
        Cind = np.where(((ik1grid == 0) | (ik1grid == N1 / 2)) &
                        ((ik2grid == 0) | (ik2grid == N2 / 2)) &
                        ((ik3grid > 0) & (ik3grid < N3 / 2)))
        Cxyz[:, Cind[0], -Cind[1], -Cind[2]] = np.conj(Cxyz[:, Cind[0], Cind[1], Cind[2]])

        # Make the zero and centerpoints real:
        Cind = np.where(((ik1grid == 0) | (ik1grid == N1 / 2)) &
                        ((ik2grid == 0) | (ik2grid == N2 / 2)) &
                        ((ik3grid == 0) | (ik3grid == N3 / 2)))
        Cxyz[:, Cind[0], Cind[1], Cind[2]] = np.real(Cxyz[:, Cind[0], Cind[1], Cind[2]])

        # '''
        # ============================================================================================
        #  Adjust coefficients to enforce symmetry (only about half of the coefficients are filled in)
        # ============================================================================================
        #  The logics of the symmetry conditions are based on Lasse Gilling's
        #  "TuGen" code (Gilling, L. (2009) TuGen: Synthetic Turbulence
        #  Generator, Manual and User's Guide)
        # -------------------------------------------------------------------------------------------'''

        # Cxconj = np.conj(Cx)
        # Cyconj = np.conj(Cy)
        # Czconj = np.conj(Cz)

        # Cprev = np.full((N1,N2,N3),False)
        # Cindex = ( ((ik1grid+1) == 1) | ((ik1grid+1) == N1/2+1 )) & ( ((ik2grid+1)==1) | ((ik2grid+1) == N2/2+1)) & (( (ik3grid+1) == 1) | ((ik3grid+1) == N3/2+1 ))
        # Cx[Cindex] = np.real(Cx[Cindex])
        # Cy[Cindex] = np.real(Cy[Cindex])
        # Cz[Cindex] = np.real(Cz[Cindex])
        # Cprev[Cindex] = True
        # Cindex = ( ((ik2grid+1) == 1) | ((ik2grid+1) == N2/2+1) ) & ( ((ik3grid+1)==1) | ((ik3grid+1) == N3/2+1)) & ((ik1grid+1) > (N1/2 + 1))
        # Cx[Cindex] = np.flip(np.roll(Cxconj, -1, axis = 0),axis = 0)[Cindex]
        # Cy[Cindex] = np.flip(np.roll(Cyconj, -1, axis = 0),axis = 0)[Cindex]
        # Cz[Cindex] = np.flip(np.roll(Czconj, -1, axis = 0),axis = 0)[Cindex]
        # Cprev[Cindex] = True
        # Cindex = ( ((ik1grid+1) == 1) | ((ik1grid+1) == N1/2+1) ) & ( ((ik3grid+1)==1) | ((ik3grid+1) == N3/2+1)) & ((ik2grid+1) > (N2/2 + 1))
        # Cx[Cindex] = np.flip(np.roll(Cxconj, -1, axis = 1),axis = 1)[Cindex]
        # Cy[Cindex] = np.flip(np.roll(Cyconj, -1, axis = 1),axis = 1)[Cindex]
        # Cz[Cindex] = np.flip(np.roll(Czconj, -1, axis = 1),axis = 1)[Cindex]
        # Cprev[Cindex] = True
        # Cindex = ( ((ik1grid+1) == 1) | ((ik1grid+1) == N1/2+1) ) & ( ((ik2grid+1)==1) | ((ik2grid+1) == N2/2+1)) & ((ik3grid+1) > (N3/2 + 1))
        # Cx[Cindex] = np.flip(np.roll(Cxconj, -1, axis = 2),axis = 2)[Cindex]
        # Cy[Cindex] = np.flip(np.roll(Cyconj, -1, axis = 2),axis = 2)[Cindex]
        # Cz[Cindex] = np.flip(np.roll(Czconj, -1, axis = 2),axis = 2)[Cindex]
        # Cprev[Cindex] = True
        # Cindex = ( (ik1grid+1) > N1/2 + 1) & ( ((ik2grid+1) == 1) | ((ik2grid+1) == N2/2 + 1)) & (Cprev == False)
        # Cx[Cindex] = np.flip(np.roll(Cxconj, -1, axis = (0,2)),axis = (0,2))[Cindex]
        # Cy[Cindex] = np.flip(np.roll(Cyconj, -1, axis = (0,2)),axis = (0,2))[Cindex]
        # Cz[Cindex] = np.flip(np.roll(Czconj, -1, axis = (0,2)),axis = (0,2))[Cindex]
        # Cprev[Cindex] = True
        # Cindex = ( (ik1grid+1) > N1/2 + 1) & ( ((ik3grid+1) == 1) | ((ik3grid+1) == N3/2 + 1))
        # Cx[Cindex] = np.flip(np.roll(Cxconj, -1, axis = (0,1)),axis = (0,1))[Cindex]
        # Cy[Cindex] = np.flip(np.roll(Cyconj, -1, axis = (0,1)),axis = (0,1))[Cindex]
        # Cz[Cindex] = np.flip(np.roll(Czconj, -1, axis = (0,1)),axis = (0,1))[Cindex]
        # Cprev[Cindex] = True
        # Cindex = ( (ik2grid+1) > N2/2 + 1) & ( ((ik1grid+1) == 1) | ((ik1grid+1) == N1/2 + 1))
        # Cx[Cindex] = np.flip(np.roll(Cxconj, -1, axis = (1,2)),axis = (1,2))[Cindex]
        # Cy[Cindex] = np.flip(np.roll(Cyconj, -1, axis = (1,2)),axis = (1,2))[Cindex]
        # Cz[Cindex] = np.flip(np.roll(Czconj, -1, axis = (1,2)),axis = (1,2))[Cindex]
        # Cprev[Cindex] = True
        # Cindex = ( (ik2grid+1) > N2/2 + 1) & ( ((ik3grid+1) == 1) | ((ik3grid+1) == N3/2 + 1))
        # Cx[Cindex] = np.flip(np.roll(Cxconj, -1, axis = (0,1)),axis = (0,1))[Cindex]
        # Cy[Cindex] = np.flip(np.roll(Cyconj, -1, axis = (0,1)),axis = (0,1))[Cindex]
        # Cz[Cindex] = np.flip(np.roll(Czconj, -1, axis = (0,1)),axis = (0,1))[Cindex]
        # Cprev[Cindex] = True
        # Cindex = ( (ik3grid+1) > N3/2 + 1) & ( ((ik1grid+1) == 1) | ((ik1grid+1) == N1/2 + 1))
        # Cx[Cindex] = np.flip(np.roll(Cxconj, -1, axis = (1,2)),axis = (1,2))[Cindex]
        # Cy[Cindex] = np.flip(np.roll(Cyconj, -1, axis = (1,2)),axis = (1,2))[Cindex]
        # Cz[Cindex] = np.flip(np.roll(Czconj, -1, axis = (1,2)),axis = (1,2))[Cindex]
        # Cprev[Cindex] = True
        # Cindex = ( (ik3grid+1) > N3/2 + 1) & ( ((ik2grid+1) == 1) | ((ik2grid+1) == N2/2 + 1))
        # Cx[Cindex] = np.flip(np.roll(Cxconj, -1, axis = (0,2)),axis = (0,2))[Cindex]
        # Cy[Cindex] = np.flip(np.roll(Cyconj, -1, axis = (0,2)),axis = (0,2))[Cindex]
        # Cz[Cindex] = np.flip(np.roll(Czconj, -1, axis = (0,2)),axis = (0,2))[Cindex]
        # Cprev[Cindex] = True
        # Cindex = (( (ik1grid+1)/N1 + (ik2grid+1)/N2 + (ik3grid+1)/N3 - 3/2 - 1/N3) > 0) & (Cprev == False)
        # Cx[Cindex] = np.flip(np.roll(Cxconj, -1, axis = (0,1,2)),axis = (0,1,2))[Cindex]
        # Cy[Cindex] = np.flip(np.roll(Cyconj, -1, axis = (0,1,2)),axis = (0,1,2))[Cindex]
        # Cz[Cindex] = np.flip(np.roll(Czconj, -1, axis = (0,1,2)),axis = (0,1,2))[Cindex]

        # del Cprev, Cindex, Cxconj, Cyconj, Czconj

        '''
        %===================================================
        % Inverse n-dimensional Fourier transform
        %==================================================='''
        from scipy import fft
        self.log('Inverse fft')
        uvw = Cxyz = fft.irfftn(Cxyz, axes=[3, 2, 1], workers=self.n_cpu)
        self.log('Scale and extract uvw')
        # Default output choice - "lower-left" corner of the box
        ScaleCoef = N1 * N2 * N3
        scale = np.sqrt(alphaepsilon) * ScaleCoef  # tensor made with alphaepsilon=1
        uvw = np.real(uvw[:, :Nx, :Ny, :Nz]) * np.float32(scale)
        return uvw

    def log(self, s):
        if self.verbose:
            print(s)

    @property
    def cache_name(self):
        return "mannsqrtphi_l%.1f_g%.1f_h%d_%s%dx%s%dx%s%d_%.3fx%.2fx%.2f.npy" % (
            self.L, self.Gamma, self.HighFreqComp,
            ["", "d"][self.double_x], self.Nx,
            ["", "d"][self.double_y], self.Ny,
            ["", "d"][self.double_z], self.Nz,
            self.dx, self.dy, self.dz)

    @property
    def spectral_vars(self):
        if self._spectral_vars is None:
            cache_name = self.cache_name
            if self.cache_spectral_tensor and os.path.isfile(cache_name):
                self._spectral_vars = np.load(cache_name)
            else:
                self._spectral_vars = self.generate_spectral_tensor()
                if self.cache_spectral_tensor:
                    np.save(cache_name, self._spectral_vars)
        return self._spectral_vars

    @property
    def k1(self):
        N1 = self.N1
        m1 = np.r_[np.arange(0, N1 / 2), -N1 / 2]
        k1 = m1 * 2 * np.pi / (N1 * self.dx)
        return k1

    @property
    def k23(self):
        N2, N3 = self.N2, self.N3
        m2 = np.concatenate([np.arange(0, N2 / 2), np.arange(-N2 / 2, 0)])
        m3 = np.concatenate([np.arange(0, N3 / 2), np.arange(-N3 / 2, 0)])
        k2 = m2 * 2 * np.pi / (N2 * self.dy)
        k3 = m3 * 2 * np.pi / (N3 * self.dz)
        return k2, k3

    def generate(self, seed, alphaepsilon=None, n_cpu=-1, random_generator=None):
        """Generate turbulence field

        Parameters
        ----------
        seed : int, optional
            Seed number for random generator
        alphaepsilon : float, optional
            Mann model turbulence parameter $(\\alpha \\varepsilon)^{2/3}$ (Mann, 1994), default is 1.
        n_cpu : int or None, optional
            Number of CPUs to use for the turbulence generation.
            Default is -1 (same number as used to make the spectral tensor).
            If None, all available CPUs are used.
        random_generator : function or None, optional
            If None (default), the random generator depends on n_cpu:
                n_cpu=1: hipersim.turbgen.spectral_tensor.random_generator_seq
                n_cpu!=1: hipersim.turbgen.spectral_tensor.random_generator_par
            Alternatively a function, f(MannSpectralTensor) -> RandomNumbers, dim=(3, N1r, N2, N3), can be specified

        Returns
        -------
        MannTurbulenceField
        """

        from hipersim import MannTurbulenceField
        alphaepsilon = alphaepsilon or self.alphaepsilon
        if n_cpu != -1:
            self.n_cpu = n_cpu

        uvw = self.generate_uvw(seed, alphaepsilon, random_generator)
        mtf = MannTurbulenceField(uvw, alphaepsilon, self.L, self.Gamma,
                                  (self.Nx, self.Ny, self.Nz), (self.dx, self.dy, self.dz), seed,
                                  self.HighFreqComp, (self.double_x, self.double_y, self.double_z),
                                  self.n_cpu, random_generator=self.random_generator, generator='Hipersim')
        mtf.mannSpectralTensor = self
        return mtf


class OnetimeMannSpectralTensor(MannSpectralTensor):
    @property
    def spectral_vars(self):
        spectral_vars = MannSpectralTensor.spectral_vars.fget(self)
        self._spectral_vars = None
        return spectral_vars
