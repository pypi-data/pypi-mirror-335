import multiprocessing
import time

from numpy import newaxis as na
from tqdm import tqdm

from hipersim._hipersim import TurbulenceField, TurbulenceInput
from hipersim.turbgen.manntensor import manntensorcomponents
from hipersim.turbgen.trapezoidal_sum_2d import trapezoidal_sum_2d
from hipersim.turbgen.turb_utils import get_k
import numpy as np


class MannTurbulenceInput(TurbulenceInput):
    def __init__(self, alphaepsilon, L, Gamma, Nxyz, dxyz, seed=None, HighFreqComp=0,
                 double_xyz=(False, True, True), n_cpu=1, random_generator=None, generator='unknown'):
        TurbulenceInput.__init__(self, Nxyz, dxyz, seed=seed, double_xyz=double_xyz, generator=generator)
        self.alphaepsilon = alphaepsilon
        self.L = L
        self.Gamma = Gamma
        self.HighFreqComp = HighFreqComp
        self.N1, self.N2, self.N3 = Nxyz * (np.array(double_xyz, dtype=np.int64) + 1)
        self.N1r = self.N1 // 2 + 1

        self.n_cpu = n_cpu or multiprocessing.cpu_count()  # None defaults to all
        self.random_generator = random_generator
        self.verbose = False

    @property
    def args_string(self):
        return "mann_l%.1f_ae%.4f_g%.1f_h%d_%s%dx%s%dx%s%d_%.3fx%.2fx%.2f" % (
            self.L, self.alphaepsilon, self.Gamma, self.HighFreqComp,
            ["", "d"][self.double_x], self.Nx,
            ["", "d"][self.double_y], self.Ny,
            ["", "d"][self.double_z], self.Nz,
            self.dx, self.dy, self.dz)

    def _imap_iter(self, f, args_lst, desc, N=None):
        if self.n_cpu == 1:
            imap = map
        else:
            from hipersim.turbgen.spectral_tensor import get_pool
            imap = get_pool(self.n_cpu).imap
        # if self.verbose and N is None:
        #     N = len(list(args_lst))
        return tqdm(imap(f, args_lst), total=N, desc=desc, disable=not self.verbose)

    def _integration_grid(self, k1=None, k23_resolution=100):
        if k1 is None:
            k_low = 2 * np.pi / (self.N1 * self.dx)
            k_high = np.pi / self.dx
            k1 = 10**np.linspace(np.log10(k_low), np.log10(k_high), 60)

        klogrange = np.linspace(-6, 2, k23_resolution)
        k23 = np.concatenate([-np.flip(10**klogrange), 10**klogrange])
        return k1, k23, k23

    def _spectra_integrated_k1(self, args):
        k1, k2, k3 = args
        k1 = np.ones(k2.shape) * k1
        Phi11ij, Phi22ij, Phi33ij, _, Phi13ij, _ = manntensorcomponents(
            k1, k2[:, na], k3[na, :], self.Gamma, self.L, self.alphaepsilon, 2)
        return [trapezoidal_sum_2d(Phiij, k2, k3) for Phiij in [Phi11ij, Phi22ij, Phi33ij, Phi13ij]]

    def spectra_integrated(self, k1=None, k23_resolution=100):
        k1, k2, k3 = self._integration_grid(k1, k23_resolution)
        args_lst = [(k1_, k2, k3) for k1_ in k1]
        Psi = list(self._imap_iter(self._spectra_integrated_k1, args_lst, desc='Compute spectra', N=len(k1)))
        Psi11, Psi22, Psi33, Psi13 = np.array(Psi).T
        return k1, (Psi11, Psi22, Psi33, Psi13)

    def spectra_lookup(self, k1=None):
        from hipersim.turbgen.mannspectrum import MannSpectrum_TableLookup
        k1, Phi = MannSpectrum_TableLookup(Gamma=self.Gamma, L=self.L, alphaepsilon=self.alphaepsilon, kinput=k1)
        return k1, Phi

    def get_k(self, Lx=None, dx=None):
        """Calculate the wave numbers from 1/Lx*2pi to nyquist frq i.e. Nx/2/Lx*2pi=1/(2dx)*2pi

        Parameters
        ----------
        Lx : float, optional
            Longest resolvable wave length [m]
            If None, Lx is set to Nx*dx (taken from the box properties)
        dx : float or None
            Distance, such that shortest resolvable wave = 2*dx
            If None, dx is set to the grid spacing (taken from the box properties)
        """

        Lx = Lx or self.Nx * self.dx
        dx = dx or self.dx
        Nx = Lx / dx
        return get_k(Nx, dx)

    def spectrum_variance(self, Lx=None, dx=None):
        """Calculate the variance of the theoretical Mann model spectrum of the current box

        Parameters
        ----------
        Lx : float, optional
            Longest resolvable wave length [m]
            If None, Lx is set to Nx*dx (taken from the box properties)
        dx : float or None
            Distance, such that shortest resolvable wave = 2*dx
            If None, dx is set to the grid spacing (taken from the box properties)
        """
        k = self.get_k(Lx, dx)
        Psi_uu = self.spectra_lookup(k)[1][0]
        dk = np.diff(k[:2])  # 2 * np.pi / Lx
        return np.sum(Psi_uu * 2 * dk)

    def spectrum_TI(self, U, T=None, cutoff_frq=None):
        """Calculate the Turbulence intensity of the theoretical Mann model spectrum of the current box
        Parameters
        ----------
        U : float
            Wind speed [m/s]
        T : float, int or None, optional
            Time period [s] that the TI value represents used to calculate the longest resolvable wave, Lx.
            If None, Lx is set to the box length, Nx*dx (taken from the box properties)
        cutoff_frq : float or None
            Cutoff frequency of the TI measuring device used to calculate the shortest resolvable wave, 2*dx
            If None, dx is set to the grid spacing (taken from the box properties)
        """

        Lx, dx = self.Nx * self.dx, self.dx
        if T:
            Lx = T * U
        if cutoff_frq:
            dx = U / cutoff_frq
        spectrum_u_var = self.spectrum_variance(Lx, dx)
        return np.sqrt(spectrum_u_var) / U

    def _coherence_k1(self, args):
        k1, k2, k3, dy, dz, ii, jj, ij = args
        k1 = k1

        Phi = manntensorcomponents(k1, k2[:, na], k3[na, :], self.Gamma, self.L, self.alphaepsilon, 2)

        PhiDeltaij = Phi[ij] * np.exp(1j * (k2[:, na] * dy + k3[na] * dz))
        PsiCrossij = trapezoidal_sum_2d(PhiDeltaij, k2, k3)
        PsiPointi = trapezoidal_sum_2d(Phi[ii], k2, k3)
        if ii == ij:
            return PsiCrossij / PsiPointi
        else:
            PsiPointj = trapezoidal_sum_2d(Phi[jj], k2, k3)
            return np.real(PsiCrossij * np.conj(PsiCrossij)) / (PsiPointi * PsiPointj)

    def coherence_integrated(self, dy, dz, component='u', k1=None, k23_resolution=100):
        k1, k2, k3 = self._integration_grid(k1, k23_resolution)
        component = (component + component)[:2]
        component_lst = ['uu', 'vv', 'ww', 'uv', 'uw', 'vw']
        ii = component_lst.index(component[0] * 2)
        jj = component_lst.index(component[1] * 2)
        ij = component_lst.index(component)
        args_lst = [(k1_, k2, k3, dy, dz, ii, jj, ij) for k1_ in k1]
        coh = self._imap_iter(self._coherence_k1, args_lst, desc='Compute coherence', N=len(k1))
        return k1, np.fromiter(coh, dtype=np.complex128).real

    def get_alpha_epsilon(self, TI, U, T=None, cutoff_frq=None):
        """Calculate the ae^2/3 value that gives the specified TI for the given box properties (L, Gamma, [Nx], [dx])

        Parameters
        ----------
        TI : float
            Desired turbulence intensity
        U : float
            Wind speed [m/s]
        T : float, int or None, optional
            Time period [s] that the TI value represents used to calculate the longest resolvable wave, Lx.
            If None, Lx is set to the box length, Nx*dx (taken from the box properties)
        cutoff_frq : float or None
            Cutoff frequency of the TI measuring device used to calculate the shortest resolvable wave, 2*dx
            If None, dx is set to the grid spacing (taken from the box properties)
        """
        scale = TI / self.spectrum_TI(U, T, cutoff_frq)
        return self.alphaepsilon * scale**2


class MannTurbulenceField(TurbulenceField, MannTurbulenceInput):
    def __init__(self, uvw, alphaepsilon, L, Gamma, Nxyz, dxyz, seed=None, HighFreqComp=0,
                 double_xyz=(False, True, True), n_cpu=1, random_generator=None, generator='unknown',
                 bounds=None):
        TurbulenceField.__init__(self, uvw, Nxyz, dxyz, seed, double_xyz, generator, bounds=bounds)
        MannTurbulenceInput.__init__(self, alphaepsilon, L, Gamma, Nxyz, dxyz,
                                     seed, HighFreqComp, double_xyz,
                                     n_cpu, random_generator, generator)

    @staticmethod
    def from_netcdf(filename):
        import xarray as xr
        da = xr.load_dataarray(filename)
        return MannTurbulenceField(da.values,
                                   Nxyz=da.shape[1:],
                                   dxyz=[(v[1] - v[0]).item() for v in (da.x, da.y, da.z)],
                                   generator=da.attrs['Generator'],
                                   **{k: da.attrs[k] for k in da.attrs if k not in ['Generator', 'name']}
                                   )

    @staticmethod
    def from_hawc2(filenames, alphaepsilon, L, Gamma, Nxyz, dxyz, seed,
                   HighFreqComp, double_xyz=(False, True, True), generator='Unknown'):
        uvw = np.reshape([np.fromfile(f, np.dtype('<f'), -1) for f in filenames], (3,) + tuple(Nxyz))
        return MannTurbulenceField(uvw, alphaepsilon, L, Gamma, Nxyz, dxyz, seed,
                                   HighFreqComp, double_xyz, generator=generator)

    def to_xarray(self):
        """Return xarray dataarray with u,v,w along x,y,z,uvw axes with all input parameters as attributes:
        - x: In direction of U, i.e. first yz-plane hits wind turbine last
        - y: to the left, when looking in the direction of the wind
        - z: up
        """
        import xarray as xr
        da = TurbulenceField.to_xarray(self)
        da.attrs.update({'alphaepsilon': self.alphaepsilon, 'L': self.L, 'Gamma': self.Gamma,
                         'HighFreqComp': self.HighFreqComp,
                         'Generator': 'Hipersim', 'seed': self.seed,
                         'double_xyz': np.array(self.double_xyz, dtype=int),
                         'name': self.name})
        return da

    @staticmethod
    def generate(alphaepsilon=1, L=33.6, Gamma=3.9, Nxyz=(8192, 64, 64),
                 dxyz=(1, 1, 1), seed=1, HighFreqComp=0, double_xyz=(False, True, True),
                 n_cpu=1, verbose=0, random_generator=None, cache_spectral_tensor=False):
        """Generate a MannTurbulenceField

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
        seed : int, optional
            Seed number for random generator. Default is 1
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
        random_generator : function or None, optional
            If None (default), the random generator depends on n_cpu:
                n_cpu=1: hipersim.turbgen.spectral_tensor.random_generator_seq
                n_cpu!=1: hipersim.turbgen.spectral_tensor.random_generator_par
            Alternatively a function, f(MannSpectralTensor) -> RandomNumbers, dim=(3, N1r, N2, N3), can be specified
        cache_spectral_tensor : boolean, optional
            If True, the spectral tensor is loaded from file if exists otherwise it is calculated and saved to file
            If False, the spectral tensor is always recalculated

        Returns
        -------
        MannTurbulenceField-object
        """
        from hipersim.turbgen.spectral_tensor import OnetimeMannSpectralTensor
        return OnetimeMannSpectralTensor(alphaepsilon, L, Gamma, Nxyz, dxyz, HighFreqComp,
                                         double_xyz, n_cpu=n_cpu, verbose=verbose,
                                         cache_spectral_tensor=cache_spectral_tensor).generate(
                                             seed=seed, alphaepsilon=alphaepsilon, random_generator=random_generator)

    # @property
    # def spectral_vars(self):
    #     if hasattr(self, 'mannSpectralTensor'):
    #         return self.mannSpectralTensor.spectral_vars

    def scale_TI(self, TI, U, T=None, cutoff_frq=None):
        target_alphaepsilon = self.get_alpha_epsilon(TI, U, T, cutoff_frq)

        scale = np.sqrt(target_alphaepsilon / self.alphaepsilon)
        self.uvw *= scale
        self.alphaepsilon = target_alphaepsilon

    def constrain(self, Constraints, method=2):
        '''
        ===============================================
        APPLY CONSTRAINTS
        ==============================================='''
        '''
        ====================================================================
         COMPUTE MANN TENSOR VALUES, THEN IFFT TO GET CORRELATIONS
        ===================================================================='''
        print('Computing Mann tensor / correlation arrays for constrained simulation:')

        from hipersim.turbgen.manntensor import manntensorcomponents
        tstart = time.time()
        N1, N1r, N2, N3 = self.N1, self.N1r, self.N2, self.N3
        R0uu = np.zeros((N1, N2, N3), dtype='cfloat')
        R0vv = np.zeros((N1, N2, N3), dtype='cfloat')
        R0ww = np.zeros((N1, N2, N3), dtype='cfloat')
        R0uw = np.zeros((N1, N2, N3), dtype='cfloat')
        Nx, Ny, Nz = self.Nxyz
        dx, dy, dz = self.dxyz
        '''
        The u-v, and v-w components are not considered because Rho_uv and Rho_vw
        are zero in the Mann turbulence model
        '''
        pi = np.pi
        k1sim = np.concatenate([np.arange(0, Nx), np.arange(-Nx, 0)]) * (pi / (Nx * dx))
        k2sim = np.concatenate([np.arange(0, Ny), np.arange(-Ny, 0)]) * (pi / (Ny * dy))
        k3sim = np.concatenate([np.arange(0, Nz), np.arange(-Nz, 0)]) * (pi / (Nz * dz))

        k2simgrid, k3simgrid = np.meshgrid(k2sim, k3sim)
        '''
        Only half of the wave numbers are considered, it is considered that
        the correlation will be symmetric about k1 = 0
        '''
        from numpy.testing import assert_array_equal as ae

        def phi(k1):
            Phi11ij, Phi22ij, Phi33ij, __, Phi13ij, __ = manntensorcomponents(
                k1 * np.ones(k2simgrid.shape), k2simgrid, k3simgrid, self.Gamma, self.L, self.alphaepsilon, 2)
            return Phi11ij.T, Phi22ij.T, Phi33ij.T, Phi13ij.T
        assert method in [1, 2]
        if method == 1:
            Phi = np.moveaxis([phi(k1sim[ik1]) for ik1 in np.arange(Nx)], 0, 1)
            R0 = np.fft.ifft2(Phi, axes=(2, 3))
            Ruu, Rvv, Rww, Ruw = np.real(np.fft.ifft(np.concatenate(
                [np.conj(R0), R0[:, ::-1]], axis=1), axis=1))[:, :Nx, :Ny, :Nz]
        elif method == 2:
            Phi = np.moveaxis([phi(k1sim[ik1]) for ik1 in np.arange(N1r)], 0, 1)
            Ruu, Rvv, Rww, Ruw = np.fft.irfftn(Phi, axes=(3, 2, 1))[:, :Nx, :Ny, :Nz]

        Ruw = Ruw / (np.sqrt(Ruu[0, 0, 0] * Rww[0, 0, 0]))
        Ruu = Ruu / Ruu[0, 0, 0]
        Rvv = Rvv / Rvv[0, 0, 0]
        Rww = Rww / Rww[0, 0, 0]

        del R0uu, R0vv, R0ww, R0uw  # Clear memory from unnecessary variables

        t1 = time.time()
        print('Correlation computations complete')
        print('Time elapsed is ' + str(t1 - tstart))

        '''
        ================================================================
         Compute distances, normalize wind fields and constraint fields
        ================================================================'''

        ConstraintValuesUNorm = Constraints[:, 3]
        ConstraintValuesVNorm = Constraints[:, 4]
        ConstraintValuesWNorm = Constraints[:, 5]
        Unorm, Vnorm, Wnorm = self.uvw

        '''
        ==========================================
         ASSEMBLE CONSTRAINT COVARIANCE MATRIX
        =========================================='''
        print('Populating covariance matrix for the constraints:')
        Clocx = np.rint(Constraints[:, 0] / dx)
        Clocy = np.rint(Constraints[:, 1] / dy)
        Clocz = np.rint(Constraints[:, 2] / dz)
        '''
        ---------------------------------
         Eliminate overlapping constraints
        ---------------------------------'''
        ClocA = np.concatenate([np.atleast_2d(Clocx), np.atleast_2d(Clocy), np.atleast_2d(Clocz)]).T
        __, ClocIndex = np.unique(ClocA, axis=0, return_index=True)
        Constraints = Constraints[ClocIndex, :]
        Clocx = Clocx[ClocIndex]
        Clocy = Clocy[ClocIndex]
        Clocz = Clocz[ClocIndex]
        ConstraintValuesUNorm = ConstraintValuesUNorm[ClocIndex]
        ConstraintValuesVNorm = ConstraintValuesVNorm[ClocIndex]
        ConstraintValuesWNorm = ConstraintValuesWNorm[ClocIndex]
        Nconstraints = Constraints.shape[0]

        '''
        ---------------------------------------------
         Eliminate constraints too close to each other
        ---------------------------------------------'''
        Xdist = np.dot(np.atleast_2d(Constraints[:, 0]).T, np.ones([1, Nconstraints])) - \
            np.dot(np.ones([Nconstraints, 1]), np.atleast_2d(Constraints[:, 0]))
        Ydist = np.dot(np.atleast_2d(Constraints[:, 1]).T, np.ones([1, Nconstraints])) - \
            np.dot(np.ones([Nconstraints, 1]), np.atleast_2d(Constraints[:, 1]))
        Zdist = np.dot(np.atleast_2d(Constraints[:, 2]).T, np.ones([1, Nconstraints])) - \
            np.dot(np.ones([Nconstraints, 1]), np.atleast_2d(Constraints[:, 2]))

        Rdist = np.sqrt(Xdist**2 + Ydist**2 + Zdist**2)
        Rlimit = max([self.L / 10, min([dx, dy, dz])])
        Rexceed = (Rdist > 0) & (Rdist < Rlimit)
        ValidDistIndex = np.full((Rdist.shape[0]), True, dtype='bool')
        for i in range(Nconstraints):
            if np.any(Rexceed[i, :i]):
                Rexceed[i, :] = 0
                Rexceed[:, i] = 0
                ValidDistIndex[i] = False
        Constraints = Constraints[ValidDistIndex, :]
        Clocx = Clocx[ValidDistIndex].astype('int')
        Clocy = Clocy[ValidDistIndex].astype('int')
        Clocz = Clocz[ValidDistIndex].astype('int')
        ConstraintValuesUNorm = ConstraintValuesUNorm[ValidDistIndex]
        ConstraintValuesVNorm = ConstraintValuesVNorm[ValidDistIndex]
        ConstraintValuesWNorm = ConstraintValuesWNorm[ValidDistIndex]
        Nconstraints = Constraints.shape[0]

        del Rdist, Rexceed, ValidDistIndex

        '''
        -----------------------------
         Assemble u-v-w-correlation matrix
        -----------------------------'''
        CorrCMannUVW = np.zeros((3 * Nconstraints, 3 * Nconstraints))

        for iC in range(Nconstraints):
            xloci = Clocx[iC]
            yloci = Clocy[iC]
            zloci = Clocz[iC]
            xlocCij = np.abs(xloci - Clocx).astype('int')
            ylocCij = np.abs(yloci - Clocy).astype('int')
            zlocCij = np.abs(zloci - Clocz).astype('int')

            CorrUUij = Ruu[xlocCij, ylocCij, zlocCij]
            CorrVVij = Rvv[xlocCij, ylocCij, zlocCij]
            CorrWWij = Rww[xlocCij, ylocCij, zlocCij]
            CorrUWij = Ruw[xlocCij, ylocCij, zlocCij]

            CorrCMannUVW[:Nconstraints, iC] = CorrUUij
            CorrCMannUVW[iC, :Nconstraints] = CorrUUij
            CorrCMannUVW[Nconstraints:2 * Nconstraints, Nconstraints + iC] = CorrVVij
            CorrCMannUVW[Nconstraints + iC, Nconstraints:2 * Nconstraints] = CorrVVij
            CorrCMannUVW[2 * Nconstraints:, 2 * Nconstraints + iC] = CorrWWij
            CorrCMannUVW[2 * Nconstraints + iC, 2 * Nconstraints:] = CorrWWij
            CorrCMannUVW[2 * Nconstraints:, iC] = CorrUWij
            CorrCMannUVW[iC, 2 * Nconstraints:] = CorrUWij

        t2 = time.time()
        print('Constraint-constraint covariance matrix has been assembled')
        print('Time elapsed is ' + str(t2 - t1))

        '''
        =========================================================
         APPLY CONSTRAINT EQUATIONS TO COMPUTE THE RESIDUAL FIELD
        =========================================================
         Using eq.(2) from Dimitrov & Natarajan (2016) to compute
         the residual field which is to be added to the unconstrained
         field in order to obtain the constrained result.

         Due to memory limitations, eq. (2) is evaluated in batches intended
         to avoid the need of fully assembling the first term in the equation,
         which is a matrix with size (Nx*Ny*Nz)x(Nconstraints).
         First, the product of the second and third term is evaluated,
         then it is multiplied piecewise to a subset of the rows of the
         first term.
        '''
        print('Applying constraints...')
        ConstraintValuesUVWNorm = np.concatenate([ConstraintValuesUNorm, ConstraintValuesVNorm, ConstraintValuesWNorm])
        UVWcontemporaneous = np.zeros((3 * Nconstraints))
        UVWcontemporaneous[:Nconstraints] = Unorm[Clocx, Clocy, Clocz]
        UVWcontemporaneous[Nconstraints:2 * Nconstraints] = Vnorm[Clocx, Clocy, Clocz]
        UVWcontemporaneous[2 * Nconstraints:] = Wnorm[Clocx, Clocy, Clocz]

        '''
         Computing the product of the second and third terms in eq.(2) in
         Dimitrov & Natarajan (2016)
        '''

        CConstUVW = np.linalg.solve(CorrCMannUVW, (ConstraintValuesUVWNorm - UVWcontemporaneous))
        # CConstUVW = np.dot(np.linalg.inv(CorrCMannUVW), ConstraintValuesUVWNorm - UVWcontemporaneous)

        CConstU = np.atleast_2d(CConstUVW[:Nconstraints]).T
        CConstV = np.atleast_2d(CConstUVW[Nconstraints:2 * Nconstraints]).T
        CConstW = np.atleast_2d(CConstUVW[2 * Nconstraints:]).T
        del CorrCMannUVW

        Ruu = Ruu.reshape(Nx * Ny * Nz)
        Rvv = Rvv.reshape(Nx * Ny * Nz)
        Rww = Rww.reshape(Nx * Ny * Nz)
        Ruw = Ruw.reshape(Nx * Ny * Nz)

        ures = np.zeros(Nx * Ny * Nz)
        vres = np.zeros(Nx * Ny * Nz)
        wres = np.zeros(Nx * Ny * Nz)

        dxic = (np.abs(np.arange(Nx)[na] - Clocx[:, na]) * (Ny * Nz))[:, :, na, na]
        dyic = (np.abs(np.arange(Ny)[na] - Clocy[:, na]) * Nz)[:, na, :, na]
        dzic = np.abs(np.arange(Nz)[na] - Clocz[:, na])[:, na, na, :]

        for dxi, dyi, dzi, constU, constV, constW in zip(dxic, dyic, dzic, CConstU, CConstV, CConstW):
            dlinear = (dxi + dyi + dzi).flatten()
            CorrUUi = Ruu[dlinear]
            CorrVVi = Rvv[dlinear]
            CorrWWi = Rww[dlinear]
            CorrUWi = Ruw[dlinear]
            ures += CorrUUi * constU + CorrUWi * constW
            vres += CorrVVi * constV
            wres += CorrUWi * constU + CorrWWi * constW

        Uconstrained = Unorm + np.reshape(ures, (Nx, Ny, Nz))
        Vconstrained = Vnorm + np.reshape(vres, (Nx, Ny, Nz))
        Wconstrained = Wnorm + np.reshape(wres, (Nx, Ny, Nz))

        tend = time.time()
        print('Constrained simulation complete')
        print('Total time elapsed is ' + str(tend - tstart))

        self.uvw = np.array([Uconstrained, Vconstrained, Wconstrained])
