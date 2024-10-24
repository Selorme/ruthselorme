from flask import Flask, abort, render_template, request, redirect, url_for, flash
from datetime import datetime, date
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
import smtplib
import os
from dotenv import load_dotenv
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user, login_required
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from forms import CreatePostForm, RegisterForm, LogInForm, CommentForm

# Load environment variables
load_dotenv()

# Email and password
google_email = os.getenv('MY_EMAIL')
google_password = os.getenv('PASSWORD')

app = Flask(__name__)

# Config for SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['CKEDITOR_PKG_TYPE'] = 'full'
ckeditor = CKEditor(app)
login_manager = LoginManager()
gravatar = Gravatar(app, default='retro')

# Initialize the database
class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
db.init_app(app)
login_manager.init_app(app)
bootstrap = Bootstrap(app)

year = datetime.today().year


# Configure tables
# Table to make posts
class Post(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))

    author = relationship("User", back_populates="posts")

    title: Mapped[int] = mapped_column(String, unique=True, nullable=False)
    date: Mapped[str] = mapped_column(String, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)

    comments = relationship("Comment", back_populates="parent_post")


# Table for registered users
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)

    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")


# Table for comments
class Comment(db.Model):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")

    post_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("blog_posts.id"))
    parent_post = relationship("Post", back_populates="comments")
    text: Mapped[str] = mapped_column(Text, nullable=False)


with app.app_context():
    db.create_all()


# Wrapper for admin access
def admin_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return func(*args, **kwargs)
    return wrapper


# Define your routes
# Route for registration of users
# noinspection PyArgumentList
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        if user:
            flash("You've already signed up with that email, log in instead!")
            return redirect(url_for('login'))
        name = form.name.data

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        new_user = User(email=email, password=hashed_password, name=name)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))
    return render_template("register.html", form=form)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


# TODO: Retrieve a user from the database based on their email.
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LogInForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()

        if not user:
            flash("That email does not exist, please try again.")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash('Password incorrect, please try again.')
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home'))

    return render_template("login.html", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = Post(
            title=form.title.data,
            category=form.category.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=current_user,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("make-post.html", form=form)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = db.get_or_404(Post, post_id)
    edit_form = CreatePostForm(
        title=post.title,
        category=post.category,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.category = edit_form.category.data
        post.img_url = edit_form.img_url.data
        post.author = current_user
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(Post, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('home'))












@app.route("/")
def home():
    return render_template("index.html", copyright_year=year)


@app.route("/about")
def about():
    return render_template("about.html", copyright_year=year)


@app.route("/blog", defaults={'category': None})
@app.route("/blog/<category>")
def blogs(category):
    result = db.session.execute(db.select(Post))
    posts = result.scalars().all()
    return render_template("blog.html", posts=posts)


@app.route("/<category>")
def show_category(category):
    category = category.replace('-', ' ')
    posts = Post.query.filter_by(category=category).all()
    return render_template("category.html", posts=posts, category=category, copyright_year=year)


@app.route("/Projects")
def projects():
    posts = Post.query.filter_by(category='Projects').all()
    return render_template("projects.html", posts=posts, copyright_year=year)


@app.route("/cvresume")
def cvresume():
    return render_template("cvresume.html", copyright_year=year)


@app.route("/UG-Escapades")
def ugescapades():
    posts = Post.query.filter_by(category='UG Escapades').all()
    return render_template("ugescapades.html", posts=posts, copyright_year=year)


@app.route("/Türkiye-Geçilmez")
def turkiyegecilmez():
    posts = Post.query.filter_by(category='Türkiye Geçilmez').all()
    return render_template("turkiyegecilmez.html", posts=posts, copyright_year=year)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        my_email = google_email
        password = google_password

        with smtplib.SMTP("smtp.gmail.com", 587) as connection:
            connection.starttls()
            connection.login(user=my_email, password=password)
            connection.sendmail(from_addr=my_email, to_addrs=my_email,
                                msg=f"Subject: New Message From Your Website!\n\nName: {name}\nEmail: {email}\nMessage: {message}")

        flash('Message sent successfully!', 'success')
        return redirect(url_for('contact'))

    return render_template("index.html", message_sent=False, copyright_year=year)


@app.route("/Audacious-Men-Series")
def audacity():
    posts = Post.query.filter_by(category='Audacious Men Series').all()
    return render_template("audacity.html", posts=posts, copyright_year=year)


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = db.get_or_404(Post, post_id)
    comment_form = CommentForm()

    if comment_form.validate_on_submit():
        if current_user.is_authenticated:
            new_comment = Comment(
                text=comment_form.comment.data,
                author_id=current_user.id,
                post_id=requested_post.id
            )
            db.session.add(new_comment)
            db.session.commit()
            return redirect(url_for('show_post', post_id=post_id))
        else:
            error = "Login Required! Please log in/Register to leave a comment"
            flash("Log in required error!")
            return redirect(url_for("login"))
    # Fetch all posts in the same category, excluding the current post
    all_posts = Post.query.filter(Post.category == requested_post.category, Post.id != requested_post.id).all()
    return render_template("post.html", post=requested_post, current_user=current_user, form=comment_form, all_posts=all_posts)


@app.route('/search')
def search():
    query = request.args.get('q')
    if query:
        results = Post.query.filter(
            (Post.title.ilike(f'%{query}%')) | (Post.content.ilike(f'%{query}%'))
        ).all()
    else:
        results = []

    return render_template('search.html', query=query, results=results)


if __name__ == "__main__":
    app.run(debug=True)
