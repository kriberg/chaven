from django.core.cache import cache
import eveapi


eveapi.set_user_agent('chaven//vittoros@#eve-dev')


class DjangoCache(object):
    def retrieve(self, host, path, params):
        key = hash((host, path, frozenset(params.items())))

        cached_data = cache.get(key, None)

        return cached_data

    def store(self, host, path, params, doc, obj):
        key = hash((host, path, frozenset(params.items())))

        cache_time_seconds = obj.cachedUntil - obj.currentTime

        if cache_time_seconds and cache_time_seconds > 0:
            cache.set(key, doc, timeout=cache_time_seconds)

def get_api():
    return eveapi.EVEAPIConnection(cacheHandler=DjangoCache())
