from flask import request, g, url_for
from urllib.parse import urljoin
from extensions import db
from models import Post
from utils import slugify, strip_html

class SEOMiddleware:
    def __init__(self, app):
        self.app = app
        app.before_request(self.before_request)


    def before_request(self):
        """Inject dynamic SEO metadata and GTM ID into Flask global `g`."""

        # Compute clean path
        path = request.path.rstrip('/') or '/'

        # Default SEO metadata
        g.seo = {
            "title": "Ruth Selorme Acolatse",
            "description": "Hi, I'm Ruth Selorme Acolatse— a journalist and web developer. I explore storytelling and the power of language through journalism, debate, and coding.",
            "keywords": "blog, tech, writing, programming, python, data science, journalism, web development, content creation",
            "image": url_for('static', filename='img/ogmetaimage.png', _external=True),
            "url": request.base_url,
            "canonical": f"https://www.ruthselormeacolatse.info{path}"
        }

        # Google Tag Manager ID
        g.gtm_id = "GTM-KHCML67V"

        # Customize SEO metadata for specific pages
        if request.endpoint == "show_post":
            # Fetch post based on category and post_id
            category = request.view_args.get('category', '').replace("-", " ").lower()
            post_id = request.view_args.get('post_id')
            # Use filter() with ilike() for case-insensitive comparison
            requested_post = db.session.query(Post).filter(
                Post.id == post_id,
                Post.category.ilike(category)  # ilike() performs case-insensitive search
            ).first()

            if requested_post:
                g.seo["title"] = requested_post.title
                g.seo["description"] = strip_html(requested_post.body[:160] + "...") if requested_post.body else "Check out this post."
                g.seo["image"] = requested_post.img_url
                g.seo["url"] = urljoin(request.host_url,
                                       url_for('show_post', category=requested_post.category.replace(" ", "-"), post_id=requested_post.id, slug=slugify(requested_post.title)))

                # Ensure canonical URL is in lowercase
                g.seo["canonical"] = urljoin(request.host_url,
                                             url_for('show_post', category=requested_post.category.replace(" ", "-").lower(),
                                                     post_id=requested_post.id))

        elif request.endpoint == "random_musings":
            g.seo["title"] = "Random Musings"
            g.seo["description"] = f"Explore blog posts in the Random Musings category by Ruth Selorme Acolatse."
            g.seo["url"] = "https://www.ruthselormeacolatse.info/random-musings"
            g.seo["canonical"] = g.seo["url"]
            g.seo["image"] = url_for('static', filename='img/musingsdark.png', _external=True)

        elif request.endpoint == "ugescapades":
            g.seo["title"] = "University of Ghana Escapades"
            g.seo["description"] = f"In {g.seo['title']}, I explore my experiences as a student at the University of Ghana. Enjoy!"
            g.seo["url"] = "https://www.ruthselormeacolatse.info/ug-escapades"
            g.seo["canonical"] = g.seo["url"]
            g.seo["image"] = url_for('static', filename='img/home-bg.jpg', _external=True)
            g.seo["keywords"] = "blog, university, writing, university of Ghana, housing, hostel, student life"

        elif request.endpoint == "turkiyegecilmez":
            g.seo["title"] = "Türkiye Geçilmez"
            g.seo["description"] = f"In {g.seo['title']}, I talk about what led me to choosing to study in Türkiye. Enjoy!"
            g.seo["url"] = "https://www.ruthselormeacolatse.info/türkiye-geçilmez"
            g.seo["canonical"] = g.seo["url"]
            g.seo["image"] = url_for('static', filename='img/header.jpg', _external=True)
            g.seo["keywords"] = "blog, university, writing, Türkiye, Marmara University, International student, travel, student life"

        elif request.endpoint == "audacity":
            g.seo["title"] = "Audacious Men Series"
            g.seo["description"] = f"In {g.seo['title']}, I open up about my encounters with the audacity men carry around the world and how that impacts myself and other women!"
            g.seo["url"] = "https://www.ruthselormeacolatse.info/audacious-men-series"
            g.seo["canonical"] = g.seo["url"]
            g.seo["image"] = url_for('static', filename='img/home-bg.jpg', _external=True)
            g.seo["keywords"] = "blog, men, dating, Türkiye, relationship, International student, travel, student life"

        elif request.endpoint == "projects":
            g.seo["title"] = "Python Projects"
            g.seo["description"] = f"In {g.seo['title']}, I explain the various projects I have built with Python!"
            g.seo["url"] = "https://www.ruthselormeacolatse.info/projects"
            g.seo["canonical"] = g.seo["url"]
            g.seo["image"] = url_for('static', filename='img/projects.jpeg', _external=True)
            g.seo["keywords"] = "blog, python, programming, coding, web development"

        elif request.endpoint == "about":
            g.seo["title"] = "About - Ruth Selorme Acolatse"
            g.seo["description"] = "Learn more about Ruth Selorme Acolatse."

        elif request.endpoint == "contact":
            g.seo["title"] = "Contact - Ruth Selorme Acolatse"
            g.seo["description"] = "Get in touch with Ruth Selorme Acolatse."

#Hi, I'm Ruth Selorme Acolatse — a budding computational journalist, award-winning world-traveling debate judge, and public speaking enthusiast. Based in Istanbul, I explore storytelling, culture, and the power of language through journalism, debate, and now, coding. Follow my adventures in communication, food, travel, and computational journalism!",