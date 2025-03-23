import sys
import json
from pathlib import Path
from .config import config

'''
The SolarPath is a key component of the system. It represents a path
where an event is (or will be) located on the filesystem, and can be
used to translate a request into filter for querying a nostr relay.

SolarPath is defined in accordance with the Willow Protocol, with
the following parameter definitions:

    - NamespaceId           -> A folder in the Solar data directory (default: /home)
    - SubspaceId            -> A path within the folder (e.g. username)
    - max_component_length  -> 32 bytes
    - max_component_count   -> 4
    - max_component_length  -> 128 bytes
    - PayloadDigest         -> sha256
    - hash_payload          -> Serialization according to NIP-01
    - AuthorizationToken    -> Schnorr public key
    - is_authorized_write   -> Signing the PayloadDigest with Schnorr key

'''

class SolarPath(Path):
    namespace = config.get('solar.namespace')
    subspace  = config.get('user')
    resolved  = False

    # The concept of "subspaces" is interesting, I hadn't
    # considered it before. I'll need to think it through.
    # Does it map to "zen.localhost" or "localhost/zen/"?
    # Would we want it to be both? It also needs to be
    # "zen@localhost"

    # I think that "zen.localhost" can be aliased to
    # 'localhost/zen/' if necessary, but in general the
    # namespace should be functionally distinct from
    # the subspace.

    # Path subclassing was improved in Python 3.12
    if sys.version_info.minor < 12:
        _flavour = type(Path())._flavour

    def __init__(self, *args, **kwargs):
        Path.__init__(self)
        self.namespace = kwargs.get('namespace', self.namespace)
        self.subspace = kwargs.get('subspace', self.subspace)

        # A "resolved" SolarPath is absolute
        self.resolved = kwargs.get('resolved', False)

    # Generate a path from an existing event
    @classmethod
    def from_event(cls, event, namespace=None):
        if event.name is None:
            return None

        path = SolarPath(event.directory, event.name)
        if event.author:
            path.subspace=event.author.name

        return path

    # This is the resolved path as it exists on the filesystem
    @property
    def fs(self):
        if self.resolved:
            return self
        else:
            return (SolarPath(config.get('solar.data'), self.namespace or "", self.subspace or "", resolved=True) / self).resolve()

    # Pull data from the file system, if it exists.
    def read(self, *args):
        path = self.fs
        if len(args) > 0:
            location = Path(*args)
            path = path / location

        if path.is_file():
            with open(path) as f:
                data = f.read()
                try:
                    data = json.loads(data)
                except json.decoder.JSONDecodeError:
                    pass

            return data

        elif path.is_dir():
            raise ValueError('read() not implemented for dirs yet')

        else:
            return None

    @property
    def dirs(self):
        if not self.fs.is_dir():
            return []

        return [d for d in self.fs.glob('*') if d.is_dir()]

    @property
    def files(self):
        if not self.fs.is_dir():
            return []

        return [d for d in self.fs.glob('*') if d.is_file()]

    @property
    def children(self, ext=".json"):
        return [d for d in self.fs.rglob(f'**/*{ext}')]


