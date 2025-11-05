from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from flask_login import UserMixin
from app import login
import secrets
from hashlib import md5

class User(UserMixin, db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(
        default=lambda: datetime.now(timezone.utc))
    links: so.WriteOnlyMapped['Link'] = so.relationship(
        back_populates='creator'
    )
    groups: so.WriteOnlyMapped['Group'] = so.relationship(
        back_populates='creator'
    )

    def __repr__(self):
        return '<User {}>'.format(self.email)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size
        )

class Group(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(120), index=True)
    description: so.Mapped[Optional[str]] = so.mapped_column(sa.String(500))
    max_capacity: so.Mapped[int] = so.mapped_column(default=0)  # 0 means unlimited
    current_count: so.Mapped[int] = so.mapped_column(default=0)
    expiration_type: so.Mapped[str] = so.mapped_column(sa.String(20), default='never')  # 'never' or 'hours'
    expiration_hours: so.Mapped[Optional[int]] = so.mapped_column(default=None)  # Hours until expiration
    created_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime(timezone=True), index=True, default=lambda: datetime.now(timezone.utc))
    user_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey(User.id), index=True
    )

    creator: so.Mapped[User] = so.relationship(back_populates='groups')
    links: so.WriteOnlyMapped['Link'] = so.relationship(back_populates='group')
    forms: so.WriteOnlyMapped['Form'] = so.relationship(back_populates='group')

    def __repr__(self):
        return '<Group {}>'.format(self.name)

    def is_full(self):
        """Check if group has reached capacity"""
        if self.max_capacity == 0:  # 0 means unlimited
            return False
        return self.current_count >= self.max_capacity

class Link(db.Model):
    id: so.Mapped[str] = so.mapped_column(sa.String(22), primary_key=True, default=lambda: secrets.token_urlsafe(16))
    created_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime(timezone=True), index=True)
    end_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime(timezone=True), index=True)
    user_id: so.Mapped[int] = so.mapped_column(
        sa.ForeignKey(User.id), index=True
    )
    group_id: so.Mapped[Optional[int]] = so.mapped_column(
        sa.ForeignKey(Group.id), index=True
    )
    used: so.Mapped[bool] = so.mapped_column(default=False)

    creator: so.Mapped[User] = so.relationship(back_populates='links')
    group: so.Mapped[Optional[Group]] = so.relationship(back_populates='links')

    def __repr__(self):
        return '<Link {}>'.format(self.id)

    def is_active(self):
        now = datetime.now(timezone.utc)
        return (not self.used) and (self.end_at.replace(tzinfo=timezone.utc) > now)

class Form(db.Model):
    id: so.Mapped[str] = so.mapped_column(sa.String(22), primary_key=True)
    first_name: so.Mapped[str] = so.mapped_column(sa.String(50))
    middle_name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(50))
    last_name: so.Mapped[str] = so.mapped_column(sa.String(50))
    eye_color: so.Mapped[str] = so.mapped_column(sa.String(30))
    hair_color: so.Mapped[str] = so.mapped_column(sa.String(30))
    address: so.Mapped[Optional[str]] = so.mapped_column(sa.String(200))
    date_of_birth: so.Mapped[datetime] = so.mapped_column(sa.DateTime)
    height: so.Mapped[float]
    weight: so.Mapped[float]
    state: so.Mapped[str] = so.mapped_column(sa.String(2))
    city: so.Mapped[str] = so.mapped_column(sa.String(100))
    zip_code: so.Mapped[str] = so.mapped_column(sa.String(100))
    organ_donor: so.Mapped[bool] = so.mapped_column()
    restrictions_corrective_lenses: so.Mapped[bool] = so.mapped_column()
    gender: so.Mapped[str] = so.mapped_column(sa.String(10))
    group_id: so.Mapped[Optional[int]] = so.mapped_column(
        sa.ForeignKey(Group.id), index=True
    )
    submitted_at: so.Mapped[datetime] = so.mapped_column(sa.DateTime(timezone=True), index=True, default=lambda: datetime.now(timezone.utc))

    group: so.Mapped[Optional[Group]] = so.relationship(back_populates='forms')

    def __repr__(self):
        return '<Form {}>'.format(self.id)

@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))