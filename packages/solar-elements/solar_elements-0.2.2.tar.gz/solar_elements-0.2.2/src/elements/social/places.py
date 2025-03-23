from datetime import datetime
import time
from elements.notes import Note, Notes
from elements.core.storage import slugify

# Basic implementation of OpenStreetMaps opening_hours spec.
# https://wiki.openstreetmap.org/wiki/Key:opening_hours/specification

DAYS = ["su", "mo", "tu", "we", "th", "fr", "sa", "ph"]
FULL_DAYS = [
    "Sunday", 
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Holidays"
]

class OpeningHours:
    def __init__(self, opening_hours_string):
        now = datetime.now()
        self.days = { k: (None, None) for k in DAYS }
        for entry in opening_hours_string.split(';'):
            entry = entry.strip() # Clean whitespace

            # This entry applies to all days
            if entry.find(' ') == -1:
                days = None
                hours = entry
            else:
                days, hours = entry.split(' ')

            if hours == "closed" or hours == "off":
                dt_open = None
                dt_close = None
            else:
                opening, closing = hours.split('-')

                open_h, open_m = opening.split(':')
                dt_open = now.replace(hour=int(open_h), minute = int(open_m))

                close_h, close_m = closing.split(':')
                dt_close = now.replace(hour=int(close_h), minute = int(close_m))

            # Set all days
            if days is None:
                self.days = { k: (dt_open, dt_close) for k in DAYS }
                continue
                


# A Place is a physical location where an event
# occurs. It uses GeoJSON to describe the location
# and annotates it with various OpenStreetMap-friendly
# values

# Since I always forget this: 'longitude' is east-to-west
# and it has a range of [-180, 180], centered at the 
# Royal Observatory of Greenwich in London, GB

# 'latitude' runs south-to-north and has a range of 
# [-90, 90], with 0 being the equator.

# Reference: https://github.com/nostr-protocol/nips/pull/927/files
class Place(Note):
    directory = 'places'
    kind = 37515

    @classmethod
    def new(cls, **data):
        lat = data.pop('lat', None)
        lng = data.pop('lng', None)
        name = data['name']

        if lat:
            assert -90 <= float(lat) <= 90
        if lng:
            assert -180 <= float(lng) <= 180
            

        c = cls.content_dict(**data)

        geojson = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [lng, lat]
            },
            'properties': c.content
        }

        c.content = geojson

        # Manually set the 'd' tag to a slug
        # of the name
        c.tags.replace('d', [slugify(name)])
        return c

    def __eq__(self, other):
        if other is None:
            return False

        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def update(self, data):
        lat = data.pop('lat', self.coordinates[1])
        lng = data.pop('lng', self.coordinates[0])
        name = data.pop('name', self.display_name)

        self.content = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [lng, lat]
            },
            'properties': {
                'name': name
            }
        }

        for key in data:
            self.content['properties'][key] = data[key]

    # Returns a link to OpenStreetMaps for viewing a full-size map
    def osm_link(self, zoom=16):
        lng, lat = self.coordinates
        marker = f'?mlat={lat}&amp;mlon={lng}'
        return f"https://www.openstreetmap.org/{marker}#map={zoom}/{lng}/{lat}"

    @property
    def latitude(self):
        lng, lat = self.content['geometry']['coordinates']
        return float(lat)

    @property
    def longitude(self):
        lng, lat = self.content['geometry']['coordinates']
        return float(lng)

    @property
    def coordinates(self):
        lng, lat = self.content['geometry']['coordinates']
        if lng and lat:
            return [float(lng), float(lat)]
        else:
            return [0,0]

    @property
    def display_name(self):
        return self.content['properties']['name']

    @property
    def properties(self):
        return self.content['properties']

    @property
    def open(self):
        hours = self.content['properties']['hours'] 
        return OpeningHours(hours)

class Places(Notes):
    directory = 'places'
    default_class = Place
    class_map = {
        Place.kind: Place
    }

    # Render returns a collection of places in a dictionary
    # format, to be embedded in a template
    def render(self):
        output = {}
        for place in self.content:
            output[place.name] = { 
                'coords': list(reversed(place.coordinates)) 
                # Any data that belongs in a popup will go here
            }

        return output
        

    # Returns a filter of places - implement later
    def in_radius(self, distance):
        pass
