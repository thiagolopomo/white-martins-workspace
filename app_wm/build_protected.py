#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Build script: protege lógicas com PyArmor e empacota com PyInstaller.
Uso: python build_protected.py

1. PyArmor ofusca os arquivos de lógica (impossível descompilar)
2. PyInstaller empacota tudo em um executável
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def run(cmd, **kwargs):
    print(f"  > {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, **kwargs)
    if result.stdout:
        print(result.stdout)
    if result.returncode != 0 and result.stderr:
        print(f"  STDERR: {result.stderr}")
    return result.returncode == 0


def build():
    base_dir = Path(__file__).parent
    os.chdir(base_dir)
    dist_dir = base_dir / "dist_protected"

    print("=" * 60)
    print("  BUILD PROTEGIDO - White Martins Workspace")
    print("=" * 60)

    # 1. Criar pasta de distribuição limpa
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir()

    # Copiar toda a estrutura do app
    app_dist = dist_dir / "app_wm"
    shutil.copytree(base_dir, app_dist, ignore=shutil.ignore_patterns(
        '__pycache__', '*.pyc', 'build', 'dist', 'dist_protected',
        'build_protected.py', '*.spec', '*.egg-info'
    ))

    # 2. Ofuscar lógicas com PyArmor
    print()
    print("[1/2] Ofuscando lógicas com PyArmor...")

    logic_files = [
        "logic/recon_logic.py",
        "logic/overview_logic.py",
        "logic/segregar_logic.py",
        "logic/converter_logic.py",
        "logic/empresa_detect.py",
    ]
    worker_files = [
        "workers/recon_worker.py",
        "workers/overview_worker.py",
        "workers/segregar_worker.py",
        "workers/converter_worker.py",
    ]

    all_protect = logic_files + worker_files

    for f in all_protect:
        src = app_dist / f
        if src.exists():
            ok = run(f'pyarmor gen --output "{src.parent}" "{src}"')
            if ok:
                print(f"    ✓ {f}")
            else:
                print(f"    ✗ {f} (falhou, mantendo original)")

    # 3. Build PyInstaller
    print()
    print("[2/2] Empacotando com PyInstaller...")

    main_py = app_dist / "main.py"
    icon_path = app_dist / "logowhitemartins.png"

    pyinstaller_cmd = (
        f'pyinstaller --noconfirm --onedir --windowed '
        f'--name "White Martins Workspace" '
        f'--add-data "{app_dist / "logowhitemartins.png"};." '
        f'--add-data "{app_dist / "white-martins.png"};." '
        f'--add-data "{app_dist / "app_version.json"};." '
        f'--distpath "{dist_dir / "output"}" '
        f'--workpath "{dist_dir / "build_temp"}" '
        f'--specpath "{dist_dir}" '
        f'"{main_py}"'
    )
    run(pyinstaller_cmd)

    # Limpar temporários
    build_temp = dist_dir / "build_temp"
    if build_temp.exists():
        shutil.rmtree(build_temp)

    print()
    print("=" * 60)
    print("  BUILD CONCLUÍDO!")
    print(f"  Executável em: {dist_dir / 'output'}")
    print()
    print("  Lógicas protegidas com PyArmor (ofuscação)")
    print("  App empacotado com PyInstaller (executável)")
    print("=" * 60)


if __name__ == "__main__":
    build()
