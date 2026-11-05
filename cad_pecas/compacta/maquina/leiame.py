"""Escreve saida/stl/LEIA-ME.txt: o que vai em cada impressora."""
import json
from pathlib import Path

import pagina_m as PM

AQUI = Path(__file__).parent
imp = [l for l in json.loads((AQUI / "saida" / "impressao.json").read_text(encoding="utf8")) if "erro" not in l]
fila, horas = PM.distribuir(imp)
NOME = {"Z": "em pe, como monta", "Z-": "de cabeca para baixo", "+X": "deitada sobre a face da direita",
        "-X": "deitada sobre a face da esquerda", "+Y": "deitada sobre a face de tras", "-Y": "em pe sobre a face da frente"}
L = ["PICBOX compacta R1 - arquivos para imprimir (PETG, bico 0,4, camada 0,2, 4 perimetros)",
     "As STLs ja estao na posicao de impressao e assentadas em Z 0. __xN no nome = imprimir N copias.",
     "Horas estimadas pelo volume (+-30%).", ""]
for k, t, _ in PM.IMPRESSORAS:
    L.append(f"IMPRESSORA {k} (mesa {t}) - {horas[k]} h")
    for p in fila[k]:
        l = next(x for x in imp if x["peca"] == p)
        L.append(f"  {l['arquivo']:<44} {l['quantidade']}x  {l['horas']:>4} h  {NOME[l['posicao']]}; suporte: {l['suporte']}")
    L.append("")
(AQUI / "saida" / "stl" / "LEIA-ME.txt").write_text("\n".join(L), encoding="utf8")
print("\n".join(L))
