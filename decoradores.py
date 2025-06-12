from flask import abort
from flask_login import current_user
from functools import wraps

def permissao_requerida(*perfis):
    def decorador(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if current_user.perfil not in perfis:
                abort(403)  # acesso negado
            return func(*args, **kwargs)
        return wrapper
    return decorador
