from app import app, db
from models import User, ROLE_ADMIN, Template, Plan, TipCategory, TipArticle
import json

with app.app_context():
    db.create_all()
    if not User.query.filter_by(email="admin@example.com").first():
        admin = User(full_name="Admin Demo", email="admin@example.com", phone=None, role=ROLE_ADMIN, is_active=True, accepted_terms=True)
        admin.set_password("admin12345")
        db.session.add(admin)
    if not User.query.filter_by(email="client@example.com").first():
        client = User(full_name="Cliente Demo", email="client@example.com", phone="1155555555", role="client", is_active=True, accepted_terms=True)
        client.set_password("client12345")
        db.session.add(client)
    if not Template.query.first():
        db.session.add(Template(name="Clásica", description="Plantilla clásica", preview_asset_url="/static/img/placeholder.png"))
        db.session.add(Template(name="Moderna", description="Plantilla moderna", preview_asset_url="/static/img/placeholder.png"))
    if not Plan.query.first():
        db.session.add(Plan(name="Básico", description="Funciones esenciales", price=100000, currency="ARS", features_json=json.dumps({"max_sections":3,"export_pdf":False,"export_link":True})))
        db.session.add(Plan(name="Pro", description="Funciones avanzadas", price=200000, currency="ARS", features_json=json.dumps({"max_sections":10,"export_pdf":True,"export_link":True})))
    if not TipCategory.query.first():
        cas = TipCategory(name="Casamientos", slug="casamientos", position=1, is_active=True)
        cum = TipCategory(name="Cumpleaños", slug="cumpleanos", position=2, is_active=True)
        db.session.add_all([cas, cum])
        db.session.flush()
        for pos, (name, slug) in enumerate([("15 años","15-anos"), ("Niños","ninos"), ("Adultos","adultos"), ("Tercera edad","tercera-edad")], start=1):
            db.session.add(TipCategory(name=name, slug=slug, parent_id=cum.id, position=pos, is_active=True))
    if not TipArticle.query.first():
        first_cat = TipCategory.query.first()
        db.session.add(TipArticle(category_id=first_cat.id, title="Checklist inicial para tu evento", slug="checklist-inicial-evento", summary="Guía base para empezar a organizar tu celebración.", body_richtext="<h2>Checklist</h2><p>Define presupuesto, invitados, lugar y estilo visual.</p>", status="published"))
    db.session.commit()
    print("Seed OK")
