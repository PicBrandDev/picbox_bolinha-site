"""Reconstroi tudo da Maquina A: params.json -> verificacao/exportacao de todas as pecas -> montagem -> relatorios.
Uso (de dentro de cad_py/): python tools/build_all.py"""
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PY = sys.executable
sys.path.insert(0, str(RAIZ))
from maquina_a import montagem as MT  # noqa: E402

subprocess.run(["node", str(RAIZ / "tools" / "params_to_json.mjs")], check=True)
subprocess.run([PY, "-m", "maquina_a.verifica", *MT.PECAS], cwd=RAIZ, check=True)
subprocess.run([PY, "-m", "maquina_a.assembly"], cwd=RAIZ, check=True)
subprocess.run([PY, str(RAIZ / "tools" / "render_berco.py"), str(RAIZ / "maquina_a" / "out" / "png")], cwd=RAIZ, check=True)
subprocess.run([PY, str(RAIZ / "tools" / "relatorio.py")], cwd=RAIZ, check=True)
