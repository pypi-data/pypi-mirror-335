from elements import Event, config

'''

    Comment

'''

# NIP-22 implements a standard form for commenting on other events.
# These comments refer both to the root scope as well as any parent
# comments which they are responding to.

class Comment(Event):
    kind = 1111
    directory = "comments"

    #def __init__(self, *args, **kwargs):
    #    super().__init__(*args, **kwargs)

    # Once the comment is initialized, we use this function to attach
    # it to another event or comment.
    def reference(self, ev : Event):
        k = str(ev.kind)
        p = ev.pubkey
        a = ev.address 
        e = ev.id 

        # If the event we're referencing already has root tags, we
        # adopt them for this comment.
        K = ev.meta.get('K', k)
        P = ev.meta.get('P', p)
        A = ev.meta.get('A', a)
        E = ev.meta.get('E', e)

        self.tags.add(['K', K])
        self.tags.add(['P', P])
        self.tags.add(['A', A])
        self.tags.add(['E', E])

        self.tags.add(['k', k])
        self.tags.add(['p', p])
        self.tags.add(['a', a])
        self.tags.add(['e', e])

config['kinds'][Comment.kind] = Comment
