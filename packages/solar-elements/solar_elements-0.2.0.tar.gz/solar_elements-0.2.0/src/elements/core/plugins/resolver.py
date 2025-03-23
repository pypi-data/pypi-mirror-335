import inspect
from elements import NostrDatabase, SolarPath, request

'''
This plugin allows for the automatic resolution of a request path
to one or more nostr events.

Once the Plugin is installed, routes can accept a keyword parameter
('event' by default) to resolve that route via SolarPath filtering.
'''

class Resolver:
    name = 'nostr_database'
    api = 2

    def __init__(self, relay_url, keyword="events"):
        self.db = NostrDatabase(relay_url)
        self.keyword = keyword

    def setup(self, app):
        # connect to relay
        pass

    def apply(self, callback, route):
        conf = route.config.get('nostr_database') or {}
        subspaces = route.config.get('subspaces')
        keyword = conf.get('keyword', self.keyword)

        args = inspect.getfullargspec(route.callback)[0]
        if self.keyword not in args:
            return callback

        def wrapper(*args, **kwargs):
            path = SolarPath(request.path.strip('/'))
            results = self.db.resolve(path, subspaces=subspaces)
            kwargs[keyword] = results
            result = callback(*args, **kwargs)
            return result

        return wrapper

    def close(self):
        # disconnect from relay
        pass
