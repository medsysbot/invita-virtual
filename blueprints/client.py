import json
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user
from extensions import db
from models import Invitation, Plan, CustomRequest, Template, Order
from utils.decorators import client_required

bp = Blueprint("client", __name__, url_prefix="/client")


def _order_for_invitation(invitation_id):
    return Order.query.filter_by(invitation_id=invitation_id).order_by(Order.id.desc()).first()


@bp.route("/dashboard")
@client_required
def dashboard():
    invs = Invitation.query.filter_by(user_id=current_user.id).order_by(Invitation.created_at.desc()).all()
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    custom_requests = CustomRequest.query.filter_by(user_id=current_user.id).order_by(CustomRequest.created_at.desc()).all()
    stats = {
        "invitations": len(invs),
        "orders": len(orders),
        "pending_orders": len([o for o in orders if o.status == "pending"]),
        "custom_requests": len(custom_requests),
    }
    return render_template("client/dashboard.html", invitations=invs, orders=orders, custom_requests=custom_requests, stats=stats)


@bp.route("/crear", methods=["GET", "POST"])
@client_required
def crear():
    if request.method == "POST":
        mode = request.form.get("mode")
        if mode == "DIY":
            return redirect(url_for("client.elegir_plan"))
        if mode == "SERVICIO":
            return redirect(url_for("client.custom_request"))
        flash("Seleccione un modo.", "error")
    return render_template("client/select_mode.html")


@bp.route("/planes", methods=["GET", "POST"])
@client_required
def elegir_plan():
    planes = Plan.query.filter_by(is_active=True).order_by(Plan.price.asc(), Plan.id.asc()).all()
    if request.method == "POST":
        plan_id = request.form.get("plan_id")
        plan = db.session.get(Plan, int(plan_id)) if plan_id else None
        if not plan:
            flash("Plan inválido", "error")
        else:
            inv = Invitation(user_id=current_user.id, plan_id=plan.id, status="draft")
            db.session.add(inv)
            db.session.commit()
            return redirect(url_for("client.editar_invitacion", invitation_id=inv.id))
    return render_template("client/select_plan.html", planes=planes)


@bp.route("/inv/<int:invitation_id>", methods=["GET", "POST"])
@client_required
def editar_invitacion(invitation_id):
    inv = Invitation.query.filter_by(id=invitation_id, user_id=current_user.id).first_or_404()
    templates = Template.query.filter_by(is_active=True).all()
    plan = db.session.get(Plan, inv.plan_id) if inv.plan_id else None
    features = {}
    if plan and plan.features_json:
        try:
            features = json.loads(plan.features_json)
        except Exception:
            features = {}
    if request.method == "POST":
        inv.title = (request.form.get("title") or "").strip()
        inv.date_time = (request.form.get("date_time") or "").strip()
        inv.venue = (request.form.get("venue") or "").strip()
        inv.body_text = (request.form.get("body_text") or "").strip()
        inv.template_id = int(request.form.get("template_id")) if request.form.get("template_id") else None
        db.session.commit()
        if request.form.get("action") == "save_and_preview":
            flash("Borrador guardado. Puedes revisar la vista previa.", "success")
            return redirect(url_for("client.preview_invitation", invitation_id=inv.id))
        flash("Borrador guardado", "success")
    return render_template("client/create_invitation.html", inv=inv, templates=templates, plan=plan, features=features)


@bp.route("/inv/<int:invitation_id>/preview")
@client_required
def preview_invitation(invitation_id):
    inv = Invitation.query.filter_by(id=invitation_id, user_id=current_user.id).first_or_404()
    plan = db.session.get(Plan, inv.plan_id) if inv.plan_id else None
    template = db.session.get(Template, inv.template_id) if inv.template_id else None
    order = _order_for_invitation(inv.id)
    return render_template("client/invitation_preview.html", inv=inv, plan=plan, template=template, order=order)


@bp.route("/inv/<int:invitation_id>/checkout", methods=["GET", "POST"])
@client_required
def checkout(invitation_id):
    inv = Invitation.query.filter_by(id=invitation_id, user_id=current_user.id).first_or_404()
    plan = db.session.get(Plan, inv.plan_id) if inv.plan_id else None
    order = _order_for_invitation(inv.id)
    if request.method == "POST":
        if not plan:
            flash("La invitación no tiene un plan asignado.", "error")
            return redirect(url_for("client.editar_invitacion", invitation_id=inv.id))
        if not order:
            order = Order(user_id=current_user.id, invitation_id=inv.id, amount=plan.price, currency=plan.currency, status="pending")
            db.session.add(order)
        else:
            order.amount = plan.price
            order.currency = plan.currency
            order.status = "pending"
        inv.status = "pending_payment"
        db.session.commit()
        flash("Pedido generado. Ya puedes simular el pago.", "success")
        return redirect(url_for("client.preview_invitation", invitation_id=inv.id))
    return render_template("client/checkout.html", inv=inv, plan=plan, order=order)


@bp.route("/orders/<int:order_id>/pay", methods=["POST"])
@client_required
def pay_order(order_id):
    order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    order.status = "paid"
    invitation = db.session.get(Invitation, order.invitation_id) if order.invitation_id else None
    if invitation:
        invitation.status = "paid"
    db.session.commit()
    flash("Pago registrado en modo demo.", "success")
    return redirect(url_for("client.dashboard"))


@bp.route("/custom", methods=["GET", "POST"])
@client_required
def custom_request():
    if request.method == "POST":
        cr = CustomRequest(
            user_id=current_user.id,
            event_type=(request.form.get("event_type") or "").strip(),
            event_date=(request.form.get("event_date") or "").strip(),
            contact_name=(request.form.get("contact_name") or current_user.full_name).strip(),
            phone=(request.form.get("phone") or current_user.phone or "").strip() or None,
            email=(request.form.get("email") or current_user.email).strip(),
            details_text=(request.form.get("details_text") or "").strip(),
            style_refs_text=(request.form.get("style_refs_text") or "").strip(),
            budget_range=(request.form.get("budget_range") or "-").strip(),
            status="new",
        )
        db.session.add(cr)
        db.session.commit()
        flash("Solicitud enviada. Nos pondremos en contacto.", "success")
        return redirect(url_for("client.dashboard"))
    return render_template("client/custom_request.html")
