import os
from datetime import datetime
from enum import Enum
import uuid
from flask import url_for
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UUID, String, ForeignKey, Text, Integer, MetaData, Date, Enum as SQLAlchemyEnum
from werkzeug.security import check_password_hash, generate_password_hash
from typing import List, Optional

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention={
        "ix": 'ix_%(column_0_label)s',
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    })

db = SQLAlchemy(model_class=Base)

class AnimalStatus(str, Enum):
    AVAILABLE = 'available'
    ADOPTION = 'adoption'
    ADOPTED = 'adopted'

class AdoptionStatus(str, Enum):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'
    REJECTED_ADOPTED = 'rejected_adopted'

class UserRole(Base):
    __tablename__ = "user_roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    users: Mapped[List["User"]] = relationship(back_populates="role")

class User(Base, UserMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    login: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(200), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    middle_name: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)

    role_id: Mapped[int] = mapped_column(ForeignKey("user_roles.id"), nullable=False)
    role: Mapped["UserRole"] = relationship(back_populates="users")
    adoptions: Mapped[List["Adoption"]] = relationship(back_populates="user")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name} {self.middle_name or ''}".strip()
    
    @property
    def is_admin(self):
        return self.role_id == 1
    
    @property
    def is_moderator(self):
        return self.role_id == 2
    
    @property
    def is_user(self):
        return self.role_id == 3

class Image(Base):
    __tablename__ = "images"

    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    file_name: Mapped[str] = mapped_column(String(100), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    md5_hash: Mapped[str] = mapped_column(String(100), unique=True)
    object_id: Mapped[Optional[int]]
    object_type: Mapped[Optional[str]] = mapped_column(String(100))

    animal_id: Mapped[int] = mapped_column(ForeignKey("animals.id"), nullable=False)
    animal: Mapped["Animal"] = relationship(back_populates="images")

    @property
    def storage_filename(self):
        _, ext = os.path.splitext(self.file_name)
        return self.id + ext

    @property
    def url(self):
        return url_for('main.serve_image', image_id=self.id)

class Animal(Base):
    __tablename__ = "animals"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    age_months: Mapped[int] = mapped_column(Integer, nullable=False)
    breed: Mapped[str] = mapped_column(String(100), nullable=False)
    gender: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[AnimalStatus] = mapped_column(
        SQLAlchemyEnum(AnimalStatus),
        default=AnimalStatus.AVAILABLE,
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    
    images: Mapped[List["Image"]] = relationship(
        back_populates="animal", 
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    adoptions: Mapped[List["Adoption"]] = relationship(
        back_populates="animal",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

class Adoption(Base):
    __tablename__ = "adoptions"

    id: Mapped[int] = mapped_column(primary_key=True)
    application_date: Mapped[datetime] = mapped_column(default=datetime.now)
    status: Mapped[AdoptionStatus] = mapped_column(
        SQLAlchemyEnum(AdoptionStatus),
        default=AdoptionStatus.PENDING,
        nullable=False
    )
    contact_info: Mapped[str] = mapped_column(String(200), nullable=False)
    
    animal_id: Mapped[int] = mapped_column(
        ForeignKey("animals.id", ondelete="CASCADE"), 
        nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False
    )
    animal: Mapped["Animal"] = relationship(back_populates="adoptions")
    user: Mapped["User"] = relationship(back_populates="adoptions")