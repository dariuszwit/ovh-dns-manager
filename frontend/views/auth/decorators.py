from flask import session, redirect, url_for
from functools import wraps

def login_required(f):
    """Dekorator sprawdzający, czy użytkownik jest zalogowany."""
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return wrap
