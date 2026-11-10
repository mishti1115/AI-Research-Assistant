@echo off
REM Edit the domain below once (get it free from dashboard.ngrok.com/domains)
set NGROK_DOMAIN=oversight-kilometer-goldsmith.ngrok-free.dev
ngrok http --domain=%NGROK_DOMAIN% 8000