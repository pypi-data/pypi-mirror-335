import os
from pathlib import Path
import textwrap
import struct
import Crypto.Signature.eddsa as eddsa
import Crypto.IO.PEM as PEM
from elements import config

from elements import Integration

class SSH(Integration):
    key_path = "m/2"

    @property
    def private_key(self):
        return eddsa.import_private_key(self.key)

    @property
    def public_key(self):
        return self.private_key.public_key()

    def export(self, comment=""):
        # Generate the pubkey and add the comment
        pubkey = self.public_key.export_key(format="OpenSSH")
        pubkey = pubkey.rstrip('\n') + f' {comment}\n'

        # Generate the private key with the comment
        raw_secret = exportOpenSSHKey(self.private_key, comment)
        seckey = PEM.encode(raw_secret, 'OPENSSH PRIVATE KEY') + '\n'

        # Ensure that the key is 70 characters wide
        reformat = seckey.strip().split('\n')
        seckey = reformat[0] + '\n' + textwrap.fill(''.join(reformat[1:-1]), 70) + '\n' + reformat[-1] + '\n'

        return (seckey, pubkey)

    # This will save the exported key files into the member's /home directory,
    # Which implies that each member has their own home dir
    def register(self, account):
        ssh = account.path.fs / ".ssh"
        ssh.mkdir(exist_ok=True)

        # If the key already exists, return it
        pub = ssh.read('id_solar.pub')
        if pub:
            return pub

        # Otherwise, save the keys to the filesystem
        # in a place where they can be used.

        comment = f'{account.name}@solar'
        sec, pub = self.export(comment)

            
        with open(ssh / 'id_solar', 'w') as f:
            f.write(sec)

        with open(ssh / 'id_solar.pub', 'w') as f:
            f.write(pub)

        os.chmod(ssh / 'id_solar', 0o600)
        os.chmod(ssh / 'id_solar.pub', 0o600)

        return pub


# This function returns an integer value as a binary value
def to_bytes(i):
    return struct.pack('>I', i)

# This function is based on work done by blackknight36: 
# https://github.com/blackknight36/ssh-static-key-generator. 
# It has been ported to python3 and adapted to work with a Pycryptodome eddsa key
def exportOpenSSHKey(key, comment):
  auth_magic = b"openssh-key-v1\x00"
  keytype = b'ssh-ed25519'
  #privkey = key.encode()
  #pubkey = key.verify_key.encode()
  privkey = key.seed
  pubkey = key.public_key().export_key(format='raw')

  s = auth_magic
  s += to_bytes(4)
  s += b'none'
  s += to_bytes(4)
  s += b'none'
  s += to_bytes(0)
  # number of keys - hardcoded to 1
  s += to_bytes(1)
  # total size of public key data = len(keytype) + len(pubkey) + 8 bytes of length data
  s += to_bytes(len(keytype) + len(pubkey) +8)
  s += to_bytes(len(keytype))
  s += keytype
  s += to_bytes(len(pubkey))
  s += pubkey

  privkey_block = to_bytes(0) + to_bytes(0) + to_bytes(len(keytype)) + keytype + to_bytes(len(pubkey)) + pubkey + to_bytes(len(privkey) + len(pubkey)) + privkey + pubkey + to_bytes(len(comment)) + comment.encode()
  # Add padding until list is a multiple of the cipher block size (8) - See the sshkey_private_to_blob2 function in sshkey.c
  n = 1

  while len(privkey_block) % 8 != 0:
      privkey_block += chr(n & 0xFF).encode()
      n += 1

  s += to_bytes(len(privkey_block))
  s += privkey_block
  return s

config['integrations']['ssh'] = SSH
