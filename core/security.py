import logging
import time
from pathlib import Path

# Configuração do logger de segurança
SECURITY_LOG_FILE = Path(__file__).parent.parent / "logs" / "security.log"
SECURITY_LOG_FILE.parent.mkdir(exist_ok=True) # Garante que o diretório 'logs' exista

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(SECURITY_LOG_FILE),
        logging.StreamHandler()
    ]
)

def log_security_event(event_type: str, details: str, severity: str = "INFO"):
    """Registra um evento de segurança no log."""
    # Sanitizar detalhes para evitar log injection
    sanitized_details = str(details).replace("\n", " ")
    
    if severity == "INFO":
        logging.info(f"{event_type}: {sanitized_details}")
    elif severity == "WARNING":
        logging.warning(f"{event_type}: {sanitized_details}")
    elif severity == "ERROR":
        logging.error(f"{event_type}: {sanitized_details}")
    elif severity == "CRITICAL":
        logging.critical(f"{event_type}: {sanitized_details}")

def validate_redirect_url(url):
    """Valida URLs de redirecionamento para evitar open redirect."""
    # Lista de domínios permitidos para redirecionamento
    allowed_domains = ["localhost", "127.0.0.1"]
    
    # Verificar se a URL é relativa (começa com /)
    if url.startswith("/"):
        return True
    
    # Verificar se a URL pertence a um domínio permitido
    try:
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.split(":")[0]
        
        return domain in allowed_domains
    except:
        return False

# Registrar inicialização do módulo
log_security_event("SECURITY_MODULE_INIT", "Módulo de segurança inicializado")


