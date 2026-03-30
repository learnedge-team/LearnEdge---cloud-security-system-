@echo off
echo ========================================
echo Starting Cloud Security System
echo ========================================
cd backend
call venv\Scripts\activate
python app.py
pause