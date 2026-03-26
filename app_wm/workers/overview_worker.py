#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtCore import QThread, Signal


class OverviewWorker(QThread):
    progress = Signal(int, str)
    finished = Signal(list)
    error = Signal(str)

    def __init__(self, pasta_csvs):
        super().__init__()
        self.pasta_csvs = pasta_csvs

    def run(self):
        try:
            from logic.overview_logic import executar_overview
            result = executar_overview(
                self.pasta_csvs,
                progress_callback=lambda p, m: self.progress.emit(p, m)
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
