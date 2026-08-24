# Phase 2 Completion Script
# Run this after Docker Desktop has fully started

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PHASE 2 - Database Models & Migration" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Start PostgreSQL
Write-Host "Step 1: Starting PostgreSQL via Docker Compose..." -ForegroundColor Yellow
Set-Location "A:\padhai_related\vit\projects\society_managment"
docker compose up -d
Start-Sleep -Seconds 3

# Step 2: Verify PostgreSQL is running
Write-Host "`nStep 2: Verifying PostgreSQL..." -ForegroundColor Yellow
docker ps | Select-String "society_db"

# Step 3: Generate Alembic migration
Write-Host "`nStep 3: Generating Alembic migration..." -ForegroundColor Yellow
Set-Location "A:\padhai_related\vit\projects\society_managment\backend"
& "A:\padhai_related\vit\projects\society_managment\.venv\Scripts\alembic.exe" revision --autogenerate -m "initial schema with 6 tables"

# Step 4: Apply migration
Write-Host "`nStep 4: Applying migration..." -ForegroundColor Yellow
& "A:\padhai_related\vit\projects\society_managment\.venv\Scripts\alembic.exe" upgrade head

# Step 5: Verify tables
Write-Host "`nStep 5: Verifying tables in PostgreSQL..." -ForegroundColor Yellow
docker exec society_db psql -U postgres -d society_db -c "\dt"

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Phase 2 Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`nAll 6 tables should be listed above:" -ForegroundColor White
Write-Host "  - users" -ForegroundColor White
Write-Host "  - categories" -ForegroundColor White
Write-Host "  - complaints" -ForegroundColor White
Write-Host "  - complaint_status_history" -ForegroundColor White
Write-Host "  - notices" -ForegroundColor White
Write-Host "  - notifications" -ForegroundColor White