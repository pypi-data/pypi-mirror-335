import requests
import urllib.parse
import re
import argparse
import sys

class TiktokGetInfo:
    def __init__(self, url):
        self.url = url
        self._fetch_info()

    def _fetch_info(self):
        # Resolve the final URL
        self.final_url = requests.head(self.url, allow_redirects=True).url
        self.parsed_url = urllib.parse.urljoin(
            self.final_url, urllib.parse.urlparse(self.final_url).path
        )

        # Fetch video information
        info = requests.get(f"https://www.tiktok.com/oembed?url={self.parsed_url}").json()
        self._author = info.get("author_name", "N/A")
        self._username = info.get("author_unique_id", "N/A")
        self._title = info.get("title", "N/A")
        self._thumbnail = info.get("thumbnail_url", "N/A")
        try:
            profile_page = requests.get(f"https://www.tiktok.com/@{self._username}",headers={"User-Agent": "Mozilla/5.0"}).text
            self._avatar = re.search(r'"avatarLarger":"(https:[^"]+)"', profile_page).group(1).replace("\\u002F", "/")
        except Exception:
            self._avatar = "N/A"

    def author(self):
        return self._author
    def username(self):
        return self._username
    def title(self):
        return self._title
    def thumbnail(self):
        return self._thumbnail
    def avatar(self):
        return self._avatar
    def endpoint(self):
        return self.parsed_url

def cli():
    parser = argparse.ArgumentParser(
        description="TikTokGetInfo: Fetch TikTok video details"
    )
    parser.add_argument("-url", type=str, help="TikTok video URL")
    parser.add_argument("-author", action="store_true", help="Display author")
    parser.add_argument("-username", action="store_true", help="Display username")
    parser.add_argument("-title", action="store_true", help="Display title")
    parser.add_argument("-thumbnail", action="store_true", help="Display thumbnail")
    parser.add_argument("-avatar", action="store_true", help="Display avatar")
    parser.add_argument("-endpoint", action="store_true", help="Display endpoint URL")
    parser.add_argument("-getall", action="store_true", help="Display all information")
    parser.add_argument("-help", action="store_true", help="Show usage guide")

    args = parser.parse_args()

    if args.help:
        print("""
Usage: tiktok_get [OPTIONS]

Options:
  -url <URL>          Specify TikTok video URL
  -author             Show the author
  -username           Show the username
  -title              Show the video title
  -thumbnail          Show the thumbnail URL
  -avatar             Show the avatar URL
  -endpoint           Show the endpoint URL
  -getall             Show all video information
  -help               Show this help message

Examples:
  tiktok_get -url https://vt.tiktok.com/ZS6F3MQnL/ -getall
  tiktok_get -url https://vm.tiktok.com/ZS6F3MQnL/ -getall
        """)
        sys.exit(0)

    if not args.url:
        print("Error: Please provide a TikTok URL using -url")
        sys.exit(1)

    tiktok = TiktokGetInfo(args.url)

    if args.getall:
        print(tiktok.author())
        print(tiktok.username())
        print(tiktok.title())
        print(tiktok.thumbnail())
        print(tiktok.avatar())
        print(tiktok.endpoint())
    if args.author:
        print(tiktok.author())
    if args.username:
        print(tiktok.username())
    if args.title:
        print(tiktok.title())
    if args.thumbnail:
        print(tiktok.thumbnail())
    if args.avatar:
        print(tiktok.avatar())
    if args.endpoint:
        print(tiktok.endpoint())


if __name__ == "__main__":
    cli()
