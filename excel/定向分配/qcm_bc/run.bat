@echo
FOR  /L %%i IN (1, 1, 5) DO (
start cmd /k python company_search.py "%%i"
ping -n 10 127.0.01>null
)
