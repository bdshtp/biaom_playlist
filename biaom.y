import requests
from datetime import datetime, timedelta, timezone
import os

API_URL = "https://cmsx5.mtbkta.xyz/api/live-streams?limit=50&actionStatus=live&actionStatus=scheduled&brandName=all"
OUTPUT_FILE = "biaom.m3u"

VN_TZ = timezone(timedelta(hours=7))

# thêm token vào header
headers = {
    "Authorization": "Bearer 5ce148fe3b92694d818c1677f43d9473f1b7a76b4632417e1de97ede6bc4bd70",
    "User-Agent": "Mozilla/5.0"
}

def fetch_streams():
    resp = requests.get(API_URL, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data["data"]

def convert_to_vn_time(utc_str):
    dt_utc = datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
    dt_vn = dt_utc.astimezone(VN_TZ)
    return dt_vn.strftime("%d-%m-%Y %H:%M")

def build_playlist(streams):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for s in streams:
            home = s["match"]["home"]["name"]
            away = s["match"]["away"]["name"]
            start_time = s["match"]["starting_at"]
            start_vn = convert_to_vn_time(start_time)
            logo = s["match"]["home"]["image_url"]
            commentator = s["streamer"]["displayName"]
            status = s["actionStatus"].upper()
            url = s.get("mobileStreamUrl") or s.get("streamUrl")

            line_title = f'{start_vn} ⚽ {home} vs {away} [{status}] ({commentator})'
            if url:
                f.write(f'#EXTINF:-1 tvg-logo="{logo}" group-title="Biaom TV" , {line_title}\n')
                f.write(f"{url}\n")
            else:
                f.write(f'#EXTINF:-1 , {line_title} - KHÔNG CÓ LINK\n')

if __name__ == "__main__":
    streams = fetch_streams()
    print(f"🔎 API trả về {len(streams)} trận")
    for s in streams[:5]:
        print("Match:", s["title"], "| Status:", s["actionStatus"],
              "| URL:", s.get("mobileStreamUrl") or s.get("streamUrl"))
    build_playlist(streams)
    print(f"✅ File {OUTPUT_FILE} đã được ghi tại: {os.path.abspath(OUTPUT_FILE)}")
