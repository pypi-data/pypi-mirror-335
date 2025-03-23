from elements import Account, SolarPath, config, request

def nip05(*args, **kwargs):
    results = {
        'names': {},
        'relays': {}
    }

    name = request.query.get('name')
    if name is None:
        p = SolarPath('.', subspace=None)
        for subspace in p.dirs:
            a = Account(subspace.name)
            results['names'][subspace.name] = a.pubkey
            if a.name == config.get('user'):
                results['names']['_'] = a.pubkey

            results['relays'][a.pubkey] = a.relays
    elif name == "_":
        a = Account(config.get('user'))
        results['names']['_'] = a.pubkey
        results['relays'][a.pubkey] = a.relays

    else:
        a = Account(name)
        results['names'][a.name] = a.pubkey
        results['relays'][a.pubkey] = a.relays

    return results

config['actions']['nip05'] = nip05
