import os
import re
import shutil
from pathlib import Path
from datetime import datetime

# ---------------------------
# 配置路径
# ---------------------------
POSTS_DIR = Path(r"F:\work\write\obsidian vault\pages\posts")
MD_DIR = Path(r"F:\tools\web\myweb\bookblog\content\docs\poems")
ATTACHMENTS_DIR = Path(r"F:\work\write\obsidian vault\Attachments")
STATIC_IMAGES_DIR = Path(r"F:\tools\web\myweb\bookblog\static\images")

COPYRIGHT_LINE = "© 2025 [Violey Gleem]. Licensed under CC BY-NC-ND 4.0"

# 确保目录存在
MD_DIR.mkdir(parents=True, exist_ok=True)
STATIC_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------
# 工具函数
# ---------------------------
def parse_front_matter(md_text):
    match = re.match(r"^---\n(.*?)\n---\n(.*)$", md_text, re.S)
    if match:
        return match.group(1), match.group(2)
    else:
        return "", md_text

def update_front_matter(front_matter, title, date_str):
    fm_lines = front_matter.split("\n") if front_matter else []
    fm_dict = {}
    for line in fm_lines:
        if ":" in line:
            key, value = line.split(":", 1)
            fm_dict[key.strip()] = value.strip()
    # 自动更新或新增必要字段
    fm_dict["title"] = title
    fm_dict["date"] = date_str
    fm_dict["layout"] = "single"  # 用 single 保证 Hugo Book 正常显示标题
    fm_dict["type"] = "docs"
    fm_dict["sidebar"] = "true"

    fm_new_lines = ["---"]
    for k, v in fm_dict.items():
        fm_new_lines.append(f"{k}: {v}")
    fm_new_lines.append("---")
    return "\n".join(fm_new_lines)


def copy_images_and_update_paths(md_content):
    # 标准 Markdown 图片
    def repl_md(match):
        img_path = match.group(1)
        img_name = Path(img_path).name
        src_img_path = ATTACHMENTS_DIR / img_name
        if src_img_path.exists():
            dst_img_path = STATIC_IMAGES_DIR / img_name
            shutil.copy2(src_img_path, dst_img_path)
        return f"![](/images/{img_name.replace(' ', '%20')})"

    md_content = re.sub(r"!\[.*?\]\((.*?)\)", repl_md, md_content)

    # Obsidian ![[xxx.png]]
    def repl_obsidian(match):
        img_name = match.group(1)
        src_img_path = ATTACHMENTS_DIR / img_name
        if src_img_path.exists():
            dst_img_path = STATIC_IMAGES_DIR / img_name
            shutil.copy2(src_img_path, dst_img_path)
        return f"![](/images/{img_name.replace(' ', '%20')})"

    md_content = re.sub(r"!\[\[(.*?)\]\]", repl_obsidian, md_content)
    return md_content

def process_md_file(md_path: Path):
    md_text = md_path.read_text(encoding="utf-8")
    front_matter, content = parse_front_matter(md_text)

    title = md_path.stem

    date_match = re.search(r"date:\s*(.*)", front_matter)
    if date_match:
        try:
            date_obj = datetime.strptime(date_match.group(1), "%Y-%m-%d")
        except ValueError:
            date_obj = datetime.now()
    else:
        date_obj = datetime.now()
    date_str = date_obj.strftime("%Y-%m-%d")

    front_matter_new = update_front_matter(front_matter, title, date_str)
    content = copy_images_and_update_paths(content)

    # 添加版权
    if COPYRIGHT_LINE not in content:
        content += "\n\n" + COPYRIGHT_LINE

    # 写回文件
    md_path.write_text(front_matter_new + "\n" + content, encoding="utf-8")
    print(f"Processed {md_path.name}")

def ensure_index_md(section_dir: Path, title: str):
    index_md = section_dir / "_index.md"
    if not index_md.exists():
        fm_dict = {
            "title": title,
            "type": "docs",
            "sidebar": "true",
            "layout": "single",  # 保证 section 首页显示标题
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        fm_lines = ["---"] + [f"{k}: {v}" for k, v in fm_dict.items()] + ["---"]
        index_md.write_text("\n".join(fm_lines) + f"\n\n{COPYRIGHT_LINE}", encoding="utf-8")
        print(f"Created _index.md in {section_dir}")



# ---------------------------
# 主函数
# ---------------------------
def main():
    # 创建 _index.md
    ensure_index_md(MD_DIR, "Poems")

    # 拷贝原始 md
    for post_md in POSTS_DIR.rglob("*.md"):
        dst_path = MD_DIR / post_md.name
        shutil.copy2(post_md, dst_path)
        print(f"Copied {post_md.name} to docs folder")

    # 处理 docs 下所有 md
    for md_file in MD_DIR.rglob("*.md"):
        if md_file.name == "_index.md":
            continue
        process_md_file(md_file)

    print("All markdown files copied and processed.")

if __name__ == "__main__":
    main()
