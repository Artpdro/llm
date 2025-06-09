import streamlit as st
import sys
import os
from pathlib import Path
import json
import requests
from urllib.parse import urlencode

# Adicionar o diretório raiz ao path para importar os módulos corretamente
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from core.auth import (
    init_session,
    login_user,
    register_user,
    get_user_by_email,
    get_user_by_oauth
)

from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações da página
st.set_page_config(
    page_title="HuB-IA - OAuth Callback",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Inicializar sessão
init_session()

def handle_google_callback():
    """Processa o callback do OAuth do Google."""
    # Em uma implementação real, este código seria executado após o redirecionamento do Google
    # Aqui estamos simulando o processo para fins de demonstração
    
    # Obter o código de autorização da URL (simulado)
    code = st.experimental_get_query_params().get("code", [""])[0]
    
    if not code:
        st.error("Erro na autenticação com Google. Código de autorização não encontrado.")
        return False
    
    # Trocar o código por um token de acesso (simulado)
    # Em uma implementação real, faríamos uma requisição POST para o endpoint do Google
    token_data = {
        "access_token": "google_simulated_token",
        "token_type": "Bearer",
        "expires_in": 3600
    }
    
    # Obter informações do usuário (simulado)
    # Em uma implementação real, faríamos uma requisição GET para o endpoint do Google
    user_info = {
        "id": "123456789",
        "email": "usuario@gmail.com",
        "name": "Usuário Google",
        "picture": "https://example.com/profile.jpg"
    }
    
    # Verificar se o usuário já existe
    user = get_user_by_oauth("google", user_info["id"])
    
    if not user:
        # Verificar se existe um usuário com o mesmo e-mail
        user = get_user_by_email(user_info["email"])
        
        if user:
            # Atualizar o usuário existente com as informações do Google
            register_user(
                user_info["email"],
                None,
                user_info["name"],
                "google",
                user_info["id"]
            )
        else:
            # Registrar um novo usuário
            register_user(
                user_info["email"],
                None,
                user_info["name"],
                "google",
                user_info["id"]
            )
        
        # Buscar o usuário novamente
        user = get_user_by_oauth("google", user_info["id"])
    
    if user:
        login_user(user)
        return True
    
    return False

def handle_github_callback():
    """Processa o callback do OAuth do GitHub."""
    # Em uma implementação real, este código seria executado após o redirecionamento do GitHub
    # Aqui estamos simulando o processo para fins de demonstração
    
    # Obter o código de autorização da URL (simulado)
    code = st.experimental_get_query_params().get("code", [""])[0]
    
    if not code:
        st.error("Erro na autenticação com GitHub. Código de autorização não encontrado.")
        return False
    
    # Trocar o código por um token de acesso (simulado)
    # Em uma implementação real, faríamos uma requisição POST para o endpoint do GitHub
    token_data = {
        "access_token": "github_simulated_token",
        "token_type": "Bearer",
        "scope": "user:email"
    }
    
    # Obter informações do usuário (simulado)
    # Em uma implementação real, faríamos uma requisição GET para o endpoint do GitHub
    user_info = {
        "id": "987654321",
        "login": "github_user",
        "name": "Usuário GitHub",
        "email": "usuario@github.com",
        "avatar_url": "https://example.com/github_profile.jpg"
    }
    
    # Verificar se o usuário já existe
    user = get_user_by_oauth("github", user_info["id"])
    
    if not user:
        # Verificar se existe um usuário com o mesmo e-mail
        user = get_user_by_email(user_info["email"])
        
        if user:
            # Atualizar o usuário existente com as informações do GitHub
            register_user(
                user_info["email"],
                None,
                user_info["name"],
                "github",
                user_info["id"]
            )
        else:
            # Registrar um novo usuário
            register_user(
                user_info["email"],
                None,
                user_info["name"],
                "github",
                user_info["id"]
            )
        
        # Buscar o usuário novamente
        user = get_user_by_oauth("github", user_info["id"])
    
    if user:
        login_user(user)
        return True
    
    return False

def main():
    st.title("🤖 HuB-IA")
    st.subheader("Autenticação OAuth")
    
    # Obter o provedor da URL
    provider = st.experimental_get_query_params().get("provider", [""])[0]
    
    if not provider:
        st.error("Provedor OAuth não especificado.")
        st.button("Voltar para o Login", on_click=lambda: st.switch_page("login"))
        return
    
    with st.spinner(f"Processando autenticação com {provider.capitalize()}..."):
        success = False
        
        if provider == "google":
            success = handle_google_callback()
        elif provider == "github":
            success = handle_github_callback()
        else:
            st.error(f"Provedor OAuth não suportado: {provider}")
    
    if success:
        st.success("Autenticação realizada com sucesso!")
        st.switch_page("app.py") # Redireciona para o script principal
    else:
        st.error("Falha na autenticação. Tente novamente.")
        st.button("Voltar para o Login", on_click=lambda: st.switch_page("login"))

if __name__ == "__main__":
    main()

