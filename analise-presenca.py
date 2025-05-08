import streamlit as st
import pandas as pd
import plotly.express as px

import streamlit as st
# Configuração da página
st.set_page_config(layout="wide", page_title="Painel de Presença e Habilidades")
st.markdown(
    """
    <div style="text-align: left; font-size: 10px;">
        Copyright ©-2025 Direitos Autorais Desenvolvedor Rogério Ferreira
    </div>
    """,
    unsafe_allow_html=True
)
# Configuração da página
#st.set_page_config(layout="wide", page_title="Personalizar Fundo")

# CSS para alterar a cor de fundo
def set_background_color(color):
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: {color};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Exemplo de uso: escolhendo a cor de fundo
cor_escolhida = st.sidebar.color_picker("Escolha uma cor de fundo", "#f6f6f8")  # Branco como padrão
set_background_color(cor_escolhida)

# Barra lateral para upload e navegação
with st.sidebar:
    st.image(
        "https://automni.com.br/wp-content/uploads/2022/08/Logo-IDLogistics-PNG.svg",
        use_container_width=False, width=150,
    )
    st.title("Navegue pelas páginas")
    menu = st.radio("", ["Relatório de Absenteísmo", "Totais de Habilitações", "Gráficos Interativos", "Painel ABS", "Suporte"])
    uploaded_file = st.file_uploader("Coloque o seu arquivo Excel aqui", type="xlsx")

if uploaded_file is not None:
    # Leitura do arquivo Excel
    df = pd.read_excel(uploaded_file)

    # Limpeza dos nomes das colunas para remover espaços e caracteres especiais
    df.columns = df.columns.str.strip().str.replace(r"[^\w\s]", "", regex=True)

    # Alterar os nomes das colunas 'falta' para 'ausente' e 'dsr' para 'folga escala'
   # df = df.rename(columns={"FALTA": "AUSENTE", "DSR": "FOLGA ESCALA"})
    # Renomeando a última coluna para 'STATUS'
    ultima_coluna = df.columns[-1]
    df = df.rename(columns={ultima_coluna: "DIARIO"})

    # Definindo as colunas que serão usadas
    col_setor = "SETOR"
    col_nome = "NOME"
    col_status = "DIARIO"
    col_bancada = "BANCADA"
    col_picking = "PICKING"
    col_ptl = "PTL"
    col_ubicacao = "UBICAÇÃO"

    # Navegação entre as páginas
    if menu == "Relatório de Absenteísmo":
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
                <div style="background-color: #00417b; padding: 10px; border-radius: 100px;">
                    <h2 style="color: #ffffff; text-align: center; font-size: 50px">Total Geral de Presentes</h2>
                    <h1 style="color: #ffffff; text-align: center; font-size: 50px">{total_geral_presentes}</h1>
                </div>
            """, unsafe_allow_html=True)

            # Exibição do total de presentes no setor selecionado
            col1, col2 = st.columns(2)

            with col1:
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
                            <div style="background-color: #00417b; padding: 10px; border-radius: 20px; text-align: center;">
                            <strong style ="color: #FFFFFF; font-size: 18px;">{setor}</strong><br>
                            <span style="color: #FFFFFF; font-size: 24px; font-weight: bold;">{total_setor}</span>
                            </div>
                 """, unsafe_allow_html=True)

        except KeyError as e:
            st.error(f"Erro: Coluna ausente no arquivo carregado. Detalhes: {e}")

    elif menu == "Totais de Habilitações":
        st.subheader("Totais de Habilitações")
        colunas_habilidades = [col_bancada, col_picking, col_ptl, col_ubicacao]
        colunas_exibicao = st.columns(len(colunas_habilidades))

        for i, coluna in enumerate(colunas_habilidades):
            if coluna in df.columns:
                # Condição para contar "HABILITADO" e "PRESENTE"
                total_habilitado_presente = df[(df[coluna] == "HABILITADO") & (df['DIARIO'] == 'PRESENTE')][coluna].count()
                # Condição para contar   "NÃO HABILITADO" e "PRESENTE"              
                total_nao_habilitado_presente = df[(df[coluna] == "NÃO HABILITADO") & (df["DIARIO"] == 'PRESENTE')][coluna].count()

                
                
                with colunas_exibicao[i]:
                    #st.metric(f"HABILITADO ({coluna})", total_habilitado)
                    #st.metric(f"NÃO HABILITADO ({coluna})", total_nao_habilitado)
                #with colunas_exibicao[i]:
                    st.markdown(f"""
                                <div style="background-color: #00418b; padding: 10px; border-radius: 100px;">
                                <h2 style="color: #ffffff; text-align: center;">{coluna}</h2>
                                <p style="color: #ffffff; text-align: center;">HABILITADO: {total_habilitado_presente}</p>
                                <p style="color: #ffffff; text-align: center;">NÃO HABILITADO: {total_nao_habilitado_presente}</p>
                                 </div>
                    """, unsafe_allow_html=True)   
                    
            elif menu == "Totais de Habilitações":
                st.subheader("Totais de Habilitações")
                # ...
                
    elif menu == "Gráficos Interativos":
        
        # Substituir o hífen '-' por 'INTEGRAÇÃO' na coluna STATUS
        df[col_status] = df[col_status].replace("-", "INTEGRAÇÃO")
        
        status_counts = df[col_status].value_counts().reset_index()
        status_counts.columns = ["STATUS", "Quantidade"]

        fig_line = px.line(
            status_counts,
            x="STATUS",
            y="Quantidade",
            markers=True,
            text="Quantidade",
            title="Análise de Absenteísmo por STATUS",
            labels={"Quantidade": "Total", "STATUS": "Tipo de Status"}
        )
        
        fig_line.update_traces(
             textposition="top center",
             texttemplate="<span style='color:#04178b; fonte-size: 14px;'>%{x}</span><br><span style='color:green; fonte-size: 15px;'>%{y}</span>",
             hovertemplate="<br><b>%{x}</b><br>Total: %{y}",  # Hover text com formatação básica
             textfont=dict(size=12)
        )
        fig_line.update_traces(textposition="top center")
        fig_line.update_layout(
            showlegend=False,
            xaxis_title="Status",
            yaxis_title="Quantidade",
            plot_bgcolor="white",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=False),
        )

        st.plotly_chart(fig_line, use_container_width=True)

    elif menu == "Painel ABS":
        st.title("Painel de ABS e Quadro Ativo")
        total_ocorrencia = df[df[col_status] == "OCORRÊNCIA"].shape[0]
        total_falta = df[df[col_status] == "FALTA"].shape[0]
        total_afastamento_medico = df[df[col_status] == "AFASTAMENTO MÉDICO"].shape[0]
        total_presente = df[df[col_status] == "PRESENTE"].shape[0]
        total_atestado_medico = df[df[col_status] == "ATESTADO MÉDICO"].shape[0]

        total_abs = total_ocorrencia + total_falta + total_atestado_medico
        quadro_ativo = total_presente + total_ocorrencia + total_falta + total_atestado_medico 
        porcentagem_abs = (total_abs / quadro_ativo) * 100 if quadro_ativo > 0 else 0

        col1, col2, col3, col4, col5, = st.columns(5)
        def create_metric_card(label, value, color="white"):
            st.markdown(f"""
            <div style="background-color: #00418b; padding: 10px; border-radius: 10px; text-align: center;">
                 <p style="color: {color}; font-size: 18px;">{label}</p>
                 <h2 style="color: {color}; font-size: 24px;">{value}</h2>
            </div>
            """, unsafe_allow_html=True)   
            
        col1.metric("PRESENTE", total_presente)
        col2.metric("OCORRÊNCIA", total_ocorrencia)
        col3.metric("FALTAS", total_falta)
        col4.metric("ATESTADO MÉDICO",total_atestado_medico)
        col5.metric("AFASTAMENTO MÉDICO", total_afastamento_medico)
        st.markdown(f"""
        <div style="background-color: #f0f0f0; padding: 10px; border-radius: 100px; text-align: center;">
             <p style="color: #00418b; font-size: 16px;">Porcentagem ABS/Quadro Ativo</p>
             <h2 style="color: red; font-size: 28px;">{porcentagem_abs:.2f}%</h2>
        </div>
        """, unsafe_allow_html=True) 
               
        # Filtrar "MO Direta" e "MO Indireta"
        df_mo_direta = df[df["VÍNCULO"] == "MO Direta"]
        df_mo_indireta = df[df["VÍNCULO"] == "MO Indireta"]

        # Categorias para análise
        categorias = [
            "PRESENTE",
            "FALTA",
            "ATESTADO MÉDICO",
            "DSR",
            "AFASTAMENTO MÉDICO",
            "FÉRIAS",
            "OCORRÊNCIA",
        ]

        # Calcular totais por categoria
        totais_direta = {cat: df_mo_direta[df_mo_direta["DIARIO"] == cat].shape[0] for cat in categorias}
        totais_indireta = {cat: df_mo_indireta[df_mo_indireta["DIARIO"] == cat].shape[0] for cat in categorias}
        totais_gerais = {cat: totais_direta[cat] + totais_indireta[cat] for cat in categorias}

        # Totais gerais
        total_mo_direta = sum(totais_direta.values())
        total_mo_indireta = sum(totais_indireta.values())
        total_geral_tudo = total_mo_direta + total_mo_indireta

        # Porcentagens absolutas
        porcentagens = {
            cat: (totais_gerais[cat] / total_geral_tudo * 100) if total_geral_tudo > 0 else 0
            for cat in categorias
        }

        # Reorganizar a tabela para exibição no formato solicitado
        df_resultados = pd.DataFrame({
            "Indicador": ["MO Direta", "MO Indireta", "Total Geral", "Porcentagem (%)"],
            **{cat: [
                totais_direta[cat],
                totais_indireta[cat],
                totais_gerais[cat],
                f"{porcentagens[cat]:.2f}%",
            ] for cat in categorias},
        })

        # Exibir a tabela
        st.subheader("Resumo por Categoria")
        st.table(df_resultados)
    
 
    elif menu == "Suporte":
        if st.sidebar.radio("Entre em contato:", ["Não", "Sim"]) == "Sim":
            link_whatsapp = "https://wa.me/5511954678363?text=Olá,%20Rogério.%20Preciso%20de%20suporte."
            st.markdown(f"""
            <a href="{link_whatsapp}" target="_blank">
                <button style="background-color: #25D366; color: white; padding: 10px 20px; border-radius: 5px; font-size: 16px;">
                    Falar com Rogério (WhatsApp)
                </button>
            </a>
            """, unsafe_allow_html=True)

else:
    st.info("Por favor, faça upload de um arquivo Excel para começar a análise.")
# Botão para suporte