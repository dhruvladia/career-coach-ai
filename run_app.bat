@echo off
echo Starting LearnTube AI Career Coach...
echo.

:: Start backend in a new window
echo Starting backend server...
start "LearnTube Backend" cmd /k "cd backend && python run.py"

:: Wait a few seconds for backend to start
timeout /t 5 /nobreak > nul

:: Start frontend in a new window
echo Starting Streamlit frontend...
start "LearnTube Frontend" cmd /k "cd frontend && streamlit run streamlit_app.py"

echo.
echo Both services are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:8501
echo.
echo Press any key to stop both services...
pause > nul 