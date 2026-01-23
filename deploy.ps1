# -----------------------------
# 一键 Hugo 部署脚本 (PowerShell 优化版)
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

# 1. 先把本地的新内容加入暂存区
git add -A

# 2. 检查是否有需要提交的内容
$status = git status --porcelain
if ($status) {
    Write-Host "📝 检测到本地修改，正在提交..." -ForegroundColor Gray
    git commit -m "Update content and theme: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
} else {
    Write-Host "ℹ️ 本地没有新变化，跳过提交。" -ForegroundColor Gray
}

# 3. 拉取远程更新 (因为本地已 commit，不再会有 unstaged changes 报错)
Write-Host "🔄 同步远程仓库..." -ForegroundColor Gray
git pull origin main --rebase

# 4. 推送源码到 main
Write-Host "📤 推送源码到 GitHub..." -ForegroundColor Gray
git push origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ main 分支推送遇到问题，请检查是否存在冲突。" -ForegroundColor Yellow
}

# === Step 2: 清理并构建 Hugo 网站 ===
Write-Host "==> Step 2: 清理旧文件并构建 Hugo" -ForegroundColor Cyan
$PublicPath = Join-Path $RepoPath "public"
if (Test-Path $PublicPath) {
    # 强制清理 public 文件夹，确保生成最新内容
    Remove-Item -Recurse -Force $PublicPath -ErrorAction SilentlyContinue
}

# 执行 Hugo 构建
hugo --minify
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Hugo 构建失败，停止部署。" -ForegroundColor Red
    exit 1
}

# === Step 3: 部署 gh-pages (发布静态网页) ===
Write-Host "==> Step 3: 推送到 gh-pages 分支" -ForegroundColor Cyan
if (-not (Test-Path "$RepoPath/public")) {
    Write-Host "❌ 错误：public 文件夹不存在，构建可能未成功。" -ForegroundColor Red
    exit 1
}

Set-Location "$RepoPath/public"

# 1. 重新初始化编译后的静态仓库
if (Test-Path ".git") { Remove-Item -Recurse -Force ".git" }
git init
git config core.quotepath false

# 2. 准备分支环境
git checkout -b $BranchName
git remote add origin $RemoteURL
# 创建 .nojekyll 确保 GitHub 不会拦截特殊文件夹
New-Item -Path . -Name ".nojekyll" -ItemType "file" -Force | Out-Null

# 3. 提交静态页面
git add .
$deployMsg = "Deploy site $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
git commit -m "$deployMsg"

# 4. 强制推送静态网页到 gh-pages 分支
$headExists = git rev-parse --verify HEAD 2>$null
if ($headExists) {
    Write-Host "🚀 正在推送静态网页至 GitHub gh-pages..." -ForegroundColor Cyan
    git push -f origin $BranchName
} else {
    Write-Host "❌ 错误：本地没有产生提交记录，请检查内容是否生成。" -ForegroundColor Red
    exit 1
}

Write-Host "`n✅ 部署完成！请等待 1-2 分钟查看网页更新。" -ForegroundColor Green
Set-Location $RepoPath