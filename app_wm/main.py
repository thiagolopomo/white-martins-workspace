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

from PySide6.QtWidgets import QApplication, QMessageBox, QProgressDialog
from PySide6.QtCore import QTimer, Qt

from resources import obter_icone, carregar_fontes_app
from theme import build_app_qss
from splash import SplashScreen
from access import TelaAcesso
from shell import MainShell


def verificar_atualizacao(shell):
    """Verifica se ha update disponivel e oferece ao usuario."""
    try:
        from update_service import check_for_update, download_update_package, extract_update_package
        from update_dialog import UpdateDialog

        info = check_for_update()
        if not info:
            return

        dlg = UpdateDialog(info, shell)
        dlg.setWindowIcon(shell.windowIcon())
        result = dlg.exec()

        if result == UpdateDialog.Accepted and dlg._accepted:
            url = info.get("url", "")
            if not url:
                QMessageBox.warning(shell, "Erro", "URL de download nao disponivel.")
                return

            # Progress dialog
            progress = QProgressDialog("Baixando atualizacao...", "Cancelar", 0, 100, shell)
            progress.setWindowTitle("Atualizando")
            progress.setWindowModality(Qt.WindowModal)
            progress.setMinimumDuration(0)
            progress.show()

            def on_progress(pct, msg):
                progress.setValue(pct)
                progress.setLabelText(msg)
                QApplication.processEvents()

            zip_path = download_update_package(url, progress_callback=on_progress)

            progress.setLabelText("Extraindo...")
            source_dir = extract_update_package(zip_path, progress_callback=on_progress)
            progress.close()

            # Verificar hash se disponivel
            expected_sha = info.get("sha256", "")
            if expected_sha:
                from update_service import sha256_file
                actual_sha = sha256_file(zip_path)
                if actual_sha != expected_sha:
                    QMessageBox.critical(shell, "Erro",
                        "Hash do pacote nao confere. Download corrompido.")
                    return

            # Aplicar update e reiniciar
            try:
                from updater_client import iniciar_instalacao_update
                iniciar_instalacao_update(source_dir)

                # Atualizar app_version.json com a nova versao
                import json as _json
                from pathlib import Path as _Path
                # Tentar no diretorio do app primeiro, senao no AppData
                ver_path = _Path(__file__).with_name("app_version.json")
                try:
                    ver_path.write_text(_json.dumps({"version": info["version"]}), encoding="utf-8")
                except PermissionError:
                    # Program Files nao tem permissao - salvar no AppData
                    appdata = _Path.home() / "AppData" / "Local" / "WhiteMartinsWorkspace"
                    appdata.mkdir(parents=True, exist_ok=True)
                    (appdata / "app_version.json").write_text(
                        _json.dumps({"version": info["version"]}), encoding="utf-8"
                    )

                # Reiniciar o app imediatamente
                import subprocess
                exe = sys.executable
                args = sys.argv[:]
                if getattr(sys, 'frozen', False):
                    subprocess.Popen([exe] + args[1:])
                else:
                    subprocess.Popen([exe] + args)
                QApplication.quit()
            except Exception as e:
                QMessageBox.warning(shell, "Aviso",
                    f"Atualizacao sera aplicada no proximo inicio.\n{e}")

    except Exception as e:
        print(f"[UPDATE] Erro: {e}")


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

            # Verificar atualizacao 1s apos abrir
            QTimer.singleShot(1000, lambda: verificar_atualizacao(shell))
        else:
            app.quit()

    splash.iniciar(abrir_fluxo)

    sys.exit(app.exec())


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
