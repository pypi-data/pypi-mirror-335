from elements import config, request, redirect

## Requires:
# name ----- for Session.login
# password - for Session.login

## Optional
# redirect - where to go once the login completes (default '/')

def login(**kwargs):
    app = kwargs.get('app')

    name = request.forms.get('name')
    password = request.forms.get('password')
    remember = request.forms.get('remember')
    redirect_path = request.forms.get('redirect') or request.query.get('redirect') or app.config.get('root') or '/'
    try:
        app.sessions.login(name, password, remember)
    except ValueError as e:
        if hasattr(app, 'flash'):
            app.flash(str(e), 'error')

        return redirect(app.get_url('login'))

    return redirect(redirect_path)

config['actions']['login'] = login

def logout(*args, **kwargs):
    pass
