"""Plano de impressao: pecas detalhadas e expostas na impressora grande (A), o resto nas duas Creality (B e C).
Junta pecas na mesma mesa (placas), na ordem da montagem, e grava uma STL por placa ja arrumada.

  python plano.py   ->  saida/placas/*.stl, saida/plano.json, saida/stl/LEIA-ME.txt
"""
import json
import math
from pathlib import Path

import numpy as np
import trimesh

import layout as L

AQUI = Path(__file__).parent
S = AQUI / "saida"
GAP = 8.0

# impressora A (a boa): precisao (encaixes que deslizam, dentes, furos pequenos) e pecas que o jogador ve de perto
NA_A = ["Guia impressa inferior", "Guia impressa superior", "Base", "Espacador", "Suporte do motor", "Suporte do servo",
        "Braco da comporta", "Rampa", "Carro B", "Anel", "Cabine", "Carro A", "Tubo inferior", "Tubo superior"]

FUNCAO = {
    "Base": "Pé do elevador, no piso do gabinete. Segura a guia de baixo e a polia de baixo (porca presa na bochecha). "
            "Tem o batente onde a cabine para embaixo.",
    "Guia impressa inferior": "Metade de baixo do trilho do elevador: dois trilhos em T por onde a cabine desliza. "
                              "Precisa sair reta e lisa.",
    "Guia impressa superior": "Metade de cima do trilho do elevador. Encaixa na de baixo por 2 pinos e segura o fim de curso de cima.",
    "Cabine": "Leva uma bola por vez para cima. Desliza nos trilhos em T. A correia prende nas duas fendas dentadas do bloco da direita.",
    "Espacador": "Anel que afasta a polia de baixo do pé da guia, para a correia ficar alinhada.",
    "Suporte do motor": "Segura o motor N20 no topo do elevador. A orelha da frente vai parafusada na parede direita.",
    "Tubo inferior": "Parede transparente da frente e dos lados do elevador (metade de baixo). Impede a bola de cair da cabine.",
    "Tubo superior": "Metade de cima do tubo. No topo, prende no suporte do motor.",
    "Fila": "Calha onde as bolas esperam a vez de subir. Desce para a direita até a comporta. Na frente, à esquerda de X 40, "
            "tem um lábio baixo por onde a bola entra vindo da bandeja.",
    "Fila esquerda": "Continuação da fila até a parede esquerda. Recebe as bolas que caem no lado esquerdo da bandeja.",
    "Rampa": "Recebe a bola que sai da cabine lá em cima e a leva rolando até o bolso, onde o ímã do carro A pega. "
             "O piso cai para a direita para a bola encostar sempre no mesmo lugar.",
    "Suporte do servo": "Segura o servo SG90 que mexe a comporta, no piso, na frente da fila.",
    "Braco da comporta": "Braço no servo com a lâmina que deixa passar uma bola por vez para a cabine. A ponta da lâmina "
                         "tem 0,8 mm (por isso imprimir 3 e escolher a melhor).",
    "Bloco esquerdo": "Prende a ponta esquerda do perfil 2020 na parede esquerda. Leva o fim de curso KW10 que dá a posição "
                      "zero do carro. São 2 iguais: eixo de cima e de baixo.",
    "Bloco direito": "Prende a ponta direita do perfil na parede direita. Leva a polia tensora da correia, num rasgo para "
                     "esticar. São 2 iguais.",
    "Suporte do NEMA de cima": "Segura o motor NEMA 17 do eixo de cima, com o eixo virado para cima, na parede esquerda.",
    "Suporte do NEMA de baixo": "Segura o motor NEMA 17 do eixo de baixo, apoiado no piso.",
    "Carro A": "Vai parafusado no patim do trilho de cima. Prende a correia na fenda dentada e leva o eletroímã que segura e solta a bola.",
    "Carro B": "Vai parafusado no patim do trilho de baixo. Prende a correia e leva o anel.",
    "Anel": "O alvo do jogo: a bola tem que passar pelo furo de 38 mm. Nos furos laterais vão o LED infravermelho e o "
            "fototransistor que contam o acerto.",
    "Bandeja esquerda": "Piso inclinado que recebe a bola depois da queda e a leva para a fila. O EVA 5 mm vai colado em cima.",
    "Bandeja do meio": "Parte do meio da bandeja (embaixo do anel).",
    "Bandeja direita": "Parte da direita da bandeja. Leva a bola para a esquerda, até a entrada da fila.",
    "Prateleira da esteira": "Apoio deitado da esteira porta-cabo do carro A, perto do teto. São 2 metades.",
    "Gancho da prateleira": "Pendura a prateleira no teto do gabinete. São 3 iguais.",
    "Ponta fixa da esteira": "Onde a ponta parada de cada esteira porta-cabo é parafusada: a A na prateleira e a B no piso.",
}
POR_QUE_POSICAO = {
    "Z": "Impressa como monta: a base dela já é plana e as paredes sobem retas.",
    "Z-": "De cabeça para baixo: a face de cima é a maior e mais plana, então vira a base e nada fica pendurado.",
    "+X": "Deitada sobre a face que encosta na parede: essa face é plana e tudo o mais cresce para cima, sem suporte.",
    "-X": "Deitada sobre a face que encosta na parede (ou na lateral): a face plana vai na mesa.",
    "+Y": "Deitada de costas: a face de trás é plana e comprida, e assim as faces que deslizam ou ficam à vista saem lisas.",
    "-Y": "Em pé sobre a frente: assim as nervuras saem retas, sem suporte, e o piso fica liso.",
}
ESPECIAL = {
    "Guia impressa inferior": "Deitada de costas para os trilhos em T saírem retos e lisos, sem suporte (a aba do T tem só 2 mm).",
    "Guia impressa superior": "Igual à de baixo: de costas, trilhos para cima.",
    "Cabine": "Em pé como monta, sobre a base plana. Só o bloco da correia precisa de suporte embaixo.",
    "Carro A": "De lado: é a única posição em que a prateleira do ímã fica forte (a força passa ao longo das camadas). "
               "Precisa de suporte embaixo da presilha, da prateleira e da nervura, e de aba (brim) de 5 mm.",
    "Tubo inferior": "Deitado com a abertura para baixo: a frente transparente fica lisa, em ponte de 32 mm.",
    "Tubo superior": "Igual ao de baixo.",
    "Fila": "Em pé como monta: as nervuras embaixo do piso seguram o piso inclinado durante a impressão.",
    "Fila esquerda": "Em pé como monta, igual à fila da direita.",
    "Anel": "De cabeça para baixo: a borda do anel (a parte que leva as batidas da bola) sai na mesa, plana e forte.",
    "Braco da comporta": "De cabeça para baixo: o topo da lâmina fica na mesa, então a ponta de 0,8 mm sai inteira.",
}


def empacotar(itens, lado):
    """Prateleiras: cada item (w, h) vai na primeira prateleira em que cabe; devolve posicoes ou None."""
    util = lado - 10.0
    pos, prat = [], []          # prat: [y0, altura, x_livre]
    for w, h in itens:
        ok = False
        for rot in ((w, h), (h, w)):
            ww, hh = rot
            if ww > util or hh > util:
                continue
            for p in prat:
                if hh <= p[1] + 1e-6 and p[2] + ww <= util + 1e-6:
                    pos.append((p[2], p[0], rot != (w, h)))
                    p[2] += ww + GAP
                    ok = True
                    break
            if ok:
                break
            y0 = (prat[-1][0] + prat[-1][1] + GAP) if prat else 0.0
            if y0 + hh <= util + 1e-6:
                prat.append([y0, hh, ww + GAP])
                pos.append((0.0, y0, rot != (w, h)))
                ok = True
                break
        if not ok:
            return None
    return pos


def placas(linhas, lado, teto_h):
    """Agrupa na ordem dada; abre placa nova quando nao cabe ou passaria de teto_h horas."""
    out = []
    atual = []
    for l in linhas:
        for _ in range(l["quantidade"]):
            cand = atual + [l]
            hs = sum(x["horas"] / x["quantidade"] for x in cand) + 0.2
            sup = {x["suporte"].startswith(("sim", "so")) for x in cand}
            if atual and (hs > teto_h or len(sup) > 1 or empacotar([tuple(x["xy"]) for x in cand], lado) is None):
                out.append(atual)
                atual = [l]
            else:
                atual = cand
    if atual:
        out.append(atual)
    return out


def main():
    imp = [l for l in json.loads((S / "impressao.json").read_text(encoding="utf8")) if "erro" not in l]
    for l in imp:
        base = l["peca"]
        for suf in (" esquerda", " direita", " A (prateleira)", " B (piso)"):
            if base.endswith(suf) and base[:-len(suf)] in L.PECAS:
                base = base[:-len(suf)]
        l["base"] = base
        l["etapa"] = L.PECAS.get(base, ("", "", 99))[2]
        l["funcao"] = FUNCAO.get(base, "")
        l["por_que"] = ESPECIAL.get(base, POR_QUE_POSICAO[l["posicao"]])
        l["impressora"] = "A" if base in NA_A else "BC"
        ext = trimesh.load(str(S / "stl" / l["arquivo"]), force="mesh").extents
        l["xy"] = [float(ext[0]), float(ext[1])]          # medida real na mesa (X, Y) da STL
    ordem = lambda l: (l["etapa"], -l["horas"])
    A = sorted([l for l in imp if l["impressora"] == "A"], key=ordem)
    # as pecas que precisam de suporte (cabine e carro A) ficam juntas numa placa, logo depois da primeira
    com_sup = [l for l in A if l["suporte"].startswith(("sim", "so"))]
    sem_sup = [l for l in A if l not in com_sup]
    BC = sorted([l for l in imp if l["impressora"] == "BC"], key=ordem)
    pa = placas(sem_sup, 260, 14.0)
    pl = {"A": pa[:1] + placas(com_sup, 260, 14.0) + pa[1:]}
    # B e C: placas de ate 10 h, distribuidas alternando pela que termina antes
    pbc = placas(BC, 220, 10.0)
    pl["B"], pl["C"] = [], []
    tempo = {"B": 0.0, "C": 0.0}
    for p in pbc:
        k = min(tempo, key=tempo.get)
        pl[k].append(p)
        tempo[k] += sum(x["horas"] / x["quantidade"] for x in p) + 0.2
    # STL de cada placa
    (S / "placas").mkdir(exist_ok=True)
    for f in (S / "placas").glob("*.stl"):
        f.unlink()
    plano = {}
    for k, lista in pl.items():
        lado = 260 if k == "A" else 220
        plano[k] = []
        for i, p in enumerate(lista, 1):
            pos = empacotar([tuple(x["xy"]) for x in p], lado)
            ms = []
            for x, (px, py, girou) in zip(p, pos):
                me = trimesh.load(str(S / "stl" / x["arquivo"]), force="mesh")
                if girou:
                    me.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, (0, 0, 1)))
                lo = me.bounds[0]
                me.apply_translation((5 + px - lo[0] - lado / 2, 5 + py - lo[1] - lado / 2, -lo[2]))
                ms.append(me)
            nome = f"placa_{k}{i}.stl"
            trimesh.util.concatenate(ms).export(str(S / "placas" / nome))
            horas = round(sum(x["horas"] / x["quantidade"] for x in p) + 0.2, 1)
            plano[k].append(dict(n=f"{k}{i}", arquivo=nome, horas=horas, pecas=[x["peca"] for x in p],
                                 suporte=any(x["suporte"].startswith(("sim", "so")) for x in p),
                                 altura=max(x["altura_mm"] for x in p)))
            for x in p:
                x.setdefault("placas", [])
                if f"{k}{i}" not in x["placas"]:
                    x["placas"].append(f"{k}{i}")
    tot = {k: round(sum(p["horas"] for p in v), 1) for k, v in plano.items()}
    (S / "plano.json").write_text(json.dumps(dict(placas=plano, total=tot, pecas=imp), ensure_ascii=False, indent=1),
                                  encoding="utf8")
    # LEIA-ME
    NOME = {"A": "A - impressora grande (a melhor): pecas de precisao e as que ficam a vista",
            "B": "B - Creality 220 x 220", "C": "C - Creality 220 x 220"}
    txt = ["PICBOX compacta R1 - ORDEM DE IMPRESSAO", "",
           "Cada placa_XX.stl ja tem as pecas arrumadas na mesa: e so abrir no fatiador e imprimir.",
           "Imprima na ordem (A1, A2, ...). PETG, bico 0,4, camada 0,2, 4 perimetros, 25% de preenchimento.",
           "Placas marcadas COM SUPORTE: ligue suporte (arvore) so onde precisa e aba (brim) de 5 mm.",
           "As STLs avulsas de cada peca continuam em saida/stl/ (se quiser imprimir uma so de novo).", ""]
    for k in ("A", "B", "C"):
        txt.append(f"IMPRESSORA {NOME[k]}  -  total {tot[k]} h")
        for p in plano[k]:
            txt.append(f"  {p['n']:<4} {p['arquivo']:<16} {p['horas']:>5} h  altura {p['altura']:.0f} mm"
                       f"{'  COM SUPORTE' if p['suporte'] else ''}")
            for x in p["pecas"]:
                txt.append(f"         - {x}")
        txt.append("")
    (S / "stl" / "LEIA-ME.txt").write_text("\n".join(txt), encoding="utf8")
    (S / "placas" / "LEIA-ME.txt").write_text("\n".join(txt), encoding="utf8")
    print("\n".join(txt))


if __name__ == "__main__":
    main()
