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

p90    = generate_pulse(2.5, 40, 50,  '0 2 0 2 1 3 1 3 0 2 0 2 1 3 1 3')
p180_2 = generate_pulse(5,   40, 0.1, '1 3 3 1 2 0 0 2 0 2 2 0 3 1 1 3')

seq = [ p90, p180_2 ]

se_tnmr_otf_module.acq_phase_cycle = '0 2 0 2 1 3 1 3 2 0 2 0 3 1 3 1'
se_tnmr_otf_module.acquisition_time = 204.8 # us
se_tnmr_otf_module.num_acqs = 1024
se_tnmr_otf_module.ringdown_time = 1 # us
se_tnmr_otf_module.post_acquisition_time = 500 # ms
se_tnmr_otf_module.obs_freq = 41.59 # MHz

mhz_constant = 1639.0
half_range = mhz_constant*3
N=40
fields = [ (68176.0 - half_range)+i*half_range*2/N for i in range(0, N+1) ] #Oe. 1639Oe corresponds to about 1MHz

eta = 0
for f in fields:
    eta += estimate_sequence_length(seq)
print(timestring(eta))

begin_tnmr_scan()
for field in fields:
    maw(se_mf, field/1e4) # tesla
    print_sequence(seq)

    # Acquire data
    scan_sequences([seq], [ (se_tt.read, 'ppms_temperature'), (se_mf.read, 'ppms_field') ]) # gather the data

finish_tnmr_scan()