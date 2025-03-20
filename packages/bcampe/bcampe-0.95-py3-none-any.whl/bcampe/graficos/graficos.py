
import plotly.express as px
import colorsys
import plotly.graph_objects as go
import pandas as pd
import matplotlib.colors as mcolors
import locale
def converte_br(numero):
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
            valor = numero / s
            if valor.is_integer():
                valor_formatado = locale.format_string("%.0f", valor, grouping=True)
            else:
                valor_formatado = locale.format_string("%.2f", valor, grouping=True)
            return f"{'-' if negativo else ''}{valor_formatado}{suf[s]}"
    
    if numero.is_integer():
        return locale.format_string("%.0f", numero, grouping=True)
    return locale.format_string("%.2f", numero, grouping=True)

def abreviar_palavra(palavra, max_caracteres=7):
    if len(palavra) > max_caracteres:
        return palavra[:max_caracteres] + '...'
    return palavra

AZUL_PADRAO = ['#052E59']

################## GRAFICO DE BARRAS H/V #################
def grafico_barras(df, var_categorica, var_numerica=None, cor=None, titulo="", 
                   n=5, orientacao="h", agregacao="sum", hover_x="x", hover_y="y",
                   abreviar_rotulos=False, max_caracteres=7,tamanho_fonte_hover=12):
    """
    Parâmetros:
        df (pd.DataFrame): DataFrame com os dados.
        var_categorica (str): Nome da coluna categórica.
        var_numerica (str, opcional): Nome da coluna numérica. Se None, fará contagem de ocorrências.
        cor (list, opcional): Lista de cores para o gráfico.
        titulo (str, opcional): Título do gráfico.
        n (int, opcional): Quantidade de categorias a exibir (padrão: 5).
        orientacao (str, opcional): Orientação do gráfico ('h' para horizontal, 'v' para vertical).
        agregacao (str, opcional): Tipo de agregação a ser usada. Pode ser 'sum', 'mean', 'median'.
        hover_x (str, opcional): Nome do eixo x no hover.
        hover_y (str, opcional): Nome do eixo y no hover.
        abreviar_rotulos (bool, opcional): Se True, abrevia os rótulos do gráfico.
        max_caracteres (int, opcional): Número máximo de caracteres permitidos nos rótulos.
    """
    cor = cor or AZUL_PADRAO

    if agregacao not in ['sum', 'mean', 'median']:
        raise ValueError("O parâmetro 'agregacao' deve ser 'sum', 'mean' ou 'median'.")

    # Verifica se o DataFrame está vazio
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title=titulo,
            xaxis=dict(title=hover_x if orientacao == "v" else None),
            yaxis=dict(title=hover_y if orientacao == "h" else None),
        )
        fig.add_annotation(
            text="Não há dados disponíveis",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        return fig

    # Agregação dos dados
    if var_numerica:
        if agregacao == "sum":
            agg_func = 'sum'
        elif agregacao == "mean":
            agg_func = 'mean'
        elif agregacao == "median":
            agg_func = 'median'

        if orientacao == "h":
            df_agg = df.groupby(var_categorica)[var_numerica].agg(agg_func).sort_values(ascending=True).tail(n)
        else:
            df_agg = df.groupby(var_categorica)[var_numerica].agg(agg_func).sort_values(ascending=False).head(n)
    else:
        if orientacao == "h":
            df_agg = df[var_categorica].value_counts().sort_values(ascending=True).tail(n)
        else:
            df_agg = df[var_categorica].value_counts().sort_values(ascending=False).head(n)

    # Verifica se há dados suficientes para o gráfico
    if df_agg.empty:
        fig = go.Figure()
        fig.update_layout(
            title=titulo,
            xaxis=dict(title=hover_x if orientacao == "v" else None),
            yaxis=dict(title=hover_y if orientacao == "h" else None),
        )
        fig.add_annotation(
            text="Não há dados disponíveis",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        return fig

    # Abrevia os rótulos se necessário
    if abreviar_rotulos:
        labels_abreviados = df_agg.index.to_series().apply(lambda x: abreviar_palavra(x, max_caracteres))
    else:
        labels_abreviados = df_agg.index

    # Gera cores se necessário
    num_categorias = len(df_agg)
    if cor and len(cor) < num_categorias:
        cor = cor * (num_categorias // len(cor) + 1)

    # Prepara customdata para o hover (rótulo original e valor formatado)
    customdata = df_agg.index  # Rótulos originais
    customdata_br = [converte_br(v) for v in df_agg.values] if var_numerica else df_agg.values
    customdata_combinado = list(zip(customdata, customdata_br))

    # Cria o gráfico
    if orientacao == "h":
        fig = px.bar(
            x=df_agg.values,
            y=df_agg.index,
            orientation='h',
            title=titulo
        )
        # Atualiza o hovertemplate para usar customdata[0] (rótulo) e customdata[1] 
        fig.update_traces(
            customdata=customdata_combinado,
            hovertemplate=f'{hover_y}: %{{customdata[0]}}<br>{hover_x}: %{{customdata[1]}}<extra></extra>'
        )
    else:
        fig = px.bar(
            x=df_agg.index,
            y=df_agg.values,
            orientation='v',
            title=titulo
        )
        # Atualiza o hovertemplate para usar customdata[0] (rótulos) e customdata[1] (valores formatados)
        fig.update_traces(
            customdata=customdata_combinado,
            hovertemplate=f'{hover_x}: %{{customdata[0]}}<br>{hover_y}: %{{customdata[1]}}<extra></extra>'
        )

    # Ajusta layout
    fig.update_layout(
        xaxis=dict(title=None, fixedrange=True),
        yaxis=dict(title=None, fixedrange=True),
        hoverlabel=dict(font=dict(size=tamanho_fonte_hover))
    )

    # Aplica cores se fornecidas
    if cor:
        fig.update_traces(marker=dict(color=cor[:num_categorias]))

    # Aplica rótulos abreviados apenas no eixo
    if orientacao == "h":
        fig.update_layout(
            yaxis=dict(
                tickmode='array',
                tickvals=df_agg.index,  
                ticktext=labels_abreviados  # Aplica os rótulos abreviados
            )
        )
    else:
        fig.update_layout(
            xaxis=dict(
                tickmode='array',
                tickvals=df_agg.index,  
                ticktext=labels_abreviados  # Aplica os rótulos abreviados
            )
        )

    return fig
############################ GRAFICO DE BARRAS AGRUPADAS ##################################
def grafico_barras_agrupadas(df, var_categorica, var_numerica, n=10, cor=None, titulo="Gráfico de Barras", ordenado_por=None, hover_y=None, hover_x=None):
    """
    Parâmetros:
        df (pd.DataFrame): DataFrame contendo os dados.
        var_categorica (str): Nome da coluna categórica.
        var_numerica (list): Lista de colunas numéricas para somar e exibir no gráfico.
        n (int): Número de categorias principais a exibir.
        cor (list, opcional): Lista de cores para as barras. Se None, usa as cores padrão.
        titulo (str): Título do gráfico.
        ordenado_por (str, opcional): Nome da variável numérica para ordenar as barras.
        hover_y (list, opcional): Lista de nomes personalizados para as variáveis numéricas.
        hover_x (str, opcional): Texto para aparecer antes do nome da variável categórica no hover. Se None, usa o nome da variável.
    """
    
    # Verifica se o DataFrame está vazio
    if df.empty:
        # Retorna um gráfico vazio com uma mensagem
        fig = go.Figure()
        fig.update_layout(
            title=titulo,
            xaxis=dict(title=None),
            yaxis=dict(title=None),
        )
        # Adiciona uma mensagem ao gráfico
        fig.add_annotation(
            text="Não há dados disponíveis",
            xref="paper", yref="paper",
            x=0.5, y=0.5,  # Centraliza a mensagem
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        return fig

    if isinstance(var_numerica, str):
        var_numerica = [var_numerica]

    grouped_df = df.groupby(var_categorica)[var_numerica].sum()

    # Se 'ordenado_por' não for fornecido, usa o primeiro elemento de var_numerica
    if ordenado_por is None:
        ordenado_por = var_numerica[0]  

    grouped_df = grouped_df.sort_values(by=ordenado_por, ascending=False)
    grouped_df = grouped_df.reset_index()[:n]

    # Verifica se o DataFrame agrupado está vazio
    if grouped_df.empty:
        # Retorna um gráfico vazio com uma mensagem
        fig = go.Figure()
        fig.update_layout(
            title=titulo,
            xaxis=dict(title=None),
            yaxis=dict(title=None),
        )
        # Adiciona uma mensagem ao gráfico
        fig.add_annotation(
            text="Não há dados disponíveis",
            xref="paper", yref="paper",
            x=0.5, y=0.5,  # Centraliza a mensagem
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        return fig

    # Definir cores padrão se não forem fornecidas
    if cor is None:
        cor = ['#052E59', '#517496', '#7A89B2', '#A0ADCC', '#C4D1E2']

    customdata_br = {col: [converte_br(v) for v in grouped_df[col]] for col in var_numerica}

    # Se hover_y for fornecido, usamos os nomes personalizados
    if hover_y is None:
        hover_y = [col.replace('_', ' ').title() for col in var_numerica]

    # Se hover_x não for fornecido, usa o nome da variável categórica
    if hover_x is None:
        hover_x = var_categorica.replace('_', ' ').title()

    fig = go.Figure()

    # Criar uma barra separada para cada variável numérica
    for i, col in enumerate(var_numerica):
        nome_formatado = hover_y[i]  # Usando nome personalizado, se fornecido
        fig.add_trace(go.Bar(
            x=grouped_df[var_categorica],
            y=grouped_df[col],
            name=nome_formatado,
            marker_color=cor[i % len(cor)],  # Usa a cor correspondente
            customdata=customdata_br[col],  # Apenas os valores da variável atual
            hovertemplate=f"{hover_x}: %{{x}}<br>{nome_formatado}: %{{customdata}}<extra></extra>"  # Corrigido
        ))

    # Ajustando layout
    fig.update_layout(
        title=titulo,
        xaxis=dict(title=None),  # Usa o nome_x para o eixo X
        yaxis=dict(title=None),
        xaxis_fixedrange=True,
        yaxis_fixedrange=True,
        barmode='group',
        hoverlabel=dict(font=dict(size=14))
    )

    return fig
#################### GRAFICO DE PIZZZA ###############
def gerador_de_cores(base_color="#052E59", num_colors=5):
    """
    Gera um gradiente de azul baseado na cor base, ajustando a luminosidade e saturação para
    aumentar o contraste entre as cores quando há menos categorias.
    """
    if num_colors <= 0:
        return []
    
    # Converte HEX para RGB
    base_rgb = tuple(int(base_color[i:i+2], 16) for i in (1, 3, 5))
    base_hls = colorsys.rgb_to_hls(*(x / 255.0 for x in base_rgb))
    
    # Define limites para luminosidade e saturação
    max_luminosity = 0.85  # Máximo de luminosidade (evita cores muito claras)
    min_saturation = 0.20  # Mínimo de saturação
    
    # Calcula os passos para luminosidade e saturação
    luminosity_step = (max_luminosity - base_hls[1]) / (num_colors - 1) if num_colors > 1 else 0
    saturation_step = (base_hls[2] - min_saturation) / (num_colors - 1) if num_colors > 1 else 0
    
    gradient = []
    for i in range(num_colors):
        new_luminosity = base_hls[1] + i * luminosity_step
        new_saturation = max(min_saturation, base_hls[2] - i * saturation_step)
        
        # Garante que os valores estejam dentro dos limites
        new_luminosity = max(0.0, min(new_luminosity, 1.0))
        new_saturation = max(0.0, min(new_saturation, 1.0))
        
        # Converte HLS para RGB e depois para HEX
        rgb = colorsys.hls_to_rgb(base_hls[0], new_luminosity, new_saturation)
        hex_color = "#%02X%02X%02X" % (
            int(rgb[0] * 255),
            int(rgb[1] * 255),
            int(rgb[2] * 255)
        )
        gradient.append(hex_color)
    
    return gradient

def grafico_pizza(df, var_categorica, var_numerica=None, outros=True, n=7, colors_base=None, 
                  cor_outros=None, cores_categoria=None, titulo="Gráfico de Pizza", valor="percentual",
                  hole_size=0.5, altura=350, expessura_linha=0.4, cor_linha='white',
                  hover_cat="Categoria", hover_num="Total", cor_gradiente="#052E59"):
    """
    Parâmetros:
        df (pd.DataFrame): DataFrame contendo os dados.
        var_categorica (str): Nome da coluna categórica para agrupar os dados e criar as fatias do gráfico.
        var_numerica (str, opcional): Nome da coluna numérica para calcular os valores das fatias. Se None, conta a frequência das categorias.
        outros (bool, opcional): Se True, categorias menores que não estão entre as top `n` são agrupadas em "Outros". Se False, exibe apenas as top `n` categorias.
        n (int, opcional): Número de categorias principais a serem exibidas. Categorias além desse número são agrupadas em "Outros" se `outros=True`.
        colors_base (list, opcional): Lista de cores personalizadas para as fatias do gráfico. Se None, as cores são geradas automaticamente.
        cor_outros (str, opcional): Cor da fatia "Outros". Se None, usa a última cor de `colors_base`.
        cores_categoria (list, opcional): Lista de cores específicas para cada categoria. Se fornecida, sobrescreve `colors_base`.
        titulo (str, opcional): Título do gráfico.
        valor (str, opcional): Tipo de valor exibido nas fatias. Pode ser "percentual", "numero", "percentual+numero" ou "label".
        hole_size (float, opcional): Tamanho do buraco central do gráfico (0 a 1). Um valor de 0.5 cria um gráfico de rosca.
        altura (int, opcional): Altura do gráfico em pixels.
        expessura_linha (float, opcional): Espessura da linha que separa as fatias do gráfico.
        cor_linha (str, opcional): Cor da linha que separa as fatias do gráfico.
        hover_cat (str, opcional): Nome customizado para a categoria no hover.
        hover_num (str, opcional): Nome customizado para o valor numérico no hover.
        cor_gradiente (str, opcional): Cor base para gerar o gradiente de cores automaticamente.

    Retorno:
        go.Figure: Objeto de gráfico Plotly.
    """
    # Verifica se o DataFrame está vazio ou se a coluna categórica não existe
    if df.empty or var_categorica not in df.columns:
        # Retorna um gráfico vazio com uma mensagem
        fig = go.Figure()
        fig.update_layout(
            title=titulo,
            height=altura,
            margin=dict(t=50, b=30, l=0, r=0),
        )
        # Adiciona uma mensagem ao gráfico
        fig.add_annotation(
            text="Não há dados disponíveis",
            xref="paper", yref="paper",
            x=0.5, y=0.5,  # Centraliza a mensagem
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        return fig

    if var_numerica and var_numerica in df.columns:
        # Agrupar dados
        df_grouped = df.groupby(var_categorica)[var_numerica].sum().sort_values(ascending=False)
    else:
        # Contar frequência de categorias
        df_grouped = df[var_categorica].value_counts()
        titulo = f"Distribuição das Categorias de {var_categorica}"

    # Verifica se há dados após a agregação
    if df_grouped.empty:
        # Retorna um gráfico vazio com uma mensagem
        fig = go.Figure()
        fig.update_layout(
            title=titulo,
            height=altura,
            margin=dict(t=50, b=30, l=0, r=0),
        )
        # Adiciona uma mensagem ao gráfico
        fig.add_annotation(
            text="Não há dados disponíveis",
            xref="paper", yref="paper",
            x=0.5, y=0.5,  # Centraliza a mensagem
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        return fig

    if outros and len(df_grouped) > n:
        top_categorias = df_grouped[:n-1]  # Pega as (n-1) categorias principais
        outros_valores_sum = df_grouped[n-1:].sum()
        df_agrupado = pd.concat([top_categorias, pd.Series({'Outros': outros_valores_sum})])
    else:
        df_agrupado = df_grouped[:n]  # Apenas as top n categorias sem "Outros"

    num_categorias = len(df_agrupado)

    # Gerar cores caso não seja passado pelo usuário
    if colors_base is None:
        colors_base = gerador_de_cores(cor_gradiente, num_categorias)

    while len(colors_base) < num_categorias:
        colors_base *= 2

    if "Outros" in df_agrupado.index:
        if cor_outros is None:
            cor_outros = colors_base[-1]
        cores_mapeadas = {categoria: colors_base[i] for i, categoria in enumerate(df_agrupado.index) if categoria != "Outros"}
        cores_mapeadas["Outros"] = cor_outros
        colors_base = [cores_mapeadas[c] for c in df_agrupado.index]
    else:
        colors_base = colors_base[:num_categorias]

    if cores_categoria:
        cores_categoria = cores_categoria[:num_categorias]
        sorted_values = df_agrupado.sort_values(ascending=False)
        cores_categoria_sorted = sorted(cores_categoria, reverse=True)
        cores_mapeadas = {categoria: cores_categoria_sorted[i] for i, categoria in enumerate(sorted_values.index)}
        if "Outros" in df_agrupado.index:
            cores_mapeadas["Outros"] = cor_outros if cor_outros else colors_base[-1]
        colors_base = [cores_mapeadas[c] for c in df_agrupado.index]

    if valor == "percentual":
        textinfo = "percent"
        valores_formatados = None  # Apenas percentual, sem números
    elif valor == "numero":
        textinfo = "text"  # Mostra apenas os números formatados
        valores_formatados = [converte_br(v) for v in df_agrupado.values]  # Formata os números
    elif valor == "percentual+numero":
        textinfo = "text+percent"  # Mostra número + percentual
        valores_formatados = [converte_br(v) for v in df_agrupado.values]
    else:
        textinfo = "label"  # Caso padrão
        valores_formatados = None

    if var_numerica:
        customdata = [converte_br(v) for v in df_agrupado.values]
        hovertemplate = f"{hover_cat}: %{{label}}<br>{hover_num}: %{{customdata}}<br>Percentual: %{{percent}}<extra></extra>"
    else:
        customdata = None
        hovertemplate = f"{hover_cat}: %{{label}}<br>Quantidade: %{{value}}<br>Percentual: %{{percent}}<extra></extra>"

    fig = go.Figure(data=[ 
        go.Pie(
            labels=df_agrupado.index,
            values=df_agrupado.values,
            hole=hole_size,
            text=valores_formatados,  # Aplica os valores formatados
            textinfo=textinfo,  # Define o que exibir dentro do gráfico
            customdata=customdata,
            hovertemplate=hovertemplate,
            marker=dict(colors=colors_base, line=dict(color=cor_linha, width=expessura_linha))
        )
    ])

    fig.update_layout(
        margin=dict(t=50, b=30, l=0, r=0),
        legend=dict(font=dict(size=11)),
        height=altura,
        title=titulo,
        hoverlabel=dict(
            font=dict(size=13)  # Define a fonte do hover para tamanho 14
        )
    )
    fig.update_traces(
        textfont=dict(size=13)  # Aumenta a fonte dos rótulos dentro do gráfico
    )

    return fig

######################### GRAFICO DE LINHA #############
def ajustar_cor_preenchimento(cor_linha, opacidade=0.35):
        try:
            rgb = mcolors.to_rgb(mcolors.CSS4_COLORS.get(cor_linha, cor_linha))
            return f'rgba({int(rgb[0]*255)}, {int(rgb[1]*255)}, {int(rgb[2]*255)}, {opacidade})'
        except ValueError:
            return 'rgba(0, 0, 0, 0.1)'
def grafico_linha(df, periodo, var_numerica=None, var_categorica=None, categoria=None, agregacao='sum', 
                  cor_linha=None, hover_x='Ano', hover_y='Total', titulo='', preenchimento=False, 
                  cor_preenchimento=None, opacidade=0.35, altura=350):
    """
    Gera um gráfico de linha com a opção de preenchimento abaixo da curva.

    Parâmetros:
    - df (pd.DataFrame): DataFrame contendo os dados.
    - periodo (str): Nome da coluna usada para agrupar os dados no eixo X (ex: 'mes', 'ano').
    - var_numerica (str, opcional): Nome da coluna numérica a ser plotada (ex: 'Despesas_empenhadas').
    - var_categorica (str, opcional): Nome da coluna categórica para filtragem (ex: 'Categoria').
    - categoria (str, opcional): Valor específico da var_categorica para filtrar os dados.
    - agregacao (str, opcional): Método de agregação ('sum', 'mean', 'median'). Padrão: 'sum'.
    - cor_linha (str, opcional): Cor da linha do gráfico. Padrão: '#052E59'.
    - hover_x (str, opcional): Nome do eixo X exibido no hover. Padrão: 'Ano'.
    - hover_y (str, opcional): Nome do eixo Y exibido no hover. Padrão: 'Total'.
    - titulo (str, opcional): Título do gráfico.
    - preenchimento (bool, opcional): Se True, preenche a área abaixo da linha. Padrão: False.
    - cor_preenchimento (str, opcional): Cor do preenchimento. Se None, ajusta com base na cor_linha.
    - opacidade (float, opcional): Opacidade do preenchimento (0 a 1). Padrão: 0.35.
    - altura (int, opcional): Altura do gráfico em pixels. Padrão: 350.
    """
    
    # Validação da função de agregação
    funcoes_agregacao = {'sum': 'sum', 'mean': 'mean', 'median': 'median'}
    if agregacao not in funcoes_agregacao:
        raise ValueError("O parâmetro 'agregacao' deve ser 'sum', 'mean' ou 'median'.")
    
    # Criação de uma cópia do DataFrame para evitar modificações diretas
    df = df.copy()
    
    # Aplicação do filtro, se necessário
    if var_categorica and categoria:
        df = df[df[var_categorica] == categoria]
    
    # Verifica se o DataFrame está vazio após a filtragem
    if df.empty:
        # Retorna um gráfico vazio com uma mensagem
        fig = go.Figure()
        fig.update_layout(
            title=titulo,
            xaxis=dict(title=hover_x),
            yaxis=dict(title=hover_y),
            height=altura
        )
        # Adiciona uma mensagem ao gráfico
        fig.add_annotation(
            text="Não há dados disponíveis",
            xref="paper", yref="paper",
            x=0.5, y=0.5,  # Centraliza a mensagem
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        return fig
    
    # Agrupamento dos dados
    if var_numerica:
        df_grouped = df.groupby(periodo, as_index=True)[var_numerica].agg(funcoes_agregacao[agregacao])
    else:
        df_grouped = df.groupby(periodo, as_index=True).size()  # Conta ocorrências se var_numerica for None
    
    # Definição das cores
    cor_linha = cor_linha or '#052E59'
    cor_preenchimento = cor_preenchimento or ajustar_cor_preenchimento(cor_linha, opacidade)
    
    # Formatação dos dados para exibição no hover
    customdata = df_grouped.values
    customdata_br = [converte_br(v) for v in customdata] if var_numerica else customdata
    
    # Criação do gráfico
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_grouped.index,
        y=df_grouped.values,
        mode='lines+markers',
        fill='tozeroy' if preenchimento else 'none',
        fillcolor=cor_preenchimento if preenchimento else 'rgba(0,0,0,0)',
        line=dict(color=cor_linha),
        marker=dict(color=cor_linha, size=6),
        name='',
        customdata=customdata_br,  # Valores formatados no hover
        hovertemplate=(f"{hover_x}: <b>%{{x}}</b><br>{hover_y}: <b>%{{customdata}}</b><br>")
    ))

    # Ajuste da aparência do gráfico
    fig.update_layout(
        title=titulo,
        xaxis_tickangle=-90,
        yaxis=dict(title=None),
        xaxis_fixedrange=True,
        yaxis_fixedrange=True,
        height=altura,
        hoverlabel=dict(
            font=dict(size=14))
    )
    
    fig.update_xaxes(type='category')
    return fig
    
######################### GRAFICO DE DISPERSAO #################
def grafico_dispersao(df, var_numericaX, var_numericaY, custom_data=None, text_custom_data=None, title="Gráfico de Dispersão", 
                      log_x=True, height=400, size_max=60, tickvals=None, ticktext=None, 
                      titulo_x=None, titulo_y=None, cor='blue', hover_x=None, hover_y=None):
    """
    Parâmetros:
        df (pd.DataFrame): DataFrame contendo os dados.
        var_numericaX (str): Nome da coluna para o eixo X.
        var_numericaY (str): Nome da coluna para o eixo Y.
        custom_data (list, opcional): Lista de colunas a serem exibidas no hover.
        text_custom_data (dict, opcional): Dicionário com o mapeamento das colunas para o texto a ser exibido no hover (ex: {coluna: 'Texto'}).
        title (str, opcional): Título do gráfico (padrão: "Gráfico de Dispersão").
        log_x (bool, opcional): Se True, usa escala logarítmica no eixo X (padrão: True).
        height (int, opcional): Altura do gráfico (padrão: 400).
        size_max (int, opcional): Tamanho máximo dos pontos (padrão: 60).
        tickvals (list, opcional): Lista de valores para os ticks do eixo X.
        ticktext (list, opcional): Lista de rótulos correspondentes aos ticks.
        titulo_x (str, opcional): Título do eixo X.
        titulo_y (str, opcional): Título do eixo Y.
        cor (str, opcional): Cor dos pontos (padrão: 'blue').
        hover_x (str, opcional): Nome customizado para o eixo X no hover.
        hover_y (str, opcional): Nome customizado para o eixo Y no hover.

    Retorno:
        go.Figure: Objeto de gráfico Plotly.
    """
    if df.empty:
        fig = go.Figure()
        fig.update_layout(
            title=title,
            height=height,
            xaxis=dict(title=titulo_x),
            yaxis=dict(title=titulo_y),
        )
        fig.add_annotation(
            text="Não há dados disponíveis",
            xref="paper", yref="paper",
            x=0.5, y=0.5,  # Centraliza a mensagem
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        return fig

    if var_numericaX not in df.columns or var_numericaY not in df.columns:
        fig = go.Figure()
        fig.update_layout(
            title=title,
            height=height,
            xaxis=dict(title=titulo_x),
            yaxis=dict(title=titulo_y),
        )
        fig.add_annotation(
            text="Colunas não encontradas no DataFrame",
            xref="paper", yref="paper",
            x=0.5, y=0.5,  # Centraliza a mensagem
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        return fig

    fig = px.scatter(df, x=var_numericaX, y=var_numericaY, title=title, custom_data=custom_data, log_x=log_x, size_max=size_max)

    if log_x:
        fig.update_xaxes(tickvals=tickvals, ticktext=ticktext)

    fig.update_layout(height=height)

    if titulo_x:
        fig.update_xaxes(title_text=titulo_x)  

    if titulo_y:
        fig.update_yaxes(title_text=titulo_y)  

    fig.update_traces(marker=dict(color=cor))  
    
    hover_template = [
        f"{var_numericaX}: <b>%{{x}}</b>",  
        f"{var_numericaY}: <b>%{{y}}</b>"   
    ]

    # Se custom_data foi passado
    if custom_data:
        if text_custom_data is None:
            text_custom_data = {col: col for col in custom_data}

        # Montando o template para as colunas customizadas
        for i, label in enumerate(custom_data):
            # Verificando se a coluna foi renomeada no text_custom_data
            label_text = text_custom_data.get(label, label)  # Se a coluna estiver no mapeamento, usa o nome novo, senão usa o nome original
            
            # Verificando se a coluna é numérica
            if df[label].dtype in ['int64', 'float64']:  
                hover_template.append(f"{label_text}: <b>%{{customdata[{i}]}}</b>")  # Valores dinâmicos com customdata
            else:
                hover_template.append(f"{label_text}: <b>%{{customdata[{i}]}}</b>")

    if hover_x:
        hover_template[0] = f"{hover_x}: <b>%{{x}}</b>"  # Substitui o nome da variável X pelo nome customizado

    if hover_y:
        hover_template[1] = f"{hover_y}: <b>%{{y}}</b>"  # Substitui o nome da variável Y pelo nome customizado

    hover_template.append("<extra></extra>")

    fig.update_traces(hovertemplate="<br>".join(hover_template))
    fig.update_layout(hoverlabel=dict(
            font=dict(size=14)))

    return fig