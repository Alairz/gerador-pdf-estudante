import streamlit as st
import io
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime
import pytz

# --- CONFIGURAÇÃO INICIAL ---
SENHA_ACESSO = "estudante2024"
ARQUIVO_QUESTOES = "questoes.pdf"

# --- DEFINIÇÃO DO PERÍODO DE USO (Horário de Brasília) ---
fuso_brasil = pytz.timezone('America/Sao_Paulo')
# Data Início: 22/02/2026 às 13:00
DATA_INICIO = datetime(2026, 2, 22, 13, 0, 0, tzinfo=fuso_brasil)
# Data Fim Atualizada: 05/03/2026 às 08:00
DATA_FIM = datetime(2026, 3, 5, 8, 0, 0, tzinfo=fuso_brasil)

def gerar_prova_estudante(matricula):
    try:
        # --- REGISTRO DE LOG (Aparece no painel Manage App > Logs) ---
        # Captura a hora exata do clique no fuso horário de Brasília
        agora_brasil = datetime.now(fuso_brasil)
        hora_formatada = agora_brasil.strftime('%H:%M:%S')
        data_formatada = agora_brasil.strftime('%d/%m/%Y')
        
        # Esta linha abaixo é o que você deve procurar nos logs:
        print(f"--- [LOG] ACESSO: Matrícula {matricula} gerou PDF em {data_formatada} às {hora_formatada} ---")
        
        # 1. Ler o PDF original das questões
        leitor_questoes = PdfReader(ARQUIVO_QUESTOES)
        escritor_final = PdfWriter()
        
        # 2. Processar cada página do arquivo original
        for num_pagina in range(len(leitor_questoes.pages)):
            pagina_original = leitor_questoes.pages[num_pagina]
            
            # Criar o cabeçalho personalizado
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=A4)
            
            # Formatação do cabeçalho (Direita, Fonte 9)
            can.setFont("Helvetica-Bold", 9)
            can.drawRightString
