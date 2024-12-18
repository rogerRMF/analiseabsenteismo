import streamlit as st
import pandas as pd


# Configuração da página
st.set_page_config(layout="wide", page_title="Painel de Presença e Habilidades")

# Barra lateral para upload e filtros
with st.sidebar:
    st.image(
        "https://automni.com.br/wp-content/uploads/2022/08/Logo-IDLogistics-PNG.svg",
        use_container_width=False, width=150,
    )
    st.title("Análise de Presença")
    uploaded_file = st.file_uploader("Coloque o seu arquivo Excel aqui", type="xlsx")

if uploaded_file is not None:
    # Leitura do arquivo Excel
    df = pd.read_excel(uploaded_file)

    # Limpeza dos nomes das colunas para remover espaços e caracteres especiais
    df.columns = df.columns.str.strip().str.replace(r"[^\w\s]", "", regex=True)

    # Renomeando a última coluna para 'STATUS'
    ultima_coluna = df.columns[-1]
    df = df.rename(columns={ultima_coluna: "STATUS"})

    # Definindo as colunas que serão usadas
    col_setor = "SETOR"
    col_nome = "NOME"
    col_status = "STATUS"

    # Verificação das colunas necessárias
    if col_setor in df.columns and col_nome in df.columns and col_status in df.columns:
        try:
            # Exibindo o painel de informações
            st.title("Relatório de Absenteísmo")

            # Configuração de filtros
            with st.sidebar:
                # Filtro por setor
                distinct_sectors = df[col_setor].unique().tolist()
                sector_selected = st.selectbox("Selecione o SETOR:", ["Todos"] + distinct_sectors)

                # Filtrando os funcionários com base no setor selecionado
                if sector_selected != "Todos":
                    df_filtered_by_sector = df[df[col_setor] == sector_selected]
                else:
                    df_filtered_by_sector = df

                # Filtro por nome do funcionário
                distinct_employees = df_filtered_by_sector[col_nome].unique().tolist()
                employee_selected = st.selectbox("Selecione o Funcionário:", ["Todos"] + distinct_employees)

            # Filtrando os dados pelo setor e/ou funcionário
            if sector_selected != "Todos":
                df_sector_filtered = df[df[col_setor] == sector_selected]
            else:
                df_sector_filtered = df

            if employee_selected != "Todos":
                df_filtered = df_sector_filtered[df_sector_filtered[col_nome] == employee_selected]
            else:
                df_filtered = df_sector_filtered

            # Calculando o total geral de "STATUS" com valor "PRESENTE"
            total_geral_presentes = df[df[col_status] == "PRESENTE"][col_status].count()

            # Calculando o total de "STATUS" com valor "PRESENTE" para o setor selecionado
            total_present = df_sector_filtered[df_sector_filtered[col_status] == "PRESENTE"][col_status].count()

            # Layout para exibição de informações gerais
            st.markdown(f"""
                <div style="background-color: #dff0d8; padding: 10px; border-radius: 5px;">
                    <h2 style="color: green; text-align: center;">Total Geral de Presentes</h2>
                    <h1 style="color: green; text-align: center;">{total_geral_presentes}</h1>
                </div>
            """, unsafe_allow_html=True)

            # Exibição do total de presentes no setor selecionado
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Total de Presentes no SETOR Selecionado")
                st.write(f"Setor: **{sector_selected}**")
                st.metric("Total de Presentes", total_present)

            # Exibindo habilidades do funcionário selecionado
            if employee_selected != "Todos":
                with col2:
                    st.subheader(f"Habilidades do Funcionário: {employee_selected}")
                    habilidades_cols = ["BANCADA", "PICKING", "PTL", "UBICAÇÃO"]
                    habilidades = df_filtered[df_filtered[col_nome] == employee_selected][habilidades_cols]
                    st.dataframe(habilidades, use_container_width=True)

            # Exibindo totais por setor em caixas de texto separadas
            st.subheader("Totais de Presentes por SETOR")
            setores = df[col_setor].unique()
            colunas = st.columns(len(setores))

            for i, setor in enumerate(setores):
                total_setor = df[(df[col_setor] == setor) & (df[col_status] == "PRESENTE")][col_status].count()
                with colunas[i]:
                    st.markdown(f"""
                        <div style="background-color: #d9edf7; padding: 5px; border-radius: 5px; text-align: center; font-size: 12px;">
                            <strong>{setor}</strong><br>
                            <span style="color: green; font-size: 16px;">{total_setor}</span>
                        </div>
                    """, unsafe_allow_html=True)

            # Exibindo uma prévia do DataFrame carregado na parte inferior
            st.subheader("Dados Carregados")
            st.dataframe(df.head(), use_container_width=True)

        except KeyError as e:
            st.error(f"Erro: Coluna ausente no arquivo carregado. Detalhes: {e}")
    else:
        st.error("Erro: O arquivo carregado não contém as colunas necessárias: 'SETOR', 'NOME' e 'STATUS'. Verifique o arquivo.")

else:
    st.info("Por favor, faça upload de um arquivo Excel para começar a análise.")
