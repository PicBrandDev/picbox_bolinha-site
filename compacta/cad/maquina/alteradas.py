"""Monta compacta/imprimir/ALTERADAS_R1.x/ (+ .zip) so com as pecas que mudaram em cada revisao. Chamado no fim de publicar.py."""
import shutil
import zipfile
from pathlib import Path

import trimesh

AQUI = Path(__file__).parent
IMP = AQUI.parents[1] / "imprimir"
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
- Carro A e Carro B: no lugar dos dentes impressos, uma presilha para o fixador de correia
  de aluminio (40 x 9 x 5). O fixador fica EM PE, com a face dentada direto na face dentada
  da correia; as costas lisas da correia encostam na parede da presilha. Um M3x16 entra de
  frente pelo furo do meio do fixador (entre as duas pontas da correia) e a porca M3, presa
  na fenda da presilha (entra por baixo), aperta tudo. Aperte com a tensora solta, afastando
  o ramo da frente com o dedo; depois estique na tensora do bloco direito.
  A face esquerda da presilha aperta o fim de curso (casa em X = -146).
- Bloco esquerdo: ganhou o braco que segura o fim de curso KW10 de cada eixo
  (2 parafusos M2x12).
- Carro A: copo impresso em volta do ima + arruela M10 de aco colada na face de baixo.
  A bola encaixa 1,1 mm no furo da arruela e fica centrada.
- Anel: 0,7 mm mais alto para acompanhar a nova altura da bola.
- Elevador: sem mudanca.

COMPRAR / SEPARAR
- 2 fixadores de correia GT2 de aluminio (os da foto) + 2 M3x16 + 2 porcas M3
- 1 arruela M10 lisa de ACO comum (nao inox, inox nao gruda no ima)
- 1 par de barreira infravermelha 5 mm (emissor + receptor com saida digital)
- 4 fins de curso KW10 (eixo A, eixo B, elevador embaixo e em cima) + 8 M2x12

Onde fica cada coisa: pagina/PICBOX_novidades_R1.1.html
"""


LEIA_12 = """PICBOX COMPACTA - PECAS ALTERADAS (R1.2) - elevador

Imprima so estas. Elas substituem as de mesmo nome (Cabine da mesa A1, Suporte do motor e Rampa da mesa A3).
PETG, bico 0,4, camada 0,16 (por causa das buchas), 4 perimetros, 25%. Nao use orientacao automatica.

A_impressora_grande__elevador_R1.2.stl   (impressora A, uma mesa so, ~6 h)
   - Cabine            -> suporte em arvore so embaixo do bloco da correia
   - Rampa
   - Suporte do motor  (de cabeca para baixo, placa na mesa, sem suporte)
   - 4 buchas da polia do N20 (2 de reserva) -> 100% de preenchimento
   Aba (brim) de 5 mm. Se o fatiador juntar tudo, use 'Dividir em objetos'.

pecas_avulsas/ = as mesmas pecas, uma por arquivo.

O QUE MUDOU
- Cabine: a bola caia 3,5 mm da cabine para a rampa porque o fim de curso de cima
  so disparava 3 mm acima do ponto de entrega. O C de fora (lado direito, o que aperta
  a alavanca) ficou 2,5 mm mais alto: a cabine para 2,5 mm mais baixo e o degrau cai
  para 1 mm. A guia de cima e o fim de curso nao mudam. Se ainda sobrar degrau, dobre
  de leve a alavanca do KW10 de cima para baixo.
- Rampa: piso do bolso 3 mm mais largo para fora (X 186 em vez de 189), batente junto.
  A tira de EVA do batente agora tem 20 mm de largura (era 17).
- Suporte do motor: placa reforcada (10 mm na frente, travessa atras do motor, nervuras
  de 12 mm dos lados), paredes do abraco do motor de 3 mm, orelha da parede presa na
  placa por um braco e 2 almas, e 2 parafusos de madeira na parede (era 1).
- Bucha da polia do N20: furo redondo de 3,2 mm (serve no eixo redondo ou com lado chato).

COMPRAR / SEPARAR
- +1 parafuso de madeira 3,5x16 para a orelha do suporte do motor
"""


def mesa(itens, nome, lado, d):
    ms, x, y, linha = [], 0.0, 0.0, 0.0
    for f in itens:
        m = trimesh.load(IMP / "pecas_avulsas" / f"{f}.stl", force="mesh")
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
    t.export(d / nome)


def pacote(rev, avulsas, itens_mesa, nome_mesa, leia, imagens=None):
    d, zp = IMP / f"ALTERADAS_{rev}", IMP / f"PICBOX_alteradas_{rev}.zip"
    shutil.rmtree(d, ignore_errors=True)
    (d / "pecas_avulsas").mkdir(parents=True)
    for f in avulsas:
        shutil.copy2(IMP / "pecas_avulsas" / f"{f}.stl", d / "pecas_avulsas")
    mesa(itens_mesa, nome_mesa, 260, d)
    (d / "LEIA-ME.txt").write_text(leia, encoding="utf8")
    if imagens and imagens.exists():                       # imagens das mudancas (render_r12.py)
        (d / "imagens").mkdir()
        for f in sorted(imagens.glob("*.png")):
            shutil.copy2(f, d / "imagens" / f.name)
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(d.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(IMP).as_posix())
    print("ok", zp.name, zp.stat().st_size // 1024, "KB")


def main():
    pacote("R1.1", AVULSAS, ["carro_a", "carro_b", "anel", "bloco_esquerdo__x2", "bloco_esquerdo__x2"],
           "A_impressora_grande__todas_as_alteradas.stl", LEIA)
    pacote("R1.2", ["cabine", "rampa", "suporte_do_motor", "bucha_da_polia_do_n20__x4"],
           ["suporte_do_motor", "rampa", "cabine", "bucha_da_polia_do_n20__x4"], "A_impressora_grande__elevador_R1.2.stl", LEIA_12,
           imagens=AQUI / "saida" / "imagens_r12")


if __name__ == "__main__":
    main()
