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

# === Step 3: 推送到 gh-pages 分支 ===
Write-Host "==> Step 3: 部署构建产物到 gh-pages" -ForegroundColor Cyan
Set-Location $PublicPath

# 即使删除了 .git 重新 init，也要确保添加 .nojekyll (GitHub Pages 必须)
New-Item -ItemType File -Name ".nojekyll" -Force | Out-Null

git init
git checkout -b $BranchName
git remote add origin $RemoteURL
git add -A
git commit -m "Deploy site $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"

# 强制推送覆盖远程 gh-pages，因为 public 每次都是重新生成的
git push -f origin $BranchName

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 部署成功！已推送到 gh-pages 分支。" -ForegroundColor Green
} else {
    Write-Host "❌ 部署失败，请检查 SSH 权限。" -ForegroundColor Red
}

Set-Location $RepoPath
Write-Host "`n===============================" -ForegroundColor Cyan
Write-Host "🏁 部署流程完成。" -ForegroundColor Cyan