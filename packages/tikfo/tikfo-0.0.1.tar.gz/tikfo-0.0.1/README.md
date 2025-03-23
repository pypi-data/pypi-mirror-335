# TikTokInfo

**TikTokInfo** is a Python library and command-line tool for fetching TikTok video metadata, including the author, title, thumbnail, and avatar.

---

```bash
pip install tiktok_info
```
```bash
tiktok_get -url <url_tiktok> -help
```
```bash
#run using the script

from tiktok_get_info import TiktokGetInfo
url = "https://vm.tiktok.com/vid_id/"
tiktok = TiktokGetInfo(url)

print("Author:", tiktok.author())
print("Title:", tiktok.title())
print("Username:", tiktok.username())
print("Thumbnail:", tiktok.thumbnail())
print("Avatar:", tiktok.avatar())
print("Endpoint URL:", tiktok.endpoint())
