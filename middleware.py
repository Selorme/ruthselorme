from flask import request, g, url_for
from urllib.parse import urljoin


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
            "description": "Hi, I'm Ruth Selorme Acolatse — a journalist and web developer. I explore storytelling and the power of language through journalism, debate, and coding.",
            "keywords": "blog, tech, writing, programming, python, data science, journalism",
            "image": url_for('static', filename='img/ogmetaimage.png', _external=True),
            "url": request.base_url,
            "canonical": f"https://www.ruthselormeacolatse.info{path}"
        }

        # Google Tag Manager ID
        g.gtm_id = "GTM-KHCML67V"

        # Customize SEO metadata for specific pages
        if request.endpoint == "show_post":
            post = getattr(request.view_args, 'post', None)
            if post:
                g.seo["title"] = post.title
                g.seo["description"] = (post.body[:160] + "...") if post.body else "Check out this post."
                g.seo["image"] = post.img_url
                g.seo["url"] = urljoin(request.host_url,
                                       url_for('show_post', category=post.category.replace(" ", "-"), post_id=post.id))

                # Ensure canonical URL is in lowercase
                g.seo["canonical"] = urljoin(request.host_url,
                                             url_for('show_post', category=post.category.replace(" ", "-").lower(),
                                                     post_id=post.id))

        elif request.endpoint == "about":
            g.seo["title"] = "About - Ruth Selorme Acolatse"
            g.seo["description"] = "Learn more about Ruth Selorme Acolatse."

        elif request.endpoint == "contact":
            g.seo["title"] = "Contact - Ruth Selorme Acolatse"
            g.seo["description"] = "Get in touch with Ruth Selorme Acolatse."

#Hi, I'm Ruth Selorme Acolatse — a budding computational journalist, award winning world-traveling debate judge, and public speaking enthusiast. Based in Istanbul, I explore storytelling, culture, and the power of language through journalism, debate, and now, coding. Follow my adventures in communication, food, travel, and computational journalism!",