@echo off
chcp 65001
call conda activate subtitle-orc3.10
unicorn --bind 192.168.0.100:8999 main:app --log-level=info --workers=1 -c "accesslog='access.log',errorlog='error.log'"