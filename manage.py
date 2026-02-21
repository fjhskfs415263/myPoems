import re
import shutil
import os
from pathlib import Path
from datetime import datetime

# ---------------------------
# 配置路径 (请确保与你的实际环境一致)
# ---------------------------
POSTS_DIR = Path(r"F:\work\write\obsidian vault\pages\posts")
ATTACHMENTS_DIR = Path(r"F:\work\write\obsidian vault\Attachments")
HUGO_CONTENT_DIR = Path(r"F:\tools\web\myweb\bookblog\content\docs")
STATIC_IMAGES_DIR = Path(r"F:\tools\web\myweb\bookblog\static\images")

# 自动生成版权年份区间
START_YEAR = 2025
CURRENT_YEAR = datetime.now().year
YEAR_RANGE = f"{START_YEAR}-{CURRENT_YEAR}" if CURRENT_YEAR > START_YEAR else str(START_YEAR)
COPYRIGHT_LINE = f"© {YEAR_RANGE} [Violey Gleem]. Licensed under CC BY-NC-ND 4.0"

# ---------------------------
# 1. 环境清理
# ---------------------------
if HUGO_CONTENT_DIR.exists():
    print(f"🧹 Cleaning up Hugo content directory: {HUGO_CONTENT_DIR}")
    shutil.rmtree(HUGO_CONTENT_DIR)

if STATIC_IMAGES_DIR.exists():
    print(f"🖼️ Cleaning up Hugo static images: {STATIC_IMAGES_DIR}")
    shutil.rmtree(STATIC_IMAGES_DIR)

HUGO_CONTENT_DIR.mkdir(parents=True, exist_ok=True)
STATIC_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------
# 2. 工具函数
# ---------------------------
def parse_front_matter(md_text):
    """拆分 YAML 元数据和正文"""
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", md_text, re.S)
    if match:
        return match.group(1), match.group(2)
    return "", md_text

def update_front_matter(front_matter, title, date_str=None):
    """更新或注入 YAML 字段"""
    fm_lines = front_matter.split("\n") if front_matter else []
    fm_dict = {line.split(":",1)[0].strip(): line.split(":",1)[1].strip()
               for line in fm_lines if ":" in line}

    # 核心字段设置
    fm_dict.update({
        "title": title,
        "layout": "single",
        "type": "docs",
        "sidebar": "true",
        "bookCollapseSection": "true"
    })

    if date_str:
        fm_dict["date"] = date_str

    fm_new_lines = ["---"]
    for k, v in fm_dict.items():
        # 针对日期增加引号保护，防止 Hugo 解析出错
        if k == "date":
            fm_new_lines.append(f'{k}: "{v}"')
        else:
            fm_new_lines.append(f"{k}: {v}")
    fm_new_lines.append("---")
    return "\n".join(fm_new_lines)

def copy_images_and_update_paths(md_content):
    """处理图片引用，将 Obsidian 链接转为 Hugo 静态链接"""
    def repl_md(match):
        img_name = Path(match.group(1)).name
        src = ATTACHMENTS_DIR / img_name
        if src.exists():
            shutil.copy2(src, STATIC_IMAGES_DIR / img_name)
        return f"![](/images/{img_name.replace(' ','%20')})"
    
    md_content = re.sub(r"!\[.*?\]\((.*?)\)", repl_md, md_content)
    md_content = re.sub(r"!\[\[(.*?)\]\]", repl_md, md_content)
    return md_content

def process_md(md_path: Path, dst_dir: Path):
    """核心处理：读取、日期保底、清理旧版权、写入新文件"""
    text = md_path.read_text(encoding="utf-8")
    front, content = parse_front_matter(text)

    # 日期解析逻辑
    date_str = None
    date_match = re.search(r"^date:\s*(.+)$", front, re.M)
    if date_match:
        raw_date = date_match.group(1).strip().replace('"', '')
        try:
            dt = datetime.strptime(raw_date, "%Y-%m-%d %H:%M") if " " in raw_date else datetime.strptime(raw_date, "%Y-%m-%d")
            date_str = dt.isoformat()
        except ValueError:
            date_str = raw_date
    else:
        # 【新增】保底日期：取文件最后修改时间
        mtime = os.path.getmtime(md_path)
        date_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")

    fm_new = update_front_matter(front, md_path.stem, date_str)
    content = copy_images_and_update_paths(content)

    # 【优化】先清除可能存在的旧版权行，避免重复堆叠
    content = re.sub(r"© \d{4}.*?CC BY-NC-ND 4.0", "", content).strip()
    content += "\n\n" + COPYRIGHT_LINE

    dst_file = dst_dir / md_path.name
    dst_file.write_text(fm_new + "\n" + content, encoding="utf-8")

def folder_to_category(folder_name: str):
    """【修正】文件夹名到 Hugo 分类的映射"""
    mapping = {
        "01_poems": "poems", 
        "02_故事": "storys", 
        "05_剧本": "plays",  # 对应你的实际文件夹
        "剧本": "plays", 
        "04_articles": "articles"
    }
    return mapping.get(folder_name, folder_name.lower())

# ---------------------------
# 3. 批量执行逻辑
# ---------------------------
ALLOWED_CATEGORIES = {"poems", "storys", "plays", "articles"}

print(f"🚀 Starting to process files from {POSTS_DIR}...")

for md_file in POSTS_DIR.rglob("*.md"):
    # 跳过已经生成的 _index.md 避免死循环逻辑
    if md_file.name == "_index.md":
        continue

    parent_folder = md_file.parent.name
    hugo_subdir = folder_to_category(parent_folder)

    if hugo_subdir not in ALLOWED_CATEGORIES:
        continue

    hugo_target_dir = HUGO_CONTENT_DIR / hugo_subdir
    hugo_target_dir.mkdir(parents=True, exist_ok=True)
    process_md(md_file, hugo_target_dir)

# ---------------------------
# 4. 生成侧边栏索引 (_index.md)
# ---------------------------
INDEX_TEMPLATE = """---
title: {title}
type: docs
sidebar: true
bookCollapseSection: true
---
"""

for category in ALLOWED_CATEGORIES:
    cat_dir = HUGO_CONTENT_DIR / category
    cat_dir.mkdir(parents=True, exist_ok=True)
    index_file = cat_dir / "_index.md"

    index_file.write_text(
        INDEX_TEMPLATE.format(title=category.capitalize()),
        encoding="utf-8"
    )
    print(f"📄 Generated/Reset _index.md for {category}")

print("\n✨ All posts and Sidebars are refreshed successfully.")