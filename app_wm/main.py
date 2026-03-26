#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import multiprocessing

from PySide6.QtWidgets import QApplication

from resources import obter_icone, carregar_fontes_app
from theme import build_app_qss
from splash import SplashScreen
from shell import MainShell


def main():
    app = QApplication(sys.argv)

    familia = carregar_fontes_app()
    app.setStyleSheet(build_app_qss(familia))

    icone = obter_icone()
    app.setWindowIcon(icone)

    splash = SplashScreen()

    shell = None

    def abrir_app():
        nonlocal shell
        shell = MainShell()
        shell.setWindowIcon(icone)
        shell.show()
        shell.showMaximized()

    splash.iniciar(abrir_app)

    sys.exit(app.exec())


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
