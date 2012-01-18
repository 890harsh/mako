"""Provide a :class:`.CacheImpl` for the Beaker caching system."""

from mako import exceptions

from mako.cache import CacheImpl

_beaker_cache = None
class BeakerCacheImpl(CacheImpl):
    """A :class:`.CacheImpl` provided for the Beaker caching system.
    
    This plugin is used by default, based on the default
    value of ``'beaker'`` for the ``cache_impl`` parameter of the
    :class:`.Template` or :class:`.TemplateLookup` classes.
    
    """

    def __init__(self, cache):
        global _beaker_cache
        if _beaker_cache is None:
            try:
                from beaker import cache as beaker_cache
            except ImportError, e:
                raise exceptions.RuntimeException(
                            "the Beaker package is required to use cache "
                            "functionality.")

            _beaker_cache = beaker_cache.CacheManager()
        super(BeakerCacheImpl, self).__init__(cache)

    def _get_cache(self, **kw):
        expiretime = kw.pop('timeout', None)
        if 'dir' in kw:
            kw['data_dir'] = kw.pop('dir')
        elif self.cache.template.module_directory:
            kw['data_dir'] = self.cache.template.module_directory

        if kw.get('type') == 'memcached':
            kw['type'] = 'ext:memcached'

        return _beaker_cache.get_cache(self.cache.id, **kw), \
                    {'expiretime':expiretime, 'starttime':self.cache.starttime}

    def get_or_create(self, key, creation_function, **kw):
        cache, kw = self._get_cache(**kw)
        return cache.get(key, createfunc=creation_function, **kw)

    def put(self, key, value, **kw):
        cache, kw = self._get_cache(**kw)
        cache.put(key, value, **kw)
 
    def get(self, key, **kw):
        cache, kw = self._get_cache(**kw)
        return cache.get(key, **kw)
 
    def invalidate(self, key, **kw):
        cache, kw = self._get_cache(**kw)
        cache.remove_value(key, **kw)
