import requests
from datetime import datetime, timedelta, timezone
import os

FIXTURES_URL = "https://biaomtv.link/wp-json/s8-live/v1/fixtures"
DETAIL_URL = "https://biaomtv.link/wp-json/s8-live/v1/fixture/{}"
OUTPUT_FILE = "biaom_full.m3u"

VN_TZ = timezone(timedelta(hours=7))

def convert_to_vn_time(utc_str):
    dt_utc = datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
    dt_vn = dt_utc.astimezone(VN_TZ)
    return dt_vn.strftime("%d-%m-%Y %H:%M")

def fetch_fixtures():
    resp = requests.get(FIXTURES_URL, timeout=30)
    resp.raise_for_status()
    return resp.json().get("data", [])

def fetch_fixture_detail(fixture_id):
    resp = requests.get(DETAIL_URL.format(fixture_id), timeout=30)
    resp.raise_for_status()
    return resp.json().get("data", {})

def build_playlist(fixtures):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for fx in fixtures:
            fixture_id = fx["id"]
            title = fx["title"]
            start_time = fx["time"]
            start_vn = convert_to_vn_time(start_time)
            home = fx["left_club"]["name"]
            away = fx["right_club"]["name"]
            logo = fx["left_club"]["avatar_url"]

            # gọi chi tiết để lấy link stream
            detail = fetch_fixture_detail(fixture_id)
            streams = detail.get("streams", [])
            if streams:
                for s in streams:
                    url = s.get("link_m3u8") or s.get("link_flv")
                    commentator = s.get("commentator", {}).get("name", "N/A")
                    line_title = f'{start_vn} ⚽ {home} vs {away} ({commentator})'
                    f.write(f'#EXTINF:-1 tvg-logo="{logo}" group-title="Biaom TV" , {line_title}\n')
                    f.write(f"{url}\n")
            else:
                f.write(f'#EXTINF:-1 , {start_vn} ⚽ {home} vs {away} - KHÔNG CÓ LINK\n')

if __name__ == "__main__":
    fixtures = fetch_fixtures()
    print(f"🔎 API fixtures trả về {len(fixtures)} trận")
    build_playlist(fixtures)
    print(f"✅ File {OUTPUT_FILE} đã được ghi tại: {os.path.abspath(OUTPUT_FILE)}")
