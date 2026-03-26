#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pipeline completo de reconciliacao White Martins.
4 etapas: CSV->Parquet, Consolidar, Conciliar, Exportar CSV.
"""

import os
import re
import csv
import unicodedata
from pathlib import Path

import polars as pl


# =============== ETAPA 1: CSV -> PARQUET ===============

def _normalize(s):
    return unicodedata.normalize('NFKD', s).encode('ASCII', 'ignore').decode('ASCII').lower().strip()


def extrair_info(nome):
    """
    Extrai empresa, periodo e tipo do nome do arquivo.
    Formatos suportados:
      - "Razão 012026 - Gilda"  → empresa=gilda, periodo=012026, tipo=razao
      - "Fiscal 012026 - Gilda" → empresa=gilda, periodo=012026, tipo=fiscal
      - "Razao Grupo 1 2024"    → empresa=grupo_1, periodo=2024, tipo=razao (legado)
    Retorna (identificador, tipo) onde identificador = "empresa_periodo".
    """
    nome_n = _normalize(nome)

    # Detecta tipo
    tipo = None
    if 'razao' in nome_n:
        tipo = 'razao'
    elif 'fiscal' in nome_n:
        tipo = 'fiscal'

    # Formato novo: "Razão 012026 - Gilda" ou "Fiscal 012026 - Gilda"
    # Padrão: (razao|fiscal) MMAAAA - EMPRESA
    match_novo = re.search(r'(?:razao|fiscal)\s+(\d{6})\s*-\s*(\w+)', nome_n)
    if match_novo:
        periodo = match_novo.group(1)
        empresa = match_novo.group(2).strip()
        return f"{empresa}_{periodo}", tipo

    # Formato legado: "grupo X YYYY"
    match_legado = re.search(r'grupo[\s_-]*(\d+)[\s_-]*(\d{4})', nome_n)
    if match_legado:
        return f"grupo_{match_legado.group(1)}_{match_legado.group(2)}", tipo

    return None, tipo


def etapa_csv_para_parquet(pasta_csv, progress_callback=None):
    pasta_csv = Path(pasta_csv)
    pasta_parquet = pasta_csv / "parquet"
    pasta_parquet.mkdir(parents=True, exist_ok=True)

    arquivos = list(pasta_csv.glob("*.csv"))
    total = len(arquivos)

    for idx, arquivo in enumerate(arquivos):
        if progress_callback:
            progress_callback(int((idx / max(total, 1)) * 100), f"Convertendo: {arquivo.name}")

        grupo, tipo = extrair_info(arquivo.stem)
        if not grupo or not tipo:
            continue

        try:
            df = pl.read_csv(arquivo, separator=";", truncate_ragged_lines=True, infer_schema_length=0)
            df = df.with_columns([pl.col(col).cast(pl.Utf8) for col in df.columns])
            df = df.with_columns(pl.lit(tipo.upper()).alias("FONTE"))
            destino = pasta_parquet / f"{grupo}_{tipo}.parquet"
            df.write_parquet(destino, compression="zstd")
        except Exception as e:
            if progress_callback:
                progress_callback(int((idx / max(total, 1)) * 100), f"Erro: {arquivo.name} - {e}")

    if progress_callback:
        progress_callback(100, "Etapa 1 concluida!")

    return str(pasta_parquet)


# =============== ETAPA 2: CONSOLIDAR ===============

COLUNAS_RAZAO = [
    "Index", "Fonte", "Período", "Tipo", "Explicaçao", "Empresa",
    "Conta do Razão", "Centro de lucro", "Divisão", "Sociedade parceira",
    "Partida individual", "Tipo partida indiv.", "Mont.moeda empresa",
    "Referência 1", "PI criada por", "ID de referência de documento",
    "Data de lançamento", "Dt.part.individual", "Está estornando", "Estornado",
    "Divisão - AA", "Tipo partida indiv. - AA", "Valor - AA", "NF - AA", "SÉRIE - AA",
    "Txt.it.partida indv."
]

COLUNAS_SOMENTE_FISCAL = [
    "Chave Eletrônica", "Código CFOP", "Modelo/Espécie", "Tipo de Nota",
    "UF Nota Fiscal", "UF Filial", "Código do Participante",
    "CNPJ_CPF Participante", "Descrição da Situação do Documento", "OBS",
    "Descrição do Item", "ICMS - Valor do Imposto", "FCP ICMS - Valor do Imposto",
    "Observação", "Natureza da Operação", "Numero do Titulo"
]

MAPEAMENTO_FISCAL_PARA_RAZAO = {
    "Index": "Index",
    "Fonte": "Fonte",
    "Período": "Período",
    "Entrada/Saída": "Tipo",
    "Empresa": "Empresa",
    "__montante_icms_total__": ["Mont.moeda empresa", "Valor - AA"],
    "Usuário": "PI criada por",
    "Número NF": "NF - AA",
    "Data Entrada/Saída": "Data de lançamento",
    "Data Emissão": "Dt.part.individual",
    "Série": "SÉRIE - AA",
    "Numero do Titulo": "Partida individual",
    "DOCNUM / NF_ID": "ID de referência de documento",
    "Filial": "Divisão - AA",
}


def somar_valores_br(icms, fcp):
    try:
        icms_val = float(str(icms).replace(".", "").replace(",", "."))
    except Exception:
        icms_val = 0.0
    try:
        fcp_val = float(str(fcp).replace(".", "").replace(",", "."))
    except Exception:
        fcp_val = 0.0
    total = icms_val + fcp_val
    total_str = str(total).replace(".", ",")
    if total_str.endswith(",0"):
        total_str = total_str.rstrip("0").rstrip(",")
    return total_str


def _find_col(df, name):
    """Tenta encontrar coluna por nome exato ou similar (sem acentos)."""
    if name in df.columns:
        return name
    name_norm = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII').lower()
    for col in df.columns:
        col_norm = unicodedata.normalize('NFKD', col).encode('ASCII', 'ignore').decode('ASCII').lower()
        if col_norm == name_norm:
            return col
    return None


def obter_pares(pasta):
    pasta = Path(pasta)
    arquivos = list(pasta.glob("*_*.parquet"))
    pares = {}
    for arq in arquivos:
        # Novo formato: empresa_periodo_(razao|fiscal).parquet
        # Legado: grupo_X_YYYY_(razao|fiscal).parquet
        match = re.match(r"(.+)_(razao|fiscal)\.parquet", arq.name)
        if match:
            chave, tipo = match.groups()
            if chave not in pares:
                pares[chave] = {}
            pares[chave][tipo] = arq
    return {k: v for k, v in pares.items() if "razao" in v and "fiscal" in v}


def etapa_consolidar(pasta_parquet, progress_callback=None):
    pasta = Path(pasta_parquet)
    pasta_consolidado = pasta / "Consolidado"
    pasta_consolidado.mkdir(exist_ok=True)

    pares = obter_pares(pasta)
    total = len(pares)

    for idx, (chave, arquivos) in enumerate(pares.items()):
        if progress_callback:
            progress_callback(int((idx / max(total, 1)) * 100), f"Consolidando: {chave}")

        df_razao = pl.read_parquet(arquivos["razao"])
        df_fiscal = pl.read_parquet(arquivos["fiscal"])

        df_razao = df_razao.rename({col: col.strip() for col in df_razao.columns})
        df_fiscal = df_fiscal.rename({col: col.strip() for col in df_fiscal.columns})

        icms_col = _find_col(df_fiscal, "ICMS - Valor do Imposto")
        fcp_col = _find_col(df_fiscal, "FCP ICMS - Valor do Imposto")

        if icms_col and fcp_col:
            df_fiscal = df_fiscal.with_columns([
                pl.struct([icms_col, fcp_col]).map_elements(
                    lambda x: somar_valores_br(x[icms_col], x[fcp_col]),
                    return_dtype=pl.Utf8
                ).alias("__montante_icms_total__")
            ])
        else:
            df_fiscal = df_fiscal.with_columns([pl.lit("NULL").alias("__montante_icms_total__")])

        todas_colunas = COLUNAS_RAZAO + COLUNAS_SOMENTE_FISCAL
        dados_fiscal_dict = {}

        for col in todas_colunas:
            origem_encontrada = None
            for origem, destino in MAPEAMENTO_FISCAL_PARA_RAZAO.items():
                if isinstance(destino, list):
                    if col in destino:
                        origem_encontrada = origem
                        break
                elif destino == col:
                    origem_encontrada = origem
                    break

            real_col = _find_col(df_fiscal, origem_encontrada) if origem_encontrada else None
            if real_col:
                dados_fiscal_dict[col] = df_fiscal[real_col]
            else:
                real_col2 = _find_col(df_fiscal, col)
                if real_col2:
                    dados_fiscal_dict[col] = df_fiscal[real_col2]
                else:
                    dados_fiscal_dict[col] = [None] * df_fiscal.height

        df_fiscal_formatado = pl.DataFrame(dados_fiscal_dict)

        for col in COLUNAS_SOMENTE_FISCAL:
            real = _find_col(df_razao, col)
            if not real:
                df_razao = df_razao.with_columns(pl.lit(None).alias(col))

        # Alinha colunas
        for col in todas_colunas:
            real = _find_col(df_razao, col)
            if real and real != col:
                df_razao = df_razao.rename({real: col})

        cols_razao_existentes = [c for c in todas_colunas if c in df_razao.columns]
        for c in todas_colunas:
            if c not in df_razao.columns:
                df_razao = df_razao.with_columns(pl.lit(None).alias(c))

        df_razao = df_razao.select(todas_colunas)
        df_fiscal_formatado = df_fiscal_formatado.select(todas_colunas)

        df_consolidado = pl.concat([df_razao, df_fiscal_formatado], how="vertical_relaxed")
        df_consolidado = df_consolidado.with_columns([
            pl.col(col).cast(pl.Utf8).fill_null("NULL") for col in df_consolidado.columns
        ])

        df_consolidado.write_parquet(pasta_consolidado / f"{chave}_consolidado.parquet", compression="zstd")

    if progress_callback:
        progress_callback(100, "Etapa 2 concluida!")

    return str(pasta_consolidado)


# =============== ETAPA 3: CONCILIAR ===============

def etapa_conciliar(pasta_consolidado, progress_callback=None):
    pasta = Path(pasta_consolidado)
    pasta_saida = pasta / "Conciliado"
    pasta_saida.mkdir(exist_ok=True)

    arquivos = [f for f in os.listdir(pasta) if f.endswith(".parquet")]
    total = len(arquivos)

    for idx, nome_arquivo in enumerate(arquivos):
        if progress_callback:
            progress_callback(int((idx / max(total, 1)) * 100), f"Conciliando: {nome_arquivo}")

        caminho_arquivo = os.path.join(pasta, nome_arquivo)
        nome_base = os.path.splitext(nome_arquivo)[0]
        caminho_saida = os.path.join(pasta_saida, f"{nome_base}_conciliado.parquet")

        df = pl.read_parquet(caminho_arquivo)

        # Normaliza NF - AA
        nf_col = _find_col(df, "NF - AA")
        if nf_col:
            df = df.with_columns([
                pl.when(
                    pl.col(nf_col).is_not_null() &
                    pl.col(nf_col).cast(pl.Utf8).str.contains(r"^\d+$")
                ).then(
                    pl.col(nf_col).cast(pl.Utf8).str.replace(r"^0+", "").str.replace_all(r"^$", "0")
                ).otherwise(
                    pl.col(nf_col).cast(pl.Utf8)
                ).alias(nf_col)
            ])

        # Marca CFOPs excluir
        cfops_excluir = ["1949", "2949", "5949", "6949", "3949", "7949",
                         "1904", "2904", "3904", "5904", "6904", "7904"]

        obs_col = _find_col(df, "OBS")
        if not obs_col:
            df = df.with_columns(pl.lit("").alias("OBS"))
            obs_col = "OBS"

        cfop_col = _find_col(df, "Codigo CFOP") or _find_col(df, "Código CFOP")
        if cfop_col:
            df = df.with_columns([
                pl.when(pl.col(cfop_col).cast(pl.Utf8).is_in(cfops_excluir))
                .then(pl.lit("NÃO INCLUIR"))
                .otherwise(pl.col(obs_col))
                .alias(obs_col)
            ])

        df = df.with_columns([pl.col(obs_col).str.to_uppercase().alias(obs_col)])

        # Mont.moeda empresa seguro
        mont_col = _find_col(df, "Mont.moeda empresa")
        if mont_col:
            df = df.with_columns(
                pl.col(mont_col)
                .fill_null("0,00")
                .str.strip_chars()
                .str.replace_all(r"^\s*$", "0,00")
                .str.replace_all("NULL", "0,00")
                .str.replace_all(r"^-$", "0,00")
                .str.replace_all(r"\.", "")
                .str.replace_all(",", ".")
                .cast(pl.Float64, strict=False)
                .fill_null(0.0)
                .alias(mont_col)
            )

        # Cria colunas auxiliares
        fonte_col = _find_col(df, "Fonte")
        tipo_col = _find_col(df, "Tipo")

        df = df.with_columns([
            pl.when((pl.col(fonte_col) == "Fiscal") & (pl.col(tipo_col) == "Entrada"))
            .then(-pl.col(mont_col))
            .otherwise(pl.col(mont_col))
            .alias("Inverter Valor"),
            pl.col(mont_col).abs().alias("Abs")
        ])

        df = df.with_columns([
            pl.lit("Não").alias("Conciliado"),
            pl.lit("NULL").alias("Chave")
        ])

        div_col = _find_col(df, "Divisao - AA") or _find_col(df, "Divisão - AA")
        nf_col = _find_col(df, "NF - AA")

        df = df.with_columns([
            (pl.col(tipo_col).fill_null("NULL").cast(pl.Utf8) + "_" +
             pl.col(div_col).fill_null("NULL").cast(pl.Utf8) + "_" +
             pl.col(nf_col).fill_null("NULL").cast(pl.Utf8))
            .alias("Chave_1"),
        ])

        df = df.with_columns([
            (pl.col("Chave_1") + "_" +
             pl.col("Abs").round(2).cast(pl.Utf8).str.replace_all(r"\.", ","))
            .alias("Chave_2")
        ])

        tipo_part_col = _find_col(df, "Tipo partida indiv. - AA")
        filtros_partida = ["RC", "SA", "MA"]

        if tipo_part_col:
            df = df.with_columns([
                pl.when(
                    (pl.col(fonte_col) == "Razão") &
                    (pl.col(tipo_part_col).is_in(filtros_partida))
                ).then(
                    pl.col(div_col).fill_null(pl.lit("NULL")).cast(pl.Utf8) + "_" +
                    pl.col(nf_col).fill_null(pl.lit("NULL")).cast(pl.Utf8)
                ).otherwise(pl.lit("NULL"))
                .alias("Chave_3")
            ])
        else:
            df = df.with_columns([pl.lit("NULL").alias("Chave_3")])

        df_nao_conciliavel = df.filter(pl.col(obs_col).str.contains("NÃO INCLUIR"))
        df_conciliavel = df.filter(~pl.col(obs_col).str.contains("NÃO INCLUIR"))

        for chave in ["Chave_1", "Chave_2", "Chave_3"]:
            df_nao_conciliado = df_conciliavel.filter(
                (pl.col("Conciliado") != "Sim") &
                (~pl.col(chave).str.contains("NULL")) &
                (~pl.col(obs_col).str.contains("NÃO INCLUIR"))
            )

            soma = (
                df_nao_conciliado
                .group_by(chave)
                .agg(pl.col("Inverter Valor").sum().alias("soma"))
                .with_columns([pl.col("soma").abs().lt(1e-6).alias("conciliado")])
            )

            df_conciliavel = df_conciliavel.join(soma, on=chave, how="left")

            df_conciliavel = df_conciliavel.with_columns([
                pl.when(
                    (pl.col("conciliado") == True) &
                    (pl.col("Conciliado") != pl.lit("Sim")) &
                    (~pl.col(obs_col).str.contains("NÃO INCLUIR"))
                ).then(pl.lit("Sim"))
                .otherwise(pl.col("Conciliado"))
                .alias("Conciliado"),

                pl.when(
                    (pl.col("conciliado") == True) &
                    (pl.col("Conciliado") != pl.lit("Sim")) &
                    (~pl.col(obs_col).str.contains("NÃO INCLUIR"))
                ).then(pl.lit(chave))
                .otherwise(pl.col("Chave"))
                .alias("Chave")
            ]).drop("soma", "conciliado")

        df_final = pl.concat([df_conciliavel, df_nao_conciliavel])

        df_final = df_final.with_columns([
            pl.col(mont_col).round(2).cast(pl.Utf8).str.replace_all(r"\.", ",").alias(mont_col),
            pl.col("Inverter Valor").round(2).cast(pl.Utf8).str.replace_all(r"\.", ",").alias("Inverter Valor"),
            pl.col("Abs").round(2).cast(pl.Utf8).str.replace_all(r"\.", ",").alias("Abs"),
        ])

        df_final.write_parquet(caminho_saida, compression="snappy")

    if progress_callback:
        progress_callback(100, "Etapa 3 concluida!")

    return str(pasta_saida)


# =============== ETAPA 4: EXPORTAR CSV ===============

def _extrair_nome_csv_de_parquet(stem):
    """
    Converte nome do parquet conciliado em nome amigável para CSV.
    Ex: 'gilda_012026_consolidado_conciliado' → 'Recon_Gilda_012026.csv'
        'grupo_1_2024_consolidado_conciliado' → 'Recon_Grupo_1_2024.csv' (legado)
    """
    # Remove sufixos de pipeline
    base = stem.replace("_consolidado_conciliado", "").replace("_consolidado", "").replace("_conciliado", "")

    # Legado: grupo_X_YYYY
    match_legado = re.match(r"grupo_(\d+)_(\d{4})", base)
    if match_legado:
        return f"Recon_Grupo_{match_legado.group(1)}_{match_legado.group(2)}.csv"

    # Novo: empresa_periodo (ex: gilda_012026)
    match_novo = re.match(r"(\w+)_(\d{6})", base)
    if match_novo:
        empresa = match_novo.group(1).capitalize()
        periodo = match_novo.group(2)
        return f"Recon_{empresa}_{periodo}.csv"

    return base + ".csv"


def etapa_exportar_csv(pasta_conciliado, progress_callback=None):
    pasta = Path(pasta_conciliado)
    pasta_csv = pasta / "csvs"
    pasta_csv.mkdir(exist_ok=True)

    arquivos = list(pasta.glob("*.parquet"))
    total = len(arquivos)

    for idx, parquet_file in enumerate(arquivos):
        if progress_callback:
            progress_callback(int((idx / max(total, 1)) * 100), f"Exportando: {parquet_file.name}")

        df = pl.read_parquet(parquet_file)
        nome_csv = _extrair_nome_csv_de_parquet(parquet_file.stem)
        csv_file = pasta_csv / nome_csv

        with open(csv_file, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f, delimiter=';', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(df.columns)
            for row in df.iter_rows():
                writer.writerow(row)

    if progress_callback:
        progress_callback(100, "Etapa 4 concluida!")

    return str(pasta_csv)


# =============== PIPELINE COMPLETO ===============

def executar_recon_completa(pasta_csv, progress_callback=None):
    """
    Executa o pipeline completo de reconciliacao a partir de uma pasta de CSVs.
    progress_callback(pct, msg) para reportar progresso geral.
    Retorna caminho da pasta de CSVs finais.
    """
    def sub_progress(etapa, total_etapas, pct_local, msg):
        if progress_callback:
            base = int((etapa / total_etapas) * 100)
            faixa = int((1 / total_etapas) * 100)
            pct_global = base + int((pct_local / 100) * faixa)
            progress_callback(min(pct_global, 100), f"[Etapa {etapa + 1}/{total_etapas}] {msg}")

    pasta_parquet = etapa_csv_para_parquet(
        pasta_csv,
        progress_callback=lambda p, m: sub_progress(0, 4, p, m)
    )

    pasta_consolidado = etapa_consolidar(
        pasta_parquet,
        progress_callback=lambda p, m: sub_progress(1, 4, p, m)
    )

    pasta_conciliado = etapa_conciliar(
        pasta_consolidado,
        progress_callback=lambda p, m: sub_progress(2, 4, p, m)
    )

    pasta_csvs = etapa_exportar_csv(
        pasta_conciliado,
        progress_callback=lambda p, m: sub_progress(3, 4, p, m)
    )

    if progress_callback:
        progress_callback(100, "Pipeline completo finalizado!")

    return pasta_csvs


def executar_recon_arquivos(arquivo_razao, arquivo_fiscal, pasta_saida, progress_callback=None):
    """
    Executa o pipeline de reconciliacao a partir de dois arquivos (Razao + Fiscal).
    Converte ambos para Parquet, consolida, concilia e exporta CSV.

    Args:
        arquivo_razao: caminho do CSV Razao
        arquivo_fiscal: caminho do CSV Fiscal
        pasta_saida: pasta de destino para os resultados
        progress_callback: funcao(pct, msg)

    Returns:
        caminho da pasta de CSVs finais
    """
    os.makedirs(pasta_saida, exist_ok=True)
    pasta_parquet = os.path.join(pasta_saida, "parquet")
    os.makedirs(pasta_parquet, exist_ok=True)

    def sub_progress(etapa, total_etapas, pct_local, msg):
        if progress_callback:
            base = int((etapa / total_etapas) * 100)
            faixa = int((1 / total_etapas) * 100)
            pct_global = base + int((pct_local / 100) * faixa)
            progress_callback(min(pct_global, 100), f"[Etapa {etapa + 1}/{total_etapas}] {msg}")

    # Etapa 1: Converter os dois arquivos para Parquet
    if progress_callback:
        progress_callback(0, "[Etapa 1/4] Convertendo arquivos para Parquet...")

    # Determina identificador a partir de qualquer um dos arquivos
    identificador = None
    for arquivo in [arquivo_razao, arquivo_fiscal]:
        ident, _ = extrair_info(Path(arquivo).stem)
        if ident:
            identificador = ident
            break
    if not identificador:
        identificador = "recon_000000"

    for arquivo, tipo in [(arquivo_razao, "razao"), (arquivo_fiscal, "fiscal")]:
        try:
            df = pl.read_csv(arquivo, separator=";", truncate_ragged_lines=True, infer_schema_length=0)
            df = df.with_columns([pl.col(col).cast(pl.Utf8) for col in df.columns])
            df = df.with_columns(pl.lit(tipo.upper()).alias("FONTE"))
            destino = Path(pasta_parquet) / f"{identificador}_{tipo}.parquet"
            df.write_parquet(destino, compression="zstd")
        except Exception as e:
            if progress_callback:
                progress_callback(5, f"Erro convertendo {tipo}: {e}")

    if progress_callback:
        progress_callback(25, "[Etapa 1/4] Conversao concluida!")

    # Etapa 2: Consolidar
    pasta_consolidado = etapa_consolidar(
        pasta_parquet,
        progress_callback=lambda p, m: sub_progress(1, 4, p, m)
    )

    # Etapa 3: Conciliar
    pasta_conciliado = etapa_conciliar(
        pasta_consolidado,
        progress_callback=lambda p, m: sub_progress(2, 4, p, m)
    )

    # Etapa 4: Exportar CSV
    pasta_csvs = etapa_exportar_csv(
        pasta_conciliado,
        progress_callback=lambda p, m: sub_progress(3, 4, p, m)
    )

    if progress_callback:
        progress_callback(100, "Pipeline completo finalizado!")

    return pasta_csvs
