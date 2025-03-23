from datetime import timedelta
from calendar import monthrange
from math import floor
from uuid import uuid4

from elements import Event, Timestamp, Collection, config
from elements.core.libs.utilities import slugify
from .post import Post

'''
             _____________          
            |             |          
            |  June 2024  |      
            |_____________|          
            |_|_|_|_|_|_|_|          
            |_|_|_|_|X|_|_|          
            |_|_|_|_|_|_|_|          
            |_|_|_|_|_|_|_|          
                                             
               

The Booking element is used to reserve a space
for a specific amount of time.

Booking events are organized by the day(s) they
occur and the spaces where they happen. When 
making a new booking, we first check for any 
conflicts in the same location.

Booking builds on the Post element, adding
tooling to edit, duplicate and reschedule events. 
'''

# Time-based Calendar Event (NIP-52)
class Booking(Post):
    kind = 31923
    directory = 'bookings'

    calendar = None

    @classmethod
    def new(cls, **data):
        booking = cls(**data)
        if booking.start is None:
            raise ValueError('No start timestamp provided')

        if booking.end is None:
            raise ValueError('No end timestamp provided')

        if booking.start > booking.end:
            raise ValueError('End time before start time')

        booking.tags.add(['d', booking.name])
        for d in booking.days:
            booking.tags.add(['D', str(d)])

        return booking

    # We overwrite the Post's name property to append the booking's date
    @property
    def name(self):
        title = self.tags.getfirst('title')
        start = int(self.start)
        location = self.location
        if title and location:
            return f'{slugify(title)}-{location.name}-{start}'
        elif title:
            return f'{slugify(title)}-{start}'
        else:
            return super().name

    @property
    def location(self):
        name = self.tags.getfirst('location')
        return name
        #if name is None:
        #    return None

        ##place = Places.all().find(name)
        #return place or None

    @property
    def start(self):
        tag = self.tags.getfirst('start')
        if tag is None:
            return None

        return Timestamp(int(tag))

    @property
    def end(self):
        tag = self.tags.getfirst('end')
        if tag is None:
            return None

        return Timestamp(int(tag))

    @property
    def days(self):
        DAY_LENGTH = 86400

        return [floor(day / DAY_LENGTH) for day in range(int(self.start), int(self.end), DAY_LENGTH)]

    @property
    def price(self):
        value = self.tags.getfirst('price')
        cost = self.tags.getfirst('cost')

        if value == "free":
            return "free"
        elif value == "pwyc":
            return f"PWYC (suggested ${cost})"
        elif value == "paid":
            return cost
            

    # Reschedule accepts the parameters of a timedelta
    # and applies them to the start and end
    def reschedule(self, target='both', **options):
        self.unsave(**options)
        delta = timedelta(**options)

        if target == 'start' or target == 'both':
            start = self.start + delta
            self.tags.replace('start', [str(int(start))])

        if target == 'end' or target == 'both':
            end = self.end + delta
            self.tags.replace('end', [str(int(end))])

        self.save()

    # By default, duplicate creates a new event one week from the day.
    # It can be passed any of the same options as reschedule.
    def duplicate(self, **options):
        if len(options) == 0:
            options['weeks'] = 1

        cls = type(self)
        dupe = cls(**self.flatten())
        dupe.reschedule(**options)
        return dupe

class Calendar(Post):
    kind = 31924
    directory = 'calendar'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bookings = []

    # TODO: Is there an equivalence between
    # Collection and List-like objects?
    def hydrate(self, **kwargs):

        # When we initialize the calendar, we need
        # to inflate all of the 'a' tags into their
        # bookings. 
        booking_references = self.tags.getall('a')
        db = kwargs.get('db', config.get('db'))
        for ref in booking_references:
            [address] = ref

            # Look the booking up by address and add it
            booking = db.get(address)
            if booking:
                self.bookings.append(booking)

    def add(self, booking: Booking):
        for b in self.bookings:
            if  b.start <= booking.start <= b.end or b.start <= booking.end <= b.end:
                raise ValueError('Booking overlaps with ' + str(b.path), b)

        self.tags.add(['a', booking.address])
        self.bookings.append(booking)
        self.created_at = Timestamp()

    def on(self, start, **kwargs):
        if len(kwargs) == 0:
            kwargs['days'] = 1

        end = start + timedelta(**kwargs)

        return [booking for booking in self.bookings if start <= booking.start <= end]

    # TODO options will be used to specify filters
    def upcoming(self, limit=None, **options):
        now = Timestamp()
        results = []
        for booking in self.bookings:
            if booking.start > now:
                results.append(booking)

        results.sort(key=lambda e: e.start)

        if limit:
            return results[:limit]
        else:
            return results

class RSVP(Event):
    kind = 31925

    @classmethod
    def new(cls, *args, **kwargs):
        e = kwargs.pop('event')

        if e is None:
            raise ValueError('No event passed')

        if e.kind not in [31922, 31923]:
            raise ValueError('Not a calendar event')

        rsvp = cls(*args, **kwargs)
        rsvp.tags.add(['a', e.address])

        if rsvp.status not in ['accepted', 'declined', 'tentative']:
            if rsvp.status:
                del self.tags['status']

            # Default status to 'accepted' if not defined
            rsvp.tags.add(['status', 'accepted'])

        rsvp.tags.add(['d', str(uuid4())])

        return rsvp

    @property
    def status(self):
        return self.tags.getfirst('status')
    
    @property
    def event(self, **kwargs):
        db = kwargs.get("db", config.get('db'))
        e = db.get(self.tags.get('a'))

        return e


config['kinds'][Booking.kind] = Booking
config['kinds'][Calendar.kind] = Calendar
config['kinds'][RSVP.kind] = RSVP

#class Bookings(Posts):
#    default_class = Booking
#    directory = 'bookings'
#
#    class_map = {
#        Booking.kind: Booking
#    }
#
#    buckets = { **Posts.buckets, 'day': lambda e: e.days, 'location': lambda e: e.location }
#
#
#    # TODO options will be used to specify filters
#    def upcoming(self, limit=None, **options):
#        now = Timestamp()
#        results = []
#        for booking in self.content:
#            if booking is None:
#                continue
#
#            if booking.start > now:
#                results.append(booking)
#
#        results.sort(key=lambda e: e.start)
#
#        if limit:
#            return results[:limit]
#        else:
#            return results
#                
#        
#    # TODO: This will be refactored to work with HTMX
#
#    # Render returns a dictionary built for rendering
#    # in a month-to-month display
#    def render(self, **options):
#        # Number of upcoming events to set aside
#        upcoming = options.get('upcoming') or 5
#
#        now = Timestamp()
#
#        calendar_data = { 'upcoming': [] }
#        for booking in self.content:
#
#            # Skip any recently deleted bookings
#            if booking is None:
#                continue
#
#            m = booking.start.month
#            y = booking.start.year
#            d = booking.start.day - 1 # Zero-indexing
#
#
#            # Record how long the event goes for
#            diff = booking.end - booking.start
#
#            key = f'{m}{y}'
#            if calendar_data.get(key) is None:
#                _, days = monthrange(y, m)
#                calendar_data[key] = [None] * days
#
#            data = booking.meta
#            data['name'] = booking.name
#            if booking.location:
#                data['location'] = booking.location.display_name
#            else:
#                data['location'] = ""
#
#            # We iterate over all the days of the event
#            for i in range(diff.days) or range(1):
#                day = d + i
#                if calendar_data[key][day] is None:
#                    calendar_data[key][day] = [data]
#                else:
#                    calendar_data[key][day].append(data)
#
#            # Manage the 'upcoming' list
#            if booking.start > now and len(calendar_data['upcoming']) < upcoming:
#                calendar_data['upcoming'].append(data)
#
#        return calendar_data
