from flask import Blueprint, render_template, request, abort
from models import TipCategory, TipArticle

bp = Blueprint("public", __name__)


@bp.route("/")
def home():
    cats = []
    latest = []

    try:
        cats = (
            TipCategory.query
            .filter_by(is_active=True)
            .order_by(TipCategory.position.asc())
            .all()
        )

        latest = (
            TipArticle.query
            .filter_by(status="published")
            .order_by(TipArticle.published_at.desc())
            .limit(5)
            .all()
        )
    except Exception:
        cats = []
        latest = []

    return render_template("public/home.html", cats=cats, latest=latest)


@bp.route("/tips")
def tips_index():
    q = request.args.get("q", "").strip()
    articles = []
    cats = []

    try:
        articles_query = TipArticle.query.filter(TipArticle.status == "published")

        if q:
            like = f"%{q}%"
            articles_query = articles_query.filter(
                (TipArticle.title.ilike(like))
                | (TipArticle.summary.ilike(like))
                | (TipArticle.body_richtext.ilike(like))
            )

        articles = (
            articles_query
            .order_by(
                TipArticle.published_at.desc().nullslast(),
                TipArticle.id.desc()
            )
            .limit(50)
            .all()
        )

        cats = (
            TipCategory.query
            .filter_by(is_active=True)
            .order_by(TipCategory.position.asc())
            .all()
        )
    except Exception:
        articles = []
        cats = []

    return render_template(
        "public/tips_index.html",
        articles=articles,
        cats=cats,
        q=q,
    )


@bp.route("/tips/c/<slug>")
def tips_category(slug):
    try:
        cat = TipCategory.query.filter_by(slug=slug, is_active=True).first_or_404()

        articles = (
            TipArticle.query
            .filter_by(category_id=cat.id, status="published")
            .order_by(
                TipArticle.published_at.desc().nullslast(),
                TipArticle.id.desc()
            )
            .all()
        )

        return render_template(
            "public/tips_category.html",
            cat=cat,
            articles=articles,
        )
    except Exception:
        return render_template(
            "public/tips_index.html",
            articles=[],
            cats=[],
            q="",
        )


@bp.route("/tips/a/<slug>")
def tip_view(slug):
    try:
        art = TipArticle.query.filter_by(slug=slug, status="published").first_or_404()
        return render_template("public/tip_view.html", art=art)
    except Exception:
        abort(404)
