@echo off
echo 🔍 Chatnary - Meilisearch Server
echo ================================
echo.

REM Kiểm tra xem meilisearch.exe có tồn tại không
if exist "meilisearch.exe" (
    echo ✅ Found meilisearch.exe in current directory
    goto :start_meilisearch
)

REM Kiểm tra trong PATH
where meilisearch >nul 2>&1
if %errorlevel% == 0 (
    echo ✅ Found meilisearch in PATH
    goto :start_meilisearch
)

echo ❌ Meilisearch not found!
echo.
echo 📥 Please download Meilisearch:
echo    1. Go to: https://github.com/meilisearch/meilisearch/releases
echo    2. Download meilisearch-windows-amd64.exe
echo    3. Rename it to meilisearch.exe
echo    4. Place it in this folder: %~dp0
echo.
echo 🔧 Or install via package manager:
echo    scoop install meilisearch
echo    # or
echo    winget install MeiliSearch.MeiliSearch
echo.
pause
exit /b 1

:start_meilisearch
REM Tạo thư mục data nếu chưa có
if not exist "meili_data" mkdir meili_data

echo 🚀 Starting Meilisearch with master key...
echo    Host: http://localhost:7700
echo    Master Key: chatnary_master_key_2025
echo    Data Path: ./meili_data
echo.
echo 🛑 Press Ctrl+C to stop
echo ================================
echo.

REM Khởi động Meilisearch với cấu hình
if exist "meilisearch.exe" (
    meilisearch.exe --master-key=chatnary_master_key_2025 --db-path=./meili_data --http-addr=0.0.0.0:7700
) else (
    meilisearch --master-key=chatnary_master_key_2025 --db-path=./meili_data --http-addr=0.0.0.0:7700
)

echo.
echo 📝 Meilisearch stopped
pause
echo.

meilisearch.exe --master-key="chatnary_master_key_2025" --db-path="./meili_data" --http-addr="127.0.0.1:7700"

pause
