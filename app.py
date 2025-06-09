import streamlit as st
import time
import logging
import re
import pandas as pd
from rapidfuzz import process
from core.engine import auto_generate_and_run_query

try:
    from ollama._client import ResponseError
except ImportError:
    ResponseError = Exception

# --- LOG DE ERROS ---
logging.basicConfig(filename="hubia_erros.log", level=logging.ERROR)

# --- CONFIGURAÇÃO DE PÁGINA ---
st.set_page_config(
    page_title="HuB-IA - Assistente Inteligente para Dados Públicos da Fecomércio",
    layout="wide"
)


# --- ESTILOS ---
st.markdown("""
    <style>
        body { background-color: #0E1117; color: white; }
        .stTextInput > div > input { font-size: 20px !important; }
        .main-title { font-size: 40px !important; text-align: center; font-weight: bold; margin-top: 1em; }
        .sub-title { font-size: 24px !important; text-align: center; margin-top: 0.5em; }
        .placeholder-text { font-style: italic; color: #ccc; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# --- ESTADO DA SESSÃO ---
st.session_state.setdefault("historico", [])
st.session_state.setdefault("resposta_atual", None)
st.session_state.setdefault("mostrar_sobre", False)
if "resposta_atual" not in st.session_state:
    st.session_state.resposta_atual = None

if "mostrar_sobre" not in st.session_state:
    st.session_state.mostrar_sobre = False

# --- FUNÇÕES ---
def corrigir_sql(sql: str) -> str:
    sql = re.sub(r"\'\s*-\s*(group|order|having|limit)\b", r"'\n\1", sql, flags=re.IGNORECASE)
    sql = re.sub(r"([^\s])-(group|order|having|limit)\b", r"\1 \2", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\s+;", ";", sql)
    return sql

def consultar(pergunta):
    resultado = auto_generate_and_run_query(pergunta.strip())
    sql_corrigido = corrigir_sql(resultado["sql"])
    return resultado["interpretacao"], sql_corrigido, resultado.get("resultado", [])

def is_read_only_query(sql):
    return sql.strip().lower().startswith("select")

def typing_effect(text, speed=0.01):
    placeholder = st.empty()
    typed = ""
    for char in text:
        typed += char
        placeholder.markdown(typed)
        time.sleep(speed)

def sugerir_perguntas(pergunta):
    if "ipca" in pergunta.lower():
        return [
            "Qual a média do IPCA em 2023?",
            "Compare o IPCA entre Recife e Salvador.",
            "IPCA variou quanto em janeiro de 2022?"
        ]
    elif "pms" in pergunta:
        return [
            "Qual foi a variação da PMS em São Paulo?",
            "PMS de 2020 a 2023 no Brasil."
        ]
    return []

# --- SIDEBAR ---
with st.sidebar:
    st.title("Welcome to HuB-IA")
    if st.button("ℹ️ Sobre o HuB-IA"):
        st.session_state.mostrar_sobre = not st.session_state.mostrar_sobre

    st.markdown("---")
    st.subheader("🕘 Histórico")
    for i, item in enumerate(reversed(st.session_state.historico)):
        if st.button(item['pergunta'], key=f"hist_{i}"):
            st.session_state.resposta_atual = item
    if st.button("🧹 Limpar histórico"):
        st.session_state.historico.clear()
        st.session_state.resposta_atual = None

# --- ÁREA PRINCIPAL ---
st.markdown('<div class="main-title">HuB‑IA – Assistente Inteligente para Dados Públicos da Fecomércio</div>', unsafe_allow_html=True)

if st.session_state.mostrar_sobre:
    st.markdown("## Sobre o HuB-IA")
    st.markdown("""
    O **HuB-IA** é um assistente inteligente que traduz perguntas em linguagem natural em consultas SQL sobre dados econômicos públicos.

    Ele utiliza o **LangChain** e **SQLite**, com dados como:

    - 📈 Índice de Preços ao Consumidor Amplo (IPCA)  
    - 🛒 Pesquisa Mensal do Comércio (PMC)  
    - 🏭 Pesquisa Mensal de Serviços (PMS)  
    - 💳 Transações com cartões  

    Desenvolvido pela **Fecomércio** para democratizar o acesso e a interpretação dos dados econômicos.
    """)
    st.stop()

st.markdown('<div class="sub-title">O que você quer saber?</div>', unsafe_allow_html=True)

# --- FORMULÁRIO COM ENTER ---
with st.form("pergunta_form", clear_on_submit=True):
    pergunta = st.text_input("", placeholder="Qual a inflação acumulada em Recife?", label_visibility="collapsed")
    submit = st.form_submit_button("enviar")

if submit and pergunta.strip():
    try:
        resposta, sql, dados = consultar(pergunta)
        
        if not is_read_only_query(sql):
            st.error("⚠️ Apenas comandos de leitura (SELECT) são permitidos.")
        else:
            registro = {"pergunta": pergunta, "resposta": resposta, "dados": dados}
            st.session_state.historico.append(registro)
            registro = {
                "pergunta": pergunta,
                "resposta": resposta,
            }
            st.session_state.resposta_atual = registro

    except ResponseError:
        logging.exception(f"Erro LLM - pergunta: {pergunta}")
        st.error("❌ Erro ao processar a pergunta. Tente novamente mais tarde.")
    except Exception:
        logging.exception(f"Erro inesperado - pergunta: {pergunta}")
        st.error("❌ Ocorreu um erro ao interpretar sua pergunta. Tente reformular.")

# --- EXIBIÇÃO DA RESPOSTA ---
if st.session_state.resposta_atual:
    typing_effect(st.session_state.resposta_atual["resposta"])

    dados = st.session_state.resposta_atual.get("dados")
    if dados and isinstance(dados, list):
        try:
            df = pd.DataFrame(dados)
            if not df.empty:
                st.markdown("### Resultado:")
                st.dataframe(df)
            else:
                st.warning("⚠️ Nenhum dado encontrado para essa consulta.")
        except Exception as e:
            st.error("❌ Erro ao exibir os dados.")
            st.exception(e)
    else:
        st.warning("⚠️ Nenhum dado encontrado para essa consulta.")

    st.markdown("<p class='placeholder-text'>Você pode perguntar por ano, por localidade ou comparar períodos distintos.</p>", unsafe_allow_html=True)

    sugestoes = sugerir_perguntas(st.session_state.resposta_atual["pergunta"])
    if sugestoes:
        st.markdown("### 💡 Sugestões:")
        for s in sugestoes:
            st.markdown(f"- {s}")