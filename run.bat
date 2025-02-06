@echo off

REM Set Flask environment variables
set FLASK_APP=app.py
set FLASK_ENV=development

REM Run the Flask app
flask run

pause  REM Keeps the window open to view any errors