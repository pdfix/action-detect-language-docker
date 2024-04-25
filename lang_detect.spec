# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None


def find_pdfixsdk(start_path):
    for root, dirs, files in os.walk(start_path):
        if 'pdfixsdk' in dirs:
            pdfixsdk_path = os.path.join(root, 'pdfixsdk')
            return pdfixsdk_path
    return None


path = os.getcwd()

pdfix_sdk = find_pdfixsdk(path)

if pdfix_sdk:
    print("Found directory:", pdfix_sdk)
else:
    print("No directory found with prefix:", prefix)


a = Analysis(
    ['src/lang_detect.py'],
    pathex=[],
    binaries=[(pdfix_sdk, 'pdfixsdk/')],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='lang_detect',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='lang_detect',
)
