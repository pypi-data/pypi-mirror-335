import numpy as np
from numpy import newaxis as na
import os
from hipersim.turbgen.turb_utils import logbin_values, spectra, bin_values
import struct
from enum import auto, Enum

from wetb.hawc2.htc_file import HTCFile
import warnings


class TurbulenceInput():
    def __init__(self, Nxyz, dxyz, seed=None, double_xyz=(False, False, False), generator='unknown',
                 offset_xyz=(0, 0, 0)):
        self.Nx, self.Ny, self.Nz = self.Nxyz = Nxyz
        self.dx, self.dy, self.dz = self.dxyz = dxyz
        self.seed = seed
        self.double_xyz = double_xyz
        self.generator = generator
        self.offset_xyz = offset_xyz

    @property
    def double_x(self):
        return self.double_xyz[0]

    @property
    def double_y(self):
        return self.double_xyz[1]

    @property
    def double_z(self):
        return self.double_xyz[2]

    @property
    def args_string(self):
        return "%s%dx%s%dx%s%d_%.3fx%.2fx%.2f" % (
            ["", "d"][self.double_x], self.Nx,
            ["", "d"][self.double_y], self.Ny,
            ["", "d"][self.double_z], self.Nz,
            self.dx, self.dy, self.dz)

    @property
    def name(self):
        return "%s_%s_s%04d" % (
            self.generator, self.args_string, self.seed)


class Bounds(Enum):
    Error = auto()
    Warning = auto()
    Repeat = auto()
    Mirror = auto()


class TurbulenceField(TurbulenceInput):
    def __init__(self, uvw, Nxyz, dxyz, seed=None, double_xyz=(False, False, False), generator='unknown',
                 bounds=None, offset_xyz=(0, 0, 0), htc_dict={}):
        TurbulenceInput.__init__(self, Nxyz, dxyz, seed=seed, double_xyz=double_xyz, generator=generator)
        self.uvw = uvw
        if bounds is None:
            self.bounds_xyz = [(Bounds.Repeat, Bounds.Mirror)[int(d)] for d in double_xyz]
        else:
            self.bounds_xyz = (np.atleast_1d(bounds).tolist() * 3)[:3]
        self.offset_xyz = offset_xyz
        self.htc_dict = htc_dict

    def to_xarray(self):
        """Return xarray dataarray with u,v,w along x,y,z,uvw axes with all input parameters as attributes:
        - x: In direction of U, i.e. first yz-plane hits wind turbine last
        - y: to the left, when looking in the direction of the wind
        - z: up
        """
        import xarray as xr
        ox, oy, oz = self.offset_xyz
        return xr.DataArray(self.uvw, dims=('uvw', 'x', 'y', 'z'),
                            coords={'x': np.arange(self.Nx) * self.dx + ox,
                                    'y': np.arange(self.Ny) * self.dy + oy,
                                    'z': np.arange(self.Nz) * self.dz + oz,
                                    'uvw': ['u', 'v', 'w']},
                            attrs={'double_xyz': np.array(self.double_xyz, dtype=int),
                                   'name': self.name})

    def to_netcdf(self, folder='', filename=None):
        da = self.to_xarray()
        filename = os.path.join(folder, filename or self.name + ".nc")
        da.to_netcdf(filename)

    @staticmethod
    def from_hawc2(filenames, Nxyz, dxyz, seed=None, double_xyz=(0, 0, 0), generator='Unknown'):
        uvw = np.reshape([np.fromfile(f, np.dtype('<f'), -1) for f in filenames], (3,) + tuple(Nxyz))
        return TurbulenceField(uvw, Nxyz, dxyz, seed, double_xyz, generator=generator)

    def to_hawc2(self, folder='', basename=None, htc_dict={}):
        basename = basename or self.name
        for turb, uvw in zip(self.uvw, 'uvw'):
            filename = os.path.join(folder, basename + f"{uvw}.turb")
            turb.astype('<f').tofile(filename)
        return self.get_htc_section(folder=folder, htc_dict=htc_dict)

    def get_htc_section(self, folder='', htc_dict={}):
        htc = HTCFile()
        htc.add_mann_turbulence(filenames=[os.path.join(folder, f'{self.name}{uvw}.turb') for uvw in 'uvw'],
                                no_grid_points=self.Nxyz, box_dimension=(np.array(self.Nxyz)) * self.dxyz,
                                dont_scale=True)
        htc.wind.mann.create_turb_parameters.delete()

        for k, v in {**self.htc_dict, **htc_dict}.items():
            htc[k].values = np.atleast_1d(v).tolist()
        return htc.wind

    def to_bladed(self, Umean, zhub=None, folder='', basename=None, TurbOptions={}):
        from hipersim.turbgen.turb_utils import output_field
        basename = basename or self.name
        zhub = zhub or self.dz * (self.Nz - 1) / 2

        output_field(*self.uvw, params={'SaveToFile': 1, 'dx': self.dx, 'dy': self.dy, 'dz': self.dz,
                                        'BaseName': os.path.join(folder, basename)},
                     TurbOptions={'FileFormat': 'Bladed', 'Umean': Umean, 'zHub': zhub, 'ShearLaw': None,
                                  'clockwise': False, **TurbOptions})

    @staticmethod
    def from_bladed(filename, double_xyz=[0, 0, 0]):
        with open(filename, 'rb') as fid:
            def read(t):
                if len(t) > 1:
                    return [read(t) for t in t]
                return struct.unpack(t, fid.read(dict(h=2, i=4, f=4)[t]))[0]
            h, i, f = 'hif'
            assert read(h) == -99  # ID
            assert read(h) == 4  # ID2
            assert read(i) == 3  # number of components (should be 3)
            read(f)  # latitude (deg)
            read(f)  # z0, Roughness length (m)
            z_ref = read(f)  # Reference height (m) = Z(1) + GridHeight / 2.0
            TI_U = read(f)   # Turbulence Intensity of u component (%)
            TI_V = read(f)   # Turbulence Intensity of v component (%)
            TI_W = read(f)   # Turbulence Intensity of w component (%)
            dz, dy, dx = read('fff')  # delta z,y,x in m
            Nx = read(i) * 2  # Number of time steps (points in longitudinal direction)
            MFFWS = read(f)  # mean full-field wind speed
            read('fff')  # zLu, yLu, xLu - unused variables
            read(i)  # _ - unused variable
            seed = read(i)  # RandSeed1 - unused variable
            Nz = read(i)  # number of points in vertical direction
            Ny = read(i)  # number of points in horizontal direction
            read('iiiiii')  # Unused variable - for BLADED
            uvw = np.moveaxis(np.fromfile(fid, np.dtype('<h'), -1).reshape((Nx, Nz, Ny, 3)),
                              [0, 1, 2, 3], [1, 3, 2, 0])
            # uvw = uvw[:, :, ::-1]  # clockwise
            scale = 0.00001 * MFFWS * np.asarray([TI_U, TI_V, TI_W])
            offset = np.array([MFFWS, 0, 0])
            uvw = uvw * scale[:, na, na, na] + offset[:, na, na, na]
            return BladedTurbulenceField(uvw, Nxyz=[Nx, Ny, Nz], dxyz=[dx, dy, dz], seed=seed,
                                         double_xyz=double_xyz, generator='wnd_file',
                                         htc_dict={'wind.wsp': MFFWS, 'wind.center_pos0': (0, 0, -z_ref)},
                                         offset_xyz=(0, -(Ny // 2) * dy, z_ref - (Nz // 2) * dz))

    def spectra(self, log10_bin_size=.2, min_bin_count=2):
        from hipersim.turbgen.turb_utils import spectra
        k, S = spectra(self.uvw, self.Nx, self.dx, exclude_zero=True)
        if log10_bin_size:
            S = [logbin_values(k, s, log10_bin_size=log10_bin_size, min_bin_count=min_bin_count) for s in S]
            k = logbin_values(k, k, log10_bin_size=log10_bin_size, min_bin_count=min_bin_count)
        return k, S

    def coherence(self, dy, dz, component='u', bin_size=.01, min_bin_count=2):
        c1, c2 = (component + component)[:2]
        i, j = 'uvw'.index(c1), 'uvw'.index(c2)
        ui, uj = self.uvw[i], self.uvw[j]
        if dy:
            dyi = int(np.round(dy / self.dy))
            ui, uj = ui[:, :-dyi], uj[:, dyi:]
        if dz:
            dzi = int(np.round(dz / self.dz))
            ui, uj = ui[:, :, :-dzi], uj[:, :, dzi:]
        Nx, dx = self.Nx, self.dx

        # k, (SUPii, SUPij, SUPjj) = spectra([ui, None, uj], Nx, dx, exclude_zero=False, spectra=['uu', 'uw', 'ww'])
        # f = (dx / (2 * np.pi * Nx)) * (1 / (np.sqrt(2) * Nx * dx))
        # SUPii, SUPij, SUPjj = [SUP / f for SUP in [SUPii, SUPij, SUPjj]]
        # Coherence = np.real(SUPij) / (np.sqrt(SUPii) * np.sqrt(SUPjj))

        if c1 == c2:
            k, (SUPii, SUPij) = spectra([ui, None, uj], Nx, dx, exclude_zero=True, spectra=['uu', 'uw'])
            Coherence = np.real(SUPij) / SUPii
        else:
            k, (SUPii, SUPij, SUPjj) = spectra([ui, None, uj], Nx, dx, exclude_zero=True, spectra=['uu', 'uw', 'ww'])
            Coherence = np.real(SUPij * np.conj(SUPij) / (SUPii * SUPjj))
        if bin_size:
            Coherence = bin_values(k, Coherence, bin_size=bin_size, min_bin_count=min_bin_count)[0]
            k = bin_values(k, k, bin_size=bin_size, min_bin_count=min_bin_count)[0]
        return k, Coherence

    def __call__(self, x, y, z):
        if np.any(self.offset_xyz != 0):
            x, y, z = [np.asarray(v) - offset for v, offset in zip([x, y, z], self.offset_xyz)]
        assert x.shape == y.shape == z.shape, (x.shape, y.shape, z.shape)
        shape = np.shape(x)
        x, y, z = [v.flatten() for v in [x, y, z]]
        ui = np.array([[0, 0, 0, 0, 1, 1, 1, 1],
                       [0, 0, 1, 1, 0, 0, 1, 1],
                       [0, 1, 0, 1, 0, 1, 0, 1]])
        V = np.moveaxis(self.uvw, 0, -1)

        def modf(x, N, bounds, i):
            if bounds == Bounds.Mirror:
                # modulo into the interval [-(N-1), (N-1)] and take abs to get xf on mirrored axis
                N1 = N - 1
                xf = N1 - np.abs(x % (2 * N1) - N1)
                x0, x1 = np.floor(xf), np.ceil(xf)

                # switch x0 and x1 where x is on mirrored part of axis that points opposite the axis direction
                m = N1 - np.abs(np.floor(x) % (2 * N1) - N1) > xf
                x0[m], x1[m] = x1[m], x0[m]
                xf = np.abs(xf - x0)
            elif bounds == Bounds.Repeat:
                xf = x % N
                xf = np.where(xf == N, 0, xf)  # if x is negative and version small, e.g. -1e14, x%N = N
                x0 = np.floor(xf)
                xf = xf - x0
                x1 = ((x0 + 1) % N)
            else:
                try:
                    assert np.all((x >= 0) & (x <= N - 1)), \
                        f"{'xyz'[i]} coordinate ({x.min() * self.dxyz[i]} to {x.max() * self.dxyz[i]}) out of bounds (0 to {(N - 1) * self.dxyz[i]})"
                except BaseException as e:
                    if bounds == Bounds.Warning:
                        warnings.warn(str(e) + "Using values at box edge")
                        x = np.clip(x, 0, N - 1)
                    else:
                        raise
                xf = x
                x0 = np.floor(xf)
                x1 = np.minimum((x0 + 1), N - 1)
                xf = xf - x0

            return xf, [x0, x1]

        xyz_i = np.array([x, y, z]).T / self.dxyz
        (xif, yif, zif), xyz_i01 = zip(*[modf(xi, N, bounds, i)
                                         for xi, N, bounds, i in zip(xyz_i.T, self.Nxyz, self.bounds_xyz, [0, 1, 2])])

        indexes = [x_i01[i] for x_i01, i in zip(np.array(xyz_i01, dtype=int), ui)]

        v000, v001, v010, v011, v100, v101, v110, v111 = V[tuple(indexes)]
        v_00 = v000 + (v100 - v000) * xif[:, na]
        v_01 = v001 + (v101 - v001) * xif[:, na]
        v_10 = v010 + (v110 - v010) * xif[:, na]
        v_11 = v011 + (v111 - v011) * xif[:, na]
        v__0 = v_00 + (v_10 - v_00) * yif[:, na]
        v__1 = v_01 + (v_11 - v_01) * yif[:, na]

        v = (v__0 + (v__1 - v__0) * zif[:, na])
        return v.reshape(shape + (3,))


class BladedTurbulenceField(TurbulenceField):

    def get_htc_section(self, folder='', htc_dict={}):
        return TurbulenceField.get_htc_section(self, folder=folder, htc_dict={**htc_dict, 'wind.shear_format': [0, 1]})
