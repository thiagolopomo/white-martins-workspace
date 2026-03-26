#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtCore import QThread, Signal


class ReconWorker(QThread):
    progress = Signal(int, str)
    finished = Signal(str)
    error = Signal(str)
    stats = Signal(dict)  # Emite estatísticas: linhas, conciliados, etc.

    def __init__(self, arquivo_razao, arquivo_fiscal, pasta_saida):
        super().__init__()
        self.arquivo_razao = arquivo_razao
        self.arquivo_fiscal = arquivo_fiscal
        self.pasta_saida = pasta_saida

    def run(self):
        try:
            from logic.recon_logic import executar_recon_arquivos
            import polars as pl
            import os
            import glob

            # Conta linhas dos arquivos de entrada
            try:
                df_r = pl.read_csv(self.arquivo_razao, separator=";", infer_schema_length=0, n_rows=0)
                linhas_razao = pl.read_csv(self.arquivo_razao, separator=";", infer_schema_length=0).height
            except Exception:
                linhas_razao = 0

            try:
                linhas_fiscal = pl.read_csv(self.arquivo_fiscal, separator=";", infer_schema_length=0).height
            except Exception:
                linhas_fiscal = 0

            self.progress.emit(2, f"Razão: {linhas_razao:,} linhas | Fiscal: {linhas_fiscal:,} linhas".replace(",", "."))

            result = executar_recon_arquivos(
                self.arquivo_razao, self.arquivo_fiscal, self.pasta_saida,
                progress_callback=lambda p, m: self.progress.emit(p, m)
            )

            # Coleta estatísticas do CSV final
            csvs = glob.glob(os.path.join(result, "*.csv"))
            total_conc = 0
            total_nconc = 0
            for csv_file in csvs:
                try:
                    df = pl.read_csv(csv_file, separator=";", infer_schema_length=0)
                    conc = df.filter(pl.col("Conciliado") == "Sim").height
                    nconc = df.filter(pl.col("Conciliado") != "Sim").height
                    total_conc += conc
                    total_nconc += nconc
                except Exception:
                    pass

            self.stats.emit({
                "linhas_razao": linhas_razao,
                "linhas_fiscal": linhas_fiscal,
                "conciliados": total_conc,
                "nao_conciliados": total_nconc,
            })

            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
