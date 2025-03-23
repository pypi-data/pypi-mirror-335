# TODO: Write the basic class for a UNIX account
import grp
import subprocess
from os import getgrouplist
import pwd
from pathlib import Path
from .solar_path import SolarPath
from .config import config
from .integrations import Nostr
from elements.core.libs.shamir import Mnemonic, Language, get_phrase, create_shares, recover_mnemonic, recover_from_phrase, Share, ThresholdError
from elements.core.libs.bip32 import BIP32, HARDENED_INDEX
from elements.core.libs.encryption import encrypt
from Crypto.Protocol.KDF import scrypt

'''
Accounts on SOLAR are fully integrated with the underlying unix system.
'''

class Account:
    namespace = config.get('solar.namespace')

    def __init__(self, name, **kwargs):
        path = SolarPath()
        path.subspace = name
        path.namespace = kwargs.get('namespace', self.namespace)
        if not path.fs.is_dir():
            path.namespace = kwargs.get('npc_namespace', 'npc')

        if not path.fs.is_dir():
            raise ValueError(f"Account {name} does not exist in namespaces {self.namespace} or {path.namespace}")

        self._profile = kwargs.get('profile')
        self._pubkey =  kwargs.get('pubkey')
        self._relays = kwargs.get('relays')
        self.path = path

    @classmethod
    def from_pubkey(cls, pubkey):
        path = SolarPath('.')
        path.namespace = None
        path.subspace = None

        # When looking for an account, we go through all of the account
        # namespaces and search each subspace to see if there is one 
        # with a matching solar pubkey.
        namespaces = ['localhost', 'friends', 'npc']

        for namespace in namespaces:
            path.namespace = namespace
            path.subspace = None

            subspaces = path.dirs

            for account in subspaces:
                path.subspace = account.name
                account_pubkey = path.read('.solar/pubkey')
                if account_pubkey and account_pubkey.strip() == pubkey:
                    return cls(account.name)

        return NPC(pubkey=pubkey)

    @classmethod
    def register(cls, **data):
        name = data.get('name')
        if name is None:
            raise ValueError('cannot register an account without a name')

        password = data.get('password') or name
        salt = data.get('salt') or name

        key = data.get('key')
        if key is None:
            mnemonic = Mnemonic.generate_random()
            key = mnemonic.seed
        else:
            mnemonic = Mnemonic.from_bytes(key)

        # The seed will also save unencrypted for people who have not backed up their
        # Mnemonic - otherwise people will run into problems if they forget their
        # password


        bip32 = BIP32.from_seed(key)

        # If 'derive_from_name' is set to True, we add an extra level of key derivation
        # so that the account cannot be recovered from a seed phrase without the name.
        if data.get('derive_from_name') == True:
            account_branch = int.from_bytes(name.encode()) % HARDENED_INDEX
            bip32 = BIP32.from_xpriv(bip32.get_xpriv_from_path(f"m/{account_branch}'"))

        password_key = scrypt(password.encode(), salt, 32, N=2**14, r=8, p=1)
        encrypted_xpriv = encrypt(bip32.get_xpriv(), password_key)

        path = SolarPath('', subspace=name, namespace=cls.namespace)

        ## If the base path is not an existing dir, the account being
        ## registered does not exist on the computer. They are an NPC
        if not path.fs.is_dir():
            path.namespace = config.get('solar.npc_namespace', 'npc')
            path.fs.mkdir(exist_ok=True, parents=True)

        account = cls(name, namespace=path.namespace)

        # This is a basic example of how the Nostr integration is used
        # To generate the pubkey. This same flow is used with sessions.
        key = bip32.get_privkey_from_path(Nostr.key_path)
        nostr = Nostr(key)

        stored_values = {
            "pubkey": nostr.public_key.hex(),
            "hsm_secret": key,
            "xpriv": encrypted_xpriv
        }

        if salt != name:
            storage['salt'] = salt

        # Save the values into the account's .solar directory
        account.store(**stored_values)

        return account

    def backup(self, recovery_threshold=1, shares=1, language="english"):
        seed = self.path.read('.solar/hsm_secret')
        if seed is None:
            raise ValueError("No hsm_secret available")

        mnemonic = Mnemonic.from_bytes(key)
            
        if recovery_threshold > shares:
            raise ValueError('you need to keep the recovery threshold even with the shares!')

        wordlists = {
            "chinese_simplified": Language.ChineseSimplified,
            "chinese_traditional": Language.ChineseTraditional,
            "czech": Language.Czech,
            "english": Language.English,
            "french": Language.French,
            "italian": Language.Italian,
            "japanese": Language.Japanese,
            "korean": Language.Korean,
            "portuguese": Language.Portuguese,
            "spanish": Language.Spanish
        }

        if shares == 1:
            return get_phrase(mnemonic, wordlists.get(language))
        else:
            backups = []
            shared_phrases = create_shares(recovery_threshold, shares, mnemonic)
            for i in range(shares):
                backups.append(get_phrase(shared_phrases[i], wordlists.get(language)))

            return backups

    @staticmethod
    def restore_key(phrase_array: [[str]],  **kwargs) -> bytes:
        language = kwargs.get('language') or "english"

        wordlists = {
            "chinese_simplified": Language.ChineseSimplified,
            "chinese_traditional": Language.ChineseTraditional,
            "czech": Language.Czech,
            "english": Language.English,
            "french": Language.French,
            "italian": Language.Italian,
            "japanese": Language.Japanese,
            "korean": Language.Korean,
            "portuguese": Language.Portuguese,
            "spanish": Language.Spanish
        }

        # If we are being passed shares, assemble them.
        if len(phrase_array) > 1:
            shares = []
            for phrase in phrase_array:
                shares.append(Share.from_share_phrase(phrase, wordlists[language]))

            mnemonic = recover_mnemonic(shares)
        else:
            mnemonic = recover_from_phrase(phrase_array[0], wordlists[language])

        return mnemonic.seed

    # Save to kwargs to the account's .solar dir
    def store(self, **kwargs):
        solar_dir = self.path.fs / ".solar"
        solar_dir.mkdir(exist_ok=True, parents=True)

        for key, value in kwargs.items():
            with open(solar_dir / key, "wb") as f:
                if type(value) is str:
                    value = value.encode()
                f.write(value)

    @property
    def name(self):
        return self.path.subspace

    @property
    def groups(self):
        try:
            details = pwd.getpwnam(self.name)
        except KeyError:
            # If self.name is not found, return
            # basic permissions.
            return ['npc']

        grouplist = getgrouplist(self.name, details.pw_gid)
        return [grp.getgrgid(gid).gr_name for gid in grouplist]

    @property
    def pubkey(self):
        if self._pubkey is None:
            self._pubkey = self.path.read('.solar/pubkey').strip()

        return self._pubkey

    @property
    def relays(self):
        if self._relays is None:
            saved_relays = self.path.read('.solar/relays')

            if saved_relays is None:
                self._relays = [config.get('solar.relay')]
            else:
                self._relays = saved_relays

        return self._relays 

    @property
    def profile(self):
        if self._profile is None:
            # Can't import Profile at the top because circular dependencies
            from elements import Profile

            db = config.get('db')
            self._profile = db.get(f'0:{self.pubkey}:') or Profile()

            #profile_path = self.path.fs / ".solar" / "profile"

            #try:
            #    profile = Profile.load(profile_path.with_suffix('.json'))
            #except FileNotFoundError:
            #    self._profile = Profile(name=self.name, pubkey=self.pubkey)

            #self._profile = profile

        return self._profile

    def __getattr__(self, attr):
        # Pass attribute requests to the profile
        return getattr(self.profile, attr)

# NPCs do not have an account on the underlying system.
class NPC(Account):
    namespace = config.get('solar.npc_namespace', 'npc')

    @property
    def groups(self):
        return ['npc']
