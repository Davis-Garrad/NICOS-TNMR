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

# Set some parameters independent of pulse sequence
globalparams = {
    'acq_phase_cycle': '0 2 0 2 1 3 1 3 2 0 2 0 3 1 3 1',
    'acquisition_time': 204.8, # us
    'num_scans': 1024, # "1D scans" in TNMR. Our 16-fold phase cycling means this should be a multiple of 16 for proper averaging
    'ringdown_time': 15, # us
    'post_acquisition_time': 250, # ms
    'obs_freq': 41.59, # MHz. Receiver frequency
    'nucleus': 'NUCMgReS',
    'comments': 'An example of a field sweep',
}
update_device_parameters(nmr_daq_scout, globalparams)

fields = [ 6.8 + i*1e-3 for i in range(2000) ]

print(timestring(estimate_scan_length(globalparams, seq)*len(fields)))

with tnmr_scan(): # Enters a mode of manual file control. Values will now be written into a single file until the context is lost
    for field in fields:
        maw(se_mf, field) # assuming se_mf controls the reader's external field strength (PPMS, etc.)
        print_sequence(seq)
    
        # Acquire data
        scan_sequence(nmr_daq_scout, seq) # gather the data
