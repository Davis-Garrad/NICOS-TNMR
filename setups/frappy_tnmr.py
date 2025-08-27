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

from os import environ
description = 'frappy tnmr setup'
group = 'optional'

sysconfig = dict(
    datasinks = [ 'hdf5filesink', ],
)

modules = [ "nicos_sinq.frappy_sinq.devices", "tnmr.commands.tnmr_commands", "tnmr.sinks.HDF5" ]

devices = {
    'se_tnmr':
        device('nicos_sinq.frappy_sinq.devices.FrappyNode',
               description='TNMR SEC node', unit='', async_only=True,
               prefix=environ.get('SE_PREFIX', 'se_'), auto_create=True, service='main',
               uri='tcp://129.129.156.98:5000',
        ),
    'hdf5filesink': 
        device('nicos_sinq.devices.tnmr.HDF5_NEXUS.HDF5ScanfileSink',
            filenametemplate=['file_%(proposal)s_%(month)02d-%(day)02d-%(hour)02d-%(minute)02d-%(second)02d.hdf'],
        ),
    #'nexusfilesink': 
    #    device('nicos.nexus.nexussink.NexusSink',
    #        templateclass='nicos_sinq.devices.tnmr.TNMRNeXus.TNMRTemplateProvider',
    #        filenametemplate=['file_%(proposal)s_%(day)02d-%(hour)02d-%(minute)02d-%(second)02d.nxs'],
    #    ),
}
