import requests
from datetime import datetime, timedelta, timezone
import os

LIVE_URL = "https://cmsx5.mtbkta.xyz/api/live-streams?limit=50&actionStatus=live&actionStatus=scheduled&brandName=all"
FIXTURES_URL = "https://biaomtv.link/wp-json/s8-live/v1/fixtures"
DETAIL_URL = "https://biaomtv.link/wp-json/s8-live/v1/fixture/{}"
OUTPUT_FILE = "biaom.m3u"

VN_TZ = timezone(timedelta(hours=7))

headers = {
    "Authorization": "Bearer 5ce148fe3b92694d818c1677f43d9473f1b7a76b4632417e1de97ede6bc4bd70",
    "User-Agent": "Mozilla/5.0"
}

def convert_to_vn_time(utc_str):
    dt_utc = datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
    dt_vn = dt_utc.astimezone(VN_TZ)
    return dt_vn.strftime("%d-%m-%Y %H:%M"), dt_vn

def fetch_live_streams():
    resp = requests.get(LIVE_URL, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json().get("data", [])

def fetch_fixtures():
    resp = requests.get(FIXTURES_URL, timeout=30)
    resp.raise_for_status()
    return resp.json().get("data", [])

def fetch_fixture_detail(fixture_id):
    resp = requests.get(DETAIL_URL.format(fixture_id), timeout=30)
    resp.raise_for_status()
    return resp.json().get("data", {})

def build_playlist(live_streams, fixtures):
    all_matches = []

    # gom trận live từ API 1
    for s in live_streams:
        start_vn, dt_vn = convert_to_vn_time(s["match"]["starting_at"])
        all_matches.append({
            "time": dt_vn,
            "title": f'{start_vn} ⚽ {s["match"]["home"]["name"]} vs {s["match"]["away"]["name"]} [LIVE] ({s.get("streamer", {}).get("displayName","N/A")})',
            "logo": s["match"]["home"]["image_url"],
            "url": s.get("mobileStreamUrl") or s.get("streamUrl"),
            "group": "Đang phát"
        })

    # gom trận sắp phát từ API 2
    for fx in fixtures:
        start_vn, dt_vn = convert_to_vn_time(fx["time"])
        detail = fetch_fixture_detail(fx["id"])
        streams = detail.get("streams", [])
        if streams:
            for s in streams:
                url = s.get("link_m3u8") or s.get("link_flv")
                commentator = s.get("commentator", {}).get("name", "N/A")
                all_matches.append({
                    "time": dt_vn,
                    "title": f'{start_vn} ⚽ {fx["left_club"]["name"]} vs {fx["right_club"]["name"]} ({commentator})',
                    "logo": fx["left_club"]["avatar_url"],
                    "url": url,
                    "group": "Sắp diễn ra"
                })
        else:
            all_matches.append({
                "time": dt_vn,
                "title": f'{start_vn} ⚽ {fx["left_club"]["name"]} vs {fx["right_club"]["name"]} - KHÔNG CÓ LINK',
                "logo": fx["left_club"]["avatar_url"],
                "url": None,
                "group": "Sắp diễn ra"
            })

    # sắp xếp tất cả theo thời gian
    all_matches.sort(key=lambda x: x["time"])

    # ghi ra file m3u
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for m in all_matches:
            if m["url"]:
                f.write(f'#EXTINF:-1 tvg-logo="{m["logo"]}" group-title="{m["group"]}" , {m["title"]}\n')
                f.write(f"{m['url']}\n")
            else:
                f.write(f'#EXTINF:-1 , {m["title"]}\n')

if __name__ == "__main__":
    live_streams = fetch_live_streams()
    fixtures = fetch_fixtures()
    print(f"🔎 Live API trả về {len(live_streams)} trận")
    print(f"🔎 Fixtures API trả về {len(fixtures)} trận")
    build_playlist(live_streams, fixtures)
    print(f"✅ File {OUTPUT_FILE} đã được ghi tại: {os.path.abspath(OUTPUT_FILE)}")
