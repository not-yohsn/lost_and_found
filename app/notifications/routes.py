from flask import render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from . import notifications_bp
from ..extensions import db
from ..models import Notification


@notifications_bp.route("/")
@login_required
def index():
    notifs = (
        Notification.query
        .filter_by(user_id=current_user.user_id)
        .order_by(Notification.created_at.desc())
        .limit(50)
        .all()
    )
    return render_template("notifications/list.html", notifs=notifs)


@notifications_bp.route("/<int:notification_id>/open")
@login_required
def open_(notification_id):
    notif = Notification.query.get_or_404(notification_id)
    if notif.user_id != current_user.user_id:
        abort(403)
    notif.is_read = True
    db.session.commit()
    return redirect(notif.link or url_for("main.dashboard"))


@notifications_bp.route("/mark-all-read", methods=["POST"])
@login_required
def mark_all_read():
    Notification.query.filter_by(
        user_id=current_user.user_id, is_read=False
    ).update({"is_read": True})
    db.session.commit()
    flash("All notifications marked as read.", "info")
    return redirect(url_for("notifications.index"))
