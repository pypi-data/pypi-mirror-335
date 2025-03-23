import argparse
import sys
from .info import tikfo

def cli():
    parser = argparse.ArgumentParser(
        description="TIKFO: Fetch TikTok video details"
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
Usage: tiktok-info [OPTIONS]

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
  tiktok-info -url https://vt.tiktok.com/ZS6F3MQnL/ -getall
  tiktok-info -url https://vm.tiktok.com/ZS6F3MQnL/ -getall
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
