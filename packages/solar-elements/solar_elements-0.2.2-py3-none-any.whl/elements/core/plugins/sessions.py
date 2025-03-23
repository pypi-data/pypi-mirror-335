import inspect
from elements import Session, WebSession, request, response, redirect
from elements.core.libs.encryption import nonce

class SessionManager:
    name = "sessions"
    api = 2

    def __init__(self, keyword="session", auth_path="login/", secret=None, add_to_request=False):
        self.sessions = {}
        self.keyword = keyword
        self.auth_path = auth_path
        self.secret = secret or nonce()
        self.add_to_request = add_to_request

    def setup(self, app):
        self.app = app
        self.app.sessions = self

    def apply(self, callback, route):
        allow = route.config.get('allow')

        # Check the args passed to the route, and bind
        # 'session' to the route if it is present.
        args = inspect.getfullargspec(route.callback)[0]

        if self.keyword not in args:
            return callback

        def wrapper(*args, **kwargs):
            # Get the session key and attempt to resolve
            # it to a session.
            session_key = request.get_cookie('session', secret=self.secret)
            if session_key is None:
                session = None
            else:
                session = self.sessions.get(session_key)
                if session is None:
                    response.delete_cookie('session', path="/")

            if session is None:
                nsec = request.get_cookie('auth', secret=self.secret)
                if nsec:
                    session = WebSession(nsec)
                    self.sessions[session.session_id] = session


            # Adding the session to the request makes it
            # accessible at request.session - This was
            # causing problems so it is off by default.
            if self.add_to_request:
                request.__setattr__('session', session)

            # The 'allow' keyword defines a list of groups
            # which are allowed to access the endpoint.
            # These groups are pulled from the Linux system.
            if allow:
                redirect_path = route.config.get('redirect', self.auth_path)
                redirect_path += f'?redirect={request.path}'
                not_authorized_path = route.config.get('not_authorized', redirect_path)

                allowed = False
                request.url

                if session is None:
                    return redirect(redirect_path)

                for group in allow:
                    if group in session.account.groups: 
                        allowed = True

                if not allowed:
                    return redirect(not_authorized_path)

            kwargs[self.keyword] = session
            return callback(*args, **kwargs)

        return wrapper

    def login(self, name, password, remember=None):
        s = Session.login(name, password)

        if remember:
            n = s.integration('nostr')
            print('remembering', n.npub)
            response.set_cookie('auth', n.nsec, path="/", maxage=60*60*24*52, secret=self.secret)
        key = s.session_id
        if s:
            self.sessions[key] = s

        response.set_cookie('session', key, path="/", maxage=60*60*24*52, secret=self.secret)

        return s



