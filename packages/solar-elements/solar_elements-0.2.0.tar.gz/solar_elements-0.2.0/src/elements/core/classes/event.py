from collections import defaultdict
from collections.abc import Iterable
from math import ceil
import json
import glob
#from elements.core.storage import SolarPath, save_file, load_file, delete, identify
from elements.core.libs.utilities import identify
from elements.core.libs.musig import schnorr_verify
from .account import Account
from .solar_path import SolarPath

from .timestamp import Timestamp
from .tagdict import TagDict

from .config import config

'''

Event is the base class that all other components in the Solar System
are based on. It implements the standard constructor, along with basic
functions for event signing and more.

'''

# ### Event ###

# When any Event is created, it is passed a dictionary of values
# that define the object. This dictionary may or may not contain
# entries for the five basic values (content, author, created_at, kind,
# tags) along with any other number of tagged values which indicate extra
# details about the Event.

# ### Content ###
# The 'content' of an event is the basis of what it displays on the page.
# It can either be a plaintext value (e.g. Comment) or a dictionary (e.g.
# Profile). In some cases (e.g Post), the plaintext value is expected to 
# be processed before being sent to the templating engine.

# Content _must_ be a json serializable value by default.

# ### Pubkey ###
# The 'pubkey' of an event is a unique string identifier for the member 
# responsible for creating the event. When an event is loaded from 
# data, most constructors will look up the pubkey from Members and 
# attach it to the event as an attribute.

# ### Created At ###
# The created_at value is a timestamp of the exact moment an Event
# is (or was) instanced. This value is passed into a Timestamp and 
# saved to the event as 'ts' so that it can be operated on more easily.

# ### Kind ###
# The kind of an event is its reference in the nostr ecosystem. A goal
# of Solar is to maintain full cross-compatibility with nostr, and every
# event with a kind between 0 and 65535 can be shared over relays.

class Event:
    kind = -1
    directory = 'events'
    content_dict = False

    # File name is used for non-addressable, replaceable events
    # (e.g. Profile, ContactList). These events will usually be
    # stored in the account's .solar directory.
    file_name = None

    def __init__(self, **data):
        if self.content_dict:
            default_content = {}
            self.content = data.pop('content', {})
            if type(self.content) is not dict:
                self.content = json.loads(self.content)
        else:
            self.content = data.pop('content', "")

        self.pubkey = data.pop('pubkey', bytes(32).hex())
        self.created_at = Timestamp(data.pop('created_at', None))
        self.tags = TagDict(data.pop('tags', []))
        self.kind = data.pop('kind', self.kind)

        # This value can be computed automatically, so if it
        # is passed to the event constructor then we make sure
        # that the values match up.
        hash_id = data.pop('id', None)

        if hash_id:
            try:
                assert self.id == hash_id
            except AssertionError:
                # If the id doesn't match, drop the signature
                data.pop('sig', None)

        sig = data.pop('sig', None)
        if sig:
            self.sig = bytes.fromhex(sig)
        else:
            self.sig = None

        # The "author" kwarg is convenient for not passing
        # the pubkey or looking up the Account from it
        self._author = data.pop('author', None)
        if self._author:
            self.pubkey = self._author.pubkey

        # We declare that this event is not part of a collection,
        # So that it has nothing to update when it saves
        self.collection = None

        # For the remaining data passed to the constructor, 
        # add each value to content if content_dict is True
        # or otherwise to the tags list.
        for key in data:
            if self.content_dict is True:
                self.content[key] = data[key]
            else:
                value = data[key]
                if isinstance(value, list):
                    self.tags.append(key, value)
                else:
                    self.tags.append(key, [value])

    @property
    def path(self):
        return SolarPath(self.directory, self.name)

    @classmethod
    def load(cls, path):
        with open(path) as file:
            data = json.load(file)

        if data:
            return cls(**data)
        else:
            return None

    def store(self, **kwargs):
        # .path will return None if the event has no name, in which
        # case we don't want to store the event on the filesystem.
        if self.path is None:
            return None

        namespace = kwargs.get('namespace', self.path.namespace)
        subspace = kwargs.get('subspace', self.path.subspace)

        # We don't want to change the original space if we're storing
        # somewhere different.
        path = SolarPath(self.path, namespace=namespace, subspace=subspace)

        path.fs.parent.mkdir(parents=True, exist_ok=True)
        with open(path.fs.with_suffix('.json'), "w") as file:
            json.dump(self.flatten(), file, indent=2)

        return path.fs.with_suffix('.json')

    # Save to relay
    def save(self, **kwargs):
        if not self.verified:
            # Sign with the passed 'session' object
            # or the default server key if not provided.
            self.sign(**kwargs)

        db = kwargs.get('db') or config.get('db')
        if db is None:
            raise AttributeError('db not initialized')

        return db.publish(self)

    # Send deletion request to relay
    def unsave(self, **kwargs):
        db = kwargs.get('db') or config.get('db')
        if db is None:
            raise AttributeError('db not initialized')

        deletion = Event(
                content=f"deletion request for {self.name}",
                kind=5,
                e=self.id,
                k=str(self.kind)
                )

        d = self.tags.getfirst('d')
        if d:
            deletion.tags.add(['a', f'{self.kind}:{self.pubkey}:{d}'])
        elif self.file_name:
            deletion.tags.add(['a', f'{self.kind}:{self.pubkey}:'])

        deletion.sign(**kwargs)
        return db.publish(deletion)

    def work(self, target=16, start=0):
        if self.tags.get('nonce'):
            del self.tags['nonce']
        tags = self.tags.flatten()
        proof = 0
        score = 0

        while score < target:
            proof += 1
            score = 0
            self.tags = TagDict(tags)
            self.tags.add(["nonce", str(proof), str(target)])
            b = bytes.fromhex(self.id)
            for i in range(32):
                if b[i] == 0:
                    score += 8
                else:
                    score += (8 - b[i].bit_length())
                    break

        print(self.flatten())


    def sign(self, sess=None, **kwargs):
        session = kwargs.get('session', sess)

        if session:
            self.pubkey = session.account.pubkey
            self.sig = session.sign(self.id)
        else:
            # If no session is supplied, sign with the default server key.
            from elements import WebSession
            s = WebSession(config.get('solar.auth'))
            self.pubkey = s.account.pubkey
            self.sig = s.sign(self.id)

        assert self.verified == True
        return self.sig

    @property
    def verified(self):
        if self.sig is None:
            return False

        pubkey = bytes.fromhex(self.pubkey)
        id_hash = bytes.fromhex(self.id)
        return schnorr_verify(id_hash, pubkey, self.sig)

    @property
    def author(self):
        if self._author is None:
            self._author = Account.from_pubkey(self.pubkey)

        return self._author

    def flatten(self, *args, **kwargs):
        representation = {
            'content': self.content,
            'pubkey': self.pubkey,
            'kind': self.kind,
            'created_at': int(self.created_at),
            'tags': self.tags.flatten(),
            'id': self.id
        }

        if self.sig and self.verified:
            representation['sig'] = self.sig.hex()
    
        # dumping a string with Json looks kind of weird.
        if kwargs.get('stringify') and type(self.content) is not str:
            representation['content'] = json.dumps(self.content)

        return representation

    @property
    def name(self):
        # If file_name is set, we always use that.
        if self.file_name:
            return self.file_name
        else:
            # Return the 'd' tag or timestamp
            return self.tags.getfirst('d') or str(int(self.created_at))

    @property
    def meta(self):
        return self.tags.metadata

    # The path used to address this event within a URL
    @property
    def url(self):
        return f'{self.path}/'

    # This computes the id of the event
    @property
    def id(self):
        serialized = [0,self.pubkey,int(self.created_at),self.kind,self.tags.flatten()]
        if type(self.content) is not str:
            serialized.append(json.dumps(self.content))
        else:
            serialized.append(self.content)
        return identify(serialized)

    @property
    def address(self):
        #if self.pubkey is None or self.pubkey == bytes(32).hex():
        #    pubkey = ""
        #else:
        #    pubkey = self.pubkey
        if self.file_name:
            return f'{self.kind}:{self.pubkey}:'
        else:
            return f'{self.kind}:{self.pubkey}:{self.name}'


    # This function defines how the Event acts as a string
    def __str__(self):
        if isinstance(self.content, dict):
            return json.dumps(self.content)
        return self.content

    # This function indicates how Event is represented interactively
    def __repr__(self):
        return f'{type(self).__name__} - {self.id}'

    def __getattr__(self, attr):
        if self.content_dict:
            # Return attributes from content before meta tags
            # if they are available
            return self.content.get(attr) or self.meta.get(attr)
        else:
            return self.meta.get(attr)

    ## Stuff for making an Event into a mapping. I don't know
    ## if I'll need this.

    #def keys(self):
    #    k = [ k for k in dir(self) if not k.startswith('_') and not callable(getattr(self, k)) ]
    #    return k

    #def __iter__(self):
    #    return iter(self.keys())

    #def __len__(self):
    #    return len(self.keys())

    #def __getitem__(self, k):
    #    return getattr(self, k)


class Profile(Event):
    kind = 0
    directory = ".solar"
    file_name = "profile"
    content_dict = True

    def update(self, **kwargs):
        self.content.update(kwargs)
        self.created_at = Timestamp()

    @property
    def path(self):
        return SolarPath(self.directory, self.file_name, namespace=config.get('solar.namespace'))

    @property
    def name(self):
        return self.content.get('name')

    @property
    def display_name(self):
        return self.content.get('display_name', self.name)

class Note(Event):
    kind = 1
    directory = "notes"

config['kinds'][-1] = Event
config['kinds'][0] = Profile
config['kinds'][1] = Note

def hydrate(data):
    kind = data.get('kind')

    # The 'hydrate' function instantiates an event from
    # a json dictionary using the most appropriate class
    # available in the configuration's "kinds" dict.
    try:
        cls = config['kinds'][kind]
    except KeyError:
        cls = Event

    return cls(**data)
