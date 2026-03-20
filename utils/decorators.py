from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user
from models import ROLE_ADMIN, ROLE_CLIENT


def login_required(view):
    from flask_login import login_required as flask_login_required
    return flask_login_required(view)


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.admin_login"))
        if current_user.role != ROLE_ADMIN:
            flash("Acceso restringido.", "error")
            return redirect(url_for("public.home"))
        return view(*args, **kwargs)
    return wrapped


def client_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        if current_user.role != ROLE_CLIENT:
            flash("Esta sección es solo para clientes.", "error")
            return redirect(url_for("admin.dashboard" if current_user.role == ROLE_ADMIN else "public.home"))
        return view(*args, **kwargs)
    return wrapped
