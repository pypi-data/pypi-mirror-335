from elements import Account, config, NostrDatabase
from requests import session
import json

# A "Friend" is an account which is hosted
# somewhere other than localhost.

class Friend(Account):
    namespace = 'friends'

    @classmethod
    def lookup(cls, address, **kwargs):
        #relay = kwargs.get('relay')
        #pubkey = kwargs.get('pubkey')

        if '@' not in address:
            raise ValueError('address must be in a NIP-05 format')

        name, host = address.split('@')

        if name == "":
            name = "_"

        s = session()
        if host.endswith('.onion'):
            # This requires the PySocks library and an active Tor node
            s.proxies['http'] = 'socks5h://localhost:9050'
            scheme = 'http'
        else:
            # Not stoked on using https by default, but it works for now
            scheme = 'https'

        response = s.get(f'{scheme}://{host}/.well-known/nostr.json?name={name}')
        index = response.json()
        names = index.get('names')

        pubkey = names.get(name)
        if pubkey is None:
            return None

        exists = Account.from_pubkey(pubkey)
        if exists:
            return exists

        try:
            relays = index['relays'][pubkey]
        except KeyError:
            relays = [config.get('solar.relay')]

        db = NostrDatabase(relays[0])

        try:
            [profile] = db.query({ 'kinds': [0], 'authors': [pubkey] })
            name = profile.name
            profile.store(subspace=name, namespace=cls.namespace)

        except ValueError as e:
            print('profile not found.')
            return None

        friend = cls(name)
        friend.store(pubkey=pubkey, relays=json.dumps(relays))

        try:
            [contacts] = db.query({ 'kinds': [3], 'authors': [pubkey] })
            contacts.store(subspace=name, namespace=cls.namespace)
        except ValueError:
            print('no contacts found.')

        return friend
