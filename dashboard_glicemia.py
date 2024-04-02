import streamlit as st
import pandas as pd
import numpy as np
import locale
import plotly.express as px
import datetime

# Definindo a localização para português do Brasil
#locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

# Caminho para o arquivo Excel dentro da pasta 'app-medglic'
caminho_arquivo = 'REGISTRO-GLICOSES.xlsx'

# Lendo os dados da planilha
dados_glicemia = pd.read_excel('REGISTRO-GLICOSES.xlsx')

# Converter a coluna 'Dia/Mês/Ano' para o formato datetime, se necessário
dados_glicemia['Data'] = pd.to_datetime(dados_glicemia['Dia/Mês/Ano'], format='%d/%m/%Y')

# Inicializar as variáveis de data mínima e máxima para o filtro de data na barra lateral
min_data = dados_glicemia['Data'].min()
max_data = dados_glicemia['Data'].max()

# Configuração da página
st.set_page_config(page_title="Dashboard - MedGlic", page_icon=":desktop_computer:", layout="wide", initial_sidebar_state="auto", menu_items=None)   

# Criar o dashboard com Streamlit
st.sidebar.title('Menu')
pagina = st.sidebar.radio("Selecione a página:", ("Médias Diárias", "Maiores Picos"))

# Adicionando o filtro de data na barra lateral
st.sidebar.subheader('Filtro de Data')
data_inicio = st.sidebar.date_input('Data de Início', value=min_data, min_value=min_data, max_value=max_data)
data_fim = st.sidebar.date_input('Data de Fim', value=max_data, min_value=min_data, max_value=max_data)

# Convertendo as datas do input para o mesmo formato do DataFrame
data_inicio = pd.to_datetime(data_inicio)
data_fim = pd.to_datetime(data_fim)

# Filtro aplicado no DataFrame principal
dados_filtrados = dados_glicemia[(dados_glicemia['Data'] >= data_inicio) & (dados_glicemia['Data'] <= data_fim)]
dados_filtrados = dados_filtrados.dropna(subset=['Glicose', 'Dose Glargina', 'Dose Asparte'])

# Convertendo a coluna 'Horario' para datetime.time se ainda não estiver nesse formato
dados_filtrados['Horario'] = pd.to_datetime(dados_filtrados['Horario'], format='%H:%M:%S').dt.time

# Adicionando o filtro de horários na barra lateral
st.sidebar.subheader('Filtro de Horários')
horario_inicio, horario_fim = st.sidebar.slider(
    "Selecione o intervalo de horários:",
    value=(datetime.time(0, 0), datetime.time(23, 59)),
    format="HH:mm"
)


st.sidebar.subheader('Versão 1.0 - Em desenvolvimento.')



# Aplicando o filtro de horários no DataFrame filtrado
# Esta é a parte onde o filtro é aplicado corretamente
dados_filtrados = dados_filtrados[
    (dados_filtrados['Horario'] >= horario_inicio) & 
    (dados_filtrados['Horario'] <= horario_fim)
]

# Aqui vamos recalcular todas as métricas usando dados_filtrados
if pagina == "Médias Diárias":
    # Cálculos com base nos dados filtrados
    media_diaria_glicose = dados_filtrados.groupby('Data')['Glicose'].mean().reset_index()
    media_glicose_total = dados_filtrados['Glicose'].mean()
    a1c_estimado = (media_glicose_total + 46.7) / 28.7
    picos_glicose = dados_filtrados.sort_values(by='Glicose', ascending=False).head(5)
    media_diaria_glargina = dados_filtrados.groupby('Data')['Dose Glargina'].mean().reset_index()
    soma_diaria_asparte = dados_filtrados.groupby('Data')['Dose Asparte'].sum().reset_index()
    media_diaria_asparte = dados_filtrados.groupby('Data')['Dose Asparte'].mean().reset_index()
    media_glargina = media_diaria_glargina['Dose Glargina'].mean()
    media_asparte = media_diaria_asparte['Dose Asparte'].mean()
    media_total_diaria_asparte = soma_diaria_asparte['Dose Asparte'].mean()
    desvio_padrao_asparte = dados_filtrados['Dose Asparte'].std()
    dentro_alvo = dados_filtrados[(dados_filtrados['Glicose'] >= 70) & (dados_filtrados['Glicose'] <= 140)]
    abaixo_alvo = dados_filtrados[dados_filtrados['Glicose'] < 70]
    acima_alvo = dados_filtrados[dados_filtrados['Glicose'] > 140]
    porcentagem_dentro_alvo = (len(dentro_alvo) / len(dados_filtrados)) * 100
    porcentagem_abaixo_alvo = (len(abaixo_alvo) / len(dados_filtrados)) * 100
    porcentagem_acima_alvo = (len(acima_alvo) / len(dados_filtrados)) * 100

# Calcular os maiores picos de glicose fora do bloco condicional da página, para estar acessível em ambas as páginas
picos_glicose = dados_filtrados.sort_values(by='Glicose', ascending=False).head(10)


if pagina == "Médias Diárias":
    st.title('Dashboard de Monitoramento da Glicemia - Paciente: Maik Selau Dimer')
    # Exibir a estimativa de A1c
    st.subheader('Estimativa da Hemoglobina Glicada (A1c)')
    st.write(f'A estimativa de A1c é de {a1c_estimado:.2f}%.')
    st.write(f'A estimativa de média é de {media_glicose_total:.2f} mg/dL.')
    # Exibir o gráfico de linhas das médias diárias de glicose
    st.subheader('Médias Diárias de Glicose')
    # Criando o gráfico com Plotly
    fig = px.line(media_diaria_glicose, x='Data', y='Glicose', title='Médias Diárias de Glicose')
    fig.update_layout(
            xaxis=dict(
                tickmode='array',
                tickvals=media_diaria_glicose['Data'],
                ticktext=[data.strftime('%a %d') for data in media_diaria_glicose['Data']]
            ),
            autosize=True
        )

    

    # Renderizando o gráfico com Streamlit
    st.plotly_chart(fig, use_container_width=True)
    st.subheader('Métricas de Insulina e Controle Glicêmico')
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Média Diária Glargina", f"{media_glargina:.2f} unidades")
    col2.metric("Média por aplicação Asparte", f"{media_asparte:.2f} unidades")
    col3.metric("Média Total Diária de Asparte", f"{media_total_diaria_asparte:.2f} unidades")
    col4.metric("Desvio Padrão Asparte", f"{desvio_padrao_asparte:.2f} unidades")

    # Adicionando uma explicação sobre o desvio padrão
    st.caption("O desvio padrão das doses de insulina Asparte indica a variação das doses administradas dia após dia. Um valor de desvio padrão menor sugere que as doses são mais consistentes, enquanto um valor maior indica uma maior variação nas doses diárias.")

    # Cálculo das porcentagens de medições fora do alvo
    abaixo_alvo = dados_glicemia[dados_glicemia['Glicose'] < 70]
    acima_alvo = dados_glicemia[dados_glicemia['Glicose'] > 140]

    porcentagem_abaixo_alvo = (len(abaixo_alvo) / len(dados_glicemia)) * 100
    porcentagem_acima_alvo = (len(acima_alvo) / len(dados_glicemia)) * 100

    # Exibição das métricas no dashboard
    st.subheader('Controle Glicêmico')
    col1, col2, col3 = st.columns(3)
    col1.metric("% Dentro do Alvo (70-140 mg/dL)", f"{porcentagem_dentro_alvo:.2f}%")
    col2.metric("% Abaixo do Alvo (<70 mg/dL)", f"{porcentagem_abaixo_alvo:.2f}%")
    col3.metric("% Acima do Alvo (>140 mg/dL)", f"{porcentagem_acima_alvo:.2f}%")
   

  

    # Análise de Correlação
    st.subheader('Análise de Correlação')
    # Garanta que não há apenas valores constantes
    if dados_filtrados['Dose Glargina'].nunique() <= 1:
        st.write("Não é possível calcular a correlação para a 'Dose Glargina' porque todos os valores são iguais.")
    else:
        # Cálculo da correlação para 'Dose Glargina'
        correlacao_glargina = dados_filtrados['Glicose'].corr(dados_filtrados['Dose Glargina'])
        st.write(f"Correlação entre Glicose e Dose Glargina: {correlacao_glargina:.2f}")
        
    correlacao_asparte = dados_filtrados['Glicose'].corr(dados_filtrados['Dose Asparte'])
    st.write(f"Correlação entre Glicose e Dose Asparte: {correlacao_asparte:.2f}")

    def traduzir_dia_semana(english_day_name):
        dias = {
            'Monday': 'Segunda-feira',
            'Tuesday': 'Terça-feira',
            'Wednesday': 'Quarta-feira',
            'Thursday': 'Quinta-feira',
            'Friday': 'Sexta-feira',
            'Saturday': 'Sábado',
            'Sunday': 'Domingo',
        }
        return dias.get(english_day_name, 'Dia inválido')

    # Aplicando a função de tradução
    dados_filtrados['Dia da Semana'] = dados_filtrados['Data'].dt.day_name().apply(traduzir_dia_semana)

    fig_dias_semana = px.box(dados_filtrados, x='Dia da Semana', y='Glicose', title='Níveis de Glicose por Dia da Semana')
    st.plotly_chart(fig_dias_semana, use_container_width=True)
    with st.expander("Entenda a distribuição por dia da semana"):
        st.caption("""
                        Este gráfico de caixa mostra a distribuição dos níveis de glicose para cada dia da semana. 
                        Os limites da caixa representam o primeiro e terceiro quartis, a linha dentro da caixa é a mediana. 
                        As linhas que se estendem das caixas ('bigodes') representam a variação dos dados fora do quartil superior e inferior, 
                        enquanto os pontos fora dos bigodes indicam valores atípicos. 
                        Isso pode ajudar a identificar padrões e variações nos níveis de glicose ao longo da semana.
                        """)
    
    # Tentativa de conversão, ignorando segundos caso existam
    try:
        dados_filtrados['Horario'] = pd.to_datetime(dados_filtrados['Horario'], format='%H:%M').dt.time
    except ValueError:
        # Se a conversão falhar, tente um formato que inclui segundos
        dados_filtrados['Horario'] = pd.to_datetime(dados_filtrados['Horario'], format='%H:%M:%S').dt.time

    # Adicione uma coluna oculta para a ordenação que seja do tipo datetime
    dados_filtrados['Data_Ordenacao'] = dados_filtrados['Data']

    # Ordenando o DataFrame pela coluna 'Data_Ordenacao' e 'Horario'
    dados_filtrados.sort_values(by=['Data_Ordenacao', 'Horario'], inplace=True)

    def classificar_refeicao(hora):
    
        if hora >= datetime.time(0, 0) and hora < datetime.time(6, 0):
            return 'Madrugada'
        elif hora >= datetime.time(6, 0) and hora < datetime.time(8, 0):
            return 'Pré-Café'
        elif hora >= datetime.time(9, 0) and hora < datetime.time(13, 0):
            return 'Pré-Almoço'
        elif hora >= datetime.time(13, 0) and hora < datetime.time(18, 0):
            return 'Pós-Almoço'
        elif hora >= datetime.time(18, 0) and hora <= datetime.time(23, 0):
            return 'Pré-Janta'
        else:
            return 'Horário Indefinido'  # Para qualquer horário que não se encaixe nas condições acima

   

    # Convertendo 'Horario' para o formato de tempo
    dados_filtrados['Horario'] = pd.to_datetime(dados_filtrados['Horario'], format='%H:%M:%S').dt.time

    # Aplicando a função para classificar a refeição
    dados_filtrados['Refeição'] = dados_filtrados['Horario'].apply(classificar_refeicao)

    # Ordenando o DataFrame pela coluna 'Data' e 'Horario'
    dados_filtrados.sort_values(by=['Data', 'Horario'], inplace=True)

    # Verificar e ajustar as classificações de refeição baseado em duplicatas
    for i in range(1, len(dados_filtrados)):
        if dados_filtrados.iloc[i]['Refeição'] in ['Pré-Almoço', 'Pré-Janta'] and \
        dados_filtrados.iloc[i - 1]['Refeição'] == dados_filtrados.iloc[i]['Refeição']:
            dados_filtrados.iloc[i, dados_filtrados.columns.get_loc('Refeição')] = 'Pós-Refeição'

    # Criando a coluna 'Dia/Mês' após a ordenação para exibição
    dados_filtrados['Dia/Mês'] = dados_filtrados['Data'].dt.strftime('%d/%m')

    st.subheader("Tabela de medições")
    # Exibindo o DataFrame atualizado
    st.dataframe(dados_filtrados[['Dia/Mês', 'Horario', 'Glicose', 'Dose Glargina', 'Dose Asparte', 'Refeição']])

    # Crie uma coluna de média móvel para a glicose
    dados_filtrados['Glicose_Media_Movel'] = dados_filtrados['Glicose'].rolling(window=7).mean()

    # Gráfico de linhas com média móvel
    fig_tendencia = px.line(dados_filtrados, x='Data', y='Glicose_Media_Movel', title='Tendência de Glicose (Média Móvel de 7 dias)')
    st.plotly_chart(fig_tendencia, use_container_width=True)
    # Para o gráfico de Tendência de Glicose (Média Móvel de 7 dias)
    with st.expander("Entenda a Tendência de Glicose"):
        st.caption("""
        Este gráfico mostra a média móvel de glicose calculada ao longo de um período de 7 dias. 
        A linha representa o valor médio que suaviza as flutuações diárias, 
        permitindo uma melhor visualização de aumentos ou diminuições na glicose ao longo do tempo. 
        Isso é especialmente útil para entender a eficácia do tratamento e para 
        identificar períodos em que as leituras de glicose foram consistentemente altas ou baixas.
        """)

    # Histograma dos níveis de glicose
    fig_distribuicao = px.histogram(dados_filtrados, x='Glicose', nbins=30, title='Distribuição dos Níveis de Glicose')
    st.plotly_chart(fig_distribuicao, use_container_width=True)
    # Para o gráfico de Distribuição dos Níveis de Glicose
    with st.expander("Entenda a Distribuição dos Níveis de Glicose"):
        st.caption("""
        O histograma exibe a frequência das leituras de glicose em diferentes intervalos de valores, 
        o que ajuda a entender a variabilidade e consistência dos níveis de glicose. 
        Áreas com maiores barras representam os intervalos de valores nos quais ocorreram mais medições, 
        indicando a faixa de glicose mais comum. Isso pode sinalizar a necessidade de ajustes no plano de 
        tratamento ou na dieta, se muitas leituras caírem fora dos níveis desejados.
        """)


    
    




else:
    st.title('Dashboard de Monitoramento da Glicemia - Maiores Picos')
    # Exibir os maiores picos de glicose
    st.subheader('Maiores Picos de Glicose')
    st.write(picos_glicose[['Data', 'Glicose']])
