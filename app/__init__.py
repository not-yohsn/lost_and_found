from flask import Flask
from flask_login import current_user

from .config import Config
from .extensions import db, login_manager, mail


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"
    mail.init_app(app)

    from . import models  # noqa: F401  (register models with SQLAlchemy)

    from .auth import auth_bp
    from .main import main_bp
    from .reports import reports_bp
    from .found import found_bp
    from .matches import matches_bp
    from .claims import claims_bp
    from .notifications import notifications_bp
    from .admin import admin_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(main_bp)
    app.register_blueprint(reports_bp, url_prefix="/reports")
    app.register_blueprint(found_bp, url_prefix="/found")
    app.register_blueprint(matches_bp, url_prefix="/matches")
    app.register_blueprint(claims_bp, url_prefix="/claims")
    app.register_blueprint(notifications_bp, url_prefix="/notifications")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    @app.context_processor
    def inject_unread_count():
        if not current_user.is_authenticated:
            return {"unread_notifications": 0}
        from .models import Notification
        count = Notification.query.filter_by(
            user_id=current_user.user_id, is_read=False
        ).count()
        return {"unread_notifications": count}

    return app
