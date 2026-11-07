"""Monta compacta/imprimir/ALTERADAS_R1.1/ (+ .zip) so com as pecas que mudaram na R1.1. Chamado no fim de publicar.py."""
import shutil
import zipfile
from pathlib import Path

import trimesh

AQUI = Path(__file__).parent
IMP = AQUI.parents[1] / "imprimir"
D = IMP / "ALTERADAS_R1.1"
ZIP = IMP / "PICBOX_alteradas_R1.1.zip"
AVULSAS = ["carro_a", "carro_b", "anel", "bloco_esquerdo__x2"]

LEIA = """PICBOX COMPACTA - PECAS ALTERADAS (R1.1)

Imprima so estas. Elas substituem as de mesmo nome das mesas A1, A4, B1 e C1.
PETG, bico 0,4, camada 0,2, 4 perimetros, 25%. Nao use orientacao automatica.

A_impressora_grande__todas_as_alteradas.stl   (impressora A, uma mesa so, ~9 h, altura 66 mm)
   - Carro A  -> COM SUPORTE em arvore so embaixo da presilha, da prateleira e da nervura.
   - Carro B
   - Anel
   - Bloco esquerdo x2
   Aba (brim) de 5 mm. Se o fatiador juntar tudo, use 'Dividir em objetos'.

pecas_avulsas/ = as mesmas pecas, uma por arquivo.

O QUE MUDOU
- Carro A e Carro B: no lugar dos dentes impressos, uma presilha com encaixe para o
  fixador de correia de aluminio (40 x 9 x 5). O fixador entra no bolso, a correia
  fica entre ele e a parede (as duas pontas se encontram no meio), e um M3x12 + porca aperta.
  A face esquerda da presilha aperta o fim de curso (casa em X = -146).
- Bloco esquerdo: ganhou o braco que segura o fim de curso KW10 de cada eixo
  (2 parafusos M2x12).
- Carro A: copo impresso em volta do ima + arruela M10 de aco colada na face de baixo.
  A bola encaixa 1,1 mm no furo da arruela e fica centrada.
- Anel: 0,7 mm mais alto para acompanhar a nova altura da bola.
- Elevador: sem mudanca.

COMPRAR / SEPARAR
- 2 fixadores de correia GT2 de aluminio (os da foto) + 2 M3x12 + 2 porcas M3
- 1 arruela M10 lisa de ACO comum (nao inox, inox nao gruda no ima)
- 1 par de barreira infravermelha 5 mm (emissor + receptor com saida digital)
- 4 fins de curso KW10 (eixo A, eixo B, elevador embaixo e em cima) + 8 M2x12

Onde fica cada coisa: pagina/PICBOX_novidades_R1.1.html
"""


def mesa(itens, nome, lado):
    ms, x, y, linha = [], 0.0, 0.0, 0.0
    for f in itens:
        m = trimesh.load(IMP / "pecas_avulsas" / f"{f}.stl")
        m.apply_translation(-m.bounds[0])
        e = m.extents
        if x + e[0] > lado - 10:
            x, y, linha = 0.0, y + linha + 8, 0.0
        m.apply_translation([x + 5, y + 5, 0])
        x += e[0] + 8
        linha = max(linha, e[1])
        ms.append(m)
    t = trimesh.util.concatenate(ms)
    t.apply_translation([lado / 2 - t.bounds[:, 0].mean(), lado / 2 - t.bounds[:, 1].mean(), 0])
    assert t.bounds[1][0] < lado and t.bounds[1][1] < lado and t.bounds[0].min() >= 0
    t.export(D / nome)


def main():
    shutil.rmtree(D, ignore_errors=True)
    (D / "pecas_avulsas").mkdir(parents=True)
    for f in AVULSAS:
        shutil.copy2(IMP / "pecas_avulsas" / f"{f}.stl", D / "pecas_avulsas")
    mesa(["carro_a", "carro_b", "anel", "bloco_esquerdo__x2", "bloco_esquerdo__x2"],
         "A_impressora_grande__todas_as_alteradas.stl", 260)
    (D / "LEIA-ME.txt").write_text(LEIA, encoding="utf8")
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(D.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(IMP).as_posix())
    print("ok", ZIP.name, ZIP.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
