Crypto.PublicKey import ECC
from base64 import b64encode

class Wireguard:
    key_path = "m/6"

    @property
    def private_key(self):
        return ECC.construct(curve="Curve25519", seed=self.key)

    @property
    def public_key(self):
        self.public_key().export_key(format="raw")

    def keypair(self):
        private = b64encode(self.key)
        public = b64encode(self.public_key)
        return (private, public)

config['integrations']['wireguard'] = Wireguard
