from datetime import datetime, timezone
from flask_login import UserMixin
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float, CheckConstraint
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
    degree: Mapped[str] = mapped_column(String, nullable=False, default="High School")

    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")
    user_skills = relationship("UserSkill", back_populates="user")
    job_matches = relationship("JobMatch", back_populates="user")


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


class SkillsReference(Base):
    __tablename__ = "skills_reference"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    skill_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=True)  # 'Technical', 'Business', 'Creative', etc.
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))


class UserSkill(Base):
    __tablename__ = "user_skills"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    skill_name: Mapped[str] = mapped_column(String(100), nullable=False)
    proficiency: Mapped[int] = mapped_column(Integer, nullable=False)
    enjoyment: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc),
                                                 onupdate=datetime.now(timezone.utc))

    # Add constraints for proficiency and enjoyment (1-10 scale)
    __table_args__ = (
        CheckConstraint('proficiency >= 1 AND proficiency <= 10', name='check_proficiency_range'),
        CheckConstraint('enjoyment >= 1 AND enjoyment <= 10', name='check_enjoyment_range'),
    )

    user = relationship("User", back_populates="user_skills")


class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    minimum_degree_required: Mapped[str] = mapped_column(String(50), nullable=False, default="High School")
    required_skills: Mapped[dict] = mapped_column(JSON, nullable=False)  # {"Python": 7, "SQL": 6}
    industry: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    job_matches = relationship("JobMatch", back_populates="job")


class JobMatch(Base):
    __tablename__ = "job_matches"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("jobs.id"), nullable=False)
    match_score: Mapped[float] = mapped_column(Float, nullable=False)  # Overall match percentage (0.00 to 100.00)
    skills_match_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    proficiency_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    enjoyment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    degree_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    last_calculated: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(timezone.utc))

    user = relationship("User", back_populates="job_matches")
    job = relationship("Job", back_populates="job_matches")

