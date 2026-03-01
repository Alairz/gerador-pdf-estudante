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
DATA_INICIO = datetime(2026, 2, 22, 13, 0, 0, tzinfo=fuso_brasil)
DATA_FIM = datetime(2026, 3, 5, 8, 0, 0, tzinfo=fuso_brasil)

def gerar_prova_estudante(matricula):
    try:
        # REGISTRO DE LOG
        agora_brasil = datetime.now(fuso_brasil)
        hora_formatada = agora_brasil.strftime('%H:%M:%S')
        data_formatada = agora_brasil.strftime('%d/%m/%Y')
        print(f"--- [LOG] ACESSO: Matricula {matricula} gerou PDF em {data_formatada} às {hora_formatada} ---")
        
        leitor_questoes = PdfReader(ARQUIVO_QUESTOES)
        escritor_final = PdfWriter()
        
        for num_pagina in range(len(leitor_questoes.pages)):
            pagina_original = leitor_questoes.pages[num_pagina]
            
            packet = io.BytesIO()
            can = canvas.Canvas(packet, pagesize=A4)
            
            # Formatação do cabeçalho
            can.setFont("Helvetica-Bold", 9)
            can.drawRightString(545, 810, f"ESTUDANTE: {matricula}")
            
            can.setFont("Helvetica", 7)
            can.drawRightString(545, 800, f"Gerado em: {data_formatada} {hora_formatada} | Pagina {num_pagina + 1}")
            
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
        st.error(f"Erro tecnico: Verifique o arquivo no GitHub.")
        print(f"--- [ERRO] Falha: {e} ---")
        return None

# --- INTERFACE DO SITE ---
st.set_page_config(page_title="Portal de Provas", page_icon="📝")
st.title("📝 Gerador de Prova Personalizada")

agora_atual = datetime.now(fuso_brasil)

if agora_atual < DATA_INICIO:
    st.warning(f"⏳ O sistema ainda não está aberto. Início: {DATA_INICIO.strftime('%d/%m/%Y às %H:%M')}.")
elif agora_atual > DATA_FIM:
    st.error(f"🚫 O prazo para geração de provas encerrou em {DATA_FIM.strftime('%d/%m/%Y às %H:%M')}.")
else:
    senha = st.text_input("Senha da Turma:", type="password")
    
    if senha == SENHA_ACESSO:
        matricula = st.text_input("Digite sua Matrícula para começar:")
        
        if st.button("Gerar meu PDF"):
            if matricula:
                with st.spinner('Preparando seu PDF...'):
                    pdf_final = gerar_prova_estudante(matricula)
                    if pdf_final:
                        st.success("Tudo pronto!")
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

st.markdown("---")
st.caption(f"Disponibilidade: de {DATA_INICIO.strftime('%d/%m/%Y')} até {DATA_FIM.strftime('%d/%m/%Y %H:%M')}")
