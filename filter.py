import re


def match_keywords(title, keywords):
    for kw in keywords:
        if kw in title:
            return True
    return False


def filter_notifications(notifications, keywords):
    matched = []
    for item in notifications:
        if match_keywords(item["title"], keywords):
            item["matched"] = True
            matched.append(item)
    return matched


def extract_date(date_str):
    if not date_str:
        return ""
    match = re.search(r"(\d{4}-\d{2}-\d{2})", date_str)
    return match.group(1) if match else date_str
