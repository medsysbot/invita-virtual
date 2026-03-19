from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from utils.decorators import admin_required
from models import User, Invitation, Order, CustomRequest, Plan, TipCategory, TipArticle

bp = Blueprint("admin", __name__, url_prefix="/admin")

@bp.route("/")
@admin_required
def dashboard():
    users_count = User.query.count()
    inv_count = Invitation.query.count()
    orders_count = Order.query.count()
    cr_count = CustomRequest.query.count()
    return render_template("admin/dashboard.html", users_count=users_count, inv_count=inv_count, orders_count=orders_count, cr_count=cr_count)

# Custom Requests
@bp.route("/custom-requests")
@admin_required
def custom_requests():
    items = CustomRequest.query.order_by(CustomRequest.created_at.desc()).all()
    return render_template("admin/custom_requests.html", items=items)

@bp.route("/custom-requests/<int:item_id>/set", methods=["POST"])
@admin_required
def custom_requests_set(item_id):
    item = CustomRequest.query.get_or_404(item_id)
    status = request.form.get("status")
    item.status = status
    db.session.commit()
    flash("Estado actualizado", "success")
    return redirect(url_for("admin.custom_requests"))

# Plans
@bp.route("/plans", methods=["GET","POST"])
@admin_required
def plans():
    if request.method == "POST":
        name = request.form.get("name")
        description = request.form.get("description")
        price = int(request.form.get("price") or 0)
        currency = request.form.get("currency") or "ARS"
        features_json = request.form.get("features_json") or "{}"
        p = Plan(name=name, description=description, price=price, currency=currency, features_json=features_json, is_active=True)
        db.session.add(p)
        db.session.commit()
        flash("Plan creado", "success")
    items = Plan.query.order_by(Plan.id.desc()).all()
    return render_template("admin/plans.html", items=items)

@bp.route("/plans/<int:plan_id>/toggle", methods=["POST"])
@admin_required
def plans_toggle(plan_id):
    p = Plan.query.get_or_404(plan_id)
    p.is_active = not p.is_active
    db.session.commit()
    return redirect(url_for("admin.plans"))

# Tips: Categories
@bp.route("/tips/categories", methods=["GET","POST"])
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

@bp.route("/tips/articles/new", methods=["GET","POST"])
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

@bp.route("/tips/articles/<int:art_id>/edit", methods=["GET","POST"])
@admin_required
def tip_article_edit(art_id):
    art = TipArticle.query.get_or_404(art_id)
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
    art = TipArticle.query.get_or_404(art_id)
    action = request.form.get("action")
    if action == "submit_for_review" and art.status == "draft":
        art.status = "in_review"
        art.submitted_by = current_user.id
        art.submitted_at = datetime.utcnow()
    elif action == "request_changes" and art.status == "in_review":
        art.status = "draft"
        art.review_notes = request.form.get("review_notes")
    elif action == "approve_and_publish" and art.status == "in_review":
        art.status = "published"
        art.reviewed_by = current_user.id
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
