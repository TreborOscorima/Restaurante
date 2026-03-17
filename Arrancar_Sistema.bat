@echo off
:: ============================================================
:: Arrancar_Sistema.bat  —  Lanzador de producción
:: TuWaykiApp / Norkys LAN POS
::
:: Instrucciones para el dueño:
::   Doble clic en este archivo para iniciar el sistema.
::   La primera vez puede tardar 1-2 minutos mientras
::   instala dependencias. Las siguientes veces es inmediato.
:: ============================================================

title TuWaykiApp - Sistema POS Restaurante
color 0A

setlocal EnableDelayedExpansion

:: -- Situarse siempre en la carpeta del proyecto ----------------
cd /d "%~dp0"

echo.
echo  ============================================
echo   TuWaykiApp / Norkys LAN POS
echo   Iniciando sistema...
echo  ============================================
echo.

:: -- 1. Verificar que el entorno virtual existe -----------------
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] No se encontro el entorno virtual.
    echo         Ejecuta primero: python -m venv venv
    pause
    exit /b 1
)

:: -- 2. Activar el entorno virtual ------------------------------
call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] No se pudo activar el entorno virtual.
    pause
    exit /b 1
)

:: -- 3. Instalar / verificar dependencias -----------------------
echo [1/3] Verificando dependencias...
pip install -q -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [ADVERTENCIA] Algunas dependencias no se pudieron instalar.
    echo               El sistema intentará arrancar de todas formas.
)

:: -- 4. Backup automático antes de iniciar ----------------------
echo [2/3] Creando respaldo de seguridad...
python scripts\backup_db.py --keep 14 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ADVERTENCIA] No se pudo crear el respaldo ^(DB aun no existe o primer inicio^).
)

:: -- 5. Iniciar Reflex en modo producción -----------------------
echo [3/3] Arrancando servidor...
echo.
echo  Cuando vea "App running at http://0.0.0.0:3000" el sistema esta listo.
echo  Abra el navegador en: http://localhost:3000
echo  Para detener el sistema presione Ctrl+C en esta ventana.
echo.

reflex run --env prod

:: -- Si Reflex termina inesperadamente --------------------------
echo.
echo [AVISO] El servidor se detuvo. Cierre esta ventana o presione una tecla para salir.
pause
endlocal
