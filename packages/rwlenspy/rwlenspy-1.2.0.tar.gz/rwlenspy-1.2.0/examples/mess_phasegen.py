import matplotlib.pyplot as plt
from time import time

import numpy as np
from astropy import constants as c
from astropy import cosmology
from astropy import units as u
from scipy.fft import rfftfreq, rfft, irfft, fftfreq, ifft, fft, fftshift

from matplotlib.colors import LogNorm

import rwlenspy.lensing as rwl
import rwlenspy.utils as utils

# Memory in bytes
maxmemory = 2E9

cosmo = cosmology.Planck18
# Comoving
D_obs_src = cosmo.comoving_distance(1)
D_obs_len = cosmo.comoving_distance(1) / 2

# Redshift
z_obs_src = cosmology.z_at_value(cosmo.comoving_distance, D_obs_src)
z_obs_len = cosmology.z_at_value(cosmo.comoving_distance, D_obs_len)

# Ang. Diam. Dist
D_obs_src = cosmo.angular_diameter_distance(z_obs_src)
D_obs_len = cosmo.angular_diameter_distance(z_obs_len)
D_len_src = cosmo.angular_diameter_distance_z1z2(z_obs_len, z_obs_src)

# Physical Lens Params.
Eins_time_const = 4 * c.G * c.M_sun / c.c**3
const_D = D_len_src / (D_obs_len * D_obs_src)
freq_ref = 800e6
phase_freq_ref = 0
mass = 1e0  # solar mass
theta_E = np.sqrt(mass * Eins_time_const * c.c * const_D).to(u.m / u.m)
windowsamples = 2048
bb_frames = 500
dumpframes = windowsamples * bb_frames
tres = 1 / 800e6
freqs = 800e6 - rfftfreq(dumpframes, d=tres)
freqs = freqs.astype(np.double).ravel(order="C")
beta_x = 0.5
beta_y = 0.0

new_freqs = freqs[:bb_frames+1]

# Grid parameters
max_fres = 5
theta_min = -max_fres
theta_max = max_fres
theta_N = 1001
nyqalias = True
verbose=False

# Lens Parameters
geom_const = ((1 / (const_D * c.c)).to(u.s)).value
geom_const = geom_const * theta_E.value**2
lens_const = mass * Eins_time_const.to(u.s).value
freq_power = 0

# Spatial Grid
x1 = np.arange(theta_N) * (theta_max - theta_min) / (theta_N - 1) + theta_min

# Lens Functions
lens_arr = -utils.LogLens(x1[None, :], x1[:, None])
lens_arr = lens_arr.astype(np.double).ravel(order="C")

# Get Transfer Function
print("Getting the transfer function with Algorithm...")
t1 = time()
transferfunc = rwl.RunUnitlessTransferFunc(
    theta_min,
    theta_max,
    theta_N,
    new_freqs,
    freq_ref,
    lens_arr,
    beta_x,
    beta_y,
    geom_const,
    lens_const,
    freq_power,
    phase_freq_ref,
    nyqalias,
    verbose=verbose
)
tv = time() - t1
print("Tranfer function obtained in:", tv, "s", " | ", tv / 60, "min", tv / 3600, "hr")
transferfunc = np.array(transferfunc).astype(np.cdouble)

freqss = 800e6 - rfftfreq(windowsamples*1,d=tres)
freqn = freqss.size
# Solutions from Algorithm
print("Getting the Images with Algorithm...")
t1 = time()
txvals, tyvals, fvals, delayvals, magvals = rwl.GetUnitlessFreqStationaryPoints(
    theta_min,
    theta_max,
    theta_N,
    lens_arr,
    new_freqs,
    beta_x,
    beta_y,
    geom_const,
    lens_const,
    freq_power,
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

subchan_tf = np.zeros(transferfunc.shape) + 0j

for i in range(new_freqs.size):
    fcut = np.where(new_freqs[i] == fvals)

    img_mags = magvals[fcut] 
    img_dels = delayvals[fcut]

    subchan_tf[i] = np.sum( img_mags*np.exp(1j*2*np.pi*(new_freqs[i])*img_dels),axis=-1)


# Analytic Solutions
_, delay_analytic, mag_analytic = utils.AnalyticPointMassGrav(
    beta_x, geom_const, lens_const
)

mag_argmax = np.argmax(np.abs(mag_analytic))

analytic_tf = mag_analytic[0] / mag_analytic[mag_argmax] * np.exp(
    1j * 2 * np.pi * new_freqs * (delay_analytic[0] - delay_analytic[mag_argmax])
) + mag_analytic[1] / mag_analytic[mag_argmax] * np.exp(1j * 2 * np.pi * new_freqs * (delay_analytic[1] - delay_analytic[mag_argmax]))

chan_center = freqss[[0,1]]

subchan_tf2 = np.zeros((chan_center.size,bb_frames)) + 0j

subchan_freqs = fftfreq(bb_frames,d=windowsamples*tres)

all_chans = chan_center[:,None] - subchan_freqs[None,:]

print(all_chans.shape)
for i in range(chan_center.size):
    fcut = np.where(chan_center[i] == fvals)

    img_mags = magvals[fcut] 
    img_dels = delayvals[fcut]

    subchan_tf2[i,:] = np.sum( img_mags[None,:]*np.exp(1j*2*np.pi*(all_chans[i,:][:,None])*img_dels[None,:]),axis=-1)

all_chans = fftshift(all_chans,axes=-1).ravel()
subchan_tf2 = fftshift(subchan_tf2,axes=-1).ravel()

fcut = (all_chans <= chan_center[0] ) * (all_chans >= chan_center[1])

all_chans = all_chans[fcut]
subchan_tf2 = subchan_tf2[fcut] 

plt.figure()
plt.plot(new_freqs, np.abs(transferfunc) )
plt.plot(all_chans, np.abs(subchan_tf2) )
plt.plot(new_freqs, np.abs(subchan_tf) )
plt.plot(new_freqs, np.abs(analytic_tf) )
plt.savefig('mess_phasegen_abs.png')

plt.figure()
plt.plot(new_freqs, np.angle(transferfunc) )
plt.plot(all_chans, np.angle(subchan_tf2) )
plt.plot(new_freqs, np.angle(subchan_tf) )
plt.plot(new_freqs, np.angle(analytic_tf) )
plt.savefig('mess_phasegen_ang.png')

assert (np.abs( np.abs(transferfunc) - np.abs(subchan_tf2)) < 1e-10).all()
assert (np.abs( np.angle(transferfunc) - np.angle(subchan_tf2)) < 1e-10).all()

assert (np.abs( np.abs(transferfunc) - np.abs(subchan_tf)) < 1e-10).all()
assert (np.abs( np.angle(transferfunc) - np.angle(subchan_tf)) < 1e-10).all()

assert (np.abs( np.abs(subchan_tf2) - np.abs(subchan_tf)) < 1e-10).all()
assert (np.abs( np.angle(subchan_tf2) - np.angle(subchan_tf)) < 1e-10).all()
