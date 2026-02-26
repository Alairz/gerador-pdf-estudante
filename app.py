import streamlit as st
import io
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime
import pytz

# --- CONFIGURAÇÃO INICIAL ---
SENHA_ACESSO = "EXAME-FINAL"
ARQUIVO_QUESTOES = "questoes.pdf"

# --- DEFINIÇÃO DO PERÍODO DE USO (Horário de Brasília) ---
fuso_brasil = pytz.timezone('America/Sao_Paulo')
# Data Início: 27/02/2026 às 13:00
DATA_INICIO = datetime(2026, 2, 26, 13, 0, 0, tzinfo=fuso_brasil)
# Data Fim: 05/03/2026 às 08:00
DATA_FIM = datetime(2026, 3, 5, 9, 0, 0, tzinfo=fuso_brasil)

def gerar_prova_estudante(matricula):
    try:
        # 1. Ler o PDF original das questões
        leitor_questoes = PdfReader(ARQUIVO_QUESTOES)
        escritor_final = PdfWriter()
        agora_str = datetime.now(fuso_brasil).strftime("%d/%m/%Y %H:%M:%S")
        
        # 2. Processar cada página do arquivo original
        for num_pagina in range(len(leitor_questoes.pages)):
            pagina_original = leitor_questoes.pages[num_pagina]
            
            # Criar o cabeçalho (carimbo) em memória
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=A4)
            
            # --- FORMATAÇÃO: LADO DIREITO E FONTE TAMANHO 9 ---
            can.setFont("Helvetica-Bold", 9)
            can.drawRightString(545, 810, f"ESTUDANTE: {matricula}")
            
            can.setFont("Helvetica", 7)
            can.drawRightString(545, 800, f"Gerado em: {agora_str} | Página {num_pagina + 1}")
            # -------------------------------------------------
            
            can.save()
            packet.seek(0)
            novo_pdf_cabecalho = PdfReader(packet)
            
            # Mescla o cabeçalho personalizado na página original
            pagina_original.merge_page(novo_pdf_cabecalho.pages[0])
            escritor_final.add_page(pagina_original)

        # 3. Preparar o arquivo para o download
        output = io.BytesIO()
        escritor_final.write(output)
        output.seek(0)
        return output
    except Exception as e:
        st.error(f"Erro técnico: Verifique se o arquivo '{ARQUIVO_QUESTOES}' está no seu GitHub.")
        return None

# --- INTERFACE DO SITE (Streamlit) ---
st.set_page_config(page_title="Portal de Provas", page_icon="📝")
st.title("📝 Gerador de Prova Personalizada")

# Verificação do Horário Atual do Servidor (ajustado para o Brasil)
agora_atual = datetime.now(fuso_brasil)

# LÓGICA DE ACESSO POR PERÍODO
if agora_atual < DATA_INICIO:
    st.warning(f"⏳ O sistema ainda não está aberto. A geração de provas começará em {DATA_INICIO.strftime('%d/%m/%Y às %H:%M')}.")
    st.info(f"Horário atual: {agora_atual.strftime('%d/%m/%Y %H:%M')}")

elif agora_atual > DATA_FIM:
    st.error(f"🚫 O prazo para geração de provas encerrou em {DATA_FIM.strftime('%d/%m/%Y às %H:%M')}.")

else:
    # SE ESTIVER DENTRO DO PRAZO: Mostra campos de Senha e Matrícula
    senha = st.text_input("Senha da Turma:", type="password")
    
    if senha == SENHA_ACESSO:
        matricula = st.text_input("Digite sua Matrícula para começar:")
        
        if st.button("Gerar meu PDF"):
            if matricula:
                with st.spinner('Preparando sua prova personalizada...'):
                    pdf_final = gerar_prova_estudante(matricula)
                    if pdf_final:
                        st.success("Tudo pronto! Você já pode baixar sua prova.")
                        st.download_button(
                            label="⬇️ Baixar Prova com meu Nome/Matrícula",
                            data=pdf_final,
                            file_name=f"prova_{matricula}.pdf",
                            mime="application/pdf"
                        )
            else:
                st.warning("Por favor, informe a matrícula.")
    elif senha != "":
        st.error("Senha incorreta.")

# Rodapé com informações fixas do período
st.markdown("---")
st.caption(f"Período de disponibilidade: de {DATA_INICIO.strftime('%d/%m/%Y %H:%M')} até {DATA_FIM.strftime('%d/%m/%Y %H:%M')}")
