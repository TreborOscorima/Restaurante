@echo off
:: ============================================================
:: Backup_DB.bat  —  Respaldo automático del POS Restaurante
:: Agrega esta tarea en el Programador de Tareas de Windows
:: para ejecutarla cada 2-4 horas durante el servicio.
:: ============================================================

setlocal
cd /d "%~dp0.."

echo [%DATE% %TIME%] Iniciando backup...

call venv\Scripts\python.exe scripts\backup_db.py --keep 14

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] El backup falló con código %ERRORLEVEL%.
    exit /b %ERRORLEVEL%
)

echo [%DATE% %TIME%] Backup completado.
endlocal
