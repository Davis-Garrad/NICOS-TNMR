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
# ...

# Create the pulse sequence
# generate_pulse(pulse_width, amplitude, delay_time, pulse_cycle)
p180   = generate_pulse(5,   40, 1,   '1 3 3 1 2 0 0 2 0 2 2 0 3 1 1 3') # 180deg
p90    = generate_pulse(2.5, 40, 50,  '0 2 0 2 1 3 1 3 0 2 0 2 1 3 1 3') # 90deg
p180_2 = generate_pulse(5,   40, 0.1, '1 3 3 1 2 0 0 2 0 2 2 0 3 1 1 3') # 180deg
seq = [ p180, p90, p180_2 ]

# Create the list of sequences to scan (specifically, for a T1 scan)
delay_times = [ 1, 10, 100, 1_000, 10_000, 100_000, 1_000_000 ] # useconds
# generates a list of sequences; copies of seq are made, only the zeroth pulse is modified. Each copy is given a 'delay_time' value from delay_times
seq_list = generate_sequences(seq, [0], 'delay_time', taus)

# Set some parameters independent of pulse sequence
se_tnmr_otf_module.acq_phase_cycle = '0 2 0 2 1 3 1 3 2 0 2 0 3 1 3 1' # somewhat standard 16-term phase cycle
se_tnmr_otf_module.acquisition_time = 204.8 # us
se_tnmr_otf_module.num_acqs = 1600 # "1D scans" in TNMR. Number of acquisitions to sum together (to kill noise)
se_tnmr_otf_module.ringdown_time = 1 # us
se_tnmr_otf_module.post_acquisition_time = 500 # ms
se_tnmr_otf_module.obs_freq = 41.59 # MHz. Receiver frequency
se_tnmr_otf_module.nucleus = '139La'
se_tnmr_otf_module.comments = 'An example script, illustrating a T1 scan'

# Acquire data
SetEnvironment(se_tt, se_mf) # Set environment, whose values will be written to the end HDF file
scan_sequences(se_tnmr_otf_module, seq_list) # gather the data
finish_tnmr_scan() # not strictly necessary, but redundancy doesn't hurt
