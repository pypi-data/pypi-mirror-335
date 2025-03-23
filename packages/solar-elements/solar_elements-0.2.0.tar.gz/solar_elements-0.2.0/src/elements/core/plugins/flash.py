import json
from elements import request, response

class FlashMessages:
    name = "flash"
    api = 2

    def __init__(self, keyword="flashes", secret='secret'):
        self.keyword = keyword
        self.secret = secret
        self.app = None

    def setup(self, app):
        self.app = app
        self.app.flash = self.flash
        self.app.get_flashes = self.get_flashes

    def load_flashes(self):
        flashes = request.get_cookie(self.keyword, secret=self.secret)
        if flashes is not None:
            response.flashes = json.loads(flashes)
        else:
            response.flashes = []

    def flash(self, message, level="info"):
        response.flashes.append({'message': message, "level": level })
        self.save_flashes()

    def get_flashes(self):
        flashes = response.flashes
        response.flashes = []
        return flashes

    def save_flashes(self):
        response.set_cookie(self.keyword, json.dumps(response.flashes), path="/", secret=self.secret)

    def apply(self, callback, route):

        def wrapper(*args, **kwargs):
            self.load_flashes()
            res = callback(*args, **kwargs)
            self.save_flashes()

            return res


        return wrapper





