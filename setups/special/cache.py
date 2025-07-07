description = 'setup for the cache server'
group = 'special'
import os
insname = os.environ['INSTRUMENT'].rsplit('.')[-1]

devices = dict(
    DB = device('nicos.services.cache.database.FlatfileCacheDatabase',
        description = 'On disk storage for Cache Server',
        storepath = os.path.join(os.environ.get('NICOS_CACHE', 'data'), insname, 'cache'),
        loglevel = 'info',
        makelinks = 'soft',
    ),
    Server=device('nicos.services.cache.server.CacheServer',
                  db='DB',
                  server='localhost:%s' % os.environ['NICOS_CACHE_PORT'],
                  loglevel='info',
                  ),
)
