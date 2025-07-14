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

# Create each individual pulse
p90    = generate_pulse(2.5, 40, 50,  '0 2 0 2 1 3 1 3 0 2 0 2 1 3 1 3')
p180_2 = generate_pulse(5,   40, 0.1, '1 3 3 1 2 0 0 2 0 2 2 0 3 1 1 3')

# Structure our pulse sequence as a list of multiple pulses
seq = [ p90, p180_2 ]

# Set global parameters
se_tnmr_otf_module.acq_phase_cycle = '0 2 0 2 1 3 1 3 2 0 2 0 3 1 3 1'
se_tnmr_otf_module.acquisition_time = 204.8 # us
se_tnmr_otf_module.num_scans = 128
se_tnmr_otf_module.ringdown_time = 1 # us
se_tnmr_otf_module.post_acquisition_time = 750 # ms

central_frequency = 41.59 # MHz
frequency_range = 0.4 # MHz
half_N = 10
frequencies = [ central_frequency - frequency_range/2 + frequency_range * (i/(2*half_N)) for i in range(0, 2*half_N+1) ]

eta = estimate_sequence_length(seq) * len(frequencies) # estimate the time to finish. This is normally pretty accurate, but by no means is it 100% perfect.
print(timestring(eta))

AddEnvironment(se_tt, se_mf) # add temperature and field to the environment to be read and saved each sequence.

begin_tnmr_scan() # we want to lump all the measurements together, but we're changing a non-sequence-specific parameter. Calling begin_tnmr_scan will ensure that scan_sequence(seq) does not deal with the datamanager.
for fq in range(len(frequencies)):
    se_tnmr_otf_module.obs_freq = frequencies[fq] # MHz
    eta = 0
    for j in frequencies[fq:]:
        eta += estimate_sequence_length(seq)
    print(timestring(eta) + ' remaining')
    scan_sequence(seq)
finish_tnmr_scan()