#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from http.cookiejar import Cookie, CookieJar

BASE = "https://lms.nju.edu.cn"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36")
DEFAULT_OUTDIR = r"C:\Users\szj\Downloads"

DOWNLOADABLE = ("document", "image", "audio")


def parse_cookies(text):
    """把粘贴的 Netscape 格式 cookie 文本解析进 CookieJar"""
    jar = CookieJar()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 7:
            parts = line.split()
            if len(parts) != 7:
                continue
        domain, include_sub, path, secure, expires, name, value = parts
        secure_flag = secure.lower() == "true"
        try:
            expires = int(expires) if expires else None
        except ValueError:
            expires = None
        c = Cookie(version=0, name=name, value=value, port=None,
                   port_specified=False, domain=domain,
                   domain_specified=domain.startswith("."),
                   domain_initial_dot=domain.startswith("."),
                   path=path, path_specified=True, secure=secure_flag,
                   expires=expires, discard=True, comment=None,
                   comment_url=None, rest={}, rfc2109=False)
        jar.set_cookie(c)
    return jar


def read_pasted_lines(prompt):
    print(prompt)
    lines = []
    while True:
        try:
            line = input()
        except EOFError:          # Windows: 行首 Ctrl+Z
            break
        if line.strip().upper() in ("END", "DONE", "结束"):
            break
        lines.append(line)
    return "\n".join(lines)


def http_get(opener, url, referer=None, accept="application/json"):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept": accept,
        "Referer": referer or BASE + "/course/",
    })
    return opener.open(req, timeout=120)


def get_json(opener, url, referer=None):
    with http_get(opener, url, referer) as r:
        return json.loads(r.read().decode("utf-8"))


def refer_query(activity):
    atype = activity.get("type")
    if atype == "exam":
        return ""
    rtype = "classroom_activity" if atype == "classroom" else "learning_activity"
    return "refer_id={}&refer_type={}".format(activity["id"], rtype)


def doc_url_endpoint(upload, activity):
    ref = upload.get("reference_id")
    path = "reference/document/{}".format(ref) if ref else "document/{}".format(upload["id"])
    parts = ["preview=true"]
    rq = refer_query(activity)
    if rq:
        parts.append(rq)
    return "{}/api/uploads/{}/url?{}".format(BASE, path, "&".join(parts))


def safe_name(name):
    name = re.sub(r'[\\/:*?"<>|\r\n]+', "_", name).strip()
    return name or "unnamed"


def fetch_media_url(opener, upload, activity, referer):
    utype = upload.get("type")
    if upload.get("status") == "ready" and utype == "document":
        info = get_json(opener, doc_url_endpoint(upload, activity), referer)
        return info.get("url")
    if upload.get("status") == "ready" and utype in ("image", "audio"):
        q = "?preview=true"
        rq = refer_query(activity)
        if rq:
            q += "&" + rq
        info = get_json(opener, "{}/api/uploads/{}{}".format(BASE, upload["id"], q), referer)
        return info.get("url")
    return None


def download(opener, url, dest, referer):
    with http_get(opener, url, referer, accept="*/*") as r:
        data = r.read()
    if not data:
        raise RuntimeError("空响应")
    with open(dest, "wb") as f:
        f.write(data)
    return len(data)


def fmt_size(n):
    n = n or 0
    if n >= 1048576:
        return "{:.1f}MB".format(n / 1048576)
    if n >= 1024:
        return "{:.1f}KB".format(n / 1024)
    return "{}B".format(n)


def collect_items(activities):
    """返回 [(活动, upload), ...] 可下载项"""
    items = []
    for act in activities:
        for up in act.get("uploads") or []:
            if up.get("status") == "ready" and up.get("type") in DOWNLOADABLE:
                items.append((act, up))
    return items


def parse_selection(text, count):
    """解析 '1,2,4-6' / 'all' / '' -> 索引集合"""
    text = text.strip().lower()
    if not text:
        return set()
    if text in ("all", "a", "*"):
        return set(range(count))
    idx = set()
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            lo, hi = part.split("-", 1)
            try:
                lo, hi = int(lo), int(hi)
                idx.update(range(max(lo, 1), min(hi, count) + 1))
            except ValueError:
                pass
        else:
            try:
                n = int(part)
                if 1 <= n <= count:
                    idx.add(n)
            except ValueError:
                pass
    return idx


def main():
    print("=" * 60)
    print("NJU LMS 课件下载器")
    print("=" * 60)

    # 1. 粘贴 cookie
    cookie_text = read_pasted_lines(
        "第 1 步：请粘贴导出的 cookie 内容（插件 Export 后全选复制）。\n"
        "粘贴完成后另起一行输入 END 并回车（或行首按 Ctrl+Z 回车）：")
    jar = parse_cookies(cookie_text)
    if not any(c.name == "session" for c in jar):
        sys.exit("没有解析到 session cookie，请检查复制内容是否完整。")
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

    # 2. 课程网址（自动解析课程 ID，无需自己找数字）
    while True:
        raw = input("第 2 步：请粘贴当前课件页面的网址（浏览器地址栏整条复制即可）: ").strip()
        m = re.search(r"/course/(\d+)", raw)
        if m:
            course_id = int(m.group(1))
            print("  已识别课程 ID = {}，只扫描该课程。".format(course_id))
            break
        print("  没有识别到 /course/<数字> 的网址，请重新粘贴。")

    referer = "{}/course/{}/learning-activity".format(BASE, course_id)

    # 3. 拉取活动列表
    print("正在读取课程活动...")
    try:
        data = get_json(opener, "{}/api/courses/{}/activities".format(BASE, course_id), referer)
    except urllib.error.HTTPError as e:
        if e.code in (401, 403, 302):
            sys.exit("登录态失效或被拦截 (HTTP {})，请重新登录后重新复制 cookie。".format(e.code))
        raise
    activities = data.get("activities", [])
    if not activities:
        sys.exit("该课程没有活动，或 cookie 没有该课程权限。")

    items = collect_items(activities)
    if not items:
        sys.exit("课程里没有可下载的课件（document/image/audio）。")

    # 4. 列出
    print("\n第 3 步：以下文件可供下载（{} 个）：".format(len(items)))
    print("-" * 70)
    cur_act = None
    for i, (act, up) in enumerate(items, 1):
        if act["id"] != cur_act:
            cur_act = act["id"]
            print("[活动 {}] {}".format(act["id"], act.get("title") or ""))
        print("  {:>2}. {}  ({} / {})".format(i, up.get("name"), up.get("type"),
                                               fmt_size(up.get("size"))))
    print("-" * 70)

    # 5. 选择
    sel_text = input(
        "第 4 步：输入要下载的序号（多个用逗号，范围用短横，如 1,2,4-6；\n"
        "         all=全部；直接回车=不下载）: ")
    sel = parse_selection(sel_text, len(items))
    if not sel:
        print("未选择任何文件，退出。")
        return

    os.makedirs(DEFAULT_OUTDIR, exist_ok=True)
    print("\n开始下载到: {}\n".format(DEFAULT_OUTDIR))
    ok = skip = fail = 0
    for n in sorted(sel):
        act, up = items[n - 1]
        name = up.get("name") or "unnamed"
        dest = os.path.join(DEFAULT_OUTDIR, safe_name(name))
        print("[{}] {} ...".format(n, name))
        if os.path.exists(dest) and os.path.getsize(dest) > 0:
            print("    已存在同名文件，跳过")
            skip += 1
            continue
        try:
            media_url = fetch_media_url(opener, up, act, referer)
            if not media_url:
                print("    无法获取直链")
                fail += 1
                continue
            size = download(opener, media_url, dest, referer)
            print("    完成: {} -> {}".format(fmt_size(size), dest))
            ok += 1
        except urllib.error.HTTPError as e:
            print("    失败 HTTP {}（可重新导出 cookie 后重试）".format(e.code))
            fail += 1
        except Exception as e:
            print("    失败: {}".format(e))
            fail += 1
        time.sleep(0.3)

    print("\n全部完成: 成功 {} 个, 跳过 {} 个, 失败 {} 个".format(ok, skip, fail))


if __name__ == "__main__":
    main()