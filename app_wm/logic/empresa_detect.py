#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Detecção automática de empresa (Gilda, Gino, Gine) via divisões nos arquivos.
"""

import re
import unicodedata
from pathlib import Path

FILIAIS_GILDA = {
    "2108", "2122", "2151", "2153", "2154", "2165", "2192", "2278", "2280", "2301",
    "2304", "2307", "2309", "2312", "2314", "2321", "2333", "2335", "2340", "2350",
    "2377", "2380", "2392", "2393", "2395", "2397", "2400", "2403", "2408", "2417",
    "2421", "2430", "2431", "2432", "2434", "2435", "2441", "2442", "2447", "2455",
    "2460", "2492", "2496", "2497", "2498", "2504", "2505", "2507", "2513", "2517",
    "2518", "2523", "2528", "2551", "2595", "2606", "2654", "2703", "2706", "2707",
    "2708", "2710", "2712", "2739", "2744", "2745", "2746", "2801", "2802", "2803",
    "2804", "2805", "2839", "2841", "2903", "2904", "2905", "2338", "2818", "2825",
    "2500", "2705", "2155", "2156",
}

FILIAIS_GINO = {
    "2299", "2361", "2180", "2359", "2452", "2236", "2221", "2363",
    "2467", "2235", "2362", "2251", "2604", "2358", "2370", "2262",
}

FILIAIS_GINE = {
    "2337", "2190", "2231", "2213", "2211", "2208", "2204", "2253", "2709", "2602",
    "2603", "2206", "2210", "2287", "2227", "2255", "2205", "2245", "2704", "2225",
    "2218", "2601", "2713", "2200", "2202", "2220", "2258", "2259", "2631", "2605",
    "2613", "2244",
}

EMPRESAS = {
    "Gilda": FILIAIS_GILDA,
    "Gino": FILIAIS_GINO,
    "Gine": FILIAIS_GINE,
}


def _extrair_divisoes_csv(caminho_csv, max_linhas=500):
    """Extrai divisões únicas de um CSV (primeiras N linhas)."""
    import csv
    divisoes = set()
    colunas_div = []

    try:
        with open(caminho_csv, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f, delimiter=";")
            header = next(reader)

            # Encontra colunas de divisão
            nomes_div = ["divisão", "divisao", "divisão - aa", "divisao - aa", "div", "filial"]
            for i, col in enumerate(header):
                col_norm = unicodedata.normalize('NFKD', col).encode('ASCII', 'ignore').decode('ASCII').lower().strip()
                if col_norm in nomes_div:
                    colunas_div.append(i)

            if not colunas_div:
                return set()

            for count, row in enumerate(reader):
                if count >= max_linhas:
                    break
                for idx in colunas_div:
                    if idx < len(row):
                        val = row[idx].strip()
                        # Extrai só o número da divisão (ex: "2312 (Filial Vinhedo)" → "2312")
                        match = re.match(r"(\d{4})", val)
                        if match:
                            divisoes.add(match.group(1))
    except Exception:
        pass

    return divisoes


def detectar_empresa_por_divisoes(divisoes):
    """
    Dado um set de divisões, identifica a empresa.
    Retorna (empresa_nome, confianca) ou (None, 0).
    """
    if not divisoes:
        return None, 0

    melhor_empresa = None
    melhor_score = 0

    for empresa, filiais in EMPRESAS.items():
        intersecao = divisoes & filiais
        if len(intersecao) > melhor_score:
            melhor_score = len(intersecao)
            melhor_empresa = empresa

    if melhor_score > 0:
        return melhor_empresa, melhor_score

    return None, 0


def detectar_empresa_arquivo(caminho_csv):
    """Detecta empresa a partir de um arquivo CSV."""
    # Tenta pelo nome do arquivo primeiro
    nome = Path(caminho_csv).stem.lower()
    nome_norm = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('ASCII')

    for empresa in ["gilda", "gino", "gine"]:
        if empresa in nome_norm:
            return empresa.capitalize()

    # Tenta pelas divisões no conteúdo
    divisoes = _extrair_divisoes_csv(caminho_csv)
    empresa, _ = detectar_empresa_por_divisoes(divisoes)
    return empresa


def validar_mesma_empresa(arquivo_razao, arquivo_fiscal):
    """
    Valida que ambos os arquivos pertencem à mesma empresa.
    Retorna (empresa, erro_msg).
    Se empresa != None e erro_msg == None, tudo OK.
    """
    emp_razao = detectar_empresa_arquivo(arquivo_razao)
    emp_fiscal = detectar_empresa_arquivo(arquivo_fiscal)

    if emp_razao and emp_fiscal:
        if emp_razao == emp_fiscal:
            return emp_razao, None
        else:
            return None, (
                f"Arquivos de empresas diferentes!\n"
                f"Razão: {emp_razao}\n"
                f"Fiscal: {emp_fiscal}\n\n"
                f"Selecione arquivos da mesma empresa."
            )

    # Se só um foi detectado, usa esse
    if emp_razao:
        return emp_razao, None
    if emp_fiscal:
        return emp_fiscal, None

    return None, None  # Não detectou, mas não é erro
