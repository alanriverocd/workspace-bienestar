#!/usr/bin/env bash
set -euo pipefail
# Build frontend and push `dist` to `gh-pages` branch using a temporary worktree
FRONTEND_DIR="frontend"
BUILD_DIR="${FRONTEND_DIR}/dist"
BRANCH="gh-pages"

echo "Building frontend..."
pushd "${FRONTEND_DIR}" >/dev/null
npm ci --silent
npm run build --silent
popd >/dev/null

TMPDIR=".ghpages_tmp"
rm -rf "${TMPDIR}"
mkdir -p "${TMPDIR}"
git worktree add -B ${BRANCH} "${TMPDIR}" origin/${BRANCH} 2>/dev/null || git worktree add -B ${BRANCH} "${TMPDIR}"

rm -rf "${TMPDIR:?}/*"
cp -r "${BUILD_DIR}/." "${TMPDIR}/"
pushd "${TMPDIR}" >/dev/null
git add --all
git commit -m "Deploy frontend build to gh-pages" || true
git push origin ${BRANCH}
popd >/dev/null
git worktree remove "${TMPDIR}" --force
echo "Deployed to branch ${BRANCH}. GitHub Pages will serve it if configured." 
