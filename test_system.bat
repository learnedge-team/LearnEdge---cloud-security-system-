@echo off
echo ========================================
echo Testing Security System
echo ========================================
echo.
echo Testing health endpoint...
curl http://localhost:5000/api/health
echo.
echo.
echo Getting alerts...
curl http://localhost:5000/api/alerts
echo.
echo.
echo To simulate an attack, run: python test_attack.py
echo.
pause