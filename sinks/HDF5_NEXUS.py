from nicos.devices.datasinks import FileSink
from nicos.core.data.sink import DataSinkHandler
from nicos.core import Override, Param
from nicos.core.constants import POINT, SCAN, SUBSCAN
from nicos import session

import h5py as hdf
import numpy as np
import time
import datetime # For simple ISO8601 usage.

class HDF5ScanfileSinkHandler(DataSinkHandler):
    def __init__(self, sink, dataset, detector):
        super().__init__(sink, dataset, detector)
        self._file = []
        self._fname = None
        self._template = sink.filenametemplate
        hdf.get_config().track_order = True # keeps the order that objects are added in.

    def prepare(self):
        self.manager.assignCounter(self.dataset)
        
        self._fname, self._filepaths = self.manager.getFilenames(self.dataset, self._template, self.sink.subdir)
        
        for f in self._filepaths:
            self._file += [ hdf.File(f, 'a', userblock_size=512) ] # make sure we can open it
            self._file[-1].close()

    def begin(self):
        for f in self._filepaths:
            with hdf.File(f, 'a') as file:
                file.attrs['version'] = '100' # reserved for non-backwards-compatible changes!
                g = file.require_group('/metadata/')
                d = g.create_dataset('date', data=f'{time.time()} ({time.gmtime()})', dtype=hdf.string_dtype(length=128))
                lc = g.create_dataset('local_contact', data=f'{session.experiment.localcontact}', dtype=hdf.string_dtype(length=128))
                p = g.create_dataset('proposal', data=f'{session.experiment.proposal}', dtype=hdf.string_dtype(length=128))
                u = g.create_dataset('users', data=f'{session.experiment.users}', dtype=hdf.string_dtype(length=128))
    
    def putMetainfo(self, mi):
        session.log.info('mi')
        session.log.info(str(mi))
        
    def __save_val(self, v, key, file, parent_group):
        ret = None
        if(isinstance(v, dict)):
            pg = parent_group.require_group(str(key))
            self.__save_dict(v, file, pg)
            ret = pg
        elif(isinstance(v, list) or isinstance(v, np.ndarray)):
            ret = parent_group.create_dataset(str(key), data=np.array(v))
        elif(isinstance(v, str)):
            ret = parent_group.create_dataset(str(key), data=v, dtype=hdf.string_dtype(length=len(v) + 16))
        else:
            ret = parent_group.create_dataset(str(key), data=np.array([v]))
        return ret
    
    def __save_dict(self, d, file, parent_group):
        for key, val in d.items():
            self.__save_val(val, key, file, parent_group)
    
    def putValues(self, vals):
        def validate_and_add(key_to_check, name, typ, group):
            tags = key_to_check.split(':')
            k = tags[-1]
            if(name in tags[:-1] and ':' in key_to_check):
                if(typ == 'list'):
                    if(name in d.attrs.keys()):
                        d.attrs[name] += [ k ]
                    else:
                        d.attrs[name] = [ k ]
                elif(typ == 'single'):
                    d.attrs[name] = k
            return k
            
        def write_val(key, val, d):
            validate_and_add(key, 'axes', 'list', d)
            validate_and_add(key, 'signal', 'single', d)
            key = validate_and_add(key, 'auxiliary_signals', 'list', d)
            newg = self.__save_val(val, key, file, d)
            
        for f in self._filepaths:
            with hdf.File(f, 'a') as file:
                entries = list(file.keys())
                tmp = []
                for i in entries:
                    if 'entry' in i:
                        tmp += [i]
                entries = tmp
                entries = [ int(i[5:]) for i in entries ]
                if(len(entries) == 0):
                    last_entry = 0
                else:
                    last_entry = max(entries)
                #print('last', last_entry)
                new_entry = last_entry + 1
                
                g = file.require_group(f'entry{new_entry}')
                g.attrs['NX_class'] = 'NXentry'
                g.attrs['signal'] = 'nmr_data'
                
                timestamp_str = str(datetime.datetime.now().astimezone().isoformat()) # NX_DATE_TIME, AKA ISO8601 date/time stamp
                timestamp = g.create_dataset('end_time', data=timestamp_str, dtype=hdf.string_dtype(length=len(timestamp_str)))
                
                d = g.require_group(f'nmr_data')
                d.attrs['NX_class'] = 'NXdata'
                
                dets = g.require_group(f'detectors')
                dets.attrs['NX_class'] = 'NXdata'
                
                env = g.require_group(f'environment')
                env.attrs['NX_class'] = 'NXdata'
                
                metadata_grp = file.require_group('/metadata/')
                
                for key, val in vals.items():
                    grp = d
                    K = key
                    if('environment/' in key):
                        K = key[len('environment/'):]
                        grp = env
                    elif('metadata/' in key) and (new_entry == 1):
                        K = key[len('metadata/'):]
                        grp = metadata_grp
                    write_val(K, val[1], grp)
                
                for key in session.experiment.detlist:
                    write_val(key, session.getDevice(key).read(), dets)
                
                for key in session.experiment.envlist:
                    write_val(key, session.getDevice(key).read(), env)
    
    def putResults(self, quality, results):
        pass
        #session.log.info('HDF_NeXus putResults is not implemented! Use putResults.')
        
    def addSubset(self, subset):
        pass
        #session.log.info('HDF_NeXus addSubset is not implemented! Use putValues.')
        
    #def end(self):
    #    pass # nothing afaik needs to be done here.


class HDF5ScanfileSink(FileSink):
    
    handlerclass = HDF5ScanfileSinkHandler
    parameter_overrides = {
        'settypes': Override(default=[SCAN, SUBSCAN]),
        'filenametemplate': Override(default=['%(proposal)s_%(year)04d-%(month)02d-%(day)02d_%(hour)02d-%(minute)02d-%(second)02d.hdf'])
    }