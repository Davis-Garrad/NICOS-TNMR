from nicos.devices.datasinks import FileSink
from nicos.core.data.sink import DataSinkHandler
from nicos.core import Override, Param
from nicos.core.constants import POINT, SCAN, SUBSCAN
from nicos import session

import h5py as hdf
import numpy as np
import time
import datetime # For simple ISO8601 usage.

# A couple specific NeXus functionalities
def initialise_nexus_entry(file, index, timestamp):
    '''file should be an HDF file object, which should be _open_. Timestamp should be an ISO8061 string, indicating the start of this entry, no longer than 48 characters.'''
    entry_group = file.require_group(f'entry{index}')
    entry_group.attrs['NX_class'] = 'NXentry'
    entry_group.attrs['default'] = 'nmr_data'

    d = entry_group.require_group(f'nmr_data')
    d.attrs['NX_class'] = 'NXdata'

    dets = entry_group.require_group(f'detectors')
    dets.attrs['NX_class'] = 'NXdata'

    env = entry_group.require_group(f'environment')
    env.attrs['NX_class'] = 'NXdata'

    start_timestamp = entry_group.create_dataset('start_time', data=timestamp, dtype=hdf.string_dtype(length=48), shape=1)
    end_timestamp = entry_group.create_dataset('end_time', data=timestamp, dtype=hdf.string_dtype(length=48), shape=1)

    return entry_group

            
def choose_entry_from_datetime(file, datetime_iso):
    '''file should be an HDF file object, which should be _open_.'''
    entries = list(file.keys())
    datetimes = []
    tmp = []
    
    # get groups which actually start with 'entry'
    for i in entries:
        if 'entry' in i:
            tmp += [i]
            starttime_str = np.array(file[i]['start_time'], 'S').tobytes().decode('utf-8')
            if(datetime_iso == starttime_str[:len(datetime_iso)]):
                return file[i]
    entries = tmp
    
    # Chop off the 'entry' part
    entry_indices = [ int(i[5:]) for i in entries ]
    
    # ... And get the last index.
    if(len(entry_indices) == 0):
        new_entry_index = 1
    else:
        new_entry_index = max(entry_indices) + 1
    
    entry_group = initialise_nexus_entry(file, new_entry_index, datetime_iso)
    
    return entry_group

# The actual workhorse
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
                try:
                    d = g.create_dataset('date', data=f'{time.time()} ({time.gmtime()})', dtype=hdf.string_dtype(length=128))
                    lc = g.create_dataset('local_contact', data=f'{session.experiment.localcontact}', dtype=hdf.string_dtype(length=128))
                    p = g.create_dataset('proposal', data=f'{session.experiment.proposal}', dtype=hdf.string_dtype(length=128))
                    u = g.create_dataset('users', data=f'{session.experiment.users}', dtype=hdf.string_dtype(length=128))
                except:
                    pass
    
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
            varr = np.array(v)
            ret = parent_group.require_dataset(str(key), data=varr, shape=varr.shape, dtype=varr.dtype, exact=False)
            ret[:] = varr
        elif(isinstance(v, str)):
            ret = parent_group.require_dataset(str(key), data=v, shape=1, dtype=hdf.string_dtype(length=len(v) + 16), exact=False)
            ret[0] = v
        else:
            varr = np.array([v])
            ret = parent_group.require_dataset(str(key), data=varr, shape=varr.shape, dtype=varr.dtype, exact=False)
            ret[:] = varr
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
            
        def write_time_val_pair(file, key, val_pair):
            '''file should be an _open_ HDF file object. Writes a value to the appropriate dataset (based on key) and entry (based on timestamp in val_pair[0])'''
            # get start datetime to find the correct entry:
            timestamp = val_pair[0]
            value = val_pair[1]
            start_dt = datetime.datetime.fromtimestamp(timestamp)
            start_dt_iso = str(start_dt.astimezone().isoformat())
            
            # Get the correct entry (entryX, where X is an integer). Creates a new entry if necessary
            g = choose_entry_from_datetime(file, start_dt_iso)
            # update end time
            et_dataset = g['end_time']
            et_dataset[0] = str(datetime.datetime.now().astimezone().isoformat())
            
            # choose the appropriate group within the entry
            if(key in session.experiment.detlist):
                group_key = 'detectors'
            elif(key in session.experiment.envlist) or ('environment/' in key):
                group_key = 'environment'
            elif('metadata/' in key):
                group_key = 'metadata'
            else:
                group_key = 'nmr_data'
            data_group = g.require_group(group_key)
            
            # remove any special characters from the key
            formatted_key = key
            tagsplit = formatted_key.split(':')
            tags = ':'.join(tagsplit[:-1]) # take everything before the last ':', these are used to signal special 'tags' on data, such as signal, axes, etc.
            formatted_key = tagsplit[-1]
            # remove the location specifier before the first '/' (multiple locations are not supported)
            if('/' in formatted_key):
                formatted_key = '/'.join(formatted_key.split('/')[1:])
            formatted_key = tags + ':' + formatted_key # recombine...
            
            #... for write_val to do its job
            write_val(formatted_key, value, data_group)
            
        for f in self._filepaths:
            with hdf.File(f, 'a') as file:
                dummytime = 0
                for key, val in vals.items():
                    write_time_val_pair(file, key, val)
                    dummytime = val[0]
                
                for key in session.experiment.detlist + session.experiment.envlist:
                    unread = True
                    v = 0
                    retries = 0
                    while(unread):
                        try:
                            v = session.getDevice(key).read()
                            unread = False
                        except:
                            retries += 1
                            if(retries > 10):
                                session.log.info(f'Failed to read {key}. Setting zero.')
                                v = 0
                                break
                            session.log.info(f'Trying to read {key} again')
                            pass
                    if(dummytime == 0):
                        dummytime = time.time()
                    val = (dummytime, v)
                    write_time_val_pair(file, key, val)
                
    
    def putResults(self, quality, results):
        pass
        #session.log.info('HDF_NeXus putResults is not implemented! Use putValues.')
        
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