@echo off

rem upgrade database
:upgrade
alembic revision --autogenerate -m %1
goto :eof

rem downgrade database
:downgrade
alembic downgrade -1
goto :eof

rem run service
:service
python main.py
goto :eof

rem run test
:test
python test.py
goto :eof

rem commit
:commit
git add .
git commit
goto :eof

rem format code
:fmt
python -m black .
goto :eof

rem
%1


:eof





