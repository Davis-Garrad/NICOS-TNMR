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

from nicos.nexus.nexussink import NexusTemplateProvider
from nicos.nexus.elements import DetectorDataset

class TNMRTemplateProvider(NexusTemplateProvider):
    def getTemplate(self):
        template = {
            'NeXus_Version': 'nexusformat v0.5.3',
            'instrument': 'TNMR-Scout',
            'owner': DeviceAttribute('tnmr', 'responsible'),
            'entry:NXentry': {
                'data:NXdata': {
                    'values': DeviceDataset('se_tnmr_otf_module'), # defaults to value
                    'sequences': DeviceDataset('se_tnmr_otf_module', parameter='sequence_data'),
                },
                'tnmr:NXinstrument': {},
            }