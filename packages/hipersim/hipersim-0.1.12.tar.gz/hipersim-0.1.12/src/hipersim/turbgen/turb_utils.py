# -*- coding: utf-8 -*-
"""
Created on Wed Nov 10 14:38:33 2021

@author: nkdi
"""
import numpy as np
import os


def get_k(Nx, dx, exclude_zero=True):
    Lx = Nx * dx
    # wave number from 1/Lx*2pi to nyquist frq i.e. Nx/2/Lx*2pi=1/(2dx)*2pi
    return np.arange(0, Nx // 2 + 1)[int(exclude_zero):] * 2 * np.pi / Lx


def spectra(uvw, Nx, dx, exclude_zero=True, spectra=['uu', 'vv', 'ww', 'uw'], mean_axis=(1, 2)):
    k = get_k(Nx, dx)

    s = set("".join(spectra))
    S_dict = {n: np.fft.fft(uvw[i], axis=0)[int(exclude_zero):Nx // 2 + 1] for i, n in enumerate('uvw') if n in s}

    def mean(PS):
        if mean_axis:
            PS = np.mean(PS, mean_axis)
        return PS

    return k, [(dx / (2 * np.pi * Nx)) * mean(np.real(np.conj(S_dict[n1]) * S_dict[n2])) for n1, n2 in spectra]


def bin_values(x, y, bin_size, min_bin_count=2):
    assert min_bin_count > 0
    x = x / bin_size
    low, high = np.floor(np.nanmin(x)), np.ceil(np.nanmax(x))
    bins = int(high - low)
    nbr_in_bins = np.histogram(x, bins, range=(low, high))[0]
    if len(x.shape) == 2:
        min_bin_count *= x.shape[1]
    mask = nbr_in_bins >= min_bin_count
    return np.histogram(x, bins, range=(low, high), weights=y)[0][mask] / nbr_in_bins[mask], nbr_in_bins


def logbin_values(k, S, log10_bin_size=.2, min_bin_count=2):
    ln_bin_size = np.log(10) * log10_bin_size
    return (bin_values(np.log(k), S, ln_bin_size, min_bin_count)[0])


def run_cpp(name, ae23, L, G, Nx, Ny, Nz, dx, dy, dz, hfc, seed, exe=r"mann_turb_x64.exe"):
    exe = os.path.abspath(exe)

    os.system(f'cmd /c "{exe}" {name} {ae23} {L} {G} {seed} {Nx} {Ny} {Nz} {dx} {dy} {dz} {int(hfc)}')
    return [f'{name}_{uvw}.bin' for uvw in 'uvw']


def run_hawc2(name, ae23, L, G, Nx, Ny, Nz, dx, dy, dz, hfc, seed, hawc2_exe=r"HAWC2MB.exe"):
    htc_name = name + ".htc"
    log_name = name + ".log"
    hawc2_exe = os.path.abspath(hawc2_exe)
    htc = f"""begin simulation;
    time_stop    0.02;
    logfile  {log_name};
end simulation;
;----------------------------------------------------------------------------------------------------------------------------------------------------------------
  begin wind;
    density    1.225;
    wsp    10;
    tint 1;
    horizontal_input    0;    0=false, 1=true
    windfield_rotations    0 0 0;    yaw, tilt, rotation
    center_pos0    0 0 -10;    hub heigth
    shear_format    1 0;    0=none,1=constant,2=log,3=power,4=linear
    turb_format    1;
    tower_shadow_method    0;    0=none, 1=potential flow, 2=jet
    begin mann;
      create_turb_parameters    {L} {ae23} {G} {seed} {hfc};    L, alfaeps, gamma, seed, highfrq compensation
      filename_u    {name}_u.bin;
      filename_v    {name}_v.bin;
      filename_w    {name}_w.bin;
      box_dim_u    {Nx} {dx};
      box_dim_v    {Ny} {dy};
      box_dim_w    {Nz} {dz};
    end mann;
  end wind;
exit;"""

    with open(htc_name, 'w') as fid:
        fid.write(htc)
    os.system(f'{hawc2_exe} {htc_name}')
    os.remove(htc_name)
    os.remove(log_name)

    return [f'{name}_{uvw}.bin' for uvw in 'uvw']


def output_field(u0, v0, w0, params, TurbOptions=None):

    import numpy as np
    import struct

    if TurbOptions is None:
        TurbOptions = {'FileFormat': 0}

    # APPLY MEAN AND VARIANCE CORRECTION
    MFFWS = TurbOptions.get('Umean', 0)

    if 'TI_u' in TurbOptions:
        TI_U = TurbOptions['TI_u']
        TI_V = TurbOptions['TI_v']
        TI_W = TurbOptions['TI_w']

        u = (u0 - np.mean(u0)) * (TI_U * MFFWS / np.std(u0))
        v = (v0 - np.mean(v0)) * (TI_V * MFFWS / np.std(v0))
        w = (w0 - np.mean(w0)) * (TI_W * MFFWS / np.std(w0))
    else:
        # Just zero-mean
        u = (u0 - np.mean(u0))
        v = (v0 - np.mean(v0))
        w = (w0 - np.mean(w0))
        TI_U, TI_V, TI_W = 1, 1, 1

    # BOX DIMENSIONS AND SPACING
    Nx = params.get('Nx', u.shape[0])
    Ny = params.get('Ny', u.shape[1])
    Nz = params.get('Nz', u.shape[2])

    dx = params['dx']
    dy = params['dy']
    dz = params['dz']

    # APPLY SHEAR CORRECTION IF NECESSARY
    ShearLaw = TurbOptions.get('ShearLaw', 'pwr')
    zOffset = TurbOptions.get('zHub', dz * (Nz - 1) / 2)

    zGoffset = 0.0  # Can in principle be an input
    z1 = zOffset - zGoffset - dz * (Nz - 1) / 2  # this is the bottom of the grid
    zbox = np.arange(Nz) * dz + z1

    if ShearLaw == 'pwr':
        alpha = TurbOptions['alpha']
        z0 = np.exp((- np.log(zOffset) * (1 / zOffset)**alpha) / (1 - (1 / zOffset)**alpha))  # Roughness length [m]
        ShearMultiplier = np.tile((zbox / zOffset)**alpha, (Nx, Ny, 1))
    elif ShearLaw == 'log':
        z0 = TurbOptions['z0']
        ShearMultiplier = np.tile(np.log(zbox / z0) / np.log(zOffset / z0), (Nx, Ny, 1))
    elif ShearLaw is None:
        ShearMultiplier = 1
        z0 = 0

    u = u + MFFWS * ShearMultiplier

    # ROTATE FIELDS IF NECESSARY
    YawAngle = TurbOptions.get('Yaw', 0)
    PitchAngle = TurbOptions.get('Pitch', 0)
    if 'Roll' in TurbOptions:
        PitchAngle = TurbOptions['Roll']
    else:
        RollAngle = 0

    if abs(YawAngle) + abs(PitchAngle) + abs(RollAngle) > 0:
        pi = np.pi
        c0 = np.cos(YawAngle * pi / 180)
        s0 = np.sin(YawAngle * pi / 180)
        c1 = np.cos(PitchAngle * pi / 180)
        s1 = np.sin(PitchAngle * pi / 180)
        c2 = np.cos(RollAngle * pi / 180)
        s2 = np.sin(RollAngle * pi / 180)

        RotationMatrix = np.zeros((3, 3))
        RotationMatrix[0, 0] = c0 * c1
        RotationMatrix[0, 1] = c0 * s1 * s2 - s0 * c2
        RotationMatrix[0, 2] = c0 * s1 * c2 + s0 * s2
        RotationMatrix[1, 0] = s0 * c1
        RotationMatrix[1, 1] = s0 * s1 * s2 + c0 * c2
        RotationMatrix[1, 2] = s0 * s1 * c2 - c0 * s2
        RotationMatrix[2, 0] = -s1
        RotationMatrix[2, 1] = c1 * s2
        RotationMatrix[2, 2] = c1 * c2

        urot = RotationMatrix[0, 0] * u + RotationMatrix[0, 1] * v + RotationMatrix[0, 2] * w
        vrot = RotationMatrix[1, 0] * u + RotationMatrix[1, 1] * v + RotationMatrix[1, 2] * w
        wrot = RotationMatrix[2, 0] * u + RotationMatrix[2, 1] * v + RotationMatrix[2, 2] * w

        u = urot
        v = vrot
        w = wrot

    FileFormat = TurbOptions.get('FileFormat', 0)
    BaseName = params.get('BaseName', 'turb_py')
    SeedNo = params.get('SeedNo', 1)
    SaveToFile = params.get('SaveToFile', 0)

    if SaveToFile:

        if (FileFormat == 0) | (FileFormat == 'Hawc2') | (FileFormat == 'Mann'):
            u.reshape(Nx * Ny * Nz).astype('single').tofile(BaseName + '_' + str(SeedNo) + '_u' + '.bin', sep='')
            v.reshape(Nx * Ny * Nz).astype('single').tofile(BaseName + '_' + str(SeedNo) + '_v' + '.bin', sep='')
            w.reshape(Nx * Ny * Nz).astype('single').tofile(BaseName + '_' + str(SeedNo) + '_w' + '.bin', sep='')
        elif (FileFormat == 'Bladed') | (FileFormat == 'wnd') | (FileFormat == 'TurbSim'):
            assert 'Umean' in TurbOptions, "Umean must be specified, otherwise the scale factor becomes 0"
            Scale = 0.00001 * MFFWS * np.asarray([TI_U * 100, TI_V * 100, TI_W * 100])
            Offset = np.array([MFFWS, 0, 0])

            uOut = np.asarray((u - Offset[0]) / Scale[0], dtype='int16')
            vOut = np.asarray((v - Offset[1]) / Scale[1], dtype='int16')
            wOut = np.asarray((w - Offset[2]) / Scale[2], dtype='int16')

            OutFileName = str(BaseName + '_' + str(SeedNo) + '.wnd')
            wnd_file = open(OutFileName, 'wb')

            # HEADER OF THE .WND FILE
            wnd_file.write(struct.pack('<h', -99))             # ID - must be -99
            wnd_file.write(struct.pack('<h', 4))               # ID2 - must be 4
            wnd_file.write(struct.pack('<i', 3))              # number of components (should be 3)
            wnd_file.write(struct.pack('<f', 0.0))             # latitude (deg)
            wnd_file.write(struct.pack('<f', z0))              # Roughness length (m)
            wnd_file.write(struct.pack('<f', zOffset))         # Reference height (m) = Z(1) + GridHeight / 2.0
            wnd_file.write(struct.pack('<f', TI_U * 100))        # Turbulence Intensity of u component (%)
            wnd_file.write(struct.pack('<f', TI_V * 100))        # Turbulence Intensity of v component (%)
            wnd_file.write(struct.pack('<f', TI_W * 100))        # Turbulence Intensity of w component (%)
            wnd_file.write(struct.pack('<f', dz))              # delta z in m
            wnd_file.write(struct.pack('<f', dy))              # delta y in m
            wnd_file.write(struct.pack('<f', dx))              # delta x in m
            # half the number of time steps (points in longitudinal direction)
            wnd_file.write(struct.pack('<i', int(Nx / 2)))
            wnd_file.write(struct.pack('<f', MFFWS))           # mean full-field wind speed
            wnd_file.write(struct.pack('<f', 0.0))             # zLu - unused variable
            wnd_file.write(struct.pack('<f', 0.0))             # yLu - unused variable
            wnd_file.write(struct.pack('<f', 0.0))             # xLu - unused variable
            wnd_file.write(struct.pack('<i', 0))               # _ - unused variable
            wnd_file.write(struct.pack('<i', 0))               # RandSeed1 - unused variable
            wnd_file.write(struct.pack('<i', Nz))              # number of points in vertical direction
            wnd_file.write(struct.pack('<i', Ny))              # number of points in horizontal direction
            wnd_file.write(struct.pack('<i', 0))               # Unused variable - for BLADED
            wnd_file.write(struct.pack('<i', 0))               # Unused variable - for BLADED
            wnd_file.write(struct.pack('<i', 0))               # Unused variable - for BLADED
            wnd_file.write(struct.pack('<i', 0))               # Unused variable - for BLADED
            wnd_file.write(struct.pack('<i', 0))               # Unused variable - for BLADED
            wnd_file.write(struct.pack('<i', 0))               # Unused variable - for BLADED

            # WRITE WIND FIELD DATA OUT
            if TurbOptions.get('clockwise', True):
                y_ix = np.flip(np.arange(Ny))
            else:
                y_ix = np.arange(Ny)

            for it in range(Nx):
                for iz in range(Nz):
                    for iy in y_ix:
                        wnd_file.write(struct.pack('<h', uOut[it, iy, iz]))
                        wnd_file.write(struct.pack('<h', vOut[it, iy, iz]))
                        wnd_file.write(struct.pack('<h', wOut[it, iy, iz]))

            wnd_file.close()

    return u, v, w
