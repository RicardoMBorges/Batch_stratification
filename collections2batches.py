# extratos_plantas_db.py

import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import os
import math
import unicodedata
import plotly.io as pio
pio.renderers.default = "notebook"

def remover_acentos(texto):
    if isinstance(texto, str):
        return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    return texto

def normalizar_colunas(df):
    df.columns = [remover_acentos(col) for col in df.columns]
    return df

def carregar_dados(caminho):
    df = pd.read_excel(caminho, sheet_name="Sheet1", engine="odf")
    return normalizar_colunas(df)

def buscar_por_apf(df, codigo_apf):
    return df[df['Registro da amostra APF'] == codigo_apf]

def listar_codigos_apf(df):
    return df['Registro da amostra APF'].dropna().unique()

def mostrar_dados_exemplo(caminho):
    df = carregar_dados(caminho)
    print("Total de registros carregados:", len(df))
    codigos_apf = listar_codigos_apf(df)
    print("Códigos de extrato (APF) encontrados:", codigos_apf[:10])
    if len(codigos_apf) > 0:
        codigo_exemplo = codigos_apf[0]
        print(f"\nDados para o código APF {codigo_exemplo}:")
        print(buscar_por_apf(df, codigo_exemplo))

def visualizar_apf_completo(df, codigo_apf):
    dados_apf = buscar_por_apf(df, codigo_apf)
    if dados_apf.empty:
        print(f"Nenhum dado encontrado para o código APF {codigo_apf}.")
    else:
        print(f"Dados completos para o código APF {codigo_apf}:")
        display(dados_apf)

def contar_amostras_por_familia(df):
    return df.dropna(subset=['Registro da amostra APF']).groupby('Família')['Registro da amostra APF'].nunique().sort_values(ascending=False)

def exportar_dados_apf(df, codigo_apf, caminho_saida):
    dados = buscar_por_apf(df, codigo_apf)
    dados.to_csv(caminho_saida, index=False)
    print(f"Dados exportados para {caminho_saida}")

def filtrar_e_reorganizar_apf(df):
    df_filtrado = df.dropna(subset=['Registro da amostra APF'])
    colunas = list(df_filtrado.columns)
    if 'Registro da amostra APF' in colunas:
        colunas.remove('Registro da amostra APF')
        colunas = ['Registro da amostra APF'] + colunas
        df_filtrado = df_filtrado[colunas]
    return df_filtrado

def distribuicao_por_familia(df):
    return df['Família'].value_counts().sort_values(ascending=False)

def distribuicao_por_genero_especie(df):
    return df['Espécies'].value_counts().sort_values(ascending=False)

def plot_bar_familia(df, output_dir="images"):
    os.makedirs(output_dir, exist_ok=True)
    contagem = distribuicao_por_familia(df)
    fig, ax = plt.subplots(figsize=(12,6))
    contagem.plot(kind='bar', ax=ax)
    ax.set_title('Distribuição por Família')
    ax.set_xlabel('Família')
    ax.set_ylabel('Número de Amostras')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "barplot_familia.png"))
    html_fig = px.bar(contagem.reset_index(), x=contagem.reset_index().columns[0], y=contagem.reset_index().columns[1], title='Distribuição por Família')
    html_path = os.path.join(output_dir, "barplot_familia.html")
    pio.write_html(html_fig, html_path)
    print(f"Gráficos salvos em {output_dir}")

def plot_bar_genero(df, output_dir="images"):
    os.makedirs(output_dir, exist_ok=True)
    contagem = distribuicao_por_genero_especie(df)
    fig, ax = plt.subplots(figsize=(12,6))
    contagem.plot(kind='bar', ax=ax)
    ax.set_title('Distribuição por Gênero/Espécies')
    ax.set_xlabel('Espécies')
    ax.set_ylabel('Número de Amostras')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "barplot_genero.png"))
    html_fig = px.bar(contagem.reset_index(), x=contagem.reset_index().columns[0], y=contagem.reset_index().columns[1], title='Distribuição por Gênero/Espécies')
    html_path = os.path.join(output_dir, "barplot_genero.html")
    pio.write_html(html_fig, html_path)
    print(f"Gráficos salvos em {output_dir}")

def plot_sunburst_familia_genero(df, output_dir="images"):
    os.makedirs(output_dir, exist_ok=True)
    df_plot = df.dropna(subset=['Família', 'Espécies']).copy()
    df_plot['count'] = 1
    fig = px.sunburst(df_plot, path=['Família', 'Espécies'], values='count',
                      title='Distribuição Sunburst por Família e Espécie')
    output_path = os.path.join(output_dir, "sunburst_familia_genero.html")
    fig.write_html(output_path)
    print(f"Gráfico salvo em {output_path}")

import os
import pandas as pd
from collections import defaultdict

def criar_batches_por_familia_genero(data, output_path, 
                                     samples_per_batch=80, 
                                     qc_samples=['Blank', 'QC_Inter_Batch', 'QC_Intra_Batch'],
                                     qc_structure=[3, 3, 2],
                                     batch_structure=[24, 24, 32],
                                     family_col='Família', genero_col='Gênero'):
    """
    Cria batches agrupando amostras preferencialmente por Família + Gênero, 
    com inserção de QCs conforme a estrutura definida.
    """

    if sum(batch_structure) != samples_per_batch:
        raise ValueError("A soma de batch_structure deve ser igual a samples_per_batch.")

    os.makedirs(output_path, exist_ok=True)
    batches = []
    batch_num = 1

    # Agrupa por Família + Gênero
    grouped = data.groupby([family_col, genero_col])
    group_sizes = grouped.size().sort_values(ascending=False)

    leftovers = pd.DataFrame()

    for (family, genero), _ in group_sizes.items():
        group = grouped.get_group((family, genero))
        
        while len(group) >= samples_per_batch:
            batch = group.iloc[:samples_per_batch]
            group = group.iloc[samples_per_batch:]
            final_batch = montar_batch_com_qcs(batch, batch_structure, qc_structure, qc_samples)
            final_batch['Batch'] = f'batch_{batch_num}'
            batches.append(final_batch)
            batch_num += 1

        # guarda sobras
        leftovers = pd.concat([leftovers, group])

    # Agrupa sobras por Família
    family_groups = leftovers.groupby(family_col)
    remaining = pd.DataFrame()

    for family, fam_group in family_groups:
        while len(fam_group) >= samples_per_batch:
            batch = fam_group.iloc[:samples_per_batch]
            fam_group = fam_group.iloc[samples_per_batch:]
            final_batch = montar_batch_com_qcs(batch, batch_structure, qc_structure, qc_samples)
            final_batch['Batch'] = f'batch_{batch_num}'
            batches.append(final_batch)
            batch_num += 1
        remaining = pd.concat([remaining, fam_group])

    # Junta todas as sobras para formar os últimos batches mistos
    while len(remaining) >= samples_per_batch:
        batch = remaining.iloc[:samples_per_batch]
        remaining = remaining.iloc[samples_per_batch:]
        final_batch = montar_batch_com_qcs(batch, batch_structure, qc_structure, qc_samples)
        final_batch['Batch'] = f'batch_{batch_num}'
        batches.append(final_batch)
        batch_num += 1

    # último batch incompleto (se houver)
    if not remaining.empty:
        final_batch = montar_batch_com_qcs(remaining, batch_structure, qc_structure, qc_samples)
        final_batch['Batch'] = f'batch_{batch_num}'
        batches.append(final_batch)

    # Salvar os batches
    for df in batches:
        batch_name = df['Batch'].iloc[0]
        df.to_csv(os.path.join(output_path, f'{batch_name}.csv'), index=False)

    print(f"{len(batches)} batches criados em '{output_path}' agrupando por Família e Gênero.")
    return batches


def montar_batch_com_qcs(batch, batch_structure, qc_structure, qc_samples):
    """
    Monta o DataFrame final de um batch com QCs intercalados.
    """
    final_batch = pd.DataFrame()
    start = 0

    for size, num_qcs in zip(batch_structure, qc_structure):
        # QCs intermediários
        qc_block = pd.DataFrame({
            'sampleid': qc_samples * num_qcs,
            'Tipo': ['QC'] * (len(qc_samples) * num_qcs)
        })
        final_batch = pd.concat([final_batch, qc_block], ignore_index=True)

        # Bloco de amostras reais
        sample_block = batch.iloc[start:start+size].copy()
        sample_block['Tipo'] = 'Amostra'
        final_batch = pd.concat([final_batch, sample_block], ignore_index=True)
        start += size

    # QCs finais
    qc_final = pd.DataFrame({
        'sampleid': qc_samples,
        'Tipo': ['QC'] * len(qc_samples)
    })
    final_batch = pd.concat([final_batch, qc_final], ignore_index=True)

    return final_batch

# Gera resumo da composição de famílias e gêneros por batch
def gerar_resumo_composicao(batches, output_path):
    resumo = []

    for df in batches:
        batch_name = df['Batch'].iloc[0]
        df_amostras = df[df['Tipo'] == 'Amostra']

        contagem = df_amostras.groupby(['Família', 'Gênero']).size().reset_index(name='Contagem')
        contagem['Batch'] = batch_name
        resumo.append(contagem)

    resumo_df = pd.concat(resumo, ignore_index=True)
    resumo_path = os.path.join(output_path, 'resumo_familia_genero_por_batch.csv')
    resumo_df.to_csv(resumo_path, index=False)
    return resumo_df
