import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime
import io

# --- CONFIGURAÇÃO ---
SENHA_ACESSO = "estudante2024"  # Mude para a senha que desejar

def criar_pdf(matricula):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    largura, altura = A4
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    for i in range(1, 13): # Gera as 12 páginas
        # Cabeçalho
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, altura - 50, f"MATRÍCULA: {matricula}")
        c.setFont("Helvetica", 10)
        c.drawString(50, altura - 65, f"Documento gerado em: {agora}")
        c.line(50, altura - 70, largura - 50, altura - 70)
        
        # Rodapé
        c.drawCentredString(largura / 2, 30, f"Página {i} de 12")
        c.showPage()
    
    c.save()
    buffer.seek(0)
    return buffer

# --- INTERFACE WEB ---
st.set_page_config(page_title="Gerador de PDF Oficial")
st.title("📄 Portal de Impressão do Estudante")

senha = st.text_input("Digite a senha da turma:", type="password")

if senha == SENHA_ACESSO:
    matricula = st.text_input("Digite seu número de matrícula:")
    
    if st.button("Gerar Documento de 12 Páginas"):
        if matricula:
            with st.spinner('Gerando seu arquivo...'):
                pdf_file = criar_pdf(matricula)
                st.success("PDF gerado com sucesso!")
                st.download_button(
                    label="⬇️ Baixar PDF para Imprimir",
                    data=pdf_file,
                    file_name=f"documento_{matricula}.pdf",
                    mime="application/pdf"
                )
        else:
            st.warning("Por favor, preencha a matrícula.")
elif senha != "":
    st.error("Senha incorreta.")
