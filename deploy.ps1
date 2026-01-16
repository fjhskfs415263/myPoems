# -----------------------------
# 一键 Hugo 部署脚本 (PowerShell)
# -----------------------------
# 功能：
# 1. 自动关闭占用 public 文件夹的程序
# 2. 提交 main 分支（源文件）
# 3. 构建 Hugo 并推送到 gh-pages 分支
# -----------------------------

$RepoPath   = "F:/tools/web/myweb/bookblog"
$RemoteURL  = "git@github.com:fjhskfs415263/myPoems.git"
$BranchName = "gh-pages"

Write-Host "===============================" -ForegroundColor Cyan
Write-Host "🚀 开始自动部署 Hugo 网站" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan

# === Step 0: 检查 public 占用 ===
Write-Host "==> Step 0: 检查并关闭占用 public 的程序" -ForegroundColor Cyan
$PublicPath = Join-Path $RepoPath "public"

if (Test-Path $PublicPath) {
    try {
        # 获取占用 public 的进程（使用 handle 工具更精准，但这里用 Get-Process 检查）
        $lockedProcs = Get-Process | Where-Object {
            ($_ | Get-Process -ErrorAction SilentlyContinue).Modules |
            Where-Object { $_.FileName -like "*public*" }
        }
        if ($lockedProcs) {
            Write-Host "⚠️ 检测到以下进程可能占用 public：" -ForegroundColor Yellow
            $lockedProcs | ForEach-Object { Write-Host " - $($_.ProcessName)" -ForegroundColor DarkYellow }
            $lockedProcs | ForEach-Object { Stop-Process -Id $_.Id -Force }
            Write-Host "✅ 已终止占用 public 的进程" -ForegroundColor Green
        }
    } catch {
        Write-Host "ℹ️ 无法精确检测，但将强制删除 public 文件夹。" -ForegroundColor Yellow
    }
}

# === Step 1: 提交 main 分支 ===
Write-Host "==> Step 1: 提交源文件到 main 分支" -ForegroundColor Cyan
Set-Location $RepoPath

git add -A
git commit -m "Update source files" -ErrorAction SilentlyContinue
git push origin main

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️ main 分支推送失败，请检查远程权限。" -ForegroundColor Yellow
}

# === Step 2: 构建 Hugo ===
Write-Host "==> Step 2: 清理并构建 Hugo 网站" -ForegroundColor Cyan
if (Test-Path "$RepoPath/public") {
    Remove-Item -Recurse -Force "$RepoPath/public"
}

hugo --minify
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Hugo 构建失败，停止部署。" -ForegroundColor Red
    exit 1
}

# === Step 3: 部署 gh-pages ===
Write-Host "==> Step 3: 推送到 gh-pages 分支" -ForegroundColor Cyan
Set-Location "$RepoPath/public"

if (Test-Path ".git") { Remove-Item -Recurse -Force ".git" }

git init
git checkout -b $BranchName
git remote add origin $RemoteURL

New-Item -Path . -Name ".nojekyll" -ItemType "file" -Force | Out-Null

git add -A
git commit -m "Deploy Hugo site to gh-pages"
git push -f origin $BranchName

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ 部署成功！已推送到 gh-pages 分支。" -ForegroundColor Green
} else {
    Write-Host "❌ 部署失败，请检查 SSH 权限或网络连接。" -ForegroundColor Red
}

Write-Host "`n===============================" -ForegroundColor Cyan
Write-Host "🏁 部署流程完成。" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan
