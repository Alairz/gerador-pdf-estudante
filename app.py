import streamlit as st
import io
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime

# --- CONFIGURAÇÃO ---
SENHA_ACESSO = "estudante2024"  # Altere sua senha aqui
ARQUIVO_QUESTOES = "questoes.pdf" # O nome do seu PDF no GitHub

def gerar_prova_estudante(matricula):
    try:
        # 1. Tenta ler o PDF original que você subiu no GitHub
        leitor_questoes = PdfReader(ARQUIVO_QUESTOES)
        escritor_final = PdfWriter()
        agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        # 2. Processa cada página do PDF original
        for num_pagina in range(len(leitor_questoes.pages)):
            pagina_original = leitor_questoes.pages[num_pagina]
            
            # Criar o "carimbo" com a matrícula em memória
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=A4)
            
            # Personalize a posição aqui (x=50, y=810 é no topo esquerdo)
            can.setFont("Helvetica-Bold", 11)
            can.drawString(50, 810, f"ESTUDANTE: {matricula}")
            can.setFont("Helvetica", 8)
            can.drawString(50, 800, f"Gerado em: {agora} | Página {num_pagina + 1}")
            can.save()
            
            packet.seek(0)
            novo_pdf_cabecalho = PdfReader(packet)
            
            # Mescla o carimbo na página original
            pagina_original.merge_page(novo_pdf_cabecalho.pages[0])
            escritor_final.add_page(pagina_original)

        # 3. Prepara o arquivo final para download
        output = io.BytesIO()
        escritor_final.write(output)
        output.seek(0)
        return output
    except Exception as e:
        st.error(f"Erro ao ler o arquivo {ARQUIVO_QUESTOES}. Verifique se ele foi enviado ao GitHub.")
        return None

# --- INTERFACE WEB (Streamlit) ---
st.set_page_config(page_title="Portal de Provas", page_icon="📝")
st.title("📝 Gerador de Prova Personalizada")

senha = st.text_input("Senha da Turma:", type="password")

if senha == SENHA_ACESSO:
    matricula = st.text_input("Digite sua Matrícula para começar:")
    
    if st.button("Gerar meu PDF"):
        if matricula:
            with st.spinner('Preparando sua prova...'):
                pdf_final = gerar_prova_estudante(matricula)
                if pdf_final:
                    st.success("Tudo pronto!")
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
