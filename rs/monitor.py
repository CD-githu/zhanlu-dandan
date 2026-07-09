import json
import schedule
import time
import sys
import os
import datetime

if sys.stdout.encoding != "utf-8":
    sys.stdout = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def load_config(config_path="config.json"):
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_once(config):
    print(f"\n{'='*60}")
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始抓取")
    print(f"{'='*60}")

    from spider import HRSSSpider
    from filter import filter_notifications
    from notifier import Notifier
    import storage

    storage.init_db()

    all_notifications = HRSSSpider(config_path="config.json").run()

    keywords = config.get("keywords", [])
    if not keywords:
        print("[WARNING] 未配置关键词，将不过滤")

    matched = filter_notifications(all_notifications, keywords)
    print(f"\n[筛选] 关键词匹配: {len(matched)} 条")

    new_notifications = []
    for item in matched:
        if not storage.is_exists(item["id"]):
            storage.save_notification(
                item["id"],
                item["title"],
                item["url"],
                item["date"],
                item["source"],
                matched=True
            )
            new_notifications.append(item)

    print(f"[新通知] {len(new_notifications)} 条")

    if new_notifications:
        Notifier(config).send(new_notifications)
    else:
        print("[INFO] 无新通知")

    print(f"\n[完成] 本次抓取结束")
    return len(new_notifications)


def main():
    config = load_config()

    print("="*60)
    print("云南省人社厅通知监控工具")
    print("="*60)

    if not config.get("schedule", {}).get("enabled", True):
        print("[INFO] 定时任务已禁用，执行单次抓取")
        run_once(config)
        return

    schedule_time = config.get("schedule", {})
    hour = schedule_time.get("hour", 8)
    minute = schedule_time.get("minute", 0)

    print(f"[INFO] 定时任务已启用，每天 {hour:02d}:{minute:02d} 执行")
    print(f"[INFO] 按 Ctrl+C 退出\n")

    schedule.every().day.at(f"{hour:02d}:{minute:02d}").do(lambda c=config: run_once(c))

    run_once(config)

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n[INFO] 程序已退出")


if __name__ == "__main__":
    main()
