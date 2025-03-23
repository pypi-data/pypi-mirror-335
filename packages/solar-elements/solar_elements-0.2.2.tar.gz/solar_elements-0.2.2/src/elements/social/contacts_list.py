import requests
from elements import Event, Account, config, NostrDatabase
from elements.core.libs.utilities import make_request

# Work In Progress - I need to be able to instantiate
# Accounts with greater detail

class ContactsList(Event):
    kind = 3
    directory = 'contacts'

    def add(self, account, **kwargs):
        name = kwargs.get('name', account.name)
        relay = kwargs.get('relay', account.relays[0])
        self.tags.add(["p", account.pubkey, relay, name])

    # Return all saved contacts in a list
    @property
    def contacts(self):
        keys = set()
        friends = []
        for tag in self.tags.getall('p'):
            key = tag[0]
            if key not in keys:
                account = Account.from_pubkey(key)
                friends.add(account)

        return friends

        


config['kinds'][3] = ContactsList
