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

import time
import math
from datetime import datetime
import traceback

from nicos import session
from nicos.core.data import DataManager
from nicos.core.data.dataset import PointDataset, ScanDataset
import nicos.core.constants as consts
from nicos.commands import helparglist, usercommand
from nicos.commands.basic import sleep as nicossleep
from nicos.commands.device import maw
from nicos.utils import createThread

TNMR_CURRENTLY_SCANNING = None
TNMR_CURRENT_POINT = 0

TNMR_MODULE_NAME = 'se_tnmr_otf_module'

@usercommand
@helparglist('pulse width (us), pulse height (a.u.), delay time (us), phase cycle (str,  e.g., "0 1 2 3")')
def generate_pulse(pw, ph, dt, pc):
    """
    Generates the necessary dictionary for adding a pulse to the NMR pulse sequence, to be fed to TNMR via the 'go' command.
    Example:

    p_180 = generate_pulse(5,   40, 1,  '0 0 2 2')
    p_90  = generate_pulse(2.5, 40, 50, '0 0 0 0')
    TNMR_MODULE_NAME.sequence_data = [ p_180, p_90, p_180 ]
    TNMR_MODULE_NAME.compile_and_run()
    """
    d = { 'pulse_width': pw, 'pulse_height': ph, 'delay_time': dt, 'phase_cycle': pc }
    
    return d
    

@usercommand
@helparglist('a pulse sequence to be copied and altered, pulse(s) to be scanned (zero-indexed) (in the case of multiple, all will scan concurrently), variable name (i.e., "pulse_width", "pulse_height", "delay_time", or "phase_cycle"), list of values')
def generate_sequences(base_sequence, pulse_indices, var_name, vals):
    try:
        pulse_indices = list(pulse_indices) # convert to list if tuple, single element, etc.. This is so we can just treat it homogeneously throughout the function
    except:
        try:
            pulse_indices = [ pulse_indices ]
        except:
            raise TypeError

    ret = []
    
    for v in vals:
        temp_seq = []
        for i in range(len(base_sequence)): # per-pulse
            temp_seq += [base_sequence[i].copy()]
    
            if(i in pulse_indices):
                temp_seq[i][var_name] = v
        ret += [temp_seq]

    return ret

@usercommand
@helparglist('start time (us), end time (us), number of points (end inclusive)')
def log_durations(s, e, N):
    equidist = [(math.log(s) + (math.log(e) - math.log(s))*i/(N-1)) for i in range(0, N) ]
    return [ math.exp(a) for a in equidist ]

@usercommand
@helparglist('a pulse sequence to estimate')
def estimate_sequence_length(seq):
    eta = 0.0 # seconds
    tnmr = session.getDevice(TNMR_MODULE_NAME)
    eta += tnmr.acquisition_time * 1e-6
    eta += tnmr.pre_acquisition_time * 1e-6
    eta += tnmr.post_acquisition_time * 1e-3
    for i in seq:
        eta += i['delay_time'] * 1e-6
        eta += i['pulse_width'] * 1e-6
    eta *= tnmr.num_scans
    return eta

@usercommand
@helparglist('a sequence of pulse sequences to estimate')
def estimate_scan_length(scan_seq):
    total_eta = 0.0
    for j in scan_seq:
        total_eta += estimate_sequence_length(j)
    return total_eta        

@usercommand
@helparglist('seconds')
def timestring(seconds):
    hours = int(seconds // 3600)
    minutes = int(seconds // 60)

    if(seconds > 3600):
        etastr = f'{hours}h{minutes - hours*60}m'
    elif(seconds > 60):
        etastr = f'{minutes}m{int(seconds) - minutes*60}s'
    elif(seconds > 1):
        etastr = f'{seconds:.1f}s'
    elif(seconds > 1e-3):
        etastr = f'{seconds*1e3:.1f}ms'
    elif(seconds > 1e-6):
        etastr = f'{seconds*1e6:.1f}us'
    elif(seconds > 1e-9):
        etastr = f'{seconds*1e9:.1f}ns'
    
    endtime = time.time() + seconds
    enddatetime = datetime.fromtimestamp(endtime)
    etastr += f' ({enddatetime})'
        
    return etastr

@usercommand
@helparglist('a pulse sequence to display')
def print_sequence(seq):
    session.log.info('------------------------')
    session.log.info('PW   |PH   |DT   |PC')
    for i in seq:
        delay_time = 0
        try:
            delay_time = i['delay_time']
        except:
            delay_time = i['relaxation_time'] # legacy
        
        session.log.info(f'{i["pulse_width"]:<5}|{i["pulse_height"]:<5}|{delay_time:<5}|{i["phase_cycle"]}')
    session.log.info('------------------------')
    session.log.info(f'ETA: {timestring(estimate_sequence_length(seq))}')
    session.log.info('------------------------')

@usercommand
@helparglist('the reference name of the tnmr module, a pulse sequence to scan')
def scan_sequence(dev, seq):
    scan_sequences(dev, [seq])

@usercommand
def begin_tnmr_scan(soft=False):
    global TNMR_CURRENTLY_SCANNING
    global TNMR_CURRENT_POINT
    
    if not(soft):
        finish_tnmr_scan()
    if(TNMR_CURRENTLY_SCANNING is None):
        dm = DataManager()
        db = dm.beginScan()
        TNMR_CURRENTLY_SCANNING = dm
        TNMR_CURRENT_POINT = 0
    return TNMR_CURRENTLY_SCANNING
  
@usercommand
def finish_tnmr_scan():
    global TNMR_CURRENTLY_SCANNING
    if not(TNMR_CURRENTLY_SCANNING is None):
        TNMR_CURRENTLY_SCANNING.finishScan()
        TNMR_CURRENTLY_SCANNING = None

@usercommand
def get_tnmr_params():
    tnmr = session.getDevice(TNMR_MODULE_NAME)
    params_dictionary = {
                          'acquisition_time':      tnmr.acquisition_time,
                          'ringdown_time':         tnmr.ringdown_time,
                          'pre_acquisition_time':  tnmr.pre_acquisition_time,
                          'post_acquisition_time': tnmr.post_acquisition_time,
                          'acq_phase_cycle':       tnmr.acq_phase_cycle,
                          'obs_freq':              tnmr.obs_freq,
                          'num_scans':             tnmr.num_scans,
                        }
    return params_dictionary

@usercommand
@helparglist('the reference name of the tnmr module, a list of pulse sequences to scan over, a list of (name, lambda) tuples to call (no argument) to be added to the save file')
def scan_sequences(dev, sequence_list, additional_saving_lambdas=[]):
    def do_scan(sequence_list):
        global TNMR_CURRENTLY_SCANNING
        global TNMR_CURRENT_POINT
        st = time.time()
        try:
            tnmr = session.getDevice(dev)
            started_scan = (TNMR_CURRENTLY_SCANNING is None) # are we starting the scan or did someone else?
            dm = begin_tnmr_scan(True)
            st = time.time()
            for i in range(len(sequence_list)):
                pb = dm.beginPoint()
                session.log.info(f'Scan: {i+1}/{len(sequence_list)}' + (f' ({float(i)/float(len(sequence_list)-1)*100:.0f}%)' if len(sequence_list) > 1 else ''))
                total_eta = 0.0
                for j in sequence_list[i:]:
                    total_eta += estimate_sequence_length(j)
                session.log.info(f'ETA: {timestring(total_eta)}')
                
                tnmr.sequence_data = sequence_list[i]
                nicossleep(1.0)
                tnmr.compile_and_run(True)
                nicossleep(estimate_sequence_length(sequence_list[i]) * 0.9)
                while(tnmr.status()[0] > 200 and tnmr.status()[0] < 300):
                    nicossleep(1.0)
                nicossleep(1.0)
                data = tnmr.read()
                nicossleep(1.0)
                sequence_dictionary = {}
                for j in range(len(sequence_list[i])):
                    sequence_dictionary[j] = sequence_list[i][j]
                current_time = time.time()
                full_value_dict = {
                  'signal:tnmr_reals':               (current_time, data['reals']), 
                  'auxiliary_signals:tnmr_imags':    (current_time, data['imags']),  
                  'axes:tnmr_times':                 (current_time, data['t']),
                  'tnmr_sequence':                   (current_time, sequence_dictionary),
                  'tnmr_params':                     (current_time, get_tnmr_params()),
                  'metadata/nucleus':                (current_time, tnmr.nucleus),
                  'metadata/sample':                 (current_time, tnmr.sample),
                  'metadata/comments':               (current_time, tnmr.comments),
                }
                for i in additional_saving_lambdas:
                    try:
                        full_value_dict['environment/'+i[0]] = (current_time, i[1]())
                    except:
                        session.log.warning(f'Could not acquire parameter `{i[0]}` for writing into NeXus file. Traceback: \n{traceback.format_exc()}')
                        pass
                
                dm.putValues(full_value_dict)
                TNMR_CURRENT_POINT += 1
                    
                dm.finishPoint()
            if(started_scan):
                finish_tnmr_scan()
        except Exception as e:
            import traceback
            session.log.warning(traceback.format_exc())
            finish_tnmr_scan()
        et = time.time()
        dt = et - st
        session.log.info(f'Finished. Took {timestring(dt)}.')
        
    do_scan(sequence_list)
