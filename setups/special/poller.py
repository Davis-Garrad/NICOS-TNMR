description = 'setup for the poller'
group = 'special'
import os

sysconfig = dict(
    # use only 'localhost' if the cache is really running on the same machine,
    # otherwise use the official computer name
    cache='localhost:%s' % os.environ['NICOS_CACHE_PORT']
)

devices = dict(
    Poller=device('nicos.services.poller.Poller',
                  autosetup=True,
                  poll=['system', 'setup'],
                  alwayspoll=[],
                  # setups that should be polled regardless if loaded
                  neverpoll=['frappy_main', 'frappy_stick', 'frappy_addons'],
                  # setups that should not be polled even if loaded
                  blacklist=[],  # DEVICES that should never be polled
                  # (usually detectors or devices that have problems
                  # with concurrent access from processes)
                  loglevel='info'
                  ),
)
