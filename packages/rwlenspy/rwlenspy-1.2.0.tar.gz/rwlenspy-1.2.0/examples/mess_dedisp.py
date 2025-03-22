from time import time

import numpy as np
from astropy import constants as c
from astropy import cosmology
from astropy import units as u
from scipy.fft import rfftfreq, rfft, irfft, fftfreq, ifft, fft, fftshift

import rwlenspy.lensing as rwl
import rwlenspy.utils as utils

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm


cosmo = cosmology.Planck18

# Comoving
D_obs_src = cosmo.comoving_distance(1)
D_obs_len = 1 * u.kpc

# Redshift
# z_obs_len = 0
z_obs_src = cosmology.z_at_value(cosmo.comoving_distance, D_obs_src)

# Ang. Diam. Distance
D_obs_len = 1 * u.kpc
D_obs_src = cosmo.angular_diameter_distance(z_obs_src)
D_len_src = cosmo.angular_diameter_distance(z_obs_src) - D_obs_len

# Physical Lens Params
const_D = D_len_src / (D_obs_len * D_obs_src)
r_e = c.alpha**2 * c.a0  # classical electron radius
kdm = (
    (r_e * c.c / (2 * np.pi)).to(u.cm**2 / u.s)
    * ((1.0 * u.pc / u.cm).to(u.m / u.m)).value
).value
lens_scale = (10 * u.AU / D_obs_len).to(u.m / u.m)
scale = lens_scale.value
geom_const = ((1 / (const_D * c.c)).to(u.s)).value
geom_const = geom_const * scale**2
lens_const = kdm
DM = 0.001
freq_power = -2.0
beta_x = 0.0
beta_y = 0.0

# Grid Parameters
max_fres = 5.0
theta_min = -max_fres
theta_max = max_fres
theta_N = 201

# Lens Parameters
freq_ref = 0
freq_phase_ref = 1e128
bb_frames = 5
freqs = 800e6 - rfftfreq(2048 * bb_frames, d=1 / (800e6))  # MHz
freqs = freqs.astype(np.double).ravel(order="C")

nyqalias = True

# Spatial Grid
x1 = np.arange(theta_N) * (theta_max - theta_min) / (theta_N - 1) + theta_min

# Lens Functions
lens_arr = utils.ConstantLens(x1[:, None], x1[None, :], DM)
lens_arr = lens_arr.astype(np.double).ravel(order="C")

# Solutions from Algorithm
print("Getting the transfer function with Algorithm...")
t1 = time()
transferfunc = rwl.RunUnitlessTransferFunc(
    theta_min,
    theta_max,
    theta_N,
    freqs,
    freq_ref,
    lens_arr,
    beta_x,
    beta_y,
    geom_const,
    lens_const,
    freq_power,
    freq_phase_ref,
    nyqalias,
)
tv = time() - t1
print(
    "Tranfer function obtained in:", tv, "s", " | ", tv / 60, "min", tv / 3600, "hr"
)
transferfunc = np.array(transferfunc).astype(np.cdouble)

# Analytic dispersion for alias sampled freq
dedispersion_tf = np.exp(
    2j * np.pi * kdm * DM * freqs**(-1)
)


fig, ax = plt.subplots()
ax.plot(freqs/1e6, np.angle(dedispersion_tf))
ax.plot(freqs/1e6, np.angle(transferfunc))
ax.set_ylabel("dedisp angle [ul]", size=14)
ax.set_xlabel("Freq [MHz]", size=14)
# save png
save_path = "mess_dedisp.png"
fig.savefig(str(save_path))

fig, ax = plt.subplots()
ax.plot(freqs/1e6, np.angle(dedispersion_tf) + np.angle(transferfunc))
ax.set_ylabel("dedisp angle [ul]", size=14)
ax.set_xlabel("Freq [MHz]", size=14)
# save png
save_path = "mess_dedisp_err.png"
fig.savefig(str(save_path))

# dedispersion removes the phase
assert (np.abs(np.angle(transferfunc * dedispersion_tf)) < 1e-10).all()
