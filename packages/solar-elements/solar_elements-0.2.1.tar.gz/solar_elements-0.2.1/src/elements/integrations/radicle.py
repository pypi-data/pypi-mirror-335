import os
import subprocess

from elements import config
from .ssh import SSH

class Radicle(SSH):
    key_path = "m/3"

    # This will save the exported key files into the member's /home directory,
    # Which implies that each member has their own home dir
    def register(self, account):
        radicle = account.path.fs / '.radicle' / 'keys'
        radicle.mkdir(exist_ok=True, parents=True)

        # If the key already exists, return it
        pub = radicle.read('keys/radicle.pub')
        if pub:
            return getDID()


        # Otherwise, save the keys to the filesystem
        # in a place where they can be used.

        comment = f'{account.name}@radicle'
        sec, pub = self.export(comment)

            
        with open(radicle / 'radicle', 'w') as f:
            f.write(sec)

        with open(radicle / 'radicle.pub', 'w') as f:
            f.write(pub)

        os.chmod(radicle / 'radicle', 0o600)
        os.chmod(radicle / 'radicle.pub', 0o600)

        config = radicle.read('..', 'config.json')
        if config is None:
            subprocess.run(['rad','config', 'init', '--alias', account.name])

        subprocess.run(['ssh-add', str(radicle / 'radicle')])

        return getDID() 

# Gets the DID for the currently active radicle keypair
def getDID():
    get_rad = subprocess.run(['which','rad'], capture_output=True)
    radicle_installed = get_rad.returncode == 0
    if radicle_installed:
        results = subprocess.run(['rad', 'self', '--did'], capture_output=True)
        if results.returncode == 0:
            return results.stdout.decode().rstrip()
        else:
            print('no Radicle account available')
            return None
    else:
        print('Radicle not installed')
        return None

config['integrations']['radicle'] = Radicle
