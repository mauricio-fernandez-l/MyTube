@echo off
echo ============================
echo 1/3: Activate environment
echo ============================
call conda activate TODO

echo ============================
echo 2/3: Switch to the directory
echo ============================
cd /d C:\TODO

echo ============================
echo 3/3: Launch app
echo ============================
python app.py
