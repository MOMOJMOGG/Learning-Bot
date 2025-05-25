import requests
import json
import time

# === API 參數設定 ===
API_BASE = "https://api.sat.cool/api/v2"
FILE_BASE = f"https://files.sat.cool/{{}}"
COURSE_LIST_URL = f"{API_BASE}/courses"
COURSE_DETAIL_URL = f"{API_BASE}/course/{{}}"
BUNDLE_URL = f"{API_BASE}/course_bundles?course_id={{}}"
COURSE_PAGE_LIMIT = 9
TOTAL_COURSE_COUNT = 30
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def fetch_course_list(page: int, limit: int):
    url = f"{COURSE_LIST_URL}?page={page}&limit={limit}"
    response = requests.get(url, headers=HEADERS)
    return response.json().get("data", [])

def fetch_course_detail(course_id: int):
    url = COURSE_DETAIL_URL.format(course_id)
    response = requests.get(url, headers=HEADERS)
    return response.json().get("data", {})

def fetch_course_bundles(course_id: int):
    url = BUNDLE_URL.format(course_id)
    response = requests.get(url, headers=HEADERS)
    return response.json().get("data", {})

def parse_bundles(data):
    if not data:
        return []
    
    parsed_data = []
    for bundle in data:
        name = bundle.get("bundle", {}).get("name", "")
        
        projects = bundle.get("projects", [])
        total_price = 0
        sale_price  = 0
        
        group = []
        
        for p in projects:
            total_price += p.get("sale_price", 0)
            sale_price += p.get("sale_price", 0)
            sale_price -= p.get("discount", 0)
            group.append({
                "id": p.get("course", {}).get("id", ""),
                "cover": p.get("course", {}).get("cover", ""),
                "name":  p.get("course", {}).get("name", "")
            })
        
        parsed_data.append({
            "name": name,
            "total": total_price,
            "sale": sale_price,
            "group": group
        })
    
    return parsed_data
    
def calc_duration(duration_sec):
    if type(duration_sec) == type(None):
        return "無限制"
    
    minite = int(duration_sec / 60)
    hour, minite = int(minite / 60), int(minite % 60)
    return f"{hour} 小時 {minite} 分鐘"
    
if __name__ == '__main__':
    # === 儲存課程資料 ===
    course_data_list = []
    
    # === 開始爬蟲 ===
    page = 1
    
    while len(course_data_list) < TOTAL_COURSE_COUNT:
        course_dict = fetch_course_list(page, COURSE_PAGE_LIMIT)
        
        for course in course_dict.get('courses', []):
            course_id = course.get("id")
            detail = fetch_course_detail(course_id)
            
            bundles = fetch_course_bundles(course_id)
            bundles_data = parse_bundles(bundles)
            
            dutation_str = calc_duration(detail.get("info", {}).get("duration", 0))
            expired_str  = calc_duration(detail.get("info", {}).get("expired_time", None))
            
            course_data = {
                "title": detail.get("name", ""),
                "teacher": {
                        "name":  detail.get("teacher", {}).get("nick_name", ""),
                        "brief": detail.get("teacher", {}).get("brief", "")
                    },
                "platform": "SAT知識衛星",
                "link": f"https://sat.cool/course/{course_id}",
                "category": detail.get("category", {}),             #? name, slug
                "intro": detail.get("info", {}).get("description", "").strip(),
                "info": {
                        "chapter_count": detail.get("info", {}).get("chapter_count", 0),
                        "duration": dutation_str,
                        "expired_time": expired_str,
                        "member_count": detail.get("info", {}).get("member_count", 0)
                    },
                "price": {
                        "original": detail.get("main_project", {}).get("original_price", 0),
                        "price": detail.get("main_project", {}).get("sale_price", 0)
                    },
                "rating": {
                        "rate": detail.get("rate", 0),
                        "rate_contents": detail.get("rate_contents", []),
                        "rate_count": detail.get("rate_count", 0)
                    },
                "image": detail.get("images", {}).get("seo_cover", ""),
                "bundles": bundles_data
            }
            
            course_data_list.append(course_data)
            print("Crawler course: {} -- Done".format(detail.get("name", "")))
            
            if len(course_data_list) >= TOTAL_COURSE_COUNT:
                break
            
            time.sleep(0.5)  # 避免過度請求
        
        page += 1

    # === 儲存為 JSON 檔案 ===
    with open("data/sat_courses.json", "w", encoding="utf-8") as f:
        json.dump(course_data_list, f, ensure_ascii=False, indent=2)
        
    print(f"✅ 已成功儲存 {len(course_data_list)} 筆課程資料至 sat_courses.json")
        
        