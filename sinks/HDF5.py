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

from nicos.devices.datasinks import FileSink
from nicos.core.data.sink import DataSinkHandler
from nicos.core import Override, Param
from nicos.core.constants import POINT, SCAN, SUBSCAN
from nicos import session

import h5py as hdf
import numpy as np
import time

class HDF5ScanfileSinkHandler(DataSinkHandler):
    def __init__(self, sink, dataset, detector):
        super().__init__(sink, dataset, detector)
        self._file = None
        self._fname = None
        self._template = sink.filenametemplate

    def prepare(self):
        self.manager.assignCounter(self.dataset)
        fp = self.manager.createDataFile(self.dataset, self._template,
                                         self.sink.subdir,
                                         filemode=self.sink.filemode)
        self._fname = fp.shortpath
        self._filepath = fp.filepath
        self._file = hdf.File(fp.filepath, 'w', userblock_size=512) # make sure we can open it (and truncate)
        self._file.close()

    def begin(self):
        with hdf.File(self._filepath, 'a') as file:
            g = file.require_group('/metadata/')
            d = g.create_dataset('date', data=f'{time.time()} ({time.gmtime()})', dtype=hdf.string_dtype(length=128))
            lc = g.create_dataset('local_contact', data=f'{session.experiment.localcontact}', dtype=hdf.string_dtype(length=128))
            p = g.create_dataset('proposal', data=f'{session.experiment.proposal}', dtype=hdf.string_dtype(length=128))
            u = g.create_dataset('users', data=f'{session.experiment.users}', dtype=hdf.string_dtype(length=128))
    
    def putMetainfo(self, mi):
        session.log.info('mi')
        session.log.info(str(mi))
    
    def __save_dict(self, d, file, parent_group):
        for key, val in d.items():
            if(type(val) is dict):
                g = parent_group.require_group(str(key))
                self.__save_dict(val, file, g)
            else:
                if(type(val) is str):
                    d = parent_group.create_dataset(str(key), data=val, dtype=hdf.string_dtype(length=len(val) + 16))
                else:
                    d = parent_group.create_dataset(str(key), data=val) 
    
    def putValues(self, vals):
        #session.log.info('vals')
        with hdf.File(self._filepath, 'a') as file:
            for key, val in vals.items():
                g = file.require_group(f'/point{val[0]}/')
                if(type(val[1]) is dict):
                    pg = g.require_group(str(key))
                    self.__save_dict(val[1], file, pg)
                else:
                    d = g.create_dataset(str(key), data=np.array(val[1]))
    
    def putResults(self, quality, results):
        pass
        #session.log.info('HDF putResults is not implemented! Use putResults.')
        
    def addSubset(self, subset):
        pass
        #session.log.info('HDF addSubset is not implemented! Use putValues.')
        
    #def end(self):
    #    pass # nothing afaik needs to be done here.


class HDF5ScanfileSink(FileSink):
    
    handlerclass = HDF5ScanfileSinkHandler
    parameter_overrides = {
        'settypes': Override(default=[SCAN, SUBSCAN]),
        'filenametemplate': Override(default=['%(proposal)s_%(year)04d-%(month)02d-%(day)02d_%(hour)02d-%(minute)02d-%(second)02d.hdf'])
    }