import re
import shutil
from pathlib import Path
from datetime import datetime

# ---------------------------
# 配置路径
# ---------------------------
POSTS_DIR = Path(r"F:\work\write\obsidian vault\pages\posts")
ATTACHMENTS_DIR = Path(r"F:\work\write\obsidian vault\Attachments")
HUGO_CONTENT_DIR = Path(r"F:\tools\web\myweb\bookblog\content\docs")
STATIC_IMAGES_DIR = Path(r"F:\tools\web\myweb\bookblog\static\images")
COPYRIGHT_LINE = "© 2025 [Violey Gleem]. Licensed under CC BY-NC-ND 4.0"

# ---------------------------
# 1. 彻底同步：清理旧的内容和图片
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
# 工具函数
# ---------------------------
def parse_front_matter(md_text):
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", md_text, re.S)
    if match:
        return match.group(1), match.group(2)
    return "", md_text

def update_front_matter(front_matter, title, date_str=None):
    fm_lines = front_matter.split("\n") if front_matter else []
    fm_dict = {line.split(":",1)[0].strip(): line.split(":",1)[1].strip()
               for line in fm_lines if ":" in line}

    # 关键点：确保这些字段存在，侧边栏才不会丢
    fm_dict.update({
        "title": title,
        "layout": "single",
        "type": "docs",
        "sidebar": "true",
        "bookCollapseSection": "true"  # 如果你使用的是 Book 主题，这个很有帮助
    })

    if date_str:
        fm_dict["date"] = date_str

    fm_new_lines = ["---"]
    for k, v in fm_dict.items():
        if k == "date":
            fm_new_lines.append(f'{k}: "{v}"')
        else:
            fm_new_lines.append(f"{k}: {v}")
    fm_new_lines.append("---")
    return "\n".join(fm_new_lines)

def copy_images_and_update_paths(md_content):
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
    text = md_path.read_text(encoding="utf-8")
    front, content = parse_front_matter(text)

    date_str = None
    date_match = re.search(r"^date:\s*(.+)$", front, re.M)
    if date_match:
        raw_date = date_match.group(1).strip().replace('"', '')
        try:
            dt = datetime.strptime(raw_date, "%Y-%m-%d %H:%M") if " " in raw_date else datetime.strptime(raw_date, "%Y-%m-%d")
            date_str = dt.isoformat()
        except ValueError:
            date_str = raw_date

    fm_new = update_front_matter(front, md_path.stem, date_str)
    content = copy_images_and_update_paths(content)

    if COPYRIGHT_LINE not in content:
        content += "\n\n" + COPYRIGHT_LINE

    dst_file = dst_dir / md_path.name
    dst_file.write_text(fm_new + "\n" + content, encoding="utf-8")

# ---------------------------
# 映射函数
# ---------------------------
def folder_to_category(folder_name: str):
    mapping = {"01_poems": "poems", "02_故事": "storys", "剧本": "plays", "04_articles": "articles"}
    return mapping.get(folder_name, folder_name.lower())

# ---------------------------
# 2. 批量处理逻辑
# ---------------------------
ALLOWED_CATEGORIES = {"poems", "storys", "plays", "articles"}

for md_file in POSTS_DIR.rglob("*.md"):
    parent_folder = md_file.parent.name
    hugo_subdir = folder_to_category(parent_folder)
    
    if hugo_subdir not in ALLOWED_CATEGORIES:
        continue

    hugo_target_dir = HUGO_CONTENT_DIR / hugo_subdir
    hugo_target_dir.mkdir(parents=True, exist_ok=True)
    process_md(md_file, hugo_target_dir)

# ---------------------------
# 3. 强制生成/重置侧边栏索引 (_index.md)
# ---------------------------
# 这是侧边栏生成的灵魂，必须确保每个子文件夹都有它
INDEX_TEMPLATE = """---
title: {title}
type: docs
sidebar: true
bookCollapseSection: true
---
"""

for category in ALLOWED_CATEGORIES:
    cat_dir = HUGO_CONTENT_DIR / category
    # 只要这个分类应该存在，就必须创建它的 _index.md
    cat_dir.mkdir(parents=True, exist_ok=True)
    index_file = cat_dir / "_index.md"
    
    # 强制覆盖生成，确保侧边栏属性正确
    index_file.write_text(
        INDEX_TEMPLATE.format(title=category.capitalize()), 
        encoding="utf-8"
    )
    print(f"📄 Generated/Reset _index.md for {category}")

print("\n🚀 All posts and Sidebars are refreshed.")