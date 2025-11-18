@echo off
call D:\source\gts\venv\Scripts\activate.bat
set DJANGO_SETTINGS_MODULE=gts.settings
python D:\source\gts\gtsservice.py
