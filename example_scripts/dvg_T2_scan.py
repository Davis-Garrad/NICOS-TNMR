# *****************************************************************************
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Davis V. Garrad <davis.last@psi.ch>
#
# *****************************************************************************

# do "accessory" stuff. Set field, temperature, etc.
SetEnvironment(se_tt, se_mf) # Add the PPMS temperature and field to the file at every write.
if(False):
    maw(se_tt, 3) # set PPMS temperature
    nicossleep(20*60) # 20 minutes
# ...

# Create the pulse sequence
# generate_pulse(pulse_width, amplitude, delay_time, pulse_cycle)
pw90 = 2.5 # us
amp = 40 # percent
tau = 50 # us

p180   = generate_pulse(2*pw90, amp, 1,   '1 3 3 1 2 0 0 2 0 2 2 0 3 1 1 3') # 180deg
p90    = generate_pulse(pw90,   amp, tau, '0 2 0 2 1 3 1 3 0 2 0 2 1 3 1 3') # 90deg
p180_2 = generate_pulse(2*pw90, amp, 0,   '1 3 3 1 2 0 0 2 0 2 2 0 3 1 1 3') # 180deg
seq = [ p180, p90, p180_2 ]

# Create the list of sequences to scan (specifically, for a T1 scan)
delay_times = log_durations(10, 1_000_000, 20)
# generates a list of sequences; copies of seq are made, only the zeroth pulse is modified. Each copy is given a 'delay_time' value from delay_times
seq_list = generate_sequences(seq, [0], 'delay_time', delay_times)

# Now, the reader should note how easy manipulating pulse sequences really is
for i in range(len(seq_list)):
    seq_list[i][1]['delay_time'] = max(seq_list[i][0]['delay_time'] - 10.0, 0.1)

# Set some parameters independent of pulse sequence
globalparams = {
    'acq_phase_cycle': '0 2 0 2 1 3 1 3 2 0 2 0 3 1 3 1',
    'acquisition_time': 204.8, # us
    'num_scans': 1024, # "1D scans" in TNMR. Our 16-fold phase cycling means this should be a multiple of 16 for proper averaging
    'ringdown_time': 1, # us
    'post_acquisition_time': 250, # ms
    'obs_freq': 41.59, # MHz. Receiver frequency
    'nucleus': 'NUCMgReS',
    'comments': 'An example of a T2 scan',
}
se_tnmr_otf_module.update_parameters(globalparams)

# Acquire data
scan_sequences(se_tnmr_otf_module, seq_list) # gather the data
