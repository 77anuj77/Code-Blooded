# Fresh Push Script for Lumina Repository
# Re-initializes git repository, creates clean structured commits, and force pushes to main

Write-Host "Resetting git repository..." -ForegroundColor Cyan
Remove-Item -Recurse -Force .git -ErrorAction SilentlyContinue

git init -b main
git remote add origin https://github.com/yashchandnani07/Lumina-Rare-Disease-Triage.git

Write-Host "Creating Commit 1: Project setup & configuration..." -ForegroundColor Green
git add .gitignore .prettierrc .vercelignore package.json pnpm-lock.yaml pnpm-workspace.yaml README.md pitch.md Dockerfile vercel.json .env.example
git commit -m "chore: initialize repository configuration and workspace structure"

Write-Host "Creating Commit 2: Core clinical packages & AI pipeline..." -ForegroundColor Green
git add packages/
git commit -m "feat(packages): add schema, ingest, scoring, extractors, and agent modules"

Write-Host "Creating Commit 3: FastAPI backend service..." -ForegroundColor Green
git add apps/api/
git commit -m "feat(api): add FastAPI service, disease triage API, and Docker configuration"

Write-Host "Creating Commit 4: Next.js frontend web application..." -ForegroundColor Green
git add apps/web/
git commit -m "feat(web): add Next.js clinical intake dashboard, referral generator, and UI components"

Write-Host "Creating Commit 5: Evaluation scripts, tests, and CI workflows..." -ForegroundColor Green
git add scripts/ tests/ .github/ .
git commit -m "test & scripts: add clinical eval benchmark suite, index builders, and GitHub workflows"

Write-Host "Force pushing clean history to GitHub (origin main)..." -ForegroundColor Yellow
git push -u origin main --force

Write-Host "Fresh push complete! All commits published cleanly to GitHub." -ForegroundColor Green
