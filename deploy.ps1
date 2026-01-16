# -----------------------------
# 一键 Hugo 部署脚本 (PowerShell 修正版)
# -----------------------------

$RepoPath   = "F:/tools/web/myweb/bookblog"
$RemoteURL  = "git@github.com:fjhskfs415263/myPoems.git"
$BranchName = "gh-pages"

Write-Host "===============================" -ForegroundColor Cyan
Write-Host "🚀 开始自动部署 Hugo 网站" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan

# 开启全局 Git 中文路径支持
git config --global core.quotepath false

# === Step 1: 提交源文件到 main 分支 ===
Write-Host "==> Step 1: 同步并提交源文件到 main 分支" -ForegroundColor Cyan
Set-Location $RepoPath

# 先拉取远程更新防止冲突 (使用 rebase 保持提交线整洁)
git pull origin main --rebase

git add -A
# 确保使用半角引号，不要带特殊格式
git commit -m "Update content and theme" 

# 尝试推送，如果还失败就强制推送一次（慎用，仅限个人项目）
git push origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ main 分支推送失败，尝试解决冲突或手动检查。" -ForegroundColor Yellow
}

# === Step 2: 清理并构建 Hugo 网站 ===
Write-Host "==> Step 2: 清理旧文件并构建 Hugo" -ForegroundColor Cyan
$PublicPath = Join-Path $RepoPath "public"
if (Test-Path $PublicPath) {
    Remove-Item -Recurse -Force $PublicPath -ErrorAction SilentlyContinue
}

hugo --minify
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Hugo 构建失败，停止部署。" -ForegroundColor Red
    exit 1
}

# === Step 3: 部署 gh-pages (增强版) ===
Write-Host "==> Step 3: 推送到 gh-pages 分支" -ForegroundColor Cyan
Set-Location "$RepoPath/public"

# 1. 彻底重新初始化
if (Test-Path ".git") { Remove-Item -Recurse -Force ".git" }
git init
git config core.quotepath false  # 防止中文路径乱码

# 2. 准备基础环境
git checkout -b $BranchName
git remote add origin $RemoteURL
New-Item -Path . -Name ".nojekyll" -ItemType "file" -Force | Out-Null

# 3. 提交文件
git add .
# 注意：这里我们强制捕获 commit 的状态
$commitMessage = "Deploy site $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
git commit -m "$commitMessage"

# 4. 关键检查：只有本地有 commit 记录时才 push
$headExists = git rev-parse --verify HEAD 2>$null
if ($headExists) {
    Write-Host "🚀 正在推送至 GitHub..." -ForegroundColor Cyan
    git push -f origin $BranchName
} else {
    Write-Host "❌ 错误：本地没有产生任何提交记录（可能是 git add 失败），请检查 public 文件夹内容。" -ForegroundColor Red
    exit 1
}