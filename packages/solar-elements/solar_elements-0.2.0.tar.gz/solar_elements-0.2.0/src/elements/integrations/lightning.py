from elements.core import Config
from .base import Integration
from secp256k1 import PrivateKey

config = Config.load()

host = config.HOST or "localhost"

# Developer Note: since the Account exists at a lower level than 
# Member (i.e. it is not attached to the 'main' Account element),
# we have no knowledge of the Member object as a whole.

# Instead, we go through the actions involved in registration
# at a system level and then hand the data back to the caller.

class Lightning(Integration):

    def __init__(self, key):
        if not isinstance(key, bytes):
            key = bytes.fromhex(key)

        # Developer note - Python is not a memory-safe language.
        # Hackers (lol) may be able to recover PrivateKey data
        # from deallocated memory. Don't let them on your server.
        self.key = PrivateKey(key)

    # When a Solar Account is registered, it becomes possible
    # to publish data to the wider network. The account's profile
    # and any shared posts become available to the public.
    def register(self, member):
        public_key = self.key.pubkey.serialize().hex()
        address = f'{member.name}@{host}'

        profile_updates = {
            'account': { 'pubkey': public_key },
            'tags': [['i', f'solar:{address}', public_key]],
            'address': address
        }

        return profile_updates

    # Exports the keypair in a designated format
    def keypair(self, fmt="hex"):
        secret_key = self.key
        public_key = secret_key.pubkey.serialize().hex()[2:]
        if fmt == "bech32":
            secret_key = bech32.encode('nsec', secret_key.private_key)
            public_key = bech32.encode('npub', bytes.fromhex(public_key))
        elif fmt == "bytes":
            public_key = secret_key.pubkey
        elif fmt == "hex":
            secret_key = self.key.private_key.hex()
        else:
            private_key = None
            public_key = None

        return (secret_key, public_key)
        
    def sign(self, data: bytes): 
        # ecdsa signing 
        #signature = self.key.ecdsa_sign(data)
        #serial = secret_key.ecdsa_serialize_compact(signature)
        #return serial.hex()

        sig = self.key.schnorr_sign(data, None, raw=True)
        return sig.hex()

    def encrypt(self, data, private_key): pass
    def decrypt(self, data, private_key): pass
