from flask import Flask, abort, render_template, request, redirect, url_for, flash, jsonify
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
from forms import CreatePostForm, RegisterForm, LogInForm, CommentForm, ForgotPasswordForm, ResetPasswordForm
from supabase import create_client, Client
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

# Load environment variables
load_dotenv()

# Supabase setup
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

# Email and password
google_email = os.getenv('MY_WEBSITE_EMAIL')
google_password = os.getenv('MY_WEBSITE_PASSWORD')

app = Flask(__name__)

# Set up for email
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # e.g., smtp.gmail.com for Gmail
app.config['MAIL_PORT'] = 587  # Use 465 for SSL, 587 for TLS
app.config['MAIL_USE_TLS'] = True  # or False if using SSL
app.config['MAIL_USE_SSL'] = False  # or True if using SSL
app.config['MAIL_USERNAME'] = os.getenv('MY_WEBSITE_EMAIL')
app.config['MAIL_PASSWORD'] = os.getenv('MY_WEBSITE_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MY_WEBSITE_EMAIL')

# Config for SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['CKEDITOR_PKG_TYPE'] = 'full'
ckeditor = CKEditor(app)
login_manager = LoginManager()
gravatar = Gravatar(app, default='retro')

mail = Mail(app)
app.config['MAIL_SECRET_KEY'] = os.getenv('MAIL_SECRET_KEY')
s = URLSafeTimedSerializer(app.config['MAIL_SECRET_KEY'])

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

    status: Mapped[str] = mapped_column(String, nullable=False, default="published")  # "draft" or "published"
    scheduled_datetime: Mapped[datetime] = mapped_column(db.DateTime, nullable=True)

    comments = relationship("Comment", back_populates="parent_post")

    views: Mapped[int] = mapped_column(Integer, default=0)
    likes: Mapped[int] = mapped_column(Integer, default=0)


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
    parent_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("comments.id"), nullable=True)
    parent_comment = relationship("Comment", remote_side=[id], backref="replies")


class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_tokens"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    token: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow)


with app.app_context():
    db.create_all()


# Wrapper for admin access
def admin_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        elif current_user.id != 1:
            return redirect(url_for('home'))
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
    return render_template("register.html", form=form, copyright_year=year)


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

    return render_template("login.html", form=form, copyright_year=year)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


def send_post_notification(post):
    """Send email notification about new blog post to all registered users."""
    try:
        # Get all registered users' emails
        users = User.query.all()
        recipients = ["ruthselormeacolatse.website@gmail.com"]
        bcc = [user.email for user in users if user.email]

        # Create the email
        subject = f"New Blog Post: {post.title}"

        # Create HTML email content
        html_content = f'''
        <html>
            <body>
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2>{post.title}</h2>
                    <p>A new post has been published on our blog!</p>
                    <div style="margin: 20px 0;">
                        <p>Category: {post.category}</p>
                    </div>
                    <a href="{url_for('show_post', post_id=post.id, _external=True)}" 
                       style="background-color: #007bff; color: white; padding: 10px 20px; 
                              text-decoration: none; border-radius: 5px;">
                        Read More
                    </a>
                    <hr style="margin-top: 30px;">
                    <p style="font-size: 12px; color: #666;">
                        You received this email because you're registered on our blog. 
                        If you'd like to unsubscribe, please update your preferences in your account settings.
                    </p>
                </div>
            </body>
        </html>
        '''

        msg = Message(
            subject=subject,
            recipients=recipients,
            bcc=bcc,
            html=html_content
        )

        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending notification: {e}")
        return False


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
            date=date.today().strftime("%B %d, %Y"),
        )

        if form.publish.data:
            new_post.status = "published"
            new_post.scheduled_datetime = None
        elif form.draft.data:
            new_post.status = "draft"
            new_post.scheduled_datetime = None
        elif form.schedule.data:
            new_post.status = "scheduled"
            # Combine the date and time fields
            if form.publish_date.data and form.publish_time.data:
                scheduled_datetime = datetime.combine(
                    form.publish_date.data,
                    form.publish_time.data
                )
                new_post.scheduled_datetime = scheduled_datetime

        db.session.add(new_post)
        db.session.commit()

        if new_post.status == "published":
            if send_post_notification(new_post):
                flash("New post created and notification sent to subscribers!", "success")
            else:
                flash("Post created, but there was an issue sending notifications.", "warning")
        else:
            flash("Post saved successfully!", "success")

        return redirect(url_for("home"))

    return render_template("make-post.html", form=form, copyright_year=year)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = db.get_or_404(Post, post_id)
    edit_form = CreatePostForm(obj=post)

    # If it's a GET request and the post is scheduled, populate the date/time fields
    if request.method == "GET" and post.scheduled_datetime:
        edit_form.publish_date.data = post.scheduled_datetime.date()
        edit_form.publish_time.data = post.scheduled_datetime.time()

    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.category = edit_form.category.data
        post.img_url = edit_form.img_url.data
        post.body = edit_form.body.data

        print("\nButton states:")
        print(f"Publish: {edit_form.publish.data}")
        print(f"Draft: {edit_form.draft.data}")
        print(f"Schedule: {edit_form.schedule.data}")
        print(f"Current post status: {post.status}")

        if edit_form.publish.data:
            print("Setting status to published")
            post.status = "published"
            post.scheduled_datetime = None
        elif edit_form.draft.data:
            print("Setting status to draft")
            post.status = "draft"
            post.scheduled_datetime = None
        elif edit_form.schedule.data:
            print("Setting status to scheduled")
            post.status = "scheduled"

            # Combine the date and time fields
            if edit_form.publish_date.data and edit_form.publish_time.data:
                scheduled_datetime = datetime.combine(
                    edit_form.publish_date.data,
                    edit_form.publish_time.data
                )
                post.scheduled_datetime = scheduled_datetime
            else:
                flash('Publish date and time are required when scheduling a post.', 'danger')
                return render_template(
                    "make-post.html",
                    form=edit_form,
                    is_edit=True,
                    post=post,
                    copyright_year=year
                )

        print(f"Post status before commit: {post.status}")

        try:
            db.session.commit()
            print(f"Post status after commit: {post.status}")
            flash("Post updated successfully!", "success")
            return redirect(url_for("show_post", post_id=post.id))
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating post: {str(e)}", "danger")
            return render_template(
                "make-post.html",
                form=edit_form,
                is_edit=True,
                post=post,
                copyright_year=year
            )

    return render_template(
        "make-post.html",
        form=edit_form,
        is_edit=True,
        post=post,
        copyright_year=year
    )


@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(Post, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('home'))


def send_reset_email(email, reset_url):
    msg = Message("Password Reset Request",
                  sender=os.getenv('MY_WEBSITE_EMAIL'),
                  recipients=[email])

    # Email body content
    msg.body = f"""To reset your password, click the following link: {reset_url}

If you did not request this, ignore this email.
"""

    # Set the Reply-To header to a non-monitored address
    msg.reply_to = "no-reply@example.com"  # Use a non-monitored address

    # Send the email
    mail.send(msg)


@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            token = s.dumps(email, salt='email-reset')

            # save or update the password reset token in the database
            reset_token = PasswordResetToken.query.filter_by(email=email).first()
            if reset_token:
                reset_token.token = token
            else:
                reset_token = PasswordResetToken(email=email, token=token)
                db.session.add(reset_token)
            db.session.commit()

            reset_url = url_for('reset_password', token=token, _external=True)
            send_reset_email(email, reset_url)
            flash("A password reset link has been sent to your email.", "info")
            return redirect(url_for('login'))
        else:
            flash("Email not found. Please register.", "warning")
            return redirect(url_for('register'))
    return render_template("forgot_password.html", form=form, copyright_year=year)


@app.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    try:
        email = s.loads(token, salt="email-reset", max_age=3600)  # Token expires in 1 hour
    except SignatureExpired:
        flash("The reset link is expired! Request for another one.", "warning")
        return redirect(url_for("forgot_password"))

    # Verify token exists and is valid
    reset_token = PasswordResetToken.query.filter_by(email=email, token=token).first()
    if not reset_token:
        flash("Invalid or already used reset link.", "warning")
        return redirect(url_for("forgot_password"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        new_password = form.new_password.data
        confirm_password = form.confirm_password.data
        if new_password == confirm_password:
            user = User.query.filter_by(email=email).first()
            user.password = generate_password_hash(new_password)
            db.session.commit()

            # Delete the token after use
            db.session.delete(reset_token)
            db.session.commit()

            flash("Password reset successful. Please log in.", "success")
            return redirect(url_for("login"))
        else:
            flash("Passwords do not match.", "danger")

    return render_template("reset_password.html", form=form, token=token, copyright_year=year)


@app.route("/")
def home():
    return render_template("index.html", copyright_year=year)


@app.route("/about")
def about():
    return render_template("about.html", copyright_year=year)


@app.route("/blog", defaults={'category': None})
@app.route("/blog/<category>")
def blogs(category):
    if category:
        # Filter posts by category and ensure they are published
        posts = Post.query.filter_by(category=category.replace('-', ' '), status='published').all()
    else:
        # Get all published posts
        posts = Post.query.filter_by(status='published').all()
    return render_template("blog.html", posts=posts, copyright_year=year)


@app.route("/<category>")
def show_category(category):
    category = category.replace('-', ' ')
    posts = Post.query.filter_by(category=category, status='published').all()
    return render_template("category.html", posts=posts, category=category, copyright_year=year)


@app.route("/Projects")
def projects():
    posts = Post.query.filter_by(category='Projects', status='published').all()
    return render_template("projects.html", posts=posts, copyright_year=year)


@app.route("/cvresume")
def cvresume():
    return render_template("cvresume.html", copyright_year=year)


@app.route("/UG-Escapades")
def ugescapades():
    posts = Post.query.filter_by(category='UG Escapades', status='published').all()
    return render_template("ugescapades.html", posts=posts, copyright_year=year)


@app.route("/random-musings")
def random_musings():
    posts = Post.query.filter_by(category='Random Musings', status='published').all()
    return render_template("randommusings.html", posts=posts, copyright_year=year)

@app.route("/Türkiye-Geçilmez")
def turkiyegecilmez():
    posts = Post.query.filter_by(category='Türkiye Geçilmez', status='published').all()
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
    posts = Post.query.filter_by(category='Audacious Men Series', status='published').all()
    return render_template("audacity.html", posts=posts, copyright_year=year)


@app.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    requested_post = db.get_or_404(Post, post_id)

    requested_post.views += 1
    db.session.commit()

    comment_form = CommentForm()

    if comment_form.validate_on_submit():
        if current_user.is_authenticated:

            parent_id = request.form.get("parent_id")

            new_comment = Comment(
                text=comment_form.comment.data,
                author_id=current_user.id,
                post_id=requested_post.id,
                parent_id=parent_id
            )
            db.session.add(new_comment)
            db.session.commit()
            return redirect(url_for('show_post', post_id=post_id))
        else:
            error = "Login Required! Please log in/Register to leave a comment"
            flash("Log in to leave a comment!")
            return redirect(url_for("login"))
    # Fetch all posts in the same category, excluding the current post
    top_level_comments = Comment.query.filter_by(post_id=post_id, parent_id=None).all()
    all_posts = Post.query.filter(Post.category == requested_post.category, Post.id != requested_post.id).all()
    categories = [cat[0] for cat in db.session.query(Post.category).distinct().all()]

    return render_template(
        "post.html",
        post=requested_post,
        comments=top_level_comments,  # Pass only top-level comments
        current_user=current_user,
        form=comment_form,
        all_posts=all_posts,
        categories=categories,
        copyright_year=year
    )


# Route to handle the like functionality
@app.route('/post/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    post = db.get_or_404(Post, post_id)
    post.likes += 1
    db.session.commit()
    return jsonify({'likes': post.likes})  # Return updated likes count as JSON


@app.route('/search')
def search():
    query = request.args.get('q')
    if query:
        results = Post.query.filter(
            (Post.title.ilike(f'%{query}%')) | (Post.body.ilike(f'%{query}%'))
        ).all()
    else:
        results = []

    return render_template('search.html', query=query, results=results, copyright_year=year)


@app.route("/drafts", methods=["GET", "POST"])
@admin_only  # Ensure only admin can access
def drafts():
    draft_posts = Post.query.filter_by(status="draft").all()

    return render_template("drafts.html", drafts=draft_posts, copyright_year=year)


@app.route("/scheduled-posts", methods=["GET"])
@admin_only
def scheduled_posts():
    post_scheduled = Post.query.filter_by(status="scheduled").all()  # Get all scheduled posts
    return render_template("scheduled.html", post_scheduled=post_scheduled, copyright_year=year)


@app.route("/Disclaimer")
def disclaimer():
    return render_template("disclaimer.html", copyright_year=year)


@app.route("/Privacy-Policy")
def privacy_policy():
    return render_template("privacy_policy.html", copyright_year=year)


@app.route("/Terms-and-Conditions")
def terms_and_conditions():
    return render_template("terms_conditions.html", copyright_year=year)


if __name__ == "__main__":
    app.run(debug=True, port=5005)
