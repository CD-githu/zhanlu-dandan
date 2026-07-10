import requests
from bs4 import BeautifulSoup
import time
import json
import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class HRSSSpider:
    def __init__(self, config_path="config.json"):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": self.config.get("user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        })
        self.delay = self.config.get("request_delay", 2)

    def fetch_page(self, url):
        try:
            resp = self.session.get(url, timeout=15)
            resp.encoding = resp.apparent_encoding
            if resp.status_code == 200:
                return resp.text
            else:
                print(f"  [ERROR] HTTP {resp.status_code}: {url}")
                return None
        except Exception as e:
            print(f"  [ERROR] Fetch failed: {url} -> {e}")
            return None

    def parse_hrss_list(self, html, source_name, base_url):
        """Parse hrss.yn.gov.cn list page"""
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        results = []

        # Find the news list ul
        news_ul = soup.select_one("ul.ul13")
        if not news_ul:
            news_ul = soup.select_one("div.listBox ul")
        if not news_ul:
            print(f"  [WARN] 未找到新闻列表容器")
            return []

        items = news_ul.find_all("li")
        if not items:
            print(f"  [WARN] 列表中没有li元素")
            return []

        for item in items:
            try:
                link = item.select_one("a")
                if not link:
                    continue

                title = link.get("title", "").strip()
                if not title:
                    title = link.get_text(strip=True)

                href = link.get("href", "")
                if not href:
                    continue

                # Build full URL
                if href.startswith("/"):
                    href = base_url.rstrip("/") + href
                elif not href.startswith("http"):
                    href = base_url.rstrip("/") + "/" + href

                # Extract date from span
                date_span = item.select_one("span")
                date_text = ""
                if date_span:
                    date_text = date_span.get_text(strip=True)

                # Extract NewsID
                news_id = ""
                if "NewsID=" in href:
                    news_id = href.split("NewsID=")[1].split("&")[0]
                elif "newsID=" in href:
                    news_id = href.split("newsID=")[1].split("&")[0]

                if title and news_id:
                    results.append({
                        "id": news_id,
                        "title": title,
                        "url": href,
                        "date": date_text,
                        "source": source_name,
                    })
            except Exception as e:
                continue

        return results

    def _fetch_zwfw_via_playwright(self, url, source_name):
        """Fetch zwfw.hrss.yn.gov.cn notifications using Playwright or fallback"""
        # 先尝试普通方式抓取，失败后再用Playwright
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                page = context.new_page()
                
                page.goto(url, timeout=30000)
                page.wait_for_load_state("networkidle")
                page.wait_for_timeout(3000)
                
                notifications = page.evaluate(f"""
                    () => {{
                        const sourceName = '{source_name}';
                        const results = [];
                        
                        const lists = document.querySelectorAll('ul.tz-header-body-ul');
                        
                        if (lists.length > 0) {{
                            lists.forEach(ul => {{
                                const items = ul.querySelectorAll('li.tz-header-body-ul-li');
                                
                                items.forEach(item => {{
                                    const linkEl = item.querySelector('a.tz-header-body-ul-li-a');
                                    if (!linkEl) return;
                                    
                                    let title = linkEl.getAttribute('title') || '';
                                    if (!title) {{
                                        const span = linkEl.querySelector('span.tz-header-body-ul-li-a-span');
                                        if (span) {{
                                            title = span.textContent?.trim() || '';
                                        }}
                                    }}
                                    
                                    title = title.replace(/[•·]/g, '').replace(/[置顶]/g, '').replace(/\\s+/g, ' ').trim();
                                    
                                    let date = '';
                                    const timeEl = linkEl.querySelector('em.tz-header-body-ul-li-a-time, .time, .date');
                                    if (timeEl) {{
                                        date = timeEl.textContent?.trim() || '';
                                    }}
                                    
                                    let url = 'https://zwfw.hrss.yn.gov.cn/zjgl/qt/index/tz?id=sy_zcgz';
                                    let id = title.substring(0, 50).replace(/[^\\u4e00-\\u9fa5a-zA-Z0-9]/g, '');
                                    
                                    if (title && title.length > 5 && !results.find(r => r.title === title)) {{
                                        results.push({{
                                            id: id,
                                            title: title,
                                            url: url,
                                            date: date,
                                            source: sourceName
                                        }});
                                    }}
                                }});
                            }});
                        }}
                        
                        return results;
                    }}
                """)
                
                browser.close()
                results = notifications
                
        except ImportError:
            print(f"  [WARN] Playwright不可用，跳过人才服务平台抓取")
            return []
        except Exception as e:
            print(f"  [ERROR] Playwright错误: {e}")
            return []
        
        return results

    def parse_exam_list(self, html, source_name, base_url):
        """Parse ynrsksw exam website list page"""
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        results = []

        # Exam website uses ul.page_newslist, ul.newslist, ul.newslist.nodatelist
        list_selectors = [
            "ul.page_newslist li",
            "ul.newslist li",
            "ul.newslist.nodatelist li",
        ]

        items = []
        for sel in list_selectors:
            items.extend(soup.select(sel))

        if not items:
            print(f"  [WARN] 未找到新闻列表容器")
            return []

        for item in items:
            try:
                link = item.select_one("a")
                if not link:
                    continue

                title = link.get_text(strip=True)
                href = link.get("href", "")

                if not href or not title:
                    continue

                # Skip non-news links
                if "javascript" in href or "void" in href:
                    continue
                if any(x in href for x in ["Special", "News4", "News5", "News6", "Page5", "Index.html"]):
                    continue

                # Build full URL
                if href.startswith("/"):
                    href = base_url.rstrip("/") + href
                elif not href.startswith("http"):
                    href = base_url.rstrip("/") + "/" + href

                # Extract date from span
                date_text = ""
                date_span = item.select_one("span, .date, .time")
                if date_span:
                    date_text = date_span.get_text(strip=True)

                # Extract ID: href like i1350.html
                news_id = ""
                id_match = re.search(r"i(\d+)\.html", href)
                if id_match:
                    news_id = id_match.group(1)

                if title and news_id:
                    results.append({
                        "id": news_id,
                        "title": title,
                        "url": href,
                        "date": date_text,
                        "source": source_name,
                    })
            except Exception as e:
                continue

        return results

    def fetch_source(self, source):
        print(f"\n[抓取] {source['name']}")
        base_url = source.get("base", "http://hrss.yn.gov.cn")
        url = source["url"]
        max_pages = self.config.get("max_pages", 5)
        all_results = []

        # HRSS site uses pagination with &page=N
        if "hrss.yn.gov.cn/ynrsksw" in url:
            # Exam website - single page
            html = self.fetch_page(url)
            if html:
                results = self.parse_exam_list(html, source["name"], base_url)
                all_results.extend(results)
                print(f"  [OK] {len(results)} 条")
        elif "zwfw.hrss.yn.gov.cn" in url:
            # zwfw platform - requires Playwright for JS rendering
            results = self._fetch_zwfw_via_playwright(url, source["name"])
            all_results.extend(results)
            print(f"  [OK] {len(results)} 条")
        else:
            # HRSS main site - paginated
            for page in range(1, max_pages + 1):
                if page == 1:
                    page_url = url
                else:
                    page_url = f"{url}&page={page + 1}"

                html = self.fetch_page(page_url)
                if not html:
                    if page == 1:
                        print("  [ERROR] 无法获取第一页")
                    break

                results = self.parse_hrss_list(html, source["name"], base_url)

                if not results:
                    print(f"  [INFO] 第 {page} 页无数据，停止翻页")
                    break

                print(f"  [OK] 第 {page} 页: {len(results)} 条")
                all_results.extend(results)

                if len(results) < 10:
                    break

                time.sleep(self.delay)

        return all_results

    def run(self):
        all_results = []
        for source in self.config["sources"]:
            results = self.fetch_source(source)
            all_results.extend(results)
            time.sleep(self.delay)

        # Deduplicate
        seen = set()
        unique_results = []
        for item in all_results:
            if item["id"] not in seen:
                seen.add(item["id"])
                unique_results.append(item)

        print(f"\n[总计] 共抓取 {len(unique_results)} 条通知")
        return unique_results
