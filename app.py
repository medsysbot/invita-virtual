import logging
import sys

from flask import Flask, render_template

from config import Config
from extensions import db, login_manager
from blueprints import auth as auth_bp
from blueprints import public as public_bp
from blueprints import client as client_bp
from blueprints import admin as admin_bp
from models import *


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    app.logger.setLevel(logging.INFO)
    app.logger.info("Iniciando aplicación")

    db.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "auth.login"
    login_manager.login_message = "Debes iniciar sesión para continuar."
    login_manager.login_message_category = "error"
    login_manager.session_protection = "strong"

    with app.app_context():
        db.create_all()

    app.register_blueprint(public_bp.bp)
    app.register_blueprint(auth_bp.bp)
    app.register_blueprint(client_bp.bp)
    app.register_blueprint(admin_bp.bp)

    @app.errorhandler(404)
    def not_found(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(error):
        app.logger.exception("Error interno del servidor: %s", error)
        return render_template("500.html"), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
