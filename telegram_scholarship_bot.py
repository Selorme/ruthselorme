import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone
from supabase import create_client
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
import os

# === LOAD ENV ===
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BUCKET_NAME = "blog-images"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# === UPLOAD TO SUPABASE STORAGE ===
def upload_to_supabase(file_name, image_buffer):
    try:
        supabase.storage.from_(BUCKET_NAME).upload(
            file_name,
            image_buffer,
            {"content-type": "image/jpeg", "upsert": True}
        )
        return f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{file_name}"
    except Exception as e:
        print("Upload error:", e)
        return "https://yourwebsite.com/default.jpg"

# === SCRAPER ===
def scrape_scholarshipregion():
    url = "https://www.scholarshipregion.com/"
    headers = {"User-Agent": "Mozilla/5.0"}
    scholarships = []

    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.select("div.td-block-span4 .td_module_mx2")[:5]

        for i, article in enumerate(articles):
            title_tag = article.select_one("h3.entry-title a")
            if not title_tag:
                continue
            title = title_tag.text.strip()
            link = title_tag["href"]

            date_tag = article.select_one("time.entry-date")
            deadline = date_tag.text.strip() if date_tag else "Deadline not specified"

            img_url = "{{ url_for('static', filename='img/scholarships.png') }}"

            scholarships.append({
                "title": title,
                "link": link,
                "deadline": deadline,
                "img_url": img_url
            })

    except Exception as e:
        print("ScholarshipRegion scrape error:", e)

    return scholarships

# === POST TO SUPABASE DB ===
def post_to_supabase(scholarships):
    for s in scholarships:
        try:
            supabase.table("blog_posts").insert({
                "author_id": 1,
                "title": s["title"],
                "date": datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                "body": f"<p><strong>Deadline:</strong> {s['deadline']}</p><p><a href='{s['link']}'>Apply here</a></p>",
                "img_url": s['img_url'],
                "category": "Scholarships",
                "status": "published",
                "scheduled_datetime": None,
                "views": 0,
                "likes": 0
            }).execute()
            print("✅ Posted to Supabase:", s["title"])
        except Exception as e:
            print("❌ Supabase post error:", e)

# === FORMAT TELEGRAM MESSAGE ===
def format_message(scholarships):
    today = datetime.now(timezone.utc).strftime('%B %d, %Y')
    message = f"<b>📢 Scholarship Updates – {today}</b>\n\n"
    for s in scholarships:
        message += f"🔹 <b>{s['title']}</b>\n"
        message += f"Deadline: <i>{s['deadline']}</i>\n"
        message += f"<a href='{s['link']}'>Apply Now</a>\n\n"
    return message

# === SEND TO TELEGRAM ===
def send_to_telegram(scholarships):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    for s in scholarships:
        message = (
            f"🔹 <b>{s['title']}</b>\n"
            f"Deadline: <i>{s['deadline']}</i>\n"
            f"<a href='{s['link']}'>Apply Now</a>"
        )
        payload = {
            "chat_id": CHANNEL_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }
        response = requests.post(url, data=payload)
        print("📨 Sent to Telegram:", response.json())

# === MAIN JOB FUNCTION ===
def job():
    all_scholarships = scrape_scholarshipregion()
    if all_scholarships:
        post_to_supabase(all_scholarships)
        send_to_telegram(all_scholarships)
        print("📨 Telegram update sent!")
    else:
        print("⚠️ No scholarships found today.")


# === SCHEDULER SETUP ===
if __name__ == "__main__":
    scheduler = BlockingScheduler(timezone="UTC")
    scheduler.add_job(job, 'cron', hour=18, minute=0)  # 6PM GMT == 18:00 UTC
    print("⏰ Scheduler running. Job will run at 6PM GMT daily...")
    scheduler.start()
