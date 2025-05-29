from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, Response
from datetime import datetime, date
from flask_bootstrap5 import Bootstrap
import smtplib
import os
from dotenv import load_dotenv
from flask_ckeditor import CKEditor
from models import Post, User, Comment, PasswordResetToken
from flask_login import login_user, LoginManager, current_user, logout_user, login_required
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from forms import CreatePostForm, RegisterForm, LogInForm, CommentForm, ForgotPasswordForm, ResetPasswordForm
from supabase import create_client, Client
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from flask_migrate import Migrate
from urllib.parse import urlparse, urljoin, urlencode, quote
from hashlib import md5
import requests
from middleware import SEOMiddleware
from flask import send_from_directory
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_assets import Environment, Bundle
from flask_compress import Compress
from extensions import db
from utils import slugify, category_to_url, url_to_category
from werkzeug.utils import secure_filename
from sqlalchemy import func
import sqlalchemy

# Load environment variables
load_dotenv()

# Supabase setup
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)
# Access the storage from Supabase
bucket = supabase.storage.from_('blog-images')

# Email and password
google_email = os.getenv('MY_WEBSITE_EMAIL')
google_password = os.getenv('MY_WEBSITE_PASSWORD')


def gravatar_url(email, size=100, rating='g', default='retro', force_default=False):
    # Convert email to lowercase and hash with MD5 (Gravatar requirement)
    email_hash = md5(email.strip().lower().encode('utf-8')).hexdigest()

    # Build query parameters
    query_params = {'d': default, 's': str(size), 'r': rating}
    if force_default:
        query_params['f'] = 'y'  # Gravatar expects 'f=y' if force_default is True

    return f"https://www.gravatar.com/avatar/{email_hash}?{urlencode(query_params)}"


app = Flask(__name__)


assets = Environment(app)

# Define JS and CSS bundles
js = Bundle('src/js/*.js', filters='jsmin', output='dist/js/bundle.js')
css = Bundle('src/css/*.css', filters='cssmin', output='dist/css/styles.css')

assets.register('js_all', js)
assets.register('css_all', css)

compress = Compress(app)


# Trust Render’s proxy (1 proxy layer)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Add the filter for Jinja templates
app.jinja_env.filters['gravatar'] = gravatar_url

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

mail = Mail(app)
app.config['MAIL_SECRET_KEY'] = os.getenv('MAIL_SECRET_KEY')
s = URLSafeTimedSerializer(app.config['MAIL_SECRET_KEY'])

HCAPTCHA_SECRET_KEY = os.getenv('HCAPTCHA_SECRET_KEY')

# Register SEO Middleware
seo_middleware = SEOMiddleware(app)

app.jinja_env.globals.update(slugify=slugify)

db.init_app(app)
login_manager.init_app(app)
bootstrap = Bootstrap(app)
migrate = Migrate(app, db)

year = datetime.today().year

with app.app_context():
    db.create_all()


@app.errorhandler(404)
def page_not_found():
    return render_template('404.html', copyright_year=year), 404


@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static/img', 'favicon.ico', mimetype='image/vnd.microsoft.icon')


def get_post_url(post):
    """Generate standard post-URL from a post-object"""
    return url_for('show_post',
                  post_id=post.id,
                  category=category_to_url(post.category),
                  slug=slugify(post.title))


@app.template_global()
def get_post_url_global(post):
    return get_post_url(post)


@app.route('/sitemap.xml')
def generate_sitemap():
    base_url = "https://www.ruthselormeacolatse.info"
    today = datetime.today().strftime('%Y-%m-%d')

    # Static pages
    static_pages = [
        '/',
        '/about',
        '/contact',
        '/register',
        '/login',
        '/cvresume',
        '/privacy-policy',
        '/terms-and-conditions',
        '/disclaimer',
        '/projects'
    ]

    blog_posts = db.session.query(Post).filter_by(status="published").all()
    categories = sorted(set(post.category.strip() for post in blog_posts))


    xml_sitemap = """<?xml version="1.0" encoding="UTF-8"?>\n"""
    xml_sitemap += """<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n"""

    # Static pages
    for page in static_pages:
        clean_path = page.strip('/')
        xml_sitemap += f"""<url>
    <loc>{base_url}/{clean_path}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.7</priority>
    </url>\n"""

    # Add blog post URLs with category and post id
    for post in blog_posts:
        category_slug = quote(category_to_url(post.category))  # URL-encoded category
        xml_sitemap += f"""<url>
            <loc>{base_url}/{category_slug}/post/{post.id}/{slugify(post.title)}</loc>
            <lastmod>{post.date}</lastmod>
            <changefreq>weekly</changefreq>
            <priority>0.7</priority>
        </url>\n"""

    # Category pages
    for category in categories:
        cat_slug = category_to_url(category)
        xml_sitemap += f"""<url>
    <loc>{base_url}/{cat_slug}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.5</priority>
    </url>\n"""

    xml_sitemap += "</urlset>"

    return Response(xml_sitemap, mimetype="application/xml")


@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'public, max-age=31536000'
    return response


@app.route("/robots.txt")
def robots():
    return send_from_directory(app.static_folder, "robots.txt", mimetype="text/plain")


@app.route('/ads.txt')
def ads_txt():
    return send_from_directory('static', 'ads.txt', mimetype='text/plain')


@app.before_request
def normalize_url():
    # Skip normalization for reset token URLs
    if request.path.startswith("/reset-password/"):
        return None
    # Redirect to the lowercase version of the path (preserves method with 308)
    if request.path != request.path.lower() and not request.path.startswith('/static/'):
        return redirect(request.path.lower(), code=308)

    # Normalize view_args["category"] for all requests, not just GET
    if request.view_args and "category" in request.view_args:
        category = request.view_args["category"]
        if isinstance(category, str):
            # Store the normalized format consistently
            request.view_args["category"] = category.lower()

    return None


@app.after_request
def add_cache_control(response):
    if request.path.startswith('/static'):
        response.cache_control.max_age = 31536000  # 1 year
    return response


# Wrapper for admin access
def admin_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        elif current_user.id != 1:
            return redirect(url_for('home'))
        return func(*args, **kwargs)  # Make sure to pass args and kwargs to the wrapped function
    return wrapper


# Define the routes
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


def is_safe_url(target):
    """Validate that the redirect URL is safe and within the same site."""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def retry_post(post_data):
    """Re-run the saved POST request after login."""
    post_url = post_data.get("url")
    post_payload = post_data.get("data")

    if post_url:
        # Simulate the original POST request
        with app.test_request_context(post_url, method="POST", data=post_payload):
            # Call the appropriate route function
            response = app.dispatch_request()
            return response
    return redirect(url_for('home'))


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LogInForm()

    # Use session.get() to avoid KeyError
    previous_url = session.get('url')

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = db.session.query(User).filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash("Invalid email or password.")
            return redirect(url_for("login"))

        login_user(user)

        # Redirect user back to the page they tried to access before login
        if previous_url:
            session.pop('url')  # Remove 'url' after using it
            return redirect(previous_url)

        return redirect(url_for("home"))

    return render_template("login.html", form=form)


@app.route("/<string:category>/post/<int:post_id>/like", methods=["POST"])
def like_post(category, post_id):
    print(f"Like post requested: Category = {category}, Post ID = {post_id}")
    #normalize category
    category = url_to_category(category)

    if not current_user.is_authenticated:
        # If not authenticated, redirect to login page and preserve the current URL
        return redirect(url_for('login'))

    # Fetch the post
    post = db.session.query(Post).filter(Post.id == post_id, Post.category.ilike(category)).first()
    print(post)

    if not post:
        print("Post not found. Redirecting to home page.")
        # If the post is not found, redirect to the home page
        flash('Post not found.', 'danger')
        return redirect(url_for('home'))

    # Increment likes
    post.likes += 1
    db.session.commit()

    print(f"Post found. Likes incremented. Current likes: {post.likes}")

    # Handle AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        print("AJAX request detected. Returning like count in response.")
        return jsonify({'likes': post.likes})

    # Non-AJAX requests should redirect back to the post
    print(f"Redirecting back to post page: Category = {category}, Post ID = {post_id}")
    return get_post_url(post)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


def send_post_notification(post):
    """Send an email notification about new blog post to all registered users."""
    try:
        # Get all registered users' emails
        users = db.session.query(User).all()
        for user in users:
            if not user.email:
                continue

            # Create the email
            subject = f"New Blog Post: {post.title}"

            def truncate_text(text, word_limit=300):
                words = text.split()
                return " ".join(words[:word_limit]) + "..." if len(words) > word_limit else text

            preview_text = truncate_text(post.body)

            # Create HTML email content
            html_content = f'''
            <html>
                <body>
                    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                        <h2>{post.title}</h2>
                        <p>{preview_text}</p>
                        <div style="margin: 20px 0;">
                            <p>Category: {post.category}</p>
                        </div>
                        <a href="{url_for('show_post', category=post.category, slug=slugify(post.title), post_id=post.id, _external=True)}" 
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
                recipients=[user.email],
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
        # Handle the image/video upload if there is one
        file = form.img_url.data  # This is the file upload field from your form
        img_url = file

        if file:
            # Secure the filename
            filename = secure_filename(file.filename)

            # Upload the file to Supabase bucket directly
            upload_response = bucket.upload(f'posts/{filename}',
                                            file.stream.read())  # 'posts' is the folder in your bucket
            if upload_response:
                # Get the public URL of the uploaded file
                img_url = bucket.get_public_url(f'posts/{filename}')

        # Find the next available ID by incrementally trying IDs until we find one that works
        max_attempts = 100  # Safeguard against infinite loops
        attempts = 0
        success = False

        # Get the initial max ID as our starting point
        next_id = db.session.query(func.max(Post.id)).scalar() or 0
        next_id += 1

        while not success and attempts < max_attempts:
            try:
                # Create the new post with the current candidate ID
                new_post = Post(
                    id=next_id,
                    title=form.title.data,
                    category=form.category.data,
                    body=form.body.data,
                    img_url=img_url,
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
                success = True

                # Log the ID that was used
                app.logger.info(f"Post created with ID: {next_id}")

                if new_post.status == "published" and new_post.category not in ["news", "scholarships"]:
                    if send_post_notification(new_post):
                        flash("New post created and notification sent to subscribers!", "success")
                    else:
                        flash("Post created, but there was an issue sending notifications.", "warning")
                else:
                    flash("Post saved successfully!", "success")

                return redirect(url_for("home"))

            except sqlalchemy.exc.IntegrityError as e:
                # If we get an integrity error, roll back and try the next ID
                db.session.rollback()

                # Log the attempted ID for debugging
                app.logger.info(f"ID {next_id} already exists, trying next ID")

                # Check if this is specifically a unique constraint violation on the ID
                if "duplicate key value violates unique constraint" in str(e) and "blog_posts_pkey" in str(e):
                    # Increment to the next ID and try again
                    next_id += 1
                    attempts += 1
                else:
                    # If it's some other integrity error, re-raise it
                    flash("An error occurred while saving the post.", "danger")
                    app.logger.error(f"Database error: {str(e)}")
                    return redirect(url_for("add_new_post"))

        if not success:
            flash("Could not find an available ID after multiple attempts.", "danger")
            return redirect(url_for("add_new_post"))

    return render_template("make-post.html", form=form, copyright_year=year, post=None)


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
        # Backup original status before changes
        original_status = post.status
        # Update post attributes
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
            # Check if the post's status was changed to 'published' and the previous status was draft or scheduled
            if original_status != "published" and post.status == "published":
                # Send email notification to users about the new post
                if send_post_notification(post):
                    flash("New post published and notification sent to subscribers!", "success")
                else:
                    flash("Post published, but there was an issue sending notifications.", "warning")
            else:
                flash("Post updated successfully!", "success")
            print(f"Post status after commit: {post.status}")
            flash("Post updated successfully!", "success")
            # Check if there’s a saved action to replay
            return redirect(url_for("show_post", post_id=post.id, category=post.category.replace(" ", "-")))
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
        user = db.session.query(User).filter_by(email=email).first()
        if user:
            token = s.dumps(email, salt='email-reset')

            # save or update the password reset token in the database
            reset_token = db.session.query(PasswordResetToken).filter_by(email=email).first()
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
        email = s.loads(token, salt="email-reset", max_age=3600)  # The token expires in 1 hour
    except SignatureExpired:
        flash("The reset link is expired! Request for another one.", "warning")
        return redirect(url_for("forgot_password"))

    # Verify token exists and is valid
    reset_token = db.session.query(PasswordResetToken).filter_by(email=email, token=token).first()
    if not reset_token:
        flash("Invalid or already used reset link.", "warning")
        return redirect(url_for("forgot_password"))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        new_password = form.new_password.data
        confirm_password = form.confirm_password.data
        if new_password == confirm_password:
            user = db.session.query(User).filter_by(email=email).first()
            user.password = generate_password_hash(new_password)
            db.session.commit()

            # check if token is used
            reset_token.is_used = True
            db.session.commit()

            flash("Password reset successful. Please log in.", "success")
            return redirect(url_for("login"))
        else:
            flash("Passwords do not match.", "danger")

    return render_template("reset_password.html", form=form, token=token, copyright_year=year)


@app.route("/")
def home():
    posts = db.session.query(Post).all()
    # Convert date strings to datetime objects and sort posts
    def parse_date(post):
        # Assuming date is stored in 'Month Day, Year' format
        return datetime.strptime(post.date, "%B %d, %Y")
    # Fetch the latest 6 posts ordered by the date (assuming 'created_at' is the column storing the post creation date)
    latest_posts = sorted(posts, key=parse_date, reverse=True)[:6]
    return render_template("index.html", copyright_year=year, latest_posts=latest_posts)


@app.route("/about")
def about():
    return render_template("about.html", copyright_year=year)


@app.route("/blog", defaults={'category': None})
@app.route("/blog/<category>")
def blogs(category):
    if category:
        # Filter posts by category and ensure they are published
        posts = db.session.query(Post).filter_by(category=category.replace('-', ' '), status='published').all()
    else:
        # Get all published posts
        posts = db.session.query(Post).filter_by(status='published').all()
    return render_template("blog.html", posts=posts, copyright_year=year)


@app.route("/<category>")
def show_category(category):
    category = url_to_category(category)
    posts = db.session.query(Post).filter_by(category=category, status='published').all()
    return render_template("category.html", posts=posts, category=category, copyright_year=year)


@app.route("/projects")
def projects():

    raw_posts = db.session.query(Post).filter_by(category='projects', status='published').all()

    def parse_date(post):
        # Assuming date is stored in 'Month Day, Year' format
        return datetime.strptime(post.date, "%B %d, %Y")
    # Fetch the latest 6 posts ordered by the date (assuming 'created_at' is the column storing the post creation date)
    posts = sorted(raw_posts, key=parse_date, reverse=True)

    return render_template("projects.html", posts=posts, copyright_year=year)


@app.route("/cvresume")
def cvresume():
    return render_template("cvresume.html", copyright_year=year)


@app.route("/ug-escapades")
def ugescapades():
    raw_posts = db.session.query(Post).filter_by(category='ug escapades', status='published').all()

    def parse_date(post):
        # Assuming date is stored in 'Month Day, Year' format
        return datetime.strptime(post.date, "%B %d, %Y")
    # Fetch all posts ordered by the date (assuming 'created_at' is the column storing the post-creation date)
    posts = sorted(raw_posts, key=parse_date, reverse=True)

    return render_template("ugescapades.html", posts=posts, copyright_year=year)


@app.route("/random-musings")
def random_musings():
    raw_posts = db.session.query(Post).filter_by(category='random musings', status='published').all()

    def parse_date(post):
        # Assuming date is stored in 'Month Day, Year' format
        return datetime.strptime(post.date, "%B %d, %Y")
    # Fetch all posts ordered by the date (assuming 'created_at' is the column storing the post-creation date)
    posts = sorted(raw_posts, key=parse_date, reverse=True)

    return render_template("randommusings.html", posts=posts, copyright_year=year)

@app.route("/türkiye-geçilmez")
def turkiyegecilmez():
    raw_posts = db.session.query(Post).filter_by(category='türkiye geçilmez', status='published').all()

    def parse_date(post):
        # Assuming date is stored in 'Month Day, Year' format
        return datetime.strptime(post.date, "%B %d, %Y")
    # Fetch all posts ordered by the date (assuming 'created_at' is the column storing the post-creation date)
    posts = sorted(raw_posts, key=parse_date, reverse=True)

    return render_template("turkiyegecilmez.html", posts=posts, copyright_year=year)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        #Honeypot field check: If the honeypot is filled out, treat it as spam
        honeypot = request.form.get('honeypot')
        if honeypot:  # If honeypot is filled out, it's a bot
            return "Spam detected, ignoring form submission."

        #Get reCAPTCHA response from form
        captcha_response = request.form.get('h-captcha-response')

        #Verify HCAPTCHA response
        payload = {

            'secret': HCAPTCHA_SECRET_KEY,

            'response': captcha_response

        }

        verify_url = "https://hcaptcha.com/siteverify"
        response = requests.post(verify_url, data=payload)
        result = response.json()

        # If HCAPTCHA verification is successful
        if result.get('success'):
            # Send email

            my_email = google_email
            password = google_password

            with smtplib.SMTP("smtp.gmail.com", 587) as connection:
                connection.starttls()
                connection.login(user=my_email, password=password)
                connection.sendmail(from_addr=my_email, to_addrs=my_email,
                                    msg=f"Subject: New Message From Your Website!\n\nName: {name}\nEmail: {email}\nMessage: {message}")

            flash('Message sent successfully!', 'success')
        #if recaptcha is not successful
        else:
            flash('HCAPTCHA verification failed. Please try again.', 'danger')
            return redirect(url_for('contact'))

    return render_template("contact.html", message_sent=False, copyright_year=year)


@app.route("/audacious-men-series")
def audacity():
    raw_posts = db.session.query(Post).filter_by(category='audacious men series', status='published').all()

    def parse_date(post):
        # Assuming date is stored in 'Month Day, Year' format
        return datetime.strptime(post.date, "%B %d, %Y")
    # Fetch all posts ordered by the date (assuming 'created_at' is the column storing the post-creation date)
    posts = sorted(raw_posts, key=parse_date, reverse=True)

    return render_template("audacity.html", posts=posts, copyright_year=year)


@app.route("/news")
def news():
    raw_posts = db.session.query(Post).filter_by(category='news', status='published').all()

    def parse_date(post):
        # Assuming date is stored in 'Month Day, Year' format
        return datetime.strptime(post.date, "%B %d, %Y")
    # Fetch all posts ordered by the date (assuming 'created_at' is the column storing the post-creation date)
    posts = sorted(raw_posts, key=parse_date, reverse=True)

    return render_template("news.html", posts=posts, copyright_year=year)


@app.route("/scholarships")
def scholarships():
    raw_posts = db.session.query(Post).filter_by(category='scholarships', status='published').all()

    def parse_date(post):
        # Assuming date is stored in 'Month Day, Year' format
        return datetime.strptime(post.date, "%B %d, %Y")
    # Fetch all posts ordered by the date (assuming 'created_at' is the column storing the post-creation date)
    posts = sorted(raw_posts, key=parse_date, reverse=True)

    return render_template("scholarships.html", posts=posts, copyright_year=year)


@app.route("/natural-hair")
def natural_hair():
    raw_posts = db.session.query(Post).filter_by(category='natural hair', status='published').all()

    def parse_date(post):
        # Assuming date is stored in 'Month Day, Year' format
        return datetime.strptime(post.date, "%B %d, %Y")
    # Fetch all posts ordered by the date (assuming 'created_at' is the column storing the post-creation date)
    posts = sorted(raw_posts, key=parse_date, reverse=True)

    return render_template("hair.html", posts=posts, copyright_year=year)


@app.route("/technology")
def technology():
    raw_posts = db.session.query(Post).filter_by(category='technology', status='published').all()

    def parse_date(post):
        # Assuming date is stored in 'Month Day, Year' format
        return datetime.strptime(post.date, "%B %d, %Y")
    # Fetch all posts ordered by the date (assuming 'created_at' is the column storing the post-creation date)
    posts = sorted(raw_posts, key=parse_date, reverse=True)

    return render_template("tech.html", posts=posts, copyright_year=year)


@app.route("/my-portfolio")
def portfolio():
    raw_posts = db.session.query(Post).filter_by(category='my portfolio', status='published').all()

    def parse_date(post):
        # Assuming date is stored in 'Month Day, Year' format
        return datetime.strptime(post.date, "%B %d, %Y")
    # Fetch all posts ordered by the date (assuming 'created_at' is the column storing the post-creation date)
    posts = sorted(raw_posts, key=parse_date, reverse=True)

    return render_template("portfolio.html", posts=posts, copyright_year=year)


@app.route("/<string:category>/post/<int:post_id>/<string:slug>", methods=["GET", "POST"])
@app.route("/<string:category>/post/<int:post_id>", methods=["GET", "POST"])
def show_post(category, post_id, slug=None):
    # First, fetch the post by ID regardless of category
    requested_post = db.session.query(Post).filter(Post.id == post_id).first()

    if not requested_post:
        print(f"[DEBUG] Post not found with ID {post_id}. Redirecting to home.")
        flash(f"Post with ID {post_id} not found.", "warning")
        return redirect(url_for("home"))

    # Get the canonical URL components
    canonical_category = category_to_url(requested_post.category)
    canonical_slug = slugify(requested_post.title)

    # If URL doesn't match canonical form, redirect (covers both category and slug issues)
    if category != canonical_category or slug != canonical_slug:
        return redirect(get_post_url(requested_post), code=301)


    if slug is None:
        return redirect(get_post_url(requested_post), code=301)

    # Increment views and commit changes
    requested_post.views += 1
    db.session.commit()

    # Only update session URL if it's not already the current post URL
    if session.get('url') != request.url:
        session['url'] = request.url

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
            return redirect(get_post_url(requested_post))
        else:
            error = "Login Required! Please log in/Register to leave a comment"
            flash(f"{error}. Log in!")
            return redirect(url_for("login", session=f"{session['url']}"))

    # Fetch all posts in the same category, excluding the current post
    top_level_comments = db.session.query(Comment).filter_by(post_id=post_id, parent_id=None).all()
    all_posts_raw = db.session.query(Post).filter(Post.category == requested_post.category,
                                              Post.id != requested_post.id).all()
    all_posts = sorted(all_posts_raw, key=lambda p: p.date, reverse=True)
    categories = [cat[0] for cat in db.session.query(Post.category).distinct().all()]

    return render_template(
        "post.html",
        post=requested_post,
        comments=top_level_comments,  # Pass only top-level comments
        current_user=current_user,
        form=comment_form,
        all_posts=all_posts,
        categories=categories,
        copyright_year=year,
        category=canonical_category,  # Pass the normalized category
    )


@app.route('/search')
def search():
    query = request.args.get('q')
    if query:
        results = db.session.query(Post).filter(
            (Post.title.ilike(f'%{query}%')) | (Post.body.ilike(f'%{query}%'))
        ).all()
    else:
        results = []

    # Query all unique categories
    categories = [cat[0] for cat in db.session.query(Post.category).distinct().all()]

    return render_template('search.html', query=query, results=results, copyright_year=year, categories=categories)


@app.route("/drafts", methods=["GET", "POST"])
@admin_only  # Ensure only admin can access
def drafts():
    draft_posts = db.session.query(Post).filter_by(status="draft").all()

    return render_template("drafts.html", drafts=draft_posts, copyright_year=year)


@app.route("/scheduled-posts", methods=["GET"])
@admin_only
def scheduled_posts():
    post_scheduled = db.session.query(Post).filter_by(status="scheduled").all()  # Get all scheduled posts
    return render_template("scheduled.html", post_scheduled=post_scheduled, copyright_year=year)


@app.route("/disclaimer")
def disclaimer():
    return render_template("disclaimer.html", copyright_year=year)


@app.route("/privacy-policy")
def privacy_policy():
    return render_template("privacy_policy.html", copyright_year=year)


@app.route("/terms-and-conditions")
def terms_and_conditions():
    return render_template("terms_conditions.html", copyright_year=year)


if __name__ == "__main__":
    app.run(debug=True, port=5005)
