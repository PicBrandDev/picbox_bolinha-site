"""R2: LEIA-ME da revisao + zip de tudo em compacta/imprimir/ (as funcoes de pacote parcial ficam para as proximas). Chamado no fim de publicar.py."""
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


LEIA_R2 = """PICBOX COMPACTA R2 - gabinete 440 x 430 x 230 (livre, tela no fundo)

IMPRIMIR TUDO DE NOVO: o gabinete mudou de tamanho, entao quase todas as pecas mudaram de
medida. As mesas prontas estao nas pastas A_impressora_grande, B_creality_1 e C_creality_2
(ORDEM_DE_IMPRESSAO.txt). Comece pela A1 (cabine + carro A): e o teste das folgas novas.
PETG, bico 0,4, camada 0,2, 4 perimetros, 25%. Nao use orientacao automatica.
As 2 torres: aba (brim) de 5 mm, sem suporte (a de cima ja vem de cabeca para baixo).
A bucha da polia do N20 NAO e mais usada. A polia de cima (R2.2) tem pecas pequenas proprias na pasta
polia_de_cima/ (adaptador N20-M5, espacador e arruela: ~25 min, 100%) - veja polia_de_cima/LEIA.txt.
TORRE DE CIMA JA IMPRESSA: corte a tira do teto entre o encaixe da frente e a janela (4,5 mm) - o cubo da polia bate ali.

O QUE MUDOU
- PECAS JUNTADAS (de 29 para 19 arquivos de impressao, menos parafusos e encaixes):
  bloco esquerdo + suporte do NEMA (1 por eixo), anel + carro B, suporte do servo + fila,
  prateleira + 3 ganchos + ponta fixa da esteira A (2 metades com 2 ganchos cada).
- Elevador: 2 pecas (torre de baixo e torre de cima) no lugar de base, 2 guias, 2 tubos,
  suporte do motor, espacador e batente. Motor, correia, trilhos, polias, sensores e
  frente do tubo ficam na propria torre. As 2 encaixam por 3 pinos + 4 M3x8.
- Cabine: 1 mm de folga por lado nos trilhos em T (era 0,5), C de 50 mm de altura, 1,5 mm
  ate a frente da torre. A correia prende no FIXADOR DE ALUMINIO (o mesmo dos carros) num
  bolso atras da cabine: as 2 pontas se encontram no meio dele, M3x14 pela direita (pela
  janela da parede direita da torre, com a cabine embaixo) e porca presa atras do fixador.
- Polia de baixo num eixo M5 com rasgo de 6 mm: puxe para baixo e aperte para esticar.
- Polia de cima (R2.2): a polia de 16 mm (cubo para o motor) num parafuso M5x45 com 1 rolamento 625ZZ atras
  (colado na sede) e o eixo do N20 na frente. O N20 gira o M5 por um ADAPTADOR IMPRESSO reforcado (o M5
  rosqueia nele); um espacador de 6,8 atravessa o furo da parede ate o rolamento. O encaixe do rolamento da
  frente fica vazio e a janela do teto vai ate ele. Montagem passo a passo em polia_de_cima/LEIA.txt.
- Sensores do elevador: 2 sensores de fenda sem placa (o da foto, 24,5 mm), presos pelas orelhas no pe e no teto
  da torre. A "bandeira" e um M2x25 rosqueado na cabine: girar ajusta a parada (meia volta
  = 0,25 mm), trava com porca. Os 2 KW10 do elevador vao para os eixos.
- Rampa: presa nos pilares da torre com 4 M3x12 em rasgos de +-4 mm. Ajuste a altura com o
  carro A na pega: a bola deve quase encostar na arruela do ima.
- Eixos: fim de curso de seguranca (KW10) no bloco direito; carro B ganhou um batedor.
  Eixo de cima em Z 410 (era 405).
- Fila 1 grau mais inclinada (5 e 4); bandeja 5 para o fundo, 3,5 / 4 para a esquerda.
- Folgas maiores em tudo: compradas 0,4 mm por lado (era 0,25), furo M3 3,5, madeira 4,5,
  porca M3 presa 6,3. Tudo o que anda fica a 1 mm de tudo (checado no curso inteiro).
- Cabos: canaleta atras da torre (fios do elevador e do bolso) e entalhe de 9 mm no piso,
  em X 30..42, por baixo da fila e da bandeja (fios da esquerda e da frente).
- Corrigido: os pes da fila e as abas da bandeja saiam soltos da peca na R1.

COMPRAR / SEPARAR (alem do que ja tinha na R1.2)
- 1 fixador de correia GT2 de aluminio 40 x 9 x 5 (o 3o, para a cabine) + 1 M3x14 + 1 porca M3
- 2 sensores opticos de fenda sem placa (os da foto) + 2 resistores de 220 ohm (LED) e 2 de 10 k (saida)
- 4 M3x10 + 4 porcas (orelhas dos sensores)
- Polia de cima: 1 rolamento 625ZZ + 1 parafuso Allen M5x45 (DIN 912) + 1 parafuso sem cabeca M3x3 (sem porca)
- 2 M2x25 + 2 porcas M2 (bandeiras)
- 1 M5x30 + 1 porca M5 + 1 porca M5 de nylon + 2 arruelas M5 (eixo da polia de baixo)
- 4 M3x8 (emenda das torres) + 2 M3x8 + 2 porcas (sensores) + 4 M3x12 + 4 porcas (rampa)
- 8 parafusos de madeira 3,5x16 (torre: 2 no piso + 4 na parede; servo/fila: 2) + 2 a mais no teto (agora 4 ganchos)
- Correia GT2 6 mm do elevador: ~860 mm
- 4 KW10 nos eixos (os 2 do elevador + os 2 que ja estavam nos eixos) + 4 M2x12

Onde fica cada coisa: pagina/PICBOX_compacta_visualizacao.html (botao 'O que mudou').
"""


def main():
    """R2: maquina inteira de novo -> LEIA-ME da revisao + zip com todas as mesas e pecas avulsas."""
    for velho in list(IMP.glob("ALTERADAS_*")) + list(IMP.glob("PICBOX_alteradas_*.zip")):
        shutil.rmtree(velho, ignore_errors=True) if velho.is_dir() else velho.unlink()
    (IMP / "LEIA-ME_R2.txt").write_text(LEIA_R2, encoding="utf8")
    zp = IMP / "PICBOX_R2_completa.zip"
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(IMP.rglob("*")):
            if p.is_file() and p != zp and p.suffix in (".stl", ".txt"):
                z.write(p, p.relative_to(IMP).as_posix())
    print("ok", zp.name, zp.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
