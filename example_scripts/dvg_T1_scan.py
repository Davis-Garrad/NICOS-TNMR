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
if(False):
    maw(se_tt, temperature) # set PPMS temperature
    nicossleep(1200) # 20 minutes
# ...

# Create the pulse sequence
# generate_pulse(pulse_width, amplitude, delay_time, pulse_cycle)
p180_2 = generate_pulse(5,   40, 1, '1 3 3 1 2 0 0 2 0 2 2 0 3 1 1 3') # 180deg
p90    = generate_pulse(2.5, 40, 50,  '0 2 0 2 1 3 1 3 0 2 0 2 1 3 1 3') # 90deg
p180_2 = generate_pulse(5,   40, 0.1, '1 3 3 1 2 0 0 2 0 2 2 0 3 1 1 3') # 180deg
seq = [ p90, p180_2 ]

# Create the list of sequences to scan (specifically, for a T1 scan)
delay_times = []
# generates a list of sequences; copies of seq are made, only the zeroth pulse is modified. Each copy is given a 'delay_time' value from delay_times
seq_list = generate_sequences(seq, [0], 'delay_time', taus)

# Set some parameters independent of pulse sequence
se_tnmr_otf_module.acq_phase_cycle = '0 2 0 2 1 3 1 3 2 0 2 0 3 1 3 1'
se_tnmr_otf_module.acquisition_time = 204.8 # us
se_tnmr_otf_module.num_scans = 1200 # "1D scans" in TNMR
se_tnmr_otf_module.ringdown_time = 1 # us
se_tnmr_otf_module.post_acquisition_time = 250 # ms
se_tnmr_otf_module.obs_freq = 41.59 # MHz. Receiver frequency

# Acquire data
scan_sequences(seq_list, [ (se_tt.read, 'ppms_temperature'), (se_mf.read, 'ppms_field') ]) # gather the data
finish_tnmr_scan() # not strictly necessary, but redundancy doesn't hurt
