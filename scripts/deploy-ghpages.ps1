Param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$frontend = "frontend"
$buildDir = Join-Path $frontend 'dist'
$branch = 'gh-pages'

Write-Host "Building frontend..."
Push-Location $frontend
cmd /c "npm ci --silent"
cmd /c "npm run build --silent"
Pop-Location

$tmp = Join-Path (Get-Location) '.ghpages_tmp'
if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
New-Item -ItemType Directory -Path $tmp | Out-Null

try {
    git worktree add -B $branch $tmp origin/$branch 2>$null
} catch {
    git worktree add -B $branch $tmp
}

Get-ChildItem -Path $tmp -Force | Where-Object { $_.Name -ne '.' -and $_.Name -ne '..' } | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
Copy-Item -Path (Join-Path $buildDir '*') -Destination $tmp -Recurse -Force

Push-Location $tmp
git add --all
try { git commit -m "Deploy frontend build to gh-pages" } catch { }
git push origin $branch
Pop-Location

git worktree remove $tmp --force
Write-Host "Deployed to branch $branch. GitHub Pages will serve it if configured."
