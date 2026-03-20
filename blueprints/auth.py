import secrets
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db, login_manager
from models import User, PasswordResetToken, ROLE_ADMIN, ROLE_CLIENT

bp = Blueprint("auth", __name__, url_prefix="/auth")

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def _normalize_email(value):
    return (value or "").strip().lower()


def _redirect_after_login(user):
    if user.role == ROLE_ADMIN:
        return redirect(url_for("admin.dashboard"))
    return redirect(url_for("client.dashboard"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return _redirect_after_login(current_user)

    if request.method == "POST":
        email = _normalize_email(request.form.get("email"))
        password = request.form.get("password", "")
        remember = request.form.get("remember_me") == "1"

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Credenciales inválidas.", "error")
            return render_template("auth/login.html")
        if not user.is_active:
            flash("Tu cuenta está inactiva. Contacta al administrador.", "error")
            return render_template("auth/login.html")

        login_user(user, remember=remember)
        user.last_login = datetime.utcnow()
        db.session.commit()
        flash(f"Bienvenido, {user.full_name}.", "success")
        return _redirect_after_login(user)

    return render_template("auth/login.html")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return _redirect_after_login(current_user)

    if request.method == "POST":
        full_name = (request.form.get("full_name") or "").strip()
        email = _normalize_email(request.form.get("email"))
        phone = (request.form.get("phone") or "").strip() or None
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        accept_terms = request.form.get("accept_terms") == "1"

        if not full_name:
            flash("El nombre completo es obligatorio.", "error")
            return render_template("auth/register.html")
        if not email:
            flash("El correo electrónico es obligatorio.", "error")
            return render_template("auth/register.html")
        if len(password) < 8:
            flash("La contraseña debe tener al menos 8 caracteres.", "error")
            return render_template("auth/register.html")
        if password != confirm_password:
            flash("Las contraseñas no coinciden.", "error")
            return render_template("auth/register.html")
        if not accept_terms:
            flash("Debes aceptar los términos y condiciones.", "error")
            return render_template("auth/register.html")
        if User.query.filter_by(email=email).first():
            flash("Ese correo ya está registrado.", "error")
            return render_template("auth/register.html")

        user = User(
            full_name=full_name,
            email=email,
            phone=phone,
            role=ROLE_CLIENT,
            is_active=True,
            accepted_terms=True,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Cuenta creada correctamente. Ya puedes ingresar.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    reset_url = None
    if request.method == "POST":
        email = _normalize_email(request.form.get("email"))
        user = User.query.filter_by(email=email).first()
        if not user or not user.is_active:
            flash("Si el correo existe y está activo, se generó un enlace de recuperación.", "success")
            return render_template("auth/forgot_password.html", reset_url=None)

        PasswordResetToken.query.filter_by(user_id=user.id, used_at=None).delete()
        token = secrets.token_urlsafe(32)
        reset = PasswordResetToken.issue(user_id=user.id, token=token, minutes=60)
        db.session.add(reset)
        db.session.commit()
        reset_url = url_for("auth.reset_password", token=token, _external=True)
        flash("Enlace de recuperación generado correctamente.", "success")
    return render_template("auth/forgot_password.html", reset_url=reset_url)


@bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    reset = PasswordResetToken.query.filter_by(token=token).first()
    if not reset or not reset.is_valid:
        flash("El enlace de recuperación es inválido o ya venció.", "error")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        new_password = request.form.get("new_password", "")
        confirm_new_password = request.form.get("confirm_new_password", "")
        if len(new_password) < 8:
            flash("La nueva contraseña debe tener al menos 8 caracteres.", "error")
            return render_template("auth/reset_password.html")
        if new_password != confirm_new_password:
            flash("Las contraseñas no coinciden.", "error")
            return render_template("auth/reset_password.html")

        user = db.session.get(User, reset.user_id)
        user.set_password(new_password)
        reset.used_at = datetime.utcnow()
        db.session.commit()
        flash("Tu contraseña fue actualizada. Ya puedes ingresar.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html")


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente.", "success")
    return redirect(url_for("public.home"))
