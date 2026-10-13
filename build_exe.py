"""
PyInstaller build script for Shalbny.
Produces a single standalone executable Shalbny.exe.
"""
import os
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
    str(BASE_DIR / "Shalbny.spec")
]

print("Building optimized Shalbny executable...")
print("Command:", " ".join(cmd))
subprocess.run(cmd, check=True)
print("\nBuild completed successfully! Executable is located in dist/Shalbny.exe")

