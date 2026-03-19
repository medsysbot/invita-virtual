from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Invitation, Plan, CustomRequest, Template, Order

bp = Blueprint("client", __name__, url_prefix="/client")

@bp.route("/dashboard")
@login_required
def dashboard():
    invs = Invitation.query.filter_by(user_id=current_user.id).order_by(Invitation.created_at.desc()).all()
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template("client/dashboard.html", invitations=invs, orders=orders)

@bp.route("/crear", methods=["GET","POST"])
@login_required
def crear():
    if request.method == "POST":
        mode = request.form.get("mode")
        if mode == "DIY":
            return redirect(url_for("client.elegir_plan"))
        if mode == "SERVICIO":
            return redirect(url_for("client.custom_request"))
        flash("Seleccione un modo.", "error")
    return render_template("client/select_mode.html")

@bp.route("/planes", methods=["GET","POST"])
@login_required
def elegir_plan():
    planes = Plan.query.filter_by(is_active=True).all()
    if request.method == "POST":
        plan_id = request.form.get("plan_id")
        plan = Plan.query.get(int(plan_id)) if plan_id else None
        if not plan:
            flash("Plan inválido", "error")
        else:
            inv = Invitation(user_id=current_user.id, plan_id=plan.id, status="draft")
            db.session.add(inv)
            db.session.commit()
            return redirect(url_for("client.editar_invitacion", invitation_id=inv.id))
    return render_template("client/select_plan.html", planes=planes)

@bp.route("/inv/<int:invitation_id>", methods=["GET","POST"])
@login_required
def editar_invitacion(invitation_id):
    inv = Invitation.query.filter_by(id=invitation_id, user_id=current_user.id).first_or_404()
    templates = Template.query.filter_by(is_active=True).all()
    if request.method == "POST":
        inv.title = request.form.get("title")
        inv.date_time = request.form.get("date_time")
        inv.venue = request.form.get("venue")
        inv.body_text = request.form.get("body_text")
        inv.template_id = int(request.form.get("template_id")) if request.form.get("template_id") else None
        db.session.commit()
        flash("Borrador guardado", "success")
    return render_template("client/create_invitation.html", inv=inv, templates=templates)

@bp.route("/custom", methods=["GET","POST"])
@login_required
def custom_request():
    if request.method == "POST":
        cr = CustomRequest(
            user_id=current_user.id,
            event_type=request.form.get("event_type"),
            event_date=request.form.get("event_date"),
            contact_name=request.form.get("contact_name"),
            phone=request.form.get("phone"),
            email=request.form.get("email"),
            details_text=request.form.get("details_text"),
            style_refs_text=request.form.get("style_refs_text"),
            budget_range=request.form.get("budget_range"),
            status="new",
        )
        db.session.add(cr)
        db.session.commit()
        flash("Solicitud enviada. Nos pondremos en contacto.", "success")
        return redirect(url_for("client.dashboard"))
    return render_template("client/custom_request.html")
