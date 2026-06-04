# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['agent\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('.env', '.'), ('agent\\knowledge\\documents', 'agent\\knowledge\\documents')],
    hiddenimports=['chromadb.telemetry.product', 'chromadb.telemetry.product.posthog', 'chromadb.api.segment', 'chromadb.api.rust', 'chromadb.segment.impl.manager.local', 'chromadb.segment.impl.vector.local_persistent_hnsw', 'chromadb.segment.impl.metadata.sqlite', 'tiktoken_ext.openai_public'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ai-npc-sentinel',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
