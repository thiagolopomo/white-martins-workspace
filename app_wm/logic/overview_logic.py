#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import unicodedata
import pandas as pd


def _normalize(s):
    return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('ASCII').lower().strip()


def _find_col(df, name):
    """Finds column by normalized name, handles accents."""
    norm = _normalize(name)
    for c in df.columns:
        if _normalize(c) == norm:
            return c
    return None


def formatar_em_dinheiro(valor):
    try:
        valor_float = float(valor)
        return f"R$ {valor_float:,.2f}".replace('.', '#').replace(',', '.').replace('#', ',')
    except Exception:
        return valor


def gerar_overview_para_grupo(caminho_csv, pasta_overview):
    df = pd.read_csv(caminho_csv, sep=';', encoding='utf-8-sig', dtype=str)

    colunas_base = df.columns.tolist()

    # Find actual column names
    col_inverter = _find_col(df, 'Inverter Valor') or 'Inverter Valor'
    col_conciliado = _find_col(df, 'Conciliado') or 'Conciliado'
    col_fonte = _find_col(df, 'Fonte') or 'Fonte'
    col_periodo = _find_col(df, 'Periodo') or _find_col(df, 'Período') or 'Período'
    col_divisao_aa = _find_col(df, 'Divisao - AA') or _find_col(df, 'Divisão - AA') or 'Divisão - AA'
    col_tipo = _find_col(df, 'Tipo') or 'Tipo'

    group_cols = [col_fonte, col_periodo, col_divisao_aa, col_tipo]

    # Validate all group columns exist
    for gc in group_cols:
        if gc not in df.columns:
            raise ValueError(f"Coluna '{gc}' não encontrada. Colunas: {list(df.columns)}")

    df[col_inverter] = df[col_inverter].str.replace(',', '.').astype(float)

    df_conciliado = df[df[col_conciliado] == 'Sim'].copy()
    df_nao_conciliado = df[df[col_conciliado] != 'Sim'].copy()

    df_conciliado['Quantidade por Chave'] = 1
    quantidade_por_grupo = df_conciliado.groupby(
        group_cols
    )['Quantidade por Chave'].sum().reset_index(name='Quantidade')

    resumo = df_conciliado.groupby(
        group_cols, as_index=False
    )[col_inverter].sum()

    resumo = pd.merge(resumo, quantidade_por_grupo, on=group_cols, how='left')

    sort_cols = [col_divisao_aa, col_fonte, col_periodo, col_tipo]
    resumo = resumo.sort_values(by=sort_cols)

    resumo[col_conciliado] = 'Sim'

    for col in colunas_base:
        if col not in resumo.columns:
            resumo[col] = 'NULL'

    if 'Quantidade' not in colunas_base:
        colunas_base.append('Quantidade')

    resumo['Quantidade'] = resumo['Quantidade'].astype(str)

    final_cols = [c for c in colunas_base if c in resumo.columns]
    resumo = resumo[final_cols]

    resumo[col_inverter] = resumo[col_inverter].apply(formatar_em_dinheiro)

    df_nao_conciliado = df_nao_conciliado.fillna('NULL')
    df_nao_conciliado[col_conciliado] = 'Nao'
    df_nao_conciliado[col_inverter] = df_nao_conciliado[col_inverter].apply(formatar_em_dinheiro)

    overview_final = pd.concat([resumo, df_nao_conciliado], ignore_index=True)

    nome_base = os.path.basename(caminho_csv).replace('Recon_', '').replace('.csv', '')
    caminho_csv_saida = os.path.join(pasta_overview, f"Overview_{nome_base}.csv")
    overview_final.to_csv(caminho_csv_saida, sep=';', index=False, encoding='utf-8-sig')

    return caminho_csv_saida


def executar_overview(pasta_csvs, progress_callback=None):
    """
    Gera overviews para todos os CSVs de reconciliacao.
    Aceita pasta com CSVs ou caminho direto de um CSV.
    progress_callback(pct, msg)
    Retorna lista de arquivos gerados.
    """
    # Se for um arquivo CSV direto, usar seu diretorio
    if os.path.isfile(pasta_csvs) and pasta_csvs.lower().endswith('.csv'):
        pasta_real = os.path.dirname(pasta_csvs)
        arquivos_csv = [os.path.basename(pasta_csvs)]
    else:
        pasta_real = pasta_csvs
        arquivos_csv = [f for f in os.listdir(pasta_real)
                        if f.lower().startswith("recon_") and f.lower().endswith(".csv")]

    pasta_overview = os.path.join(pasta_real, "Overview")
    os.makedirs(pasta_overview, exist_ok=True)

    total = len(arquivos_csv)
    gerados = []

    if total == 0 and progress_callback:
        progress_callback(100, "Nenhum CSV de reconciliação encontrado (Recon_*.csv).")
        return gerados

    for idx, arquivo in enumerate(arquivos_csv):
        if progress_callback:
            progress_callback(int((idx / max(total, 1)) * 100), f"Gerando overview: {arquivo}")

        caminho = os.path.join(pasta_real, arquivo)
        try:
            saida = gerar_overview_para_grupo(caminho, pasta_overview)
            gerados.append(saida)
        except Exception as e:
            if progress_callback:
                progress_callback(int((idx / max(total, 1)) * 100), f"Erro: {arquivo} - {e}")

    if progress_callback:
        progress_callback(100, f"Concluído! {len(gerados)} overview(s) gerado(s).")

    return gerados
