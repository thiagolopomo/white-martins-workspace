#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import multiprocessing
import ctypes

# Windows: registrar AppUserModelID para icone correto na taskbar
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
        "WhiteMartins.WorkspaceFiscal.1.0"
    )
except Exception:
    pass

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from resources import obter_icone, carregar_fontes_app
from theme import build_app_qss
from splash import SplashScreen
from access import TelaAcesso
from shell import MainShell


def main():
    app = QApplication(sys.argv)

    familia = carregar_fontes_app()
    app.setStyleSheet(build_app_qss(familia))

    icone = obter_icone()
    app.setWindowIcon(icone)

    splash = SplashScreen()

    shell = None

    def abrir_fluxo():
        nonlocal shell

        # Tela de acesso - valida usuario antes de abrir o app
        acesso = TelaAcesso()
        acesso.setWindowIcon(icone)
        result = acesso.exec()

        if result == TelaAcesso.Accepted and acesso.acesso_liberado:
            shell = MainShell()
            shell.setWindowIcon(icone)
            shell.show()
            shell.showMaximized()
        else:
            app.quit()

    splash.iniciar(abrir_fluxo)

    sys.exit(app.exec())


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
