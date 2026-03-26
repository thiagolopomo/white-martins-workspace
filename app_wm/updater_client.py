#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Cliente do updater - inicia a instalacao do update."""

import os
import sys
import shutil
import tempfile
import subprocess
import time
from pathlib import Path


def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent


def iniciar_instalacao_update(source_dir):
    """
    Copia o updater pra temp, lanca com elevacao, e espera ele sinalizar.
    source_dir: pasta com os arquivos novos extraidos.
    """
    base = get_base_dir()
    updater_src = base / "assets" / "updates" / "updater.exe"

    if not updater_src.exists():
        # Se nao tem updater.exe, fazer update simples (sem elevacao)
        return _update_simples(source_dir, base)

    # Copiar updater pra temp
    tmp = Path(tempfile.mkdtemp(prefix="wm_updater_"))
    updater_tmp = tmp / "updater.exe"
    shutil.copy2(updater_src, updater_tmp)

    ready_file = tmp / "updater_ready.flag"
    app_exe = "White Martins Workspace.exe"
    pid = os.getpid()

    # Lancar com elevacao
    args = [
        str(updater_tmp),
        "--source-dir", str(source_dir),
        "--app-dir", str(base),
        "--app-exe", app_exe,
        "--wait-pid", str(pid),
        "--ready-file", str(ready_file),
    ]

    try:
        if sys.platform == "win32":
            import ctypes
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", str(updater_tmp),
                " ".join(f'"{a}"' for a in args[1:]),
                str(tmp), 1
            )
        else:
            subprocess.Popen(args)
    except Exception as e:
        raise RuntimeError(f"Falha ao iniciar updater: {e}")

    # Esperar sinal de ready
    for _ in range(30):
        if ready_file.exists():
            return True
        time.sleep(0.5)

    raise TimeoutError("Updater nao sinalizou em tempo.")


def _update_simples(source_dir, base_dir):
    """Update sem updater.exe - copia arquivos para onde tiver permissao."""
    import shutil as sh
    source = Path(source_dir)
    target = Path(base_dir)

    for item in source.rglob("*"):
        if item.is_file():
            rel = item.relative_to(source)
            dest = target / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                sh.copy2(item, dest)
            except PermissionError:
                pass  # Program Files - sem permissao, pula
            except Exception:
                pass

    return True
