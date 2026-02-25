import streamlit as st
import io
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime

# --- CONFIGURAÇÃO ---
SENHA_ACESSO = "estudante"  # Altere sua senha aqui
ARQUIVO_QUESTOES = "questoes.pdf" # Nome do arquivo no seu GitHub

def gerar_prova_estudante(matricula):
    try:
        # 1. Ler o PDF original
        leitor_questoes = PdfReader(ARQUIVO_QUESTOES)
        escritor_final = PdfWriter()
        agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # 2. Processar cada página
        for num_pagina in range(len(leitor_questoes.pages)):
            pagina_original = leitor_questoes.pages[num_pagina]
            
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=A4)
            
            # --- AJUSTE DE POSIÇÃO E FONTE TAMANHO 9 ---
            # Fonte da Matrícula: Tamanho 9
            can.setFont("Helvetica-Bold", 9)
            can.drawRightString(545, 810, f"ESTUDANTE: {matricula}")
            
            # Fonte da Data/Hora: Tamanho 7 (menor para não poluir)
            can.setFont("Helvetica", 7)
            can.drawRightString(545, 800, f"Gerado em: {agora} | Página {num_pagina + 1}")
            # -------------------------------------------
            
            can.save()
            packet.seek(0)
            novo_pdf_cabecalho = PdfReader(packet)
            
            # Mescla o cabeçalho na página original
            pagina_original.merge_page(novo_pdf_cabecalho.pages[0])
            escritor_final.add_page(pagina_original)

        # 3. Preparar download
        output = io.BytesIO()
        escritor_final.write(output)
        output.seek(0)
        return output
    except Exception as e:
        st.error(f"Erro: Verifique se o arquivo '{ARQUIVO_QUESTOES}' está no GitHub.")
        return None

# --- INTERFACE WEB ---
st.set_page_config(page_title="Portal de Provas", page_icon="📝")
st.title("📝 Gerador de Prova Personalizada")

senha = st.text_input("Senha da Turma:", type="password")

if senha == SENHA_ACESSO:
    matricula = st.text_input("Digite sua Matrícula:")
    
    if st.button("Gerar meu PDF"):
        if matricula:
            with st.spinner('Processando seu arquivo...'):
                pdf_final = gerar_prova_estudante(matricula)
                if pdf_final:
                    st.success("PDF gerado com sucesso!")
                    st.download_button(
                        label="⬇️ Baixar Prova Personalizada",
                        data=pdf_final,
                        file_name=f"prova_{matricula}.pdf",
                        mime="application/pdf"
                    )
        else:
            st.warning("Por favor, informe a matrícula.")
elif senha != "":
    st.error("Senha incorreta.")
