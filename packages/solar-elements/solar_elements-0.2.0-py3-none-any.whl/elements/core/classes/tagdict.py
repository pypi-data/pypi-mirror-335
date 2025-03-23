from elements.core import MultiDict

class TagDict(MultiDict):
    def __init__(self, taglist=[]):
        MultiDict.__init__(self)
        self.d = None
        for tag in taglist:
            self.add(tag)

    # When we iterate through the tag dict,
    # we get each key-value pair as a tuple
    def __iter__(self):
        return self.allitems()

    def __repr__(self):
        return str(self.flatten())

    def add(self, tag):
        key, *values = tag
        self.append(key, values)
        return (key, values)

    def getfirst(self, tag):
        value = self.get(tag, index=0)
        if value:
            return value[0]
        else:
            return None

    @property
    def metadata(self):
        return {key: value[0] for key, value in self}
            

    # We automatically spread the value of
    # Each tag because we assume it will be
    # a list. This is not enforced, however.
    def flatten(self):
        return [[k, *v] for k, v in self]
