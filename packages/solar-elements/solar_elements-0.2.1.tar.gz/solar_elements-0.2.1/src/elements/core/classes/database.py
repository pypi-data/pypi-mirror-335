import json
import inspect
from .event import Event, hydrate
from .collection import Collection
from .account import Account
from .solar_path import SolarPath
from .config import config


from websockets.sync.client import connect
from websockets.exceptions import ConnectionClosed

'''
A Database is a system for storing data. Solar uses
a nostr relay as its main database for social data.

This class allows us to interface with the database
and instantiate Events and Collections by sending
requests and data over a websocket connection.
'''

class NostrDatabase:
    name = 'nostr_database'
    api = 2

    def __init__(self, relay_url=None):
        if relay_url is None:
            relay_url = config.get('solar.database')

        self.relay_url = relay_url
        self.websocket = connect(relay_url)

    def health_check(self):
        try:
            pong = self.websocket.ping()
            if pong.wait(timeout=1) is False:
                self.websocket = connect(self.relay_url)
        except ConnectionClosed:
            self.websocket = connect(self.relay_url)

    @staticmethod
    def build_filter(path : SolarPath, **kwargs):

        # Subspaces is a kwarg that can be used
        # to build a filter that queries a list
        # of accounts by name (or ["*"] for all
        # accounts in the namespace)
        subspaces = kwargs.get('subspaces')

        if subspaces == ['*']:
            ns = SolarPath('.', namespace=path.namespace, subspace=None)
            subspaces = [space.name for space in ns.dirs]
        elif subspaces == None:
            subspaces = [path.subspace]

        query_filter = {}

        pubkeys = []

        if subspaces == ["public"]:
            # "public" is the shortcut for skipping the 'authors'
            # field and querying any notes from the relay.
            # Not a common use-case within the SOLAR system,
            # when use is focused around community members.
            pass

        else:
            for name in subspaces:
                if name is not None:
                    account = Account(name)
                    if account:
                        pubkeys.append(account.pubkey)

            query_filter['authors'] = pubkeys
    
        parts = path.parts
    
        if len(parts) > 0:
            kind_name = parts[0]
    
            for kind in config['kinds']:
                cls = config['kinds'][kind]
                if cls.directory == kind_name:
                    query_filter['kinds'] = [cls.kind]
                    break
    
        if len(parts) == 2:
            identifier = parts[1]
            query_filter['ids'] = [identifier] 
    
        if len(parts) == 3:
            identifier = parts[1]
            tag = parts[2]
            query_filter[f'#{tag}'] = [identifier]
    
        return query_filter

    def query(self, query_filter, query_id="solar"):
        self.health_check()
        nostr_query = json.dumps(["REQ", query_id, query_filter])
        self.websocket.send(nostr_query)

        results = []

        recv = json.loads(self.websocket.recv())
        if recv[0] == 'NOTICE':
            raise ValueError(recv)

        while recv[0] != "EOSE":
            if recv[0] == "EVENT":
                data = recv[2]
                event = hydrate(data)
                results.append(event)

            recv = json.loads(self.websocket.recv())

        # close the query
        close_query = json.dumps(["CLOSE", query_id])
        self.websocket.send(close_query)

        return Collection(results)

    def get(self, search):

        # Address query
        if ":" in search:
            [kind, pubkey, d] = search.split(':')
            q = { 'kinds': [int(kind)], 'authors': [pubkey] }

            if d:
                q['#d'] = [d]

            res = self.query(q)

        # ID query
        else:
            res = self.query({ 'ids': [search] })

        if len(res.events) > 0:
            return res.events[0]
        else:
            return None


    def resolve(self, path: SolarPath, **kwargs):
        nostr_filter = self.build_filter(path, **kwargs)
        return self.query(nostr_filter)

    def publish(self, event: Event):
        self.health_check()
        data = event.flatten(stringify=True)
        nostr_query = json.dumps(["EVENT", data])
        self.websocket.send(nostr_query)

        recv = json.loads(self.websocket.recv())

        return recv

    def refresh(self, collection):
        # I don't need this yet, but maybe it will be used
        # to make sure data in a collection is up-to-date
        # by querying with the "since" parameter.
        pass 
        
