@echo off
rem Small model only. Stronger models are run separately with a cost estimate first.
cd /d "%~dp0"
python src\make_outlets.py || goto :end
python src\run_agents.py --models gpt-5.4-mini-2026-03-17 || goto :end
python src\analyze.py > nul
echo Results table saved to results\summary.md
:end
echo.
echo Finished. You can close this window.
pause
