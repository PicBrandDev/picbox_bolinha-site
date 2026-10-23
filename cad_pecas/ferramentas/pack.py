"""Empacota os entregaveis da Maquina A num zip (fora do git). Uso (de dentro de cad_pecas/): python ferramentas/pack.py"""
import zipfile
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
S = RAIZ / "saidas"
destino = S / f"picbox_maquina_a_{date.today():%Y%m%d}.zip"
with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(RAIZ / "README.md", "README.md")
    for p in sorted((RAIZ / "docs").glob("*.md")):
        z.write(p, f"docs/{p.name}")
    for sub in ["stl_para_imprimir", "step", "montagem", "imagens/explicativas"]:
        for p in sorted((S / sub).rglob("*")):
            if p.is_file():
                z.write(p, str(p.relative_to(S)))
    if (S / "visualizador.html").exists():
        z.write(S / "visualizador.html", "visualizador.html")
print(destino, round(destino.stat().st_size / 1e6, 1), "MB")
