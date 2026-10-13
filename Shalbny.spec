# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

BASE_DIR = Path(SPECPATH).resolve()

datas = [(str(BASE_DIR / 'assets'), 'assets')]
binaries = []
hiddenimports = [
    'pystray',
    'PIL',
    'PIL.Image',
    'PIL.ImageDraw',
    'PIL.ImageTk',
    'PIL.PngImagePlugin',
    'PIL.IcoImagePlugin',
    'PIL.BmpImagePlugin',
    'keyboard',
    'pyperclip',
    'src.i18n',
]
datas += collect_data_files('customtkinter')
hiddenimports += collect_submodules('customtkinter')

EXCLUDED_MODULES = [
    'numpy', 'scipy', 'pandas', 'matplotlib',
    'pytest', '_pytest', 'unittest', 'doctest', 'pdb', 'pydoc', 'pydoc_data', '_pyrepl',
    'yaml', 'charset_normalizer', 'olefile',
    'asyncio', 'concurrent', 'multiprocessing', 'xmlrpc',
    'email', 'http', 'html', 'ssl', '_ssl', 'ftplib', 'netrc', 'mimetypes', 'urllib',
    'sqlite3', '_sqlite3', 'decimal', '_decimal',
    'PIL.AvifImagePlugin', 'PIL._avif',
    'PIL.WebPImagePlugin', 'PIL._webp',
    'PIL.ImageCms', 'PIL._imagingcms',
    'PIL.TiffImagePlugin', 'PIL.PdfImagePlugin', 'PIL.PdfParser', 'PIL.PsdImagePlugin',
    'PIL.EpsImagePlugin', 'PIL.FpxImagePlugin', 'PIL.MicImagePlugin', 'PIL.MpoImagePlugin',
    'PIL.PalmImagePlugin', 'PIL.PcxImagePlugin', 'PIL.PixarImagePlugin', 'PIL.SpiderImagePlugin',
    'PIL.SunImagePlugin', 'PIL.TgaImagePlugin', 'PIL.WmfImagePlugin', 'PIL.XVThumbImagePlugin',
    'PIL.XbmImagePlugin', 'PIL.XpmImagePlugin', 'PIL.BlpImagePlugin', 'PIL.BufrStubImagePlugin',
    'PIL.CurImagePlugin', 'PIL.DcxImagePlugin', 'PIL.DdsImagePlugin', 'PIL.FitsImagePlugin',
    'PIL.FliImagePlugin', 'PIL.FtexImagePlugin', 'PIL.GbrImagePlugin', 'PIL.GdImageFile',
    'PIL.GribStubImagePlugin', 'PIL.Hdf5StubImagePlugin', 'PIL.IcnsImagePlugin',
    'PIL.ImImagePlugin', 'PIL.ImtImagePlugin', 'PIL.IptcImagePlugin', 'PIL.McIdasImagePlugin',
    'PIL.MpegImagePlugin', 'PIL.MspImagePlugin', 'PIL.PcdImagePlugin', 'PIL.PyAccess',
    'PIL.QoiImagePlugin', 'PIL.SgiImagePlugin', 'PIL.WalImageFile',
]

a = Analysis(
    [str(BASE_DIR / 'main.py')],
    pathex=[str(BASE_DIR)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=EXCLUDED_MODULES,
    noarchive=False,
    optimize=2,
)

EXCLUDED_BIN_SUBSTRINGS = (
    'numpy',
    'libscipy_openblas',
    '_avif',
    '_webp',
    '_imagingcms',
    'libcrypto',
    'libssl',
    '_ssl.pyd',
    '_hashlib.pyd',
    '_decimal.pyd',
    '_sqlite3.pyd',
    'sqlite3.dll',
    '_yaml',
    'charset_normalizer',
    '_lzma.pyd',
    '_bz2.pyd',
    '_zstd.pyd',
)

a.binaries = [
    b for b in a.binaries
    if not any(sub in b[0].lower() for sub in EXCLUDED_BIN_SUBSTRINGS)
]

EXCLUDED_DATA_PREFIXES = (
    '_tcl_data\\tzdata',
    '_tcl_data\\msgs',
    '_tk_data\\images',
    '_tk_data\\msgs',
)

EXCLUDED_ENCODINGS = {
    'cp936.enc', 'cp949.enc', 'cp950.enc', 'cp932.enc',
    'gb12345.enc', 'gb2312.enc', 'gb2312-raw.enc', 'big5.enc',
    'jis0208.enc', 'jis0201.enc', 'jis0212.enc', 'ksc5601.enc',
    'euc-jp.enc', 'euc-kr.enc', 'euc-cn.enc', 'shiftjis.enc',
    'cns11643.enc', 'iso2022-jp.enc', 'iso2022-kr.enc',
}

def _keep_data(item):
    dest = item[0].replace('/', '\\').lower()
    if any(dest.startswith(prefix) for prefix in EXCLUDED_DATA_PREFIXES):
        return False
    if '.dist-info' in dest:
        return False
    if dest.startswith('_tcl_data\\encoding\\') and os.path.basename(dest) in EXCLUDED_ENCODINGS:
        return False
    return True

a.datas = [d for d in a.datas if _keep_data(d)]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Shalbny',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=[str(BASE_DIR / 'assets' / 'icon.ico')],
)

