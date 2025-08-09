@echo off
echo 🔍 Starting Meilisearch Server for Chatnary Backend...

REM Tạo thư mục data nếu chưa có
if not exist "meili_data" mkdir meili_data

REM Khởi động Meilisearch với cấu hình cho Chatnary
echo 📊 Host: http://localhost:7700
echo 🔑 Master Key: chatnary_master_key_2025
echo 📂 Data Path: ./meili_data
echo.

meilisearch.exe --master-key="chatnary_master_key_2025" --db-path="./meili_data" --http-addr="127.0.0.1:7700"

pause
