import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

# Carregar o arquivo XLSX
@st.cache_data
def load_data():
    df = pd.read_excel(r"RelatorioFMX.xlsx", engine="openpyxl")
    df.columns = df.columns.str.strip()  # Remove espaços extras nos nomes de colunas
    return df

df = load_data()

st.title("Análise do Relatório de Ligações - Discadora FMX")

# Verificar se as colunas esperadas existem
colunas_necessarias = ["Duração Real", "Duracao", "SIP code", "Data e Hora", "Motivo do Desligamento", "Origem", "Destino", "Operador"]
for coluna in colunas_necessarias:
    if coluna not in df.columns:
        st.error(f"Coluna ausente no Excel: {coluna}")
        st.stop()

# Converter duração real corretamente
df["Duração Real"] = df["Duração Real"].astype(str)  # Converte para string
df["Duração Real"] = pd.to_timedelta(df["Duração Real"], errors="coerce")
df["Duração (segundos)"] = df["Duração Real"].dt.total_seconds()

# Converter coluna de Data e Hora para datetime no formato brasileiro
df["Data e Hora"] = pd.to_datetime(df["Data e Hora"], format="%d/%m/%Y %H:%M:%S", dayfirst=True, errors="coerce")

# Criar filtro interativo para datas
data_inicio = st.date_input("Data inicial", df["Data e Hora"].min().date())
data_fim = st.date_input("Data final", df["Data e Hora"].max().date())

# Converter datas do filtro para datetime corretamente
data_inicio = pd.to_datetime(data_inicio)
data_fim = pd.to_datetime(data_fim)

# Filtrar dados dentro do intervalo correto
df_filtrado = df[
    (df["Data e Hora"] >= data_inicio) & (df["Data e Hora"] <= data_fim)
]

# Converter a coluna "Destino" para string para exibir corretamente
df["Destino"] = df["Destino"].astype(str)

# Criar relatório estatístico
st.subheader("Relatório Estatístico das Ligações")
st.write(f"🔹 Número mais ligado: {df['Destino'].value_counts().idxmax()}")
st.write(f"🔹 Total de ligações por origem:")
st.dataframe(df["Origem"].value_counts())
st.write(f"🔹 Frequência de Códigos SIP:")
st.dataframe(df["SIP code"].value_counts())

# Gráfico de tendência das ligações ao longo do tempo (após conversão correta)
df_filtrado_indexado = df_filtrado.copy()
df_filtrado_indexado.set_index("Data e Hora", inplace=True)

st.subheader("Tendência de Ligações ao Longo do Tempo")
fig, ax = plt.subplots(figsize=(10, 5))
df_filtrado_indexado.resample("D").size().plot(ax=ax)
ax.set_xlabel("Data")
ax.set_ylabel("Número de Chamadas")
st.pyplot(fig)

# Gráfico de barras empilhadas por operador
st.subheader("Distribuição de Chamadas por Operador")
fig, ax = plt.subplots(figsize=(10, 5))
df["Operador"].value_counts().plot(kind="bar", ax=ax)
ax.set_xlabel("Operador")
ax.set_ylabel("Número de Chamadas")
st.pyplot(fig)

# Motivos do desligamento das chamadas - Melhorado
st.subheader("Motivos do Desligamento das Chamadas - Melhorado")
fig, ax = plt.subplots(figsize=(8, 6))
df["Motivo do Desligamento"].value_counts().plot(kind="barh", ax=ax)
ax.set_xlabel("Quantidade")
ax.set_ylabel("Motivo")
st.pyplot(fig)

# Relatório de chamadas malsucedidas
st.subheader("Chamadas Malsucedidas")
df_erro = df[df["SIP code"].isin([404, 480, 606])]
st.dataframe(df_erro)

# Alertas para chamadas muito curtas (< 5 segundos)
st.subheader("Chamadas Muito Curtas (< 5 segundos)")
df_curto = df[df["Duração (segundos)"] < 5]
st.dataframe(df_curto)

# Criar menu de pesquisa por número de destino
st.subheader("Pesquisar Chamadas por Destino")
destino_pesquisado = st.text_input("Digite um número de destino para buscar:")
if destino_pesquisado:
    resultados = df[df["Destino"].astype(str).str.contains(destino_pesquisado, na=False)]
    if not resultados.empty:
        st.write("Resultados encontrados:")
        st.dataframe(resultados)
    else:
        st.warning("Nenhuma chamada encontrada para este número.")

# Botão para exportar relatório atualizado para Excel
st.subheader("Exportar Relatório para Excel")
output = io.BytesIO()
df.to_excel(output, index=False, engine="openpyxl")
output.seek(0)
st.download_button(
    label="📥 Baixar Relatório XLSX",
    data=output,
    file_name="RelatorioFMX_atualizado.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.success("Painel atualizado com todas as correções e melhorias! 🚀")


