import streamlit as st
import io
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime
import pytz

# --- CONFIGURAÇÃO INICIAL ---
SENHA_ACESSO = "examefinal"
ARQUIVO_QUESTOES = "questoes.pdf"

# --- DEFINIÇÃO DO PERÍODO DE USO (Horário de Brasília) ---
fuso_brasil = pytz.timezone('America/Sao_Paulo')
DATA_INICIO = datetime(2026, 2, 22, 13, 0, 0, tzinfo=fuso_brasil)
DATA_FIM = datetime(2026, 3, 5, 8, 0, 0, tzinfo=fuso_brasil) # Atualizado para 05/03 às 08:00

def gerar_prova_estudante(matricula):
    try:
        # LOG DE CONTROLE: Isso aparecerá no "Manage App" > "Logs" do Streamlit
        print(f"--- [LOG] PROVA GERADA POR: {matricula} às {datetime.now(fuso_brasil).strftime('%H:%M:%S')} ---")
        
        leitor_questoes = PdfReader(ARQUIVO_QUESTOES)
        escritor_final = PdfWriter()
        agora_str = datetime.now(fuso_brasil).strftime("%d/%m/%Y %H:%M:%S")
        
        for num_pagina in range(len(leitor_questoes.pages)):
            pagina_original = leitor_questoes.pages[num_pagina]
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=A4)
            
            can.setFont("Helvetica-Bold", 9)
            can.drawRightString(545, 810, f"ESTUDANTE: {matricula}")
            can.setFont("Helvetica", 7)
            can.drawRightString(545, 800, f"Gerado em: {agora_str} | Página {num_pagina + 1}")
            
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
        st.error(f"Erro técnico: Verifique o arquivo no GitHub.")
        return None

# --- INTERFACE DO SITE ---
st.set_page_config(page_title="Portal de Provas", page_icon="📝")
st.title("📝 Gerador de Prova Personalizada")

agora_atual = datetime.now(fuso_brasil)

if agora_atual < DATA_INICIO:
    st.warning(f"⏳ O sistema ainda não está aberto. Início: {DATA_INICIO.strftime('%d/%m/%Y às %H:%M')}.")
elif agora_atual > DATA_FIM:
    st.error(f"🚫 O prazo encerrou em {DATA_FIM.strftime('%d/%m/%Y às %H:%M')}.")
else:
    senha = st.text_input("Senha da Turma:", type="password")
    if senha == SENHA_ACESSO:
        matricula = st.text_input("Digite sua Matrícula:")
        if st.button("Gerar meu PDF"):
            if matricula:
                with st.spinner('Preparando...'):
                    pdf_final = gerar_prova_estudante(matricula)
                    if pdf_final:
                        st.success("PDF pronto!")
                        st.download_button(
                            label="⬇️ Baixar Prova",
                            data=pdf_final,
                            file_name=f"prova_{matricula}.pdf",
                            mime="application/pdf"
                        )
            else:
                st.warning("Informe a matrícula.")
    elif senha != "":
        st.error("Senha incorreta.")

st.markdown("---")
st.caption(f"Disponível até: {DATA_FIM.strftime('%d/%m/%Y %H:%M')}")
