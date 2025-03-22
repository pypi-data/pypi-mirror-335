import matplotlib.pyplot
from time import time

import numpy as np
from astropy import constants as c
from astropy import cosmology
from astropy import units as u
from scipy.fft import rfftfreq, rfft, irfft, fftfreq, ifft, fft, fftshift

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm

import rwlenspy.lensing as rwl
import rwlenspy.utils as utils

# Memory in bytes
maxmemory = 2E9

cosmo = cosmology.Planck18

# Comoving
D_obs_src = 1 * u.Gpc
D_obs_r1 = D_obs_src / 2
D_obs_r2 = 3 * D_obs_src / 4

# redshift
z_obs_r1 = cosmology.z_at_value(cosmo.comoving_distance, D_obs_r1)
z_obs_r2 = cosmology.z_at_value(cosmo.comoving_distance, D_obs_r2)
z_obs_src = cosmology.z_at_value(cosmo.comoving_distance, D_obs_src)

# Ang. Diam. Distance
D_obs_r1 = cosmo.angular_diameter_distance(z_obs_r1)
D_obs_r2 = cosmo.angular_diameter_distance(z_obs_r2)
D_r1_r2 = cosmo.angular_diameter_distance_z1z2(z_obs_r1, z_obs_r2)
D_obs_src = cosmo.angular_diameter_distance(z_obs_src)
D_r2_src = cosmo.angular_diameter_distance_z1z2(z_obs_r2, z_obs_src)

# Physical Lens (r2) Params
r_e = c.alpha**2 * c.a0  # classical electron radius
kdm = (
    (r_e * c.c / (2 * np.pi)).to(u.cm**2 / u.s)
    * ((1.0 * u.pc / u.cm).to(u.m / u.m)).value
).value
const_Dr2 = D_r2_src / (D_obs_r2 * D_obs_src)
lens_r2_scale = (1000 * u.AU / D_obs_r2).to(u.m / u.m)
scale_r2 = lens_r2_scale.value
sig_DM = 0.0015
geom_const_r2 = ((1 / (const_Dr2 * c.c)).to(u.s)).value
geom_const_r2 = geom_const_r2 * scale_r2**2
lens_const_r2 = kdm * sig_DM
freq_power_r2 = -2.0
beta_r2_x = 0.2
beta_r2_y = 0.0

# Physical Lens (r1) Params
scale_r1 = 4.848e-9 #mas in rad
geom_const_r1 = 2.2e-6 # s
freq_power_r1 = 0.0
lens_const_r1 = 1.2e-7 * (100e6)**(-freq_power_r1) # s * (100 MHz)^-k
beta_r1_x = 1.5
beta_r1_y = 0.5


# Sim Parameters
freq_ref = 800e6
windowsamples = 64
bb_frames = 500
dumpframes = windowsamples * bb_frames
tres = 1 / 800e6
freqs = 800e6 - rfftfreq(dumpframes, d=tres)
freqs = freqs.astype(np.double).ravel(order="C")

# Grid Parameters
max_fres = 5
theta_min = -max_fres
theta_max = max_fres
theta_N = 251
nyqalias = True
verbose=True


# Spatial Grid
x1 = np.arange(theta_N) * (theta_max - theta_min) / (theta_N - 1) + theta_min

# Lens functions
seed = 4321
lens_arr_r2 = utils.RationalLens(x1[:, None], x1[None, :]) 
#np.ones((theta_N, theta_N)) * utils.RandomGaussianLens(theta_N, 1, 1, seed=seed)  # 1D lens
lens_arr_r1 = utils.ConstantLens(x1[:, None], x1[None, :])

lens_arr_r2 = lens_arr_r2.astype(np.double).ravel(order="C")
lens_arr_r1 = lens_arr_r1.astype(np.double).ravel(order="C")
freqs = freqs.astype(np.double).ravel(order="C")

freqss = 800e6 - rfftfreq(windowsamples*1,d=tres)
if freq_ref not in freqss:
    freqss = np.append(freqss,[freq_ref])

freqn = freqss.size
# Solutions from Algorithm
print("Getting the Images with Algorithm...")
t1 = time()
txvals, tyvals, fvals, delayvals, magvals = rwl.GetMultiplaneFreqStationaryPoints(
    theta_min,
    theta_max,
    theta_N,
    freqs,
    freq_ref,
    lens_arr_r2,
    scale_r2,
    beta_r2_x,
    beta_r2_y,
    geom_const_r2,
    lens_const_r2,
    freq_power_r2,
    lens_arr_r1,
    scale_r1,
    beta_r1_x,
    beta_r1_y,
    geom_const_r1,
    lens_const_r1,
    freq_power_r1,
    maxmemory,
    verbose=verbose
)
tv = time() - t1
print("Images obtained in:", tv, "s", " | ", tv / 60, "min", tv / 3600, "hr")

txvals = np.asarray(txvals)
tyvals = np.asarray(tyvals)
fvals = np.asarray(fvals)
delayvals = np.asarray(delayvals)
magvals = np.asarray(magvals)


ref_delay_f = np.where(fvals == freq_ref)
ref_arg = np.argmax(magvals[ref_delay_f])  
ref_mag = magvals[ref_delay_f][ref_arg]
ref_delay = delayvals[ref_delay_f][ref_arg]

print(ref_mag,ref_delay)

delayvals = delayvals - ref_delay
magvals = magvals / np.abs(ref_mag)

fig, ax = plt.subplots()
ax.scatter(delayvals/1e-6, fvals/1e6)
ax.set_ylabel("Freq [MHz]", size=14)
ax.set_xlabel("Time [us]", size=14)
# save png
save_path = "mess_1_scatterdist.png"
fig.savefig(str(save_path))



fig, ax = plt.subplots()
ax.scatter((delayvals % (dumpframes * tres))/1e-6, fvals/1e6)
ax.set_ylabel("Freq [MHz]", size=14)
ax.set_xlabel("Time [us]", size=14)
# save png
save_path = "mess_1_scatterdist_modulo.png"
fig.savefig(str(save_path))
