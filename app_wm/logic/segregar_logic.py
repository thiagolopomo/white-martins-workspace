#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Segregacao de divisoes - v9 LIGHTWEIGHT TEMPLATE.

Estrategia:
1. Le dados em chunks via COM (50s)
2. Abre arquivo, DELETA todos dados de todas abas (cria template leve)
3. Para cada divisao: escreve poucos dados, SaveCopyAs (rapido!), limpa
4. Fecha SEM salvar

Com template leve (~500KB), SaveCopyAs leva ~1s em vez de ~8s.
"""

import os
import re
import subprocess
from pathlib import Path

# Nomes de colunas que indicam divisao/filial (procura automatica)
COLUNAS_DIVISAO = ["Divisão", "Divisao", "Div", "Filial", "Division"]

ABAS_PRESERVAR_LOWER = {"capa", "capa resumo"}
CHUNK_SIZE = 40000


def _norm(s):
    return s.strip().lower().replace("á", "a").replace("é", "e").replace("ã", "a") \
        .replace("ç", "c").replace("í", "i").replace("ó", "o").replace("ú", "u") \
        .replace("õ", "o")


def _eh_preservar(nome_aba):
    return _norm(nome_aba) in ABAS_PRESERVAR_LOWER


def _div_str(val):
    if val is None:
        return None
    s = str(val).strip()
    if not s:
        return None
    try:
        n = str(int(float(s)))
        if re.match(r'^\d{3,5}$', n):
            return n
    except Exception:
        pass
    if re.match(r'^\d{3,5}$', s):
        return s
    return None


def _ler_aba_chunked(ws, header_row, col_filtro, last_row, n_cols,
                     progress_callback=None, nome_aba=""):
    data_start = header_row + 1
    total_rows = last_row - header_row
    dados_por_div = {}
    todas_divs = set()
    chunks_needed = (total_rows + CHUNK_SIZE - 1) // CHUNK_SIZE

    for chunk_idx in range(chunks_needed):
        r_start = data_start + chunk_idx * CHUNK_SIZE
        r_end = min(r_start + CHUNK_SIZE - 1, last_row)

        if progress_callback and chunks_needed > 1:
            progress_callback(
                1, f"  {nome_aba}: chunk {chunk_idx+1}/{chunks_needed}"
            )

        chunk_range = ws.Range(ws.Cells(r_start, 1), ws.Cells(r_end, n_cols))
        raw = chunk_range.Value
        if not raw:
            continue

        col_idx_0 = col_filtro - 1
        for row in raw:
            if col_idx_0 < len(row):
                d = _div_str(row[col_idx_0])
                if d:
                    todas_divs.add(d)
                    if d not in dados_por_div:
                        dados_por_div[d] = []
                    dados_por_div[d].append(row)

    return todas_divs, dados_por_div


def executar_segregacao(arquivo_origem, pasta_saida, progress_callback=None):
    os.makedirs(pasta_saida, exist_ok=True)
    extensao = Path(arquivo_origem).suffix.lower()
    arquivo_abs = os.path.abspath(arquivo_origem)

    import win32com.client
    import pythoncom
    pythoncom.CoInitialize()

    subprocess.run(["taskkill", "/F", "/IM", "EXCEL.EXE"],
                   capture_output=True, creationflags=0x08000000)

    excel = win32com.client.DispatchEx("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False
    excel.ScreenUpdating = False
    excel.EnableEvents = False

    arquivos_gerados = []

    try:
        # ============================================================
        # FASE 1: Abrir ReadOnly, ler dados em chunks
        # ============================================================
        if progress_callback:
            progress_callback(0, "Abrindo arquivo (leitura)...")

        wb_src = excel.Workbooks.Open(arquivo_abs, ReadOnly=True)
        try:
            excel.Calculation = -4135  # xlCalculationManual
        except Exception:
            pass

        abas_meta = {}
        dados_globais = {}
        todas_divisoes = set()

        for si in range(1, wb_src.Sheets.Count + 1):
            ws = wb_src.Sheets(si)
            nome_aba = ws.Name

            if _eh_preservar(nome_aba):
                continue

            if progress_callback:
                progress_callback(1, f"Analisando: {nome_aba}...")

            # Desativar AutoFilter para ler TODAS as linhas (inclusive ocultas)
            try:
                if ws.AutoFilterMode:
                    ws.AutoFilterMode = False
            except Exception:
                pass

            header_row = None
            col_filtro = None
            filtro_text = None
            # Usar INDICE da ultima coluna (nao apenas o count)
            used_range = ws.UsedRange
            n_cols_used = used_range.Column + used_range.Columns.Count - 1

            try:
                header_area = ws.Range(
                    ws.Cells(1, 1), ws.Cells(15, min(n_cols_used, 100))
                ).Value
                if header_area:
                    for ri, row in enumerate(header_area):
                        if row:
                            for ci, val in enumerate(row):
                                if val and str(val).strip() in COLUNAS_DIVISAO:
                                    header_row = ri + 1
                                    col_filtro = ci + 1
                                    filtro_text = str(val).strip()
                                    break
                        if header_row:
                            break
            except Exception:
                continue

            if not header_row:
                if progress_callback:
                    progress_callback(1, f"  {nome_aba}: sem coluna de divisao, pulando...")
                continue

            # Usar o MAIOR entre: ultimo dado na coluna filtro e UsedRange
            last_row_filtro = ws.Cells(ws.Rows.Count, col_filtro).End(-4162).Row
            try:
                used = ws.UsedRange
                last_row_used = used.Row + used.Rows.Count - 1
            except Exception:
                last_row_used = last_row_filtro
            last_row = max(last_row_filtro, last_row_used)

            # Desfazer agrupamentos de linhas que podem esconder dados
            try:
                ws.Cells.EntireRow.ShowDetail = True
            except Exception:
                pass
            try:
                ws.Outline.ShowLevels(RowLevels=8)
            except Exception:
                pass

            if last_row <= header_row:
                continue

            n_rows = last_row - header_row

            if progress_callback:
                progress_callback(1, f"Lendo {nome_aba}: {n_rows} linhas...")

            divs_aba, dados_aba = _ler_aba_chunked(
                ws, header_row, col_filtro, last_row, n_cols_used,
                progress_callback=progress_callback, nome_aba=nome_aba
            )

            todas_divisoes.update(divs_aba)
            dados_globais[nome_aba] = dados_aba
            # Calcular max linhas por divisao nesta aba
            max_rows_aba = 0
            for d_key, d_rows in dados_aba.items():
                if len(d_rows) > max_rows_aba:
                    max_rows_aba = len(d_rows)

            # Detectar offset: linhas em branco entre header e primeiro dado real
            first_data_offset = 0
            for check_offset in range(0, 10):
                check_row = header_row + 1 + check_offset
                if check_row > last_row:
                    break
                val = ws.Cells(check_row, col_filtro).Value
                if _div_str(val):
                    first_data_offset = check_offset
                    break

            abas_meta[nome_aba] = {
                "header_row": header_row,
                "data_start": header_row + 1,
                "col_filtro": col_filtro,
                "n_cols": n_cols_used,
                "last_row_original": last_row,
                "max_rows_div": max_rows_aba,
                "first_data_offset": first_data_offset,
            }

            if progress_callback:
                progress_callback(2, f"  {nome_aba}: {n_rows} linhas, {len(divs_aba)} divisoes (max {max_rows_aba}/div)")

        wb_src.Close(SaveChanges=False)

        divisoes = sorted(todas_divisoes)
        total = len(divisoes)
        if not divisoes:
            raise ValueError("Nenhuma divisao encontrada.")

        if progress_callback:
            progress_callback(5, f"{total} divisoes. Preparando template...")

        # ============================================================
        # FASE 2: Abrir arquivo, PRESERVAR FORMATACAO
        # - ClearContents nas linhas que vamos usar (mantem formato)
        # - Deletar SOMENTE o excesso acima do necessario (reduz tamanho)
        # ============================================================
        wb = excel.Workbooks.Open(arquivo_abs, ReadOnly=False)
        try:
            excel.Calculation = -4135
        except Exception:
            pass

        ws_cache = {}
        for nome_aba in abas_meta:
            for si2 in range(1, wb.Sheets.Count + 1):
                if _norm(wb.Sheets(si2).Name) == _norm(nome_aba):
                    ws_cache[nome_aba] = wb.Sheets(si2)
                    break

        if progress_callback:
            progress_callback(6, "Preparando template (preservando formatacao)...")

        for nome_aba, meta in abas_meta.items():
            ws = ws_cache.get(nome_aba)
            if ws is None:
                continue
            ds = meta["data_start"]
            lr = meta["last_row_original"]
            max_needed = meta["max_rows_div"]
            fdo_meta = meta.get("first_data_offset", 0)
            is_vf_tab = _norm(nome_aba) == _norm("Validação Fiscal")

            if is_vf_tab:
                # Para Validação Fiscal: manter APENAS offset + dados (sem margem)
                # Isso faz as linhas de subtotal/total subirem junto
                keep_rows = fdo_meta + max_needed
            else:
                # Margem de 10% pra seguranca
                keep_rows = int(max_needed * 1.1) + 10
            last_keep = ds + keep_rows - 1

            if lr >= ds:
                if progress_callback:
                    progress_callback(6, f"  {nome_aba}: mantendo {keep_rows} linhas formatadas, removendo {max(0, lr - last_keep)} excesso...")

                # DESATIVAR AutoFilter antes de limpar/deletar
                # Isso garante que linhas ocultas tambem sejam processadas
                try:
                    if ws.AutoFilterMode:
                        ws.AutoFilterMode = False
                except Exception:
                    pass

                is_validacao_fiscal = _norm(nome_aba) == _norm("Validação Fiscal")

                # ClearContents nas linhas que vamos reusar (preserva formato!)
                ws.Range(
                    ws.Cells(ds, 1),
                    ws.Cells(min(last_keep, lr), meta["n_cols"])
                ).ClearContents()

                if is_validacao_fiscal:
                    # Validação Fiscal: Clear() nas linhas EXCEDENTES alem do necessario
                    # Isso remove artefatos de borda/tabela de outras divisoes
                    max_data_rows = meta["max_rows_div"]
                    fdo = meta.get("first_data_offset", 0)
                    excess_start = ds + fdo + max_data_rows
                    if excess_start <= min(last_keep, lr):
                        ws.Range(
                            ws.Cells(excess_start, 1),
                            ws.Cells(min(last_keep, lr), meta["n_cols"])
                        ).Clear()

                # Guardar quantas linhas foram mantidas para limpeza na Fase 3
                meta["_kept_rows"] = keep_rows

                # Deletar o EXCESSO acima do necessario (reduz tamanho do arquivo)
                if lr > last_keep:
                    current = lr
                    while current > last_keep:
                        block_start = max(last_keep + 1, current - 49999)
                        ws.Rows(f"{block_start}:{current}").Delete()
                        current = block_start - 1

        if progress_callback:
            progress_callback(8, "Template pronto! Gerando arquivos...")

        # ============================================================
        # FASE 3: Para cada divisao: escrever -> SaveCopyAs -> limpar
        # ============================================================
        # Agora cada aba so tem headers. Escrever poucos dados e salvar e rapido.

        prev_rows = {}  # nome_aba -> quantas linhas foram escritas

        for div_idx, div in enumerate(divisoes):
            pct = 8 + int((div_idx / total) * 90)
            if progress_callback:
                progress_callback(pct, f"Divisao {div} ({div_idx + 1}/{total})")

            nome_saida = f"{div}{extensao}"
            caminho_saida = os.path.join(pasta_saida, nome_saida)
            caminho_saida_abs = os.path.abspath(caminho_saida)

            for nome_aba, meta in abas_meta.items():
                ws = ws_cache.get(nome_aba)
                if ws is None:
                    continue

                ds = meta["data_start"]
                n_cols = meta["n_cols"]
                offset = meta.get("first_data_offset", 0)
                write_start = ds + offset  # pula linhas em branco apos header

                # Limpar o que a divisao anterior escreveu
                prev_n = prev_rows.get(nome_aba, 0)
                if prev_n > 0:
                    prev_ws = prev_rows.get(f"{nome_aba}_ws", write_start)
                    ws.Range(
                        ws.Cells(prev_ws, 1),
                        ws.Cells(prev_ws + prev_n - 1, n_cols)
                    ).ClearContents()

                # Escrever dados desta divisao
                is_vf = _norm(nome_aba) == _norm("Validação Fiscal")
                rows_div = dados_globais.get(nome_aba, {}).get(div)
                if rows_div:
                    n_r = len(rows_div)
                    matrix = []
                    for row in rows_div:
                        clean = tuple("" if v is None else v for v in row)
                        matrix.append(clean)
                    ws.Range(
                        ws.Cells(write_start, 1),
                        ws.Cells(write_start + n_r - 1, n_cols)
                    ).Value = matrix

                    # Copiar formatacao da 1a linha e aplicar em TODAS (3 COM calls)
                    if n_r > 1:
                        try:
                            ws.Range(
                                ws.Cells(write_start, 1),
                                ws.Cells(write_start, n_cols)
                            ).Copy()
                            ws.Range(
                                ws.Cells(write_start + 1, 1),
                                ws.Cells(write_start + n_r - 1, n_cols)
                            ).PasteSpecial(Paste=-4122)  # xlPasteFormats
                            excel.CutCopyMode = False
                        except Exception:
                            pass

                    prev_rows[nome_aba] = n_r
                    prev_rows[f"{nome_aba}_ws"] = write_start

                    # Limpar TUDO abaixo da ultima linha util (exceto VF que tem subtotais)
                    if not is_vf:
                        clear_from = write_start + n_r
                        clear_to = ds + meta.get("_kept_rows", 0)
                        if clear_to >= clear_from:
                            ws.Range(
                                ws.Cells(clear_from, 1),
                                ws.Cells(clear_to, n_cols)
                            ).Clear()
                else:
                    prev_rows[nome_aba] = 0
                    prev_rows[f"{nome_aba}_ws"] = write_start
                    # Divisao sem dados: limpar toda area de dados
                    if not is_vf:
                        clear_to = ds + meta.get("_kept_rows", 0)
                        if clear_to >= write_start:
                            ws.Range(
                                ws.Cells(write_start, 1),
                                ws.Cells(clear_to, n_cols)
                            ).Clear()

            # Posicionar visualizacao no topo antes de salvar
            try:
                for si_scroll in range(1, wb.Sheets.Count + 1):
                    wb.Sheets(si_scroll).Activate()
                    excel.ActiveWindow.ScrollRow = 1
                    excel.ActiveWindow.ScrollColumn = 1
                    wb.Sheets(si_scroll).Range("A1").Select()
                wb.Sheets(1).Activate()
            except Exception:
                pass

            wb.SaveCopyAs(caminho_saida_abs)
            arquivos_gerados.append(caminho_saida)

        # Fechar SEM salvar - preserva original
        wb.Close(SaveChanges=False)

    except Exception as e:
        if progress_callback:
            progress_callback(0, f"Erro: {e}")
        raise

    finally:
        try:
            excel.Calculation = -4105
        except Exception:
            pass
        try:
            excel.EnableEvents = True
            excel.ScreenUpdating = True
            excel.DisplayAlerts = True
            excel.Quit()
        except Exception:
            pass
        pythoncom.CoUninitialize()

    if progress_callback:
        progress_callback(100, f"Concluido! {len(arquivos_gerados)} arquivos gerados.")

    return arquivos_gerados
