#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtCore import QThread, Signal


class ConverterWorker(QThread):
    progress = Signal(int, str)
    finished = Signal(list)
    error = Signal(str)

    def __init__(self, pasta_pdfs):
        super().__init__()
        self.pasta_pdfs = pasta_pdfs

    def run(self):
        try:
            from logic.converter_logic import executar_conversao
            result = executar_conversao(
                self.pasta_pdfs,
                progress_callback=lambda p, m: self.progress.emit(p, m)
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
