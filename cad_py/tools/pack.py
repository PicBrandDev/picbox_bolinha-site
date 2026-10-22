"""Empacota os entregaveis da Maquina A num zip. Uso: python tools/pack.py"""
import zipfile
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
A = RAIZ / "maquina_a"
destino = A / "out" / f"picbox_maquina_a_pecas_{date.today():%Y%m%d}.zip"
with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
    for f in ["README.md"]:
        z.write(RAIZ / f, f)
    for f in ["INVENTARIO.md", "PENDENCIAS.md", "VERIFICACAO.md", "FILA_IMPRESSAO.md", "BOM_FIXACAO.md", "CHANGELOG.md"]:
        if (A / f).exists():
            z.write(A / f, f)
    for sub in ["step", "stl", "png", "glb", "relatorios"]:
        for p in sorted((A / "out" / sub).glob("*")):
            z.write(p, f"{sub}/{p.name}")
    if (A / "out" / "assembly.step").exists():
        z.write(A / "out" / "assembly.step", "assembly.step")
print(destino, round(destino.stat().st_size / 1e6, 1), "MB")
