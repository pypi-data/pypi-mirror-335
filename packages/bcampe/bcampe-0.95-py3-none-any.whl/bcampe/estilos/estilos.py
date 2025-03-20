import streamlit as st
import os

def aplicar_css():
    # Obtém o diretório atual do script
    diretorio_atual = os.path.dirname(__file__)
    # Constrói o caminho para o arquivo CSS
    caminho_css = os.path.join(diretorio_atual, 'styles.css')
    
    # Abre o arquivo CSS e aplica o estilo
    with open(caminho_css, 'r', encoding='utf-8') as f:
        css = f.read()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

aplicar_css()

#funçao de identidade visual
def generate_colors(num_categorias, color_palette): #paletas de cores pra graficos
        colors = color_palette * (num_categorias // len(color_palette)) + color_palette[:num_categorias % len(color_palette)]
        return colors
corazul = ['#052E59']
corverde =['#355e2a']
colors_base = ['#052E59','#517496', '#7A89B2', '#A0ADCC', '#C4D1E2', '#DAE4ED', '#EAF0F6']
#funçao de titulo
def titulo(title):
    st.markdown(f"""
        <div class="header-bar">
            <span class="header-title">{title}</span>
        </div>
        """, unsafe_allow_html=True)
    
#box de erro se o filtro quebrar
def show_warning():
    st.markdown(
        """
        <div class="warning-container">
            Nenhum dado disponível para o filtro selecionado. <br>
            Apague os filtros para o Painel voltar ao estado inicial.
        </div>
        """,
        unsafe_allow_html=True
    )
    st.stop()
#box de erro se qualquer erro ocorrer
def erro():
    st.markdown(
        """
        <div class="erro">
            Algo deu errado. Tente novamente! <br>
            Em caso de persistência, entre em contato com o time de dados através dos canais <a href="http://10.11.82.21:3500/" target="_blank" style="color: white;">Help Desk (GLPI)</a> ou 
            helpdesk@cge.rj.gov.br <br>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.stop()