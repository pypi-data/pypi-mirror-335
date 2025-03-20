import locale
import re
import io
import pandas as pd
import streamlit as st  
def converte_br(numero):
    """
    Converte valores numéricos grandes para formato abreviado (ex: 1M, 2B).
    """
    suf = {
        1e3:"K",
        1e6: "M",    # milhão
        1e9: "B",    # bilhão
        1e12: "T"    # trilhão
    }
    negativo = numero < 0
    numero = abs(numero)
    for s in reversed(sorted(suf.keys())):
        if numero >= s:
            if numero % s == 0:
                valor_formatado = locale.format_string("%.0f", numero / s, grouping=True)
            else:
                valor_formatado = locale.format_string("%.2f", numero / s, grouping=True)
            return f"{'-' if negativo else ''}{valor_formatado}{suf[s]}"
    return locale.currency(numero, grouping=True, symbol=None)

def remove_illegal_characters(value):
        if isinstance(value, str):
            # Remove apenas caracteres ilegíveis, mantendo acentos e caracteres especiais
            return re.sub(r'[^\x09\x0A\x0D\x20-\x7E\u00A0-\uFFFF]', '', value)
        return value

def download_dataframe(df, file_name, file_format="xlsx"):
    """
    Limpa caracteres ilegíveis do DataFrame, exporta para Excel (XLSX) ou CSV e cria um botão de download no Streamlit.

    Parâmetros:
        df (pd.DataFrame): O DataFrame a ser exportado.
        file_name (str): Nome do arquivo para download.
        file_format (str): Formato do arquivo ('xlsx' ou 'csv').
    """
    # Aplicar a limpeza no DataFrame
    df = df.map(remove_illegal_characters)

    buffer = io.BytesIO()

    if file_format == "xlsx":
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif file_format == "csv":
        buffer.write(df.to_csv(index=False, encoding='utf-8').encode())
        mime_type = "text/csv"
    else:
        st.error("Formato inválido. Escolha 'xlsx' ou 'csv'.")
        return

    buffer.seek(0)

    st.download_button(
        label=f"Baixar Tabela",
        data=buffer,
        file_name=f"{file_name}.{file_format}",
        mime=mime_type
    )

def configurar_colunas(coluna_texto, coluna_numerica, coluna_data):
    """
    Configura colunas para o Streamlit com base nos tipos fornecidos.
    
    Parâmetros:
        coluna_texto (dict): Dicionário de colunas de texto {nome_coluna: label}.
        coluna_numerica (dict): Dicionário de colunas numéricas {nome_coluna: label}.
        coluna_data (dict): Dicionário de colunas de data {nome_coluna: label}.
    
    Retorna:
        dict: Configuração de colunas para o Streamlit.
    """
    column_config = {}
    
    # Configuração das colunas de texto
    for col, label in coluna_texto.items():
        column_config[col] = st.column_config.TextColumn(label=label)
    
    # Configuração das colunas numéricas
    for col, label in coluna_numerica.items():
        column_config[col] = st.column_config.NumberColumn(label=label)
    
    # Configuração das colunas de data
    for col, label in coluna_data.items():
        column_config[col] = st.column_config.DateColumn(label=label, format="DD/MM/YYYY")
    
    return column_config
    
config_graph = {
    "displayModeBar": True,
    "modeBarButtonsToRemove":[
        'zoom2d', 'pan2d', 'select2d', 'lasso2d', 'zoomIn2d',
        'zoomOut2d', 'autoScale2d', 'resetScale2d',
        'hoverClosestCartesian', 'hoverCompareCartesian',
        'zoom3d', 'pan3d', 'orbitRotation', 'tableRotation',
        'resetCameraDefault3d', 'resetCameraLastSave3d',
        'hoverClosest3d', 'zoomInGeo', 'zoomOutGeo',
        'resetGeo', 'hoverClosestGeo',
        'hoverClosestGl2d',
        'toggleHover', 'resetViews',
        'sendDataToCloud', 'toggleSpikelines',
        'resetViewMapbox']
    ,
    "displaylogo": False
}
