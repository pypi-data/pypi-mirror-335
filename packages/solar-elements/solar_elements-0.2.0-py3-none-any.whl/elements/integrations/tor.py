# Sourced from https://tor.stackexchange.com/questions/22663/put-ed25519-keys-in-usable-file-format-for-tor

import base64
import hashlib
import os
import pwd
import grp
import subprocess
from pathlib import Path

from elements import config
from elements import Integration
import Crypto.Signature.eddsa as eddsa

class Tor(Integration):
    key_path = "m/4"

    @property
    def private_key(self):
        return eddsa.import_private_key(self.key)

    @property
    def public_key(self):
        return self.private_key.public_key()

    def register(self, account, **kwargs):
        get_tor = subprocess.run(['which','tor'], capture_output=True)
        service_name = kwargs.get('service_name', 'solar')
        service_port = kwargs.get('service_port', 80)

        tor_installed = get_tor.returncode == 0
        if not tor_installed:
            print('Error: Tor not installed.')
            return None

        tor = account.path.fs / '.tor' 
        tor.mkdir(exist_ok=True, parents=True)

        address = tor.read('solar/hostname')
        if address:
            return address

        if tor.read('torrc') is None:
            with open(tor / 'torrc', 'w') as f:
                f.write(f'SocksPort 9060\n')
                f.write(f'ControlPort 9061\n')
                f.write(f'CookieAuthentication 1\n')
                f.write(f'RunAsDaemon 1\n')
                f.write(f'Log notice file {tor / "log"}\n')
                #f.write(f'CookieAuthFile control_auth_cookie\n')
                #f.write(f'CookieAuthFileGroupReadable 1\n')
                #f.write(f'DataDirectoryGroupReadable 1\n')
                #f.write(f'CacheDirectoryGroupReadable 1\n')


        quiet = kwargs.get('quiet', False)
        os.chmod(tor, 0o700)

        hidden_service = tor / service_name
        address = create_hidden_service_files(
            self.key,
            self.public_key.export_key(format="raw"),  
            hidden_service
        )
        verify_v3_onion_address(address)

        with open(tor / 'torrc', 'a') as f:
            f.write(f'HiddenServiceDir {hidden_service}\n')
            f.write(f'HiddenServicePort 80 localhost:{service_port}\n')

        with open(hidden_service / 'README.md', 'w') as f:
            f.write('# How to upgrade')

        return address
        
    
def expand_private_key(secret_key) -> bytes:
    hash = hashlib.sha512(secret_key[:32]).digest()
    hash = bytearray(hash)
    hash[0] &= 248
    hash[31] &= 127
    hash[31] |= 64
    return bytes(hash)


def onion_address_from_public_key(public_key: bytes) -> str:
    version = b"\x03"
    checksum = hashlib.sha3_256(b".onion checksum" + public_key + version).digest()[:2]
    onion_address = "{}.onion".format(
        base64.b32encode(public_key + checksum + version).decode().lower()
    )
    return onion_address


def verify_v3_onion_address(onion_address: str) -> list[bytes, bytes, bytes]:
    # v3 spec https://gitweb.torproject.org/torspec.git/plain/rend-spec-v3.txt
    try:
        decoded = base64.b32decode(onion_address.replace(".onion", "").upper())
        public_key = decoded[:32]
        checksum = decoded[32:34]
        version = decoded[34:]
        if (
            checksum
            != hashlib.sha3_256(b".onion checksum" + public_key + version).digest()[:2]
        ):
            raise ValueError
        return public_key, checksum, version
    except:
        raise ValueError("Invalid v3 onion address")


def create_hs_ed25519_secret_key_content(signing_key: bytes) -> bytes:
    return b"== ed25519v1-secret: type0 ==\x00\x00\x00" + expand_private_key(
        signing_key
    )


def create_hs_ed25519_public_key_content(public_key: bytes) -> bytes:
    assert len(public_key) == 32
    return b"== ed25519v1-public: type0 ==\x00\x00\x00" + public_key

def create_hidden_service_files(
    private_key: bytes,
    public_key: bytes,
    hidden_service_dir: Path,
) -> str:

    if not hidden_service_dir.is_dir():
        hidden_service_dir.mkdir()
        os.chmod(hidden_service_dir, 0o700)

    file_content_secret = create_hs_ed25519_secret_key_content(private_key)
    with open(f'{hidden_service_dir}/hs_ed25519_secret_key', "wb") as f:
        f.write(file_content_secret)
    os.chmod(f'{hidden_service_dir}/hs_ed25519_secret_key', 0o600)

    file_content_public = create_hs_ed25519_public_key_content(public_key)
    with open(f'{hidden_service_dir}/hs_ed25519_public_key', "wb") as f:
        f.write(file_content_public)

    onion_address = onion_address_from_public_key(public_key)
    with open(f'{hidden_service_dir}/hostname', "w") as f:
        f.write(onion_address)

    return onion_address

config['integrations']['tor'] = Tor
