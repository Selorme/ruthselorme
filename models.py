from datetime import datetime, timezone
from flask_login import UserMixin
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, DateTime, Boolean, ForeignKey
from typing import Optional

# SQAlchemy base class
class Base(DeclarativeBase):
    pass


# Configure tables
# Table to make posts
class Post(Base):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    author = relationship("User", back_populates="posts")

    title: Mapped[int] = mapped_column(String, unique=True, nullable=False)
    date: Mapped[str] = mapped_column(String, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)

    status: Mapped[str] = mapped_column(String, nullable=False, default="published")  # "draft" or "published"
    scheduled_datetime: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    comments = relationship("Comment", back_populates="parent_post")

    views: Mapped[int] = mapped_column(Integer, default=0)
    likes: Mapped[int] = mapped_column(Integer, default=0)


# Table for registered users
class User(UserMixin, Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)

    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")


# Table for comments
class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")

    post_id: Mapped[int] = mapped_column(Integer, ForeignKey("blog_posts.id"))
    parent_post = relationship("Post", back_populates="comments")

    text: Mapped[str] = mapped_column(Text, nullable=False)
    parent_id: Mapped[int] = mapped_column(Integer, ForeignKey("comments.id"), nullable=True)
    parent_comment = relationship("Comment", remote_side=[id], backref="replies")


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, nullable=False)
    token: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    is_used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
