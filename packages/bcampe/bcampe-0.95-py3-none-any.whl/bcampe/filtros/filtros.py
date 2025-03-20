import streamlit as st
import pandas as pd
from bcampe.estilos import show_warning


def criar_multiselect(colunas, dataframe, rename_columns=None, custom_placeholders=None):
    """
    Cria múltiplos multiselects dinamicamente com base nas colunas e dataframe fornecidos.
    Se um dicionário de renomeação for fornecido, renomeia as colunas conforme especificado.
    Se um dicionário de placeholders personalizados for fornecido, substitui o texto padrão do placeholder.
    """
    filtros = {}
    
    for coluna in colunas:
        nome_coluna = rename_columns.get(coluna, coluna) if rename_columns else coluna
        
        placeholder = custom_placeholders.get(
            coluna, 
            f"Selecione {nome_coluna.replace('_', ' ')}"
        ) if custom_placeholders else f"Selecione {nome_coluna.replace('_', ' ')}"
        
        filtros[coluna] = st.multiselect(
            label=f"{nome_coluna.replace('_', ' ').title()}:",
            options=sorted(map(str, dataframe[coluna].unique().tolist())),
            placeholder=placeholder,
            key=coluna
        )
    
    return filtros
def inicializar_sessao(filtros, data_inicio=None, data_fim=None):
    """ 
    Inicializa session_state com as chaves dos filtros.
    Parâmetros de data são opcionais.
    """
    if data_inicio is not None:
        st.session_state.setdefault('data_inicial', data_inicio)
    if data_fim is not None:
        st.session_state.setdefault('data_final', data_fim)

    for filtro in filtros.keys():
        st.session_state.setdefault(f"filtro_{filtro}", [])
def resetar_filtros(filtros, data_inicio=None, data_fim=None):
    if data_inicio is not None:
        st.session_state['data_inicial'] = data_inicio
    if data_fim is not None:
        st.session_state['data_final'] = data_fim

    for filtro in filtros.keys():  # Limpa as chaves dos filtros
        st.session_state[filtro] = []

def converter_filtros(nomes_variaveis):
    """Converte lista de nomes de variáveis em dicionário de filtros"""
    return {nome: st.session_state.get(f"filtro_{nome}", []) for nome in nomes_variaveis}


def filtrar_dados(df, filtros, data_inicial=None, data_final=None, coluna_data=None):
    """
    Filtra DataFrame com base em filtros e opcionalmente por data.
    Parâmetros de data são opcionais.
    """
    df_filtrado = df.copy()

    # Filtro de datas (opcional)
    if all([coluna_data, data_inicial, data_final]):
        inicio = pd.to_datetime(data_inicial)
        fim = pd.to_datetime(data_final) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

        if coluna_data not in df_filtrado.columns:
            st.error(f"Coluna de data '{coluna_data}' não encontrada!")
            st.stop()

        df_filtrado = df_filtrado[
            (df_filtrado[coluna_data] >= inicio) & 
            (df_filtrado[coluna_data] <= fim)
        ]

    # Aplica filtros das colunas
    for coluna, valores in filtros.items():
        if coluna in df_filtrado.columns and valores:
            df_filtrado = df_filtrado[df_filtrado[coluna].astype(str).isin(valores)]

    if df_filtrado.empty:
        show_warning()
    st.session_state.df_filtrado = df_filtrado
    return df_filtrado
