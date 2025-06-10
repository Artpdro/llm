Write-Host "Instalando dependências..." -ForegroundColor Green
pip install -r requirements.txt

Write-Host "Iniciando servidor OAuth..." -ForegroundColor Green
Start-Process python -ArgumentList "oauth_routes.py" -RedirectStandardOutput "oauth_server.log" -RedirectStandardError "oauth_server_error.log" -NoNewWindow

Start-Sleep -Seconds 5

Write-Host "Servidor OAuth iniciado. Logs em: oauth_server.log" -ForegroundColor Green

Write-Host "Iniciando aplicação Streamlit..." -ForegroundColor Green
Write-Host "Acesse: http://localhost:8501" -ForegroundColor Cyan
streamlit run app.py

Write-Host "Encerrando servidor OAuth..." -ForegroundColor Yellow
Get-Process -Name python | Where-Object { $_.Path -like "*oauth_routes.py*" } | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "Aplicação encerrada." -ForegroundColor Green

