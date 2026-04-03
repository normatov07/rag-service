from contextvars import ContextVar

current_user = ContextVar('current_user', default=None)

def set_current_user(user):
    current_user.set(user)

def get_current_user():
    return current_user.get()