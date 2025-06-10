import os
import json
from pathlib import Path
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse, JSONResponse
from starlette.routing import Route
from authlib.integrations.starlette_client import OAuth
from dotenv import load_dotenv
from urllib.parse import urlencode

# Carregar variáveis de ambiente
load_dotenv()

# Configurar OAuth
oauth = OAuth()

# Configurar Google OAuth
oauth.register(
    name="google",
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


async def auth_google(request):
    """Inicia o fluxo de autenticação com Google."""
    redirect_uri = "http://localhost:8000/callback/google"
    return await oauth.google.authorize_redirect(request, redirect_uri)

async def callback_google(request):
    """Processa o callback do Google OAuth."""
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get("userinfo")
        
        if user_info:
            # Redirecionar para o Streamlit com informações do usuário
            params = {
                "provider": "google",
                "user_id": user_info["sub"],
                "email": user_info["email"],
                "name": user_info["name"]
            }
            streamlit_url = f"http://localhost:8501/oauth_callback?{urlencode(params)}"
            return RedirectResponse(url=streamlit_url)
        else:
            return JSONResponse({"error": "Falha ao obter informações do usuário"}, status_code=400)
    
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


# Definir rotas
routes = [
    Route("/auth/google", auth_google),
    Route("/callback/google", callback_google),
]

# Configurar middleware
middleware = [
    Middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "chave_padrao_apenas_para_desenvolvimento"))
]

# Criar aplicação
app = Starlette(routes=routes, middleware=middleware)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


