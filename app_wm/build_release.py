#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Build Release - White Martins Workspace
1. Ofusca lógicas com PyArmor
2. Empacota com PyInstaller (--onedir)
3. Gera pasta pronta para distribuição
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def run(cmd, cwd=None):
    print(f"  > {cmd[:120]}...")
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    if r.returncode != 0:
        print(f"  ERRO: {r.stderr[:300]}")
    return r.returncode == 0


def main():
    base = Path(__file__).parent.resolve()
    dist = base / "release_build"

    print("=" * 60)
    print("  WHITE MARTINS WORKSPACE - BUILD RELEASE")
    print("=" * 60)

    # Limpar build anterior
    if dist.exists():
        shutil.rmtree(dist, ignore_errors=True)
    dist.mkdir()

    stage = dist / "stage"
    stage.mkdir()

    # ── 1. Copiar app ──
    print("\n[1/4] Copiando arquivos...")
    for d in ["logic", "pages", "workers"]:
        (stage / d).mkdir()
        for f in (base / d).glob("*.py"):
            shutil.copy2(f, stage / d / f.name)

    for f in ["main.py", "shell.py", "theme.py", "resources.py", "scaling.py", "splash.py"]:
        shutil.copy2(base / f, stage / f)

    for f in ["icone.ico", "logowhitemartins.png", "white-martins.png", "app_version.json"]:
        src = base / f
        if src.exists():
            shutil.copy2(src, stage / f)

    print("  OK")

    # ── 2. Ofuscar lógicas ──
    print("\n[2/4] Ofuscando lógicas com PyArmor...")
    files_to_protect = [
        "logic/recon_logic.py", "logic/overview_logic.py",
        "logic/segregar_logic.py", "logic/converter_logic.py",
        "logic/empresa_detect.py",
        "workers/recon_worker.py", "workers/overview_worker.py",
        "workers/segregar_worker.py", "workers/converter_worker.py",
    ]

    obf_dir = dist / "obfuscated"
    for f in files_to_protect:
        src = stage / f
        if src.exists():
            ok = run(f'pyarmor gen -O "{obf_dir}" "{src}"')
            if ok:
                # Substituir original pelo ofuscado
                obf_file = obf_dir / Path(f).name
                if obf_file.exists():
                    shutil.copy2(obf_file, src)
                    print(f"    OK {f}")
            else:
                print(f"    WARN {f} (mantendo original)")

    # Copiar runtime do PyArmor para stage
    rt_dir = obf_dir / "pyarmor_runtime_000000"
    if rt_dir.exists():
        shutil.copytree(rt_dir, stage / "pyarmor_runtime_000000", dirs_exist_ok=True)
        print("    OK pyarmor_runtime copiado")

    # ── 3. PyInstaller ──
    print("\n[3/4] Empacotando com PyInstaller...")

    icon_path = stage / "icone.ico"
    add_data = [
        f'--add-data={stage / "icone.ico"};.',
        f'--add-data={stage / "logowhitemartins.png"};.',
        f'--add-data={stage / "white-martins.png"};.',
        f'--add-data={stage / "app_version.json"};.',
    ]

    # Adicionar runtime PyArmor
    rt_stage = stage / "pyarmor_runtime_000000"
    if rt_stage.exists():
        add_data.append(f'--add-data={rt_stage};pyarmor_runtime_000000')

    # Hidden imports necessários
    hidden = [
        "--hidden-import=logic",
        "--hidden-import=logic.recon_logic",
        "--hidden-import=logic.overview_logic",
        "--hidden-import=logic.segregar_logic",
        "--hidden-import=logic.converter_logic",
        "--hidden-import=logic.empresa_detect",
        "--hidden-import=workers",
        "--hidden-import=workers.recon_worker",
        "--hidden-import=workers.overview_worker",
        "--hidden-import=workers.segregar_worker",
        "--hidden-import=workers.converter_worker",
        "--hidden-import=pages",
        "--hidden-import=pages.dashboard_page",
        "--hidden-import=pages.converter_page",
        "--hidden-import=pages.recon_page",
        "--hidden-import=pages.overview_page",
        "--hidden-import=pages.segregar_page",
        # Dependencias de terceiros
        "--hidden-import=polars",
        "--hidden-import=pandas",
        "--hidden-import=openpyxl",
        "--hidden-import=requests",
        "--hidden-import=win32com",
        "--hidden-import=win32com.client",
        "--hidden-import=pythoncom",
        "--hidden-import=pywintypes",
        "--hidden-import=unicodedata",
        "--hidden-import=csv",
        "--hidden-import=hashlib",
        "--collect-all=polars",
    ]

    # Paths
    paths = [
        f"--paths={stage}",
        f"--paths={stage / 'logic'}",
        f"--paths={stage / 'pages'}",
        f"--paths={stage / 'workers'}",
    ]

    cmd_parts = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--onedir", "--windowed",
        '--name=White Martins Workspace',
        f'--icon={icon_path}',
        f'--distpath={dist / "output"}',
        f'--workpath={dist / "build_temp"}',
        f'--specpath={dist}',
    ] + add_data + hidden + paths + [str(stage / "main.py")]

    cmd = " ".join(f'"{c}"' if " " in str(c) else str(c) for c in cmd_parts)
    ok = run(cmd)

    if not ok:
        print("\n  WARN PyInstaller falhou. Tentando com opções simplificadas...")
        # Fallback: copiar stage inteira como --add-data
        cmd_simple = (
            f'{sys.executable} -m PyInstaller --noconfirm --onedir --windowed '
            f'--name "White Martins Workspace" '
            f'--icon "{icon_path}" '
            f'--distpath "{dist / "output"}" '
            f'--workpath "{dist / "build_temp"}" '
            f'--specpath "{dist}" '
            f'--paths "{stage}" '
            f'"{stage / "main.py"}"'
        )
        run(cmd_simple)

    # ── 4. Copiar assets extras pro output ──
    print("\n[4/4] Finalizando...")
    output_app = dist / "output" / "White Martins Workspace"
    if output_app.exists():
        # Copiar módulos Python (pages, logic, workers) pro output
        for d in ["logic", "pages", "workers"]:
            src_d = stage / d
            dst_d = output_app / d
            if not dst_d.exists():
                shutil.copytree(src_d, dst_d)

        # Runtime PyArmor
        if rt_stage.exists() and not (output_app / "pyarmor_runtime_000000").exists():
            shutil.copytree(rt_stage, output_app / "pyarmor_runtime_000000")

        # Assets
        for f in ["icone.ico", "logowhitemartins.png", "white-martins.png", "app_version.json"]:
            src = stage / f
            dst = output_app / f
            if src.exists() and not dst.exists():
                shutil.copy2(src, dst)

    # Limpar temporários
    for d in ["build_temp", "stage", "obfuscated"]:
        p = dist / d
        if p.exists():
            shutil.rmtree(p, ignore_errors=True)

    print()
    print("=" * 60)
    print("  BUILD RELEASE CONCLUÍDO!")
    print(f"  Pasta: {output_app}")
    print()
    if output_app.exists():
        exe = output_app / "White Martins Workspace.exe"
        if exe.exists():
            size_mb = exe.stat().st_size / (1024 * 1024)
            print(f"  EXE: {exe.name} ({size_mb:.1f} MB)")
        total = sum(f.stat().st_size for f in output_app.rglob("*") if f.is_file())
        print(f"  Total: {total / (1024*1024):.0f} MB")
    print()
    print("  Para distribuir: compacte a pasta inteira em .zip")
    print("=" * 60)


if __name__ == "__main__":
    main()
