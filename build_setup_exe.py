"""
Builder script to generate standalone Windows Installer (Shalbny_Setup.exe)
using PyInstaller.
"""
import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

cmd = [
    sys.executable,
    "-m",
    "PyInstaller",
    "--clean",
    "-y",
    str(BASE_DIR / "Shalbny_Setup.spec")
]

print("Building optimized Shalbny_Setup.exe Installer...")
print("Command:", " ".join(cmd))
subprocess.run(cmd, check=True)
print("\nInstaller built successfully! Output is in dist/Shalbny_Setup.exe")

