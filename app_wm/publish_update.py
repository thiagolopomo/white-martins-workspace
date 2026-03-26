#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Publicar update do White Martins Workspace.

Uso:
  python publish_update.py 1.0.1 "Corrigido bug X, adicionado Y"
  python publish_update.py 1.0.1 "Descricao" --mandatory

Faz tudo automaticamente:
  1. Atualiza app_version.json com nova versao
  2. Ofusca logicas com PyArmor
  3. Empacota com PyInstaller
  4. Compila instalador Inno Setup
  5. Assina digitalmente (EXE + Setup)
  6. Cria ZIP do instalador
  7. Commit + push no GitHub
  8. Cria GitHub Release com o ZIP
  9. Atualiza version.json com URL do release
  10. Push final - todos os usuarios recebem o update
"""

import os
import sys
import json
import subprocess
import hashlib
from pathlib import Path


REPO_OWNER = "thiagolopomo"
REPO_NAME = "white-martins-workspace"
BASE_DIR = Path(__file__).parent
ROOT_DIR = BASE_DIR.parent
SIGNTOOL = r"C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\signtool.exe"
INNO = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"


def run(cmd, check=True):
    print(f"  > {cmd[:120]}")
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.stdout.strip():
        for line in r.stdout.strip().split("\n")[-3:]:
            print(f"    {line}")
    if check and r.returncode != 0:
        print(f"  ERRO: {r.stderr[:300]}")
        return False
    return True


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    if len(sys.argv) < 3:
        print("Uso: python publish_update.py <versao> <notas> [--mandatory]")
        print("Ex:  python publish_update.py 1.0.1 \"Bug fix no segregar\"")
        sys.exit(1)

    version = sys.argv[1]
    notes = sys.argv[2]
    mandatory = "--mandatory" in sys.argv

    print("=" * 60)
    print(f"  PUBLISH UPDATE - White Martins Workspace v{version}")
    print("=" * 60)

    # ── 1. Atualizar versao ──
    print(f"\n[1/10] Atualizando versao para {version}...")
    ver_file = BASE_DIR / "app_version.json"
    ver_file.write_text(json.dumps({"version": version}), encoding="utf-8")
    print("  OK")

    # ── 2-3. Build (PyArmor + PyInstaller) ──
    print(f"\n[2/10] Build completo (PyArmor + PyInstaller)...")
    os.chdir(BASE_DIR)
    if not run(f"{sys.executable} build_release.py"):
        print("BUILD FALHOU!")
        sys.exit(1)

    # ── 4. Compilar instalador ──
    print(f"\n[4/10] Compilando instalador Inno Setup...")

    # Atualizar versao no .iss
    iss_path = BASE_DIR / "installer.iss"
    iss_content = iss_path.read_text(encoding="utf-8")
    import re
    iss_content = re.sub(
        r'#define MyAppVersion ".*?"',
        f'#define MyAppVersion "{version}"',
        iss_content
    )
    iss_path.write_text(iss_content, encoding="utf-8")

    run(f'"{INNO}" "{iss_path}"')

    # ── 5. Assinar ──
    print(f"\n[5/10] Assinando digitalmente...")
    exe_path = BASE_DIR / "release_build" / "output" / "White Martins Workspace" / "White Martins Workspace.exe"
    setup_path = BASE_DIR / "release_build" / "installer" / f"WhiteMartinsWorkspace_Setup_v{version}.exe"

    if Path(SIGNTOOL).exists():
        for f in [exe_path, setup_path]:
            if f.exists():
                run(f'"{SIGNTOOL}" sign /a /s My /n "White Martins" /fd sha256 /td sha256 /tr http://timestamp.digicert.com "{f}"')
    else:
        print("  SignTool nao encontrado, pulando assinatura")

    # ── 6. ZIP ──
    print(f"\n[6/10] Criando ZIP...")
    import zipfile
    zip_name = f"WhiteMartinsWorkspace_v{version}.zip"
    zip_path = BASE_DIR / "release_build" / "installer" / zip_name

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        if setup_path.exists():
            zf.write(setup_path, setup_path.name)

    zip_size = zip_path.stat().st_size / (1024 * 1024)
    zip_sha = sha256_file(zip_path)
    print(f"  {zip_name} ({zip_size:.0f} MB) SHA256: {zip_sha[:16]}...")

    # ── 7. Git commit + push ──
    print(f"\n[7/10] Commit + push...")
    os.chdir(ROOT_DIR)
    run(f'git add app_wm/app_version.json app_wm/installer.iss app_wm/build_release.py')
    run(f'git commit -m "release: v{version} - {notes}"')
    run(f'git push origin master')

    # ── 8. Criar GitHub Release ──
    print(f"\n[8/10] Criando GitHub Release v{version}...")
    tag = f"v{version}"
    release_cmd = (
        f'gh release create {tag} '
        f'"{zip_path}" '
        f'--title "White Martins Workspace {tag}" '
        f'--notes "{notes}" '
        f'--repo {REPO_OWNER}/{REPO_NAME}'
    )
    run(release_cmd)

    # ── 9. Atualizar version.json ──
    print(f"\n[9/10] Atualizando version.json (manifest)...")
    download_url = f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{tag}/{zip_name}"

    manifest = {
        "version": version,
        "notes": notes,
        "mandatory": mandatory,
        "url": download_url,
        "sha256": zip_sha,
    }
    manifest_path = ROOT_DIR / "version.json"
    manifest_path.write_text(json.dumps(manifest, indent=4, ensure_ascii=False), encoding="utf-8")
    print(f"  URL: {download_url}")

    # ── 10. Push final ──
    print(f"\n[10/10] Push final do manifest...")
    run(f'git add version.json')
    run(f'git commit -m "update manifest: v{version}"')
    run(f'git push origin master')

    print()
    print("=" * 60)
    print(f"  UPDATE v{version} PUBLICADO COM SUCESSO!")
    print()
    print(f"  Instalador: {setup_path.name}")
    print(f"  ZIP: {zip_name} ({zip_size:.0f} MB)")
    print(f"  Release: https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/tag/{tag}")
    print()
    print("  Todos os usuarios receberao o update na proxima abertura do app.")
    print("=" * 60)


if __name__ == "__main__":
    main()
