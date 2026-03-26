#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtCore import QThread, Signal


class SegregarWorker(QThread):
    progress = Signal(int, str)
    finished = Signal(list)
    error = Signal(str)

    def __init__(self, arquivo_origem, pasta_saida):
        super().__init__()
        self.arquivo_origem = arquivo_origem
        self.pasta_saida = pasta_saida

    def run(self):
        try:
            from logic.segregar_logic import executar_segregacao
            result = executar_segregacao(
                self.arquivo_origem, self.pasta_saida,
                progress_callback=lambda p, m: self.progress.emit(p, m)
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
