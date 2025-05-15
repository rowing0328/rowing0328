import feedparser
from datetime import datetime
import requests
from bs4 import BeautifulSoup

URL = "https://dev-rowing.tistory.com/rss"
RSS_FEED = feedparser.parse(URL)
MAX_POST = 4

def extract_thumbnail(entry_url):
    try:
        res = requests.get(entry_url, timeout=5)
        soup = BeautifulSoup(res.text, 'html.parser')
        og_img = soup.find("meta", property="og:image")
        return og_img["content"] if og_img else ""
    except:
        return "https://t1.daumcdn.net/tistory_admin/static/images/openGraph/opengraph.png"

def format_entry_as_td(entry):
    title = entry['title']
    link = entry['link']
    pub_date = datetime(*entry['published_parsed'][:3]).strftime("%Y.%m.%d")
    thumbnail = extract_thumbnail(link)

    return (
        f'<td width="25%" align="center" style="border: none; padding: 0 4px;">'
        f'<a href="{link}">'
        f'<img width="1012" alt="image" src="{thumbnail}"><br/>'
        f'<strong>{title}</strong><br/>'
        f'<sub>{pub_date}</sub>'
        f'</a>'
        f'</td>'
    )

def build_table(feed_entries):
    rows = []
    tds = []

    for idx, entry in enumerate(feed_entries[:MAX_POST]):
        tds.append(format_entry_as_td(entry))
        # Every 4 entries, start a new row
        if (idx + 1) % 4 == 0 or (idx + 1) == len(feed_entries[:MAX_POST]):
            row_html = "<tr style='border: none;'>\n" + "\n".join(tds) + "\n</tr>"
            rows.append(row_html)
            tds = []

    table_html = f"## 📕 Latest Blog Posts\n\n<table style=\"border: none; border-collapse: collapse;\">\n" + "\n".join(rows) + "\n</table>"
    return table_html

def update_readme_section(new_content):
    with open("README.md", "r", encoding="utf-8") as file:
        lines = file.readlines()

    start_index = None
    end_index = None
    for i, line in enumerate(lines):
        if "<!-- START_CUSTOM_SECTION -->" in line:
            start_index = i
        elif "<!-- END_CUSTOM_SECTION -->" in line:
            end_index = i
            break

    if start_index is not None and end_index is not None:
        new_lines = lines[:start_index+1] + [new_content + "\n"] + lines[end_index:]
        with open("README.md", "w", encoding="utf-8") as file:
            file.writelines(new_lines)

if __name__ == "__main__":
    blog_html = build_table(RSS_FEED.entries)
    update_readme_section(blog_html)
