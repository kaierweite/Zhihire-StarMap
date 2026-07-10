@echo off
start "Backend" cmd /k "cd backend && python run.py"
timeout /t 3
start "User Frontend" cmd /k "cd frontend && npm run dev"
start "Company Frontend" cmd /k "cd frontend && npx vite --port 5174"
start "Admin Frontend" cmd /k "cd frontend && npx vite --port 5175"