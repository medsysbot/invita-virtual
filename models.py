from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from extensions import db

ROLE_CLIENT = "client"
ROLE_ADMIN = "admin"

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(32), default=ROLE_CLIENT, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    preview_asset_url = db.Column(db.String(512))

class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Integer, default=0)  # centavos/unidad mínima
    currency = db.Column(db.String(8), default="ARS")
    is_active = db.Column(db.Boolean, default=True)
    features_json = db.Column(db.Text)  # JSON en string

class Invitation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'))
    template_id = db.Column(db.Integer, db.ForeignKey('template.id'))
    title = db.Column(db.String(255))
    date_time = db.Column(db.String(64))
    venue = db.Column(db.String(255))
    body_text = db.Column(db.Text)
    status = db.Column(db.String(32), default="draft")  # draft, pending_payment, paid
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    invitation_id = db.Column(db.Integer, db.ForeignKey('invitation.id'))
    amount = db.Column(db.Integer, default=0)
    currency = db.Column(db.String(8), default="ARS")
    status = db.Column(db.String(32), default="pending")  # pending, paid, failed, canceled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    provider = db.Column(db.String(64), default="stub")
    provider_charge_id = db.Column(db.String(128))
    status = db.Column(db.String(32), default="pending")
    paid_at = db.Column(db.DateTime)
    raw_payload = db.Column(db.Text)

class Testimonial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_name = db.Column(db.String(120))
    text = db.Column(db.Text)
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Tips
class TipCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('tip_category.id'), nullable=True)
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    position = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TipArticle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('tip_category.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False)
    summary = db.Column(db.Text)
    body_richtext = db.Column(db.Text)
    hero_asset_url = db.Column(db.String(512))
    status = db.Column(db.String(32), default="draft")  # draft, in_review, published, archived
    submitted_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    submitted_at = db.Column(db.DateTime, nullable=True)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    review_notes = db.Column(db.Text, nullable=True)
    published_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TipTag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)

class TipArticleTag(db.Model):
    article_id = db.Column(db.Integer, db.ForeignKey('tip_article.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tip_tag.id'), primary_key=True)

class CustomRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    event_type = db.Column(db.String(120))
    event_date = db.Column(db.String(64))
    contact_name = db.Column(db.String(120))
    phone = db.Column(db.String(64))
    email = db.Column(db.String(255))
    details_text = db.Column(db.Text)
    style_refs_text = db.Column(db.Text)
    budget_range = db.Column(db.String(64))
    attachments_count = db.Column(db.Integer, default=0)
    status = db.Column(db.String(32), default="new")  # new, in_review, quoted, approved, canceled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
