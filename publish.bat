@echo off
setlocal
:: Переход в папку libraries, где лежит setup.py
cd /d "%~dp0"

echo === Очистка старых сборок ===
rmdir /s /q dist build pycraft_tools.egg-info 2>nul

echo === Проверка и установка инструментов публикации ===
python -m pip install --upgrade build twine >nul 2>&1

echo === Сборка ===
python -m build
if %errorlevel% neq 0 (
    echo === ОШИБКА СБОРКИ! Проверьте код и зависимости. ===
    pause
    exit /b %errorlevel%
)

echo === Проверка метаданных ===
twine check dist/*
if %errorlevel% neq 0 (
    echo === ОШИБКА ПРОВЕРКИ! Исправьте описание пакета. ===
    pause
    exit /b %errorlevel%
)

echo === Загрузка на PyPI ===
twine upload dist/*
if %errorlevel% neq 0 (
    echo === ОШИБКА ЗАГРУЗКИ! Проверьте учетные данные PyPI. ===
    pause
    exit /b %errorlevel%
)

echo === Готово! Пакет pycraft-tools опубликован. ===
pause
