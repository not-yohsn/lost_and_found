from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .extensions import db, login_manager


class User(UserMixin, db.Model):
    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20))
    role = db.Column(
        db.Enum("student", "staff", "admin", name="user_role"),
        nullable=False,
        default="student",
    )
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    lost_reports = db.relationship(
        "LostReport", back_populates="user", cascade="all, delete-orphan"
    )
    notifications = db.relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan",
        order_by="Notification.created_at.desc()",
    )

    def get_id(self):
        return str(self.user_id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Finder(db.Model):
    __tablename__ = "finders"

    finder_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    found_items = db.relationship("FoundItem", back_populates="finder")


class LostReport(db.Model):
    __tablename__ = "lost_reports"

    report_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    item_name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(60))
    location = db.Column(db.String(120))
    date_lost = db.Column(db.Date)
    photo_path = db.Column(db.String(255))
    status = db.Column(
        db.Enum("reported", "matched", "claimed", "closed", name="lost_status"),
        default="reported",
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="lost_reports")
    match = db.relationship("Match", back_populates="lost_report", uselist=False)


class FoundItem(db.Model):
    __tablename__ = "found_items"

    item_id = db.Column(db.Integer, primary_key=True)
    finder_id = db.Column(db.Integer, db.ForeignKey("finders.finder_id"))
    logged_by = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    item_name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(60))
    location_found = db.Column(db.String(120))
    date_found = db.Column(db.Date)
    photo_path = db.Column(db.String(255))
    status = db.Column(
        db.Enum("logged", "matched", "released", name="found_status"),
        default="logged",
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    finder = db.relationship("Finder", back_populates="found_items")
    match = db.relationship("Match", back_populates="found_item", uselist=False)


class Match(db.Model):
    __tablename__ = "matches"

    match_id = db.Column(db.Integer, primary_key=True)
    lost_report_id = db.Column(
        db.Integer, db.ForeignKey("lost_reports.report_id"), unique=True, nullable=False
    )
    found_item_id = db.Column(
        db.Integer, db.ForeignKey("found_items.item_id"), unique=True, nullable=False
    )
    matched_at = db.Column(db.DateTime, default=datetime.utcnow)
    confidence_score = db.Column(db.Float)

    lost_report = db.relationship("LostReport", back_populates="match")
    found_item = db.relationship("FoundItem", back_populates="match")
    claims = db.relationship("Claim", back_populates="match", cascade="all, delete-orphan")


class Claim(db.Model):
    __tablename__ = "claims"

    claim_id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey("matches.match_id"), nullable=False)
    claimant_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable=False)
    verified_by = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    status = db.Column(
        db.Enum("pending", "approved", "rejected", "released", name="claim_status"),
        default="pending",
    )
    notes = db.Column(db.Text)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)

    match = db.relationship("Match", back_populates="claims")
    claimant = db.relationship("User", foreign_keys=[claimant_id])
    verifier = db.relationship("User", foreign_keys=[verified_by])


class Notification(db.Model):
    __tablename__ = "notifications"

    notification_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.user_id"), nullable=False, index=True
    )
    title = db.Column(db.String(160), nullable=False)
    body = db.Column(db.Text)
    link = db.Column(db.String(255))
    is_read = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="notifications")
