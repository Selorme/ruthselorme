from flask import request, g, url_for
from extensions import db
from models import Post
from utils import slugify, strip_html, generate_meta_description


class SEOMiddleware:
    def __init__(self, app):
        self.app = app
        app.before_request(self.before_request)

    def before_request(self):
        """Inject dynamic SEO metadata and GTM ID into Flask global `g`."""

        # Default SEO metadata
        g.seo = {
            "title": "Ruth Selorme Acolatse",
            "description": "Hi, I am Ruth Selorme Acolatse— a journalist and web developer. I explore storytelling and the power of language through journalism, debate, and coding.",
            "keywords": "blog, tech, writing, programming, python, data science, journalism, web development, content creation",
            "image": url_for('static', filename='img/ogmetaimage.png', _external=True),
            "url": request.base_url,
            "canonical": request.url.replace("http://", "https://").replace("://ruthselormeacolatse.info", "://www.ruthselormeacolatse.info")
        }

        # Google Tag Manager ID
        g.gtm_id = "GTM-KHCML67V"

        # Customize SEO metadata for specific pages
        if request.endpoint == "show_post":
            # Fetch post based on post_id only, not using category from URL
            post_id = request.view_args.get('post_id')

            # Get the post directly by ID - don't filter by category from URL
            requested_post = db.session.query(Post).filter(Post.id == post_id).first()

            if requested_post:
                g.seo["title"] = requested_post.title
                g.seo["description"] = generate_meta_description(requested_post.body) if requested_post.body else "Check out this post."
                g.seo["image"] = requested_post.img_url

                # Generate consistent canonical URL with the actual post-category and title
                normalized_category = requested_post.category.replace(" ", "-").lower()
                expected_slug = slugify(requested_post.title)

                # IMPORTANT: Create canonical URL using the actual post-data
                post_canonical_url = url_for('show_post',
                                             category=normalized_category,
                                             post_id=requested_post.id,
                                             slug=expected_slug,
                                             _external=True)

                # Set both URL and canonical to the same consistent URL
                g.seo["url"] = post_canonical_url
                g.seo["canonical"] = post_canonical_url

        # PRESERVED: All your category SEO information
        elif request.endpoint == "random_musings":
            g.seo["title"] = "Random Musings"
            g.seo["description"] = f"Explore blog posts in the Random Musings category by Ruth Selorme Acolatse where I talk about every and anything going on in my head."
            g.seo["url"] = "https://www.ruthselormeacolatse.info/random-musings"
            g.seo["canonical"] = g.seo["url"]
            g.seo["image"] = url_for('static', filename='img/musingsdark.png', _external=True)

        elif request.endpoint == "ugescapades":
            g.seo["title"] = "University of Ghana Escapades"
            g.seo[
                "description"] = f"In {g.seo['title']}, I explore my experiences as a student at the University of Ghana. Enjoy!"
            g.seo["url"] = "https://www.ruthselormeacolatse.info/ug-escapades"
            g.seo["canonical"] = g.seo["url"]
            g.seo["image"] = url_for('static', filename='img/home-bg.jpg', _external=True)
            g.seo["keywords"] = "blog, university, writing, university of Ghana, housing, hostel, student life"

        elif request.endpoint == "turkiyegecilmez":
            g.seo["title"] = "Türkiye Geçilmez"
            g.seo[
                "description"] = f"In {g.seo['title']}, I talk about what led me to choosing to study in Türkiye and how my experience has been. Enjoy!"
            g.seo["url"] = "https://www.ruthselormeacolatse.info/türkiye-geçilmez"
            g.seo["canonical"] = g.seo["url"]
            g.seo["image"] = url_for('static', filename='img/header.jpg', _external=True)
            g.seo[
                "keywords"] = "blog, university, writing, Türkiye, Marmara University, International student, travel, student life"

        elif request.endpoint == "audacity":
            g.seo["title"] = "Audacious Men Series"
            g.seo[
                "description"] = f"In {g.seo['title']}, I open up about my encounters with the audacity men carry around the world and how that impacts myself and other women!"
            g.seo["url"] = "https://www.ruthselormeacolatse.info/audacious-men-series"
            g.seo["canonical"] = g.seo["url"]
            g.seo["image"] = url_for('static', filename='img/home-bg.jpg', _external=True)
            g.seo["keywords"] = "blog, men, dating, Türkiye, relationship, International student, travel, student life"

        elif request.endpoint == "projects":
            g.seo["title"] = "Python Projects"
            g.seo["description"] = f"In {g.seo['title']}, I explain the various projects I have built with Python and show you how you can build them too!"
            g.seo["url"] = "https://www.ruthselormeacolatse.info/projects"
            g.seo["canonical"] = g.seo["url"]
            g.seo["image"] = url_for('static', filename='img/projects.jpeg', _external=True)
            g.seo["keywords"] = "blog, python, programming, coding, web development"

        elif request.endpoint == "news":
            g.seo["title"] = "Breaking News"
            g.seo["description"] = f"{g.seo['title']}: access to all the breaking headlines across the globe on your finger tip!"
            g.seo["url"] = "https://www.ruthselormeacolatse.info/news"
            g.seo["canonical"] = g.seo["url"]
            g.seo["image"] = url_for('static', filename='img/breakingnews.png', _external=True)
            g.seo["keywords"] = "news, headlines, daily updates, journalism, writing"

        elif request.endpoint == "natural_hair":
            g.seo["title"] = "Natural Hair"
            g.seo[
                "description"] = f"Discover the beauty of {g.seo['title']} care, explore diverse hairstyles, and delve into the rich history of hair traditions. Embrace your unique hair journey today!"
            g.seo["url"] = "https://www.ruthselormeacolatse.info/natural-hair"
            g.seo["canonical"] = g.seo["url"]
            g.seo["image"] = url_for('static', filename='img/naturalhair.png', _external=True)
            g.seo["keywords"] = "natural hair, type 4 hair, 4c hair, curly hair, coily hair, hair"

        elif request.endpoint == "scholarships":
            g.seo["title"] = "Scholarship Updates"
            g.seo["description"] = f"Stay informed with the latest {g.seo['title']} updates. Discover new opportunities, deadlines, and tips to secure funding for your education today."
            g.seo["url"] = "https://www.ruthselormeacolatse.info/scholarships"
            g.seo["canonical"] = g.seo["url"]
            g.seo["image"] = url_for('static', filename='img/scholarships.png', _external=True)
            g.seo["keywords"] = "scholarship, education, university, full scholarship"

        elif request.endpoint == "technology":
            g.seo["title"] = "Technology"
            g.seo[
                "description"] = f"Find all the up to date information about the latest {g.seo['title']} and Tech news"
            g.seo["url"] = "https://www.ruthselormeacolatse.info/technology"
            g.seo["canonical"] = g.seo["url"]
            g.seo["image"] = url_for('static', filename='img/technews.png', _external=True)
            g.seo[
                "keywords"] = "latest tech news, future technology trends, AI tools 2025, machine learning vs AI, software development trends"

        elif request.endpoint == "about":
            g.seo["title"] = "About - Ruth Selorme Acolatse"
            g.seo["description"] = "Welcome to my about page, where you can learn about my experiences, values, and the motivations that inspire my personal and professional endeavors."

        elif request.endpoint == "contact":
            g.seo["title"] = "Contact - Ruth Selorme Acolatse"
            g.seo["description"] = "Do you have any ideas about a collaboration, project or you just want to have a discussion? Get in touch with Ruth Selorme Acolatse."

#"Hi, I'm Ruth Selorme Acolatse — a budding computational journalist, award-winning world-traveling debate judge, and public speaking enthusiast. Based in Istanbul, I explore storytelling, culture, and the power of language through journalism, debate, and now, coding. Follow my adventures in communication, food, travel, and computational journalism!"