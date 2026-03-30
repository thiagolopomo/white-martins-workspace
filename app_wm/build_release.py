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

    # Hidden imports necessários - COMPLETO (v1.0.12)
    hidden_modules = [
        # App modules
        "logic", "logic.recon_logic", "logic.overview_logic",
        "logic.segregar_logic", "logic.converter_logic", "logic.empresa_detect",
        "workers", "workers.recon_worker", "workers.overview_worker",
        "workers.segregar_worker", "workers.converter_worker",
        "pages", "pages.dashboard_page", "pages.converter_page",
        "pages.recon_page", "pages.overview_page", "pages.segregar_page",
        # PDF processing (pdfplumber + dependencies)
        "pdfplumber", "pdfplumber.page", "pdfplumber.pdf", "pdfplumber.table",
        "pdfplumber.utils", "pdfplumber.display", "pdfplumber.ctm",
        "pdfplumber.convert", "pdfplumber._typing",
        "pdfminer", "pdfminer.six", "pdfminer.high_level", "pdfminer.layout",
        "pdfminer.pdfinterp", "pdfminer.pdfpage", "pdfminer.pdfparser",
        "pdfminer.pdfdocument", "pdfminer.pdftypes", "pdfminer.pdfcolor",
        "pdfminer.converter", "pdfminer.cmapdb", "pdfminer.psparser",
        "pdfminer.encodingdb", "pdfminer.glyphlist", "pdfminer.utils",
        "pdfminer.image", "pdfminer.ccitt", "pdfminer.arcfour",
        "pdfminer.lzw", "pdfminer.ascii85", "pdfminer.runlength",
        "pdfminer.rijndael", "pdfminer.pdfdevice", "pdfminer.pdffont",
        "pdfminer.casting", "pdfminer._saslprep",
        # Data processing - polars
        "polars", "polars.io", "polars.io.csv", "polars.io.parquet",
        "polars.datatypes", "polars.expr", "polars.frame",
        "polars.series", "polars.lazy", "polars.functions",
        "polars.selectors", "polars.utils",
        # Data processing - pandas
        "pandas", "pandas.core", "pandas.core.frame", "pandas.core.series",
        "pandas.core.groupby", "pandas.core.reshape",
        "pandas.io", "pandas.io.excel", "pandas.io.parsers",
        "pandas._libs", "pandas._libs.tslibs",
        # Data processing - openpyxl
        "openpyxl", "openpyxl.styles", "openpyxl.styles.named_styles",
        "openpyxl.workbook", "openpyxl.worksheet",
        "openpyxl.cell", "openpyxl.utils",
        "openpyxl.reader", "openpyxl.reader.excel",
        "openpyxl.writer", "openpyxl.writer.excel",
        "openpyxl.worksheet.worksheet",
        # Image processing (pdfplumber dependency)
        "PIL", "PIL.Image", "PIL._imaging",
        "PIL.PngImagePlugin", "PIL.JpegImagePlugin",
        "PIL.ImageDraw", "PIL.ImageFont",
        # Network / HTTP
        "requests", "requests.adapters", "requests.auth",
        "requests.sessions", "requests.models",
        "urllib3", "urllib3.util", "urllib3.util.retry",
        "urllib3.util.ssl_", "urllib3.contrib",
        "certifi", "idna", "charset_normalizer",
        # Cryptography (pdfminer.six dependency)
        "cryptography", "cryptography.hazmat", "cryptography.hazmat.primitives",
        "cryptography.hazmat.primitives.ciphers",
        "cryptography.hazmat.backends",
        "cryptography.hazmat.bindings",
        # PySide6 (GUI framework)
        "PySide6", "PySide6.QtCore", "PySide6.QtGui", "PySide6.QtWidgets",
        "shiboken6",
        # Windows COM - COMPLETE (fixes win32timezone etc.)
        "win32com", "win32com.client", "win32com.client.dynamic",
        "win32com.client.gencache", "win32com.client.makepy",
        "win32com.server", "win32com.shell",
        "pythoncom", "pywintypes", "win32api", "win32con",
        "win32timezone", "win32event", "win32file", "win32process",
        "win32security", "win32gui", "win32print",
        "winerror", "mmapfile", "odbc", "perfmon",
        "servicemanager", "timer",
        # Standard library
        "unicodedata", "csv", "hashlib", "json", "re", "os", "sys",
        "multiprocessing", "ctypes", "threading", "subprocess",
        "getpass", "socket", "platform", "uuid", "time", "glob",
        "shutil", "tempfile", "zipfile", "pathlib",
        "io", "collections", "functools", "itertools",
        "datetime", "decimal", "copy", "math",
        "logging", "traceback", "struct", "binascii",
        "email", "http", "html",
    ]
    hidden = [f"--hidden-import={m}" for m in hidden_modules]
    hidden += [
        "--collect-all=polars",
        "--collect-all=pdfminer",
        "--collect-all=pdfplumber",
        "--collect-all=charset_normalizer",
        "--collect-all=certifi",
        "--collect-all=win32com",
        "--collect-all=win32timezone",
        "--collect-all=pythoncom",
        "--collect-all=pywintypes",
        "--collect-all=openpyxl",
        "--collect-all=PIL",
        "--collect-all=pandas",
        "--collect-all=PySide6",
        "--collect-all=shiboken6",
        "--collect-all=requests",
        "--collect-all=urllib3",
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
