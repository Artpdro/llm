#!/bin/bash

# Script para executar o HuB-IA com autenticação
# Versão para PowerShell no Windows

# Navegar para o diretório do projeto
Set-Location -Path "D:\vs\puf\hub-ia"

# Instalar dependências
Write-Host "Instalando dependências..." -ForegroundColor Green
pip install -r requirements.txt

# Verificar se o arquivo .env existe
if (-not (Test-Path ".env")) {
    Write-Host "Arquivo .env não encontrado. Criando um arquivo .env básico..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "Por favor, configure suas credenciais OAuth no arquivo .env antes de continuar." -ForegroundColor Red
    Write-Host "Pressione qualquer tecla para continuar após configurar o .env..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Iniciar o servidor OAuth em segundo plano
Write-Host "Iniciando servidor OAuth..." -ForegroundColor Green
Start-Process python -ArgumentList "oauth_routes.py" -RedirectStandardOutput "oauth_server.log" -RedirectStandardError "oauth_server_error.log" -NoNewWindow

# Dar um pequeno tempo para o servidor iniciar
Start-Sleep -Seconds 5

Write-Host "Servidor OAuth iniciado. Logs em: oauth_server.log" -ForegroundColor Green

# Iniciar a aplicação Streamlit
Write-Host "Iniciando aplicação Streamlit..." -ForegroundColor Green
Write-Host "Acesse: http://localhost:8501" -ForegroundColor Cyan
streamlit run app.py

# Ao sair do Streamlit, tentar matar o processo do servidor OAuth
Write-Host "Encerrando servidor OAuth..." -ForegroundColor Yellow
Get-Process -Name python | Where-Object { $_.Path -like "*oauth_routes.py*" } | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "Aplicação encerrada." -ForegroundColor Green

