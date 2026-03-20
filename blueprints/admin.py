import json
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from utils.decorators import admin_required
from models import User, Invitation, Order, CustomRequest, Plan, TipCategory, TipArticle, ROLE_ADMIN, ROLE_CLIENT

bp = Blueprint("admin", __name__, url_prefix="/admin")


def _safe_json(value):
    if not value:
        return {}
    try:
        return json.loads(value)
    except Exception:
        return {}


@bp.route("/")
@admin_required
def dashboard():
    users_count = User.query.count()
    client_count = User.query.filter_by(role=ROLE_CLIENT).count()
    admin_count = User.query.filter_by(role=ROLE_ADMIN).count()
    inv_count = Invitation.query.count()
    orders_count = Order.query.count()
    pending_orders = Order.query.filter_by(status="pending").count()
    paid_orders = Order.query.filter_by(status="paid").count()
    cr_count = CustomRequest.query.count()
    tips_review = TipArticle.query.filter_by(status="in_review").count()
    latest_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    latest_requests = CustomRequest.query.order_by(CustomRequest.created_at.desc()).limit(5).all()
    return render_template(
        "admin/dashboard.html",
        users_count=users_count,
        client_count=client_count,
        admin_count=admin_count,
        inv_count=inv_count,
        orders_count=orders_count,
        pending_orders=pending_orders,
        paid_orders=paid_orders,
        cr_count=cr_count,
        tips_review=tips_review,
        latest_orders=latest_orders,
        latest_requests=latest_requests,
    )


@bp.route("/users")
@admin_required
def users():
    role = request.args.get("role", "")
    q = User.query
    if role in (ROLE_CLIENT, ROLE_ADMIN):
        q = q.filter_by(role=role)
    items = q.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", items=items, role=role)


@bp.route("/users/new-admin", methods=["GET", "POST"])
@admin_required
def user_new_admin():
    if request.method == "POST":
        full_name = (request.form.get("full_name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        phone = (request.form.get("phone") or "").strip() or None
        password = request.form.get("password") or ""
        confirm_password = request.form.get("confirm_password") or ""

        if not full_name or not email:
            flash("Nombre y correo son obligatorios.", "error")
            return render_template("admin/user_new_admin.html")
        if len(password) < 8:
            flash("La contraseña debe tener al menos 8 caracteres.", "error")
            return render_template("admin/user_new_admin.html")
        if password != confirm_password:
            flash("Las contraseñas no coinciden.", "error")
            return render_template("admin/user_new_admin.html")
        if User.query.filter_by(email=email).first():
            flash("Ese correo ya existe.", "error")
            return render_template("admin/user_new_admin.html")

        user = User(full_name=full_name, email=email, phone=phone, role=ROLE_ADMIN, is_active=True, accepted_terms=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Administrador creado correctamente.", "success")
        return redirect(url_for("admin.users", role=ROLE_ADMIN))
    return render_template("admin/user_new_admin.html")


@bp.route("/users/<int:user_id>")
@admin_required
def user_detail(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash("Usuario no encontrado.", "error")
        return redirect(url_for("admin.users"))
    invitations = Invitation.query.filter_by(user_id=user.id).order_by(Invitation.created_at.desc()).all()
    orders = Order.query.filter_by(user_id=user.id).order_by(Order.created_at.desc()).all()
    custom_requests = CustomRequest.query.filter_by(user_id=user.id).order_by(CustomRequest.created_at.desc()).all()
    return render_template("admin/user_detail.html", user=user, invitations=invitations, orders=orders, custom_requests=custom_requests)


@bp.route("/users/<int:user_id>/update", methods=["POST"])
@admin_required
def user_update(user_id):
    user = db.session.get(User, user_id)
    if not user:
        flash("Usuario no encontrado.", "error")
        return redirect(url_for("admin.users"))
    role = request.form.get("role")
    is_active = request.form.get("is_active") == "1"
    if role not in (ROLE_CLIENT, ROLE_ADMIN):
        flash("Rol inválido.", "error")
        return redirect(url_for("admin.user_detail", user_id=user.id))
    user.role = role
    user.is_active = is_active
    db.session.commit()
    flash("Usuario actualizado.", "success")
    return redirect(url_for("admin.user_detail", user_id=user.id))


@bp.route("/invitations")
@admin_required
def invitations():
    items = Invitation.query.order_by(Invitation.created_at.desc()).all()
    users_map = {u.id: u for u in User.query.all()}
    plans_map = {p.id: p for p in Plan.query.all()}
    return render_template("admin/invitations.html", items=items, users_map=users_map, plans_map=plans_map)


@bp.route("/orders")
@admin_required
def orders():
    items = Order.query.order_by(Order.created_at.desc()).all()
    users_map = {u.id: u for u in User.query.all()}
    invitations_map = {i.id: i for i in Invitation.query.all()}
    return render_template("admin/orders.html", items=items, users_map=users_map, invitations_map=invitations_map)


@bp.route("/orders/<int:order_id>/set", methods=["POST"])
@admin_required
def orders_set(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        flash("Pedido no encontrado.", "error")
        return redirect(url_for("admin.orders"))
    status = request.form.get("status")
    if status not in ("pending", "paid", "failed", "canceled"):
        flash("Estado inválido.", "error")
        return redirect(url_for("admin.orders"))
    order.status = status
    invitation = db.session.get(Invitation, order.invitation_id) if order.invitation_id else None
    if invitation:
        invitation.status = "paid" if status == "paid" else "pending_payment"
    db.session.commit()
    flash("Estado del pedido actualizado.", "success")
    return redirect(url_for("admin.orders"))


# Custom Requests
@bp.route("/custom-requests")
@admin_required
def custom_requests():
    items = CustomRequest.query.order_by(CustomRequest.created_at.desc()).all()
    users_map = {u.id: u for u in User.query.all()}
    return render_template("admin/custom_requests.html", items=items, users_map=users_map)


@bp.route("/custom-requests/<int:item_id>/set", methods=["POST"])
@admin_required
def custom_requests_set(item_id):
    item = db.session.get(CustomRequest, item_id)
    if not item:
        flash("Solicitud no encontrada.", "error")
        return redirect(url_for("admin.custom_requests"))
    status = request.form.get("status")
    if status not in ("new", "in_review", "quoted", "approved", "canceled"):
        flash("Estado inválido.", "error")
        return redirect(url_for("admin.custom_requests"))
    item.status = status
    db.session.commit()
    flash("Estado actualizado", "success")
    return redirect(url_for("admin.custom_requests"))


# Plans
@bp.route("/plans", methods=["GET", "POST"])
@admin_required
def plans():
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        description = (request.form.get("description") or "").strip()
        price = int(request.form.get("price") or 0)
        currency = request.form.get("currency") or "ARS"
        features_json = request.form.get("features_json") or "{}"
        p = Plan(name=name, description=description, price=price, currency=currency, features_json=features_json, is_active=True)
        db.session.add(p)
        db.session.commit()
        flash("Plan creado", "success")
    items = Plan.query.order_by(Plan.price.asc(), Plan.id.desc()).all()
    items_features = {item.id: _safe_json(item.features_json) for item in items}
    return render_template("admin/plans.html", items=items, items_features=items_features)


@bp.route("/plans/<int:plan_id>/toggle", methods=["POST"])
@admin_required
def plans_toggle(plan_id):
    p = db.session.get(Plan, plan_id)
    if not p:
        flash("Plan no encontrado.", "error")
        return redirect(url_for("admin.plans"))
    p.is_active = not p.is_active
    db.session.commit()
    flash("Estado del plan actualizado.", "success")
    return redirect(url_for("admin.plans"))


# Tips: Categories
@bp.route("/tips/categories", methods=["GET", "POST"])
@admin_required
def tip_categories():
    if request.method == "POST":
        name = request.form.get("name")
        slug = request.form.get("slug")
        position = int(request.form.get("position") or 0)
        parent_id = int(request.form.get("parent_id")) if request.form.get("parent_id") else None
        c = TipCategory(name=name, slug=slug, position=position, parent_id=parent_id, is_active=True)
        db.session.add(c)
        db.session.commit()
        flash("Categoría creada", "success")
    cats = TipCategory.query.order_by(TipCategory.position.asc()).all()
    return render_template("admin/tip_categories.html", cats=cats)


# Tips: Articles
@bp.route("/tips/articles")
@admin_required
def tip_articles():
    status = request.args.get("status")
    q = TipArticle.query
    if status:
        q = q.filter_by(status=status)
    items = q.order_by(TipArticle.updated_at.desc()).limit(200).all()
    cats = TipCategory.query.order_by(TipCategory.position.asc()).all()
    return render_template("admin/tip_articles.html", items=items, cats=cats)


@bp.route("/tips/articles/new", methods=["GET", "POST"])
@admin_required
def tip_article_new():
    cats = TipCategory.query.order_by(TipCategory.position.asc()).all()
    if request.method == "POST":
        art = TipArticle(
            category_id=int(request.form.get("category_id")),
            title=request.form.get("title"),
            slug=request.form.get("slug"),
            summary=request.form.get("summary"),
            body_richtext=request.form.get("body_richtext"),
            status="draft",
        )
        db.session.add(art)
        db.session.commit()
        flash("Artículo creado (borrador)", "success")
        return redirect(url_for("admin.tip_articles"))
    return render_template("admin/tip_form.html", cats=cats, art=None)


@bp.route("/tips/articles/<int:art_id>/edit", methods=["GET", "POST"])
@admin_required
def tip_article_edit(art_id):
    art = db.session.get(TipArticle, art_id)
    if not art:
        flash("Artículo no encontrado.", "error")
        return redirect(url_for("admin.tip_articles"))
    cats = TipCategory.query.order_by(TipCategory.position.asc()).all()
    if request.method == "POST":
        art.category_id = int(request.form.get("category_id"))
        art.title = request.form.get("title")
        art.slug = request.form.get("slug")
        art.summary = request.form.get("summary")
        art.body_richtext = request.form.get("body_richtext")
        db.session.commit()
        flash("Artículo actualizado", "success")
        return redirect(url_for("admin.tip_articles"))
    return render_template("admin/tip_form.html", cats=cats, art=art)


@bp.route("/tips/articles/<int:art_id>/transition", methods=["POST"])
@admin_required
def tip_article_transition(art_id):
    art = db.session.get(TipArticle, art_id)
    if not art:
        flash("Artículo no encontrado.", "error")
        return redirect(url_for("admin.tip_articles"))
    action = request.form.get("action")
    if action == "submit_for_review" and art.status == "draft":
        art.status = "in_review"
        art.submitted_by = request.form.get("submitted_by") or None
        art.submitted_at = datetime.utcnow()
    elif action == "request_changes" and art.status == "in_review":
        art.status = "draft"
        art.review_notes = request.form.get("review_notes")
    elif action == "approve_and_publish" and art.status == "in_review":
        art.status = "published"
        art.reviewed_by = request.form.get("reviewed_by") or None
        art.reviewed_at = datetime.utcnow()
        art.published_at = datetime.utcnow()
    elif action == "archive" and art.status == "published":
        art.status = "archived"
    elif action == "restore_to_draft" and art.status == "archived":
        art.status = "draft"
    else:
        flash("Transición no permitida", "error")
        return redirect(url_for("admin.tip_articles"))
    db.session.commit()
    flash("Estado actualizado", "success")
    return redirect(url_for("admin.tip_articles"))
