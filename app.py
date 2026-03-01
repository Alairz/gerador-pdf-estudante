import streamlit as st
import io
import logging
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime
import pytz

# --- CONFIGURAÇÃO DO LOGGING ---
# Isso configura o log para aparecer de forma destacada no console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# --- CONFIGURAÇÃO INICIAL ---
SENHA_ACESSO = "examefinal"
ARQUIVO_QUESTOES = "questoes.pdf"
fuso_brasil = pytz.timezone('America/Sao_Paulo')
DATA_INICIO = datetime(2026, 2, 22, 13, 0, 0, tzinfo=fuso_brasil)
DATA_FIM = datetime(2026, 3, 5, 8, 0, 0, tzinfo=fuso_brasil)

def gerar_prova_estudante(matricula):
    try:
        agora_brasil = datetime.now(fuso_brasil)
        hora_str = agora_brasil.strftime('%H:%M:%S')
        data_str = agora_brasil.strftime('%d/%m/%Y')
        
        # REGISTRO DE LOG "BARULHENTO"
        # Aparecerá como: 16:45:10 - INFO - [PROVA_GERADA] Matricula: 12345
        logger.info(f"[PROVA_GERADA] Matricula: {matricula} em {data_str} as {hora_str}")
        
        leitor_questoes = PdfReader(ARQUIVO_QUESTOES)
        escritor_final = PdfWriter()
        
        for num_pagina in range(len(leitor_questoes.pages)):
            pagina_original = leitor_questoes.pages[num_pagina]
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=A4)
            can.setFont("Helvetica-Bold", 9)
            can.drawRightString(545, 810, f"ESTUDANTE: {matricula}")
            can.setFont("Helvetica", 7)
            can.drawRightString(545, 800, f"Gerado em: {data_str} {hora_str}")
            can.save()
            packet.seek(0)
            novo_pdf_cabecalho = PdfReader(packet)
            pagina_original.merge_page(novo_pdf_cabecalho.pages[0])
            escritor_final.add_page(pagina_original)

        output = io.BytesIO()
        escritor_final.write(output)
        output.seek(0)
        return output
    except Exception as e:
        logger.error(f"[ERRO_PDF] Matricula: {matricula} - Detalhe: {e}")
        return None

# --- INTERFACE ---
st.set_page_config(page_title="Portal de Provas", page_icon="📝")
st.title("📝 Gerador de Prova")

agora_atual = datetime.now(fuso_brasil)

if agora_atual > DATA_FIM:
    st.error("🚫 Prazo encerrado.")
else:
    senha = st.text_input("Senha da Turma:", type="password")
    if senha == SENHA_ACESSO:
        matricula = st.text_input("Digite sua Matrícula:")
        if st.button("Gerar meu PDF"):
            if matricula:
                # O comando toast mostra um balãozinho no canto da tela se você estiver logado
                st.toast(f"Gerando prova para {matricula}...")
                
                pdf = gerar_prova_estudante(matricula)
                if pdf:
                    st.success("Tudo pronto!")
                    st.download_button("⬇️ Baixar Arquivo", pdf, f"prova_{matricula}.pdf", "application/pdf")
            else:
                st.warning("Por favor, informe a matrícula.")

st.markdown("---")
st.caption(f"Prazo: {DATA_FIM.strftime('%d/%m/%Y %H:%M')}")
