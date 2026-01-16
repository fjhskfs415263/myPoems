import shutil
from pathlib import Path

# ---------------------------
# 源文件夹列表
# ---------------------------
SOURCE_ROOT = Path(r"F:\work\write\obsidian vault\pages\001_作品(out)\1_写")

# ---------------------------
# 目标 POSTS 目录
# ---------------------------
POSTS_DIR = Path(r"F:\work\write\obsidian vault\pages\posts")

# --- 新增：清理旧的 posts 数据，确保同步 ---
if POSTS_DIR.exists():
    print(f"🧹 Cleaning up old files in {POSTS_DIR}...")
    shutil.rmtree(POSTS_DIR) # 删除整个文件夹
POSTS_DIR.mkdir(parents=True, exist_ok=True) # 重新创建干净的目录

# ---------------------------
# 排除规则
# ---------------------------
EXCLUDE_KEYWORDS = ["实验"]

# ---------------------------
# 文件夹名 → 分类映射
# ---------------------------
CATEGORY_MAPPING = {
    "01_poems": "poems",
    "02_故事": "storys",
    "剧本": "plays",
    "04_articles": "articles"
}

def folder_to_category(folder_name: str):
    return CATEGORY_MAPPING.get(folder_name)

# ---------------------------
# 遍历源文件夹，拷贝到 POSTS_DIR
# ---------------------------
for md_file in SOURCE_ROOT.rglob("*.md"):
    # 排除实验文件
    if any(k in md_file.parts or k in md_file.name for k in EXCLUDE_KEYWORDS):
        continue

    category = folder_to_category(md_file.parent.name)
    if category is None:
        continue

    dst_dir = POSTS_DIR / category
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst_path = dst_dir / md_file.name
    shutil.copy2(md_file, dst_path)
    print(f"Copied {md_file.name} to {dst_dir}")

print("✅ Posts directory is now a clean reflection of your source files.")