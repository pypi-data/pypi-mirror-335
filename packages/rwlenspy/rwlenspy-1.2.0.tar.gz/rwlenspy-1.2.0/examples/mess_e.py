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
lens_r2_scale = 4.848e-11 #nas in rad
geom_const_r2 = 2.2e-5 # s
freq_power_r2 = -2.0
lens_const_r2 = 1.9e-3 * (100e6)**(-freq_power_r2) # s * (100 MHz)^-k
beta_r2_x = 0.2
beta_r2_y = 0.3

# Physical Lens (r1) Params
lens_r1_scale = 4.848e-11 #mas in rad
geom_const_r1 = 3.2e-4 # s
freq_power_r1 = 2.0
lens_const_r1 = 1.2e-6 * (100e6)**(-freq_power_r1) # s * (100 MHz)^-k
beta_r1_x = 0.1
beta_r1_y = 0.0


# Sim Parameters
freq_ref = 800e6
phase_freq_ref = 0
windowsamples = 128
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
lens_arr_r1 = utils.RationalLens(x1[:, None], x1[None, :])

lens_arr_r2 = lens_arr_r2.astype(np.double).ravel(order="C")
lens_arr_r1 = lens_arr_r1.astype(np.double).ravel(order="C")
freqs = freqs.astype(np.double).ravel(order="C")

# Get Transfer
print("Getting the Transfer Function")
t1 = time()
transferfunc = rwl.RunMultiplaneTransferFunc(
    theta_min,
    theta_max,
    theta_N,
    freqs,
    freq_ref,
    lens_arr_r2,
    lens_r2_scale,
    beta_r2_x,
    beta_r2_y,
    geom_const_r2,
    lens_const_r2,
    freq_power_r2,
    lens_arr_r1,
    lens_r1_scale,
    beta_r1_x,
    beta_r1_y,
    geom_const_r1,
    lens_const_r1,
    freq_power_r1,
    phase_freq_ref,    
    nyqalias,
)
tv = time() - t1
print("Total Time :", tv, "s", " | ", tv / 60, "min", tv / 3600, "hr")
transferfunc = np.array(transferfunc).astype(np.cdouble)

fig, ax = plt.subplots()
ax.plot(freqs/1e6,np.abs(transferfunc))
ax.set_xlabel("Freq [MHz]", size=14)
ax.set_ylabel("power [ul]", size=14)
# save png
save_path = "morphtest_tf.png"
fig.savefig(str(save_path))


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
    lens_r2_scale,
    beta_r2_x,
    beta_r2_y,
    geom_const_r2,
    lens_const_r2,
    freq_power_r2,
    lens_arr_r1,
    lens_r1_scale,
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

print(delayvals)

subchan_tf = np.zeros((freqss.size, bb_frames)) + 0j

subchan_freqs = fftfreq(bb_frames,d=windowsamples*tres)

all_chans = freqss[:,None] - subchan_freqs[None,:]

for i in range(freqss.size):
    fcut = np.where(freqss[i] == fvals)

    img_mags = magvals[fcut] 
    img_dels = delayvals[fcut]

    subchan_tf[i,:] = np.sum( img_mags[None,:]*np.exp(1j*2*np.pi*(all_chans[i,:][:,None])*img_dels[None,:]),axis=-1)


times = np.arange(dumpframes) * tres

#sig_ = np.exp(-0.5*(times - times[times.size//2])**2/(20*tres)**2)
#sig_ = sig_ * np.random.normal(size=sig_.size)
sig_ = np.zeros(times.size)
sig_[times.size//4] = 1

vstream_1 = sig_.copy()
print(ref_delay)
dumtf = np.exp(2j*np.pi*(freqs)*ref_delay)
#dumtf
# full tf
sig_ = irfft(rfft(sig_) * transferfunc)
vstream_2 = sig_

fig, ax = plt.subplots()
ax.plot(times, irfft(transferfunc))
ax.plot(times, irfft(dumtf))
ax.set_ylabel("Freq [MHz]", size=14)
ax.set_xlabel("Time [ms]", size=14)

# save png
save_path = "morphtest_baseband_volttf1.png"
fig.savefig(str(save_path))

print(windowsamples)
vstream_1 = vstream_1.reshape((vstream_1.shape[-1] // windowsamples, windowsamples))
vstream_2 = vstream_2.reshape((vstream_2.shape[-1] // windowsamples, windowsamples))

baseband_chan_to_transf = rfft(vstream_1, axis=-1).T

baseband_transf_to_chan = rfft(vstream_2, axis=-1).T

baseband_chan_to_transf = fft(baseband_chan_to_transf,axis=-1)

baseband_chan_to_transf = baseband_chan_to_transf * subchan_tf

baseband_chan_to_transf = ifft(
    baseband_chan_to_transf, axis=-1)


fig, ax = plt.subplots()
im1 = ax.imshow(
    np.abs(baseband_chan_to_transf) ** 2 / np.amax( np.abs(baseband_chan_to_transf[0,:]) ** 2),
    aspect="auto",interpolation='None',    
    extent=[0, times[-1] / 1e-3, 400, 800],
    #norm=LogNorm()
)
ax.scatter(((delayvals + (times.size//4) *  tres )% times[-1] ) / 1e-3, fvals/1e6, s = 0.02 , c='k')
ax.set_ylabel("Freq [MHz]", size=14)
ax.set_xlabel("Time [ms]", size=14)
fig.colorbar(im1)

# save png
save_path = "morphtest_baseband_c2t.png"
fig.savefig(str(save_path))


fig, ax = plt.subplots()
im1 = ax.imshow(
    np.abs(baseband_transf_to_chan) ** 2 / np.amax( np.abs(baseband_transf_to_chan[0,:]) ** 2) ,
    aspect="auto",interpolation='None',
    extent=[0, times[-1] / 1e-3, 400, 800], vmax=1,
    #norm=LogNorm()    
)
ax.scatter(((delayvals + (times.size//4) *  tres )% times[-1] ) / 1e-3, fvals/1e6, s = 0.02 , c='k')
ax.set_ylabel("Freq [MHz]", size=14)
ax.set_xlabel("Time [ms]", size=14)
fig.colorbar(im1)

# save png
save_path = "morphtest_baseband_t2c.png"
fig.savefig(str(save_path))

fig, ax = plt.subplots()
im1 = ax.imshow(
    (np.abs(baseband_chan_to_transf) ** 2 )
        - (np.abs(baseband_transf_to_chan) ** 2 ),
    aspect="auto",interpolation='None',cmap='bwr',
    extent=[0, vstream_1.shape[-1] // windowsamples * tres * windowsamples\
        / 1e-3, 400, 800], vmax=1,
)
ax.set_ylabel("Freq [MHz]", size=14)
ax.set_xlabel("Time [ms]", size=14)
fig.colorbar(im1)

# save png
save_path = "morphtest_baseband_diff.png"
fig.savefig(str(save_path))


t1 = np.sum(np.abs(baseband_chan_to_transf) ** 2,axis = 0) 
t1 = t1 / np.amax(t1)
t2 = np.sum(np.abs(baseband_transf_to_chan) ** 2,axis = 0)
t2 = t2 / np.amax(t2)
print(np.sum(t1 * t2)/ np.sqrt(np.sum(t1**2) * np.sum(t2**2)))

fig, ax = plt.subplots()
ax.plot(t1 )
ax.plot(t2 )
ax.set_xlabel("Time [samples]", size=14)

# save png
save_path = "morphtest_baseband_diff2.png"
fig.savefig(str(save_path))


fig, ax = plt.subplots()
#ax.plot(np.sum(    np.abs(baseband_chan_to_transf) ** 2,axis = 0))
#ax.plot(np.sum(    np.abs(baseband_transf_to_chan) ** 2,axis = 0))
ax.plot(t1 - t2 )
#ax.plot(np.sum(    np.abs(baseband_chan_to_transf) ** 2,axis = 0) - np.sum(    #np.abs(baseband_transf_to_chan) ** 2,axis = 0))
ax.set_xlabel("Time [samples]", size=14)

# save png
save_path = "morphtest_baseband_diff3.png"
fig.savefig(str(save_path))

print()
assert np.sum(t1 * t2)/ np.sqrt(np.sum(t1**2) * np.sum(t2**2)) > 0.9
