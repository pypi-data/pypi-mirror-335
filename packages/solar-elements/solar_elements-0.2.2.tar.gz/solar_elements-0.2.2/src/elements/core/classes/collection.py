from collections import defaultdict
from collections.abc import Iterable
from math import ceil

from .event import Event, hydrate
from .solar_path import SolarPath
from .timestamp import Timestamp

from .config import config

# ### Collections ###

# A Collection is a wrapper used to contain a list of events
# over one or more subspaces

# Collections are useful for building common spaces like
# newsfeeds, as well as collecting groups of comments.

# A collection has index maps called "pointers" and "buckets",
# where pointers are 1:1 and buckets are 1:* - these maps allow
# us to look up data from the collection in O(1) time.

class Collection:
    
    # Pointers are a 1:1 mapping of 'lookup value' to 'index' within
    # the content list
    pointers = {
        'name': lambda e: e.name
    }

    # Buckets are a 1:* mapping of 'lookup value' to a list of
    # Objects. Bucket functions must return either a hashable
    # object or a list of hashable objects.
    buckets = {
        'pubkey': lambda e: str(e.pubkey),
        'e': lambda e: sum(e.tags.getall('e'), []),
        'kind': lambda e: e.kind
    }

    # The number of results to render per-page
    page_size = 6
    
    @staticmethod
    def sorting_key(event):
        return event.created_at
    
    # A collection is initialized by passing it a list of events
    def __init__(self, events=[]):

        # Mark when the directory was last updated, so that
        # we can query updates since then.
        self.ts = Timestamp() 

        # Record the subspaces that are being used to query the
        # events. A subspace of '*' means "all subspaces in the
        # given namespace.

        # Make an empty map for each index in the class
        self.maps = {}
        for key in self.pointers:
            self.maps[key] = {}

        for key in self.buckets:
            self.maps[key] = defaultdict(list)

        # We sort the collection by the time each
        # Event was created, most recent last.
        self.events = []

        events.sort(key=self.sorting_key)

        for event in events:
            self.add(event)

    # There are a few bits of book-keeping to be done when we add
    # an event to the collection. We need to index it with the available
    # pointers and buckets, and we also need the event to know it's part
    # of a collection before adding it to the events list.
    def add(self, event):

        event.collection = self
        # Each index in pointers is a keypair
        # of a "map_name" as the key, and a
        # function for determining the label
        # used to index the content.
        for key, f in self.pointers.items():
            value = f(event)
            if value:
                self.maps[key][value] = event

        for key, f in self.buckets.items():
            values = f(event)

            # Have a a value that isn't in the bucket? add it!
            # Make sure we have a list to iterate through...
            if not isinstance(values, list):
                values = [values]
                
            for value in values:
                if value is not None and event not in self.maps[key][value]:
                    self.maps[key][value].append(event)

        self.events.append(event)

    def remove(self, event):
        for key, f in self.pointers.items():
            value = f(event)
            if value:
                del self.maps[key][value]

        for key, f in self.buckets.items():
            values = f(event)

            # Have a a value that isn't in the bucket? add it!
            # Make sure we have a list to iterate through...
            if not isinstance(values, list):
                values = [values]
                
            for value in values:
                if value is not None and event in self.maps[key][value]:
                    self.maps[key][value].remove(event)

        self.events.remove(event)


    def find(self, key, index='name'):
        return self.maps[index].get(key)

    def __iter__(self):
        return CollectionIterator(self)

    def __len__(self):
        return len(self.events)

    def __bool__(self):
        return len(self.events) > 0

    @classmethod
    def load(cls, path : SolarPath, **kwargs):
        subspaces = kwargs.get('subspaces')

        collection = cls()

        if subspaces == ['*']:
            ns = SolarPath('.', namespace=namespace, subspace=None)
            subspaces = [space.name for space in ns.dirs]
        elif subspaces == None:
            subspaces = [path.subspace]

        for subspace in subspaces:
            path.subspace = subspace
            for event_path in path.children:
                data = event_path.read()
                event = hydrate(data)
                if event:
                    collection.add(event)

        return collection

    def page(self, index, **kwargs):
        size = kwargs.get('page_size', self.page_size)
        page_start = index * size
        page_end = (index+1) * size

        latest = sorted(self.events)
        return latest[page_start:page_end]

    @property
    def pages(self):
        return list(range(ceil(len(self.events) / self.page_size)))

    def flatten(self, *args):
        return { 'content': [c.flatten() for c in self.events if c is not None] }

class CollectionIterator:
    def __init__(self, collection):
        self.events = collection.events
        self.counter = 0

    def __iter__(self):
        return self

    def __next__(self):
        try:
            next_value = None
            # find next non-null value
            while next_value is None:
                count = self.counter
                self.counter += 1
                next_value = self.events[count]
            return next_value
        except IndexError:
            raise StopIteration

