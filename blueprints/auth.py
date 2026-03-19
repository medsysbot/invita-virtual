from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db, login_manager
from models import User

bp = Blueprint("auth", __name__, url_prefix="/auth")

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            user.last_login = db.func.now()
            db.session.commit()
            return redirect(url_for("public.home"))
        flash("Credenciales inválidas", "error")
    return render_template("auth/login.html")

@bp.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email","").strip().lower()
        password = request.form.get("password","")
        if User.query.filter_by(email=email).first():
            flash("Email ya registrado", "error")
            return render_template("auth/register.html")
        user = User(email=email, role="client")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Cuenta creada. Inicie sesión.", "success")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html")

@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("public.home"))
