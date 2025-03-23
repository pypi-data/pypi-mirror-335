#!/bin/python3

# A small class for working with Bottle's ConfigDict library

from elements.core import ConfigDict, default_app
from configparser import MissingSectionHeaderError
import getpass

import logging
log = logging.getLogger(__name__)

config = default_app().config

def load_config(path=["/etc/solar.conf", "./solar.conf"]):
    try:
        config['kinds'] = {}
        config['integrations'] = {}
        config['actions'] = {}
        config.load_config(path)
        config['user'] = getpass.getuser()
        log.info(f'Loaded config from {path}')
    except MissingSectionHeaderError as e:
        log.exception(f'Error loading config from {path}: {e.message}')
        
    return config

load_config()
