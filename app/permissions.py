from flask import abort
from flask_login import current_user
from functools import wraps


def permissao_requerida(*perfis):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if current_user.perfil not in perfis:
                abort(403)
            return func(*args, **kwargs)
        return wrapper
    return decorator