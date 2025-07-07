# basic frappy setup

description = 'system setup'
group = 'lowlevel'
import os
insname = os.environ['INSTRUMENT'].split('.')[-1]

sysconfig = dict(
    cache = 'localhost:%s' % os.environ['NICOS_CACHE_PORT'],
    instrument = 'instrument',
    experiment = 'Exp',
    datasinks = ['conssink', 'dmnsink' ],
    notifiers = [],
)

modules = ['nicos.commands.standard', 'nicos_sinq.frappy_sinq.commands' ]

devices = dict(
    instrument = device('nicos.devices.instrument.Instrument',
        description = 'lab instrument %s' % insname,
        instrument = insname,
        responsible = 'whoever',
        website = '',
        operators = ['whoever'],
        facility = 'wherever',
    ),
    Sample = device('nicos.devices.sample.Sample',
        description = 'sample object',
    ),
    Exp = device('nicos.devices.experiment.Experiment',
        description = 'experiment object',
        dataroot = os.path.join(os.environ['NICOS_DATA'], insname),
        # proposalpath = 'data/%s' % insname,
        sendmail = True,
        serviceexp = 'service',
        sample = 'Sample',
        reporttemplate = '',
    ),
    conssink = device('nicos.devices.datasinks.ConsoleScanSink'),
    dmnsink = device('nicos.devices.datasinks.DaemonSink'),
    Space = device('nicos.devices.generic.FreeSpace',
        description = 'The amount of free space for storing data',
        warnlimits = (5., None),
        path = None,
        minfree = 5,
    ),
    LogSpace = device('nicos.devices.generic.FreeSpace',
        description = 'Space on log drive',
        path = os.path.join(os.environ['NICOS_LOG'], insname),
        warnlimits = (.5, None),
        minfree = 0.5,
        lowlevel = True,
    ),
)

startupcode = '''
from nicos.core import SIMULATION
if not Exp.proposal and Exp._mode != SIMULATION:
    try:
        SetMode('master')
    except Exception:
        pass
    else:
        NewExperiment(0, 'demo experiment',
                      localcontact='Nico Suser <nico.suser@psi.ch>')
        AddUser('Paul Scherrer <paul.scherrer@psi.ch')
        NewSample('ExSample')
'''
