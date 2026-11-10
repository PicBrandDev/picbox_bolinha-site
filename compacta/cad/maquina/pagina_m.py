"""Gera a pagina da maquina completa (3D + pecas + impressao + checagens + montagem).

  python pagina_m.py saida/picbox_compacta.html
"""
import base64
import json
import math
import sys
from pathlib import Path

import layout as L
import pecas as PC

AQUI = Path(__file__).resolve().parent

IMPRESSORAS = (("A", "260 x 260", 260), ("B", "220 x 220", 220), ("C", "220 x 220", 220))

ETAPAS = {
    1: "Torre de baixo, na bancada: polia de baixo no eixo M5 e sensor de fenda de baixo",
    2: "Cabine nos trilhos da torre de baixo, com as 2 bandeiras (M2x25)",
    3: "Torre de cima (motor N20, polia e sensor de cima) encaixada na de baixo",
    4: "Correia do elevador no fixador de aluminio da cabine",
    5: "Torre no gabinete: 2 parafusos de madeira no piso e 4 na parede direita",
    8: "Fila e comporta (servo)",
    9: "Rampa nos pilares da torre; blocos de ponta dos eixos nas paredes (com os 4 fins de curso)",
    10: "Perfis 2020 com trilho MGN12 nos blocos",
    11: "Motores NEMA 17 com suporte e polias tensoras",
    12: "Carros A e B nos patins, correias nos fixadores, eletroima",
    13: "Anel no carro B, esteiras porta-cabo, prateleira e ganchos",
    14: "Fila esquerda, bandejas e EVA",
}

NOTAS_ETAPA = {
    1: "Eixo M5x30 de tras para a frente pela placa de tras (rasgo de 6 mm): porca na frente da placa, arruela, polia, arruela "
       "e porca de nylon; deixe frouxo no alto do rasgo. Sensor de fenda de baixo com a fenda para cima, orelhas no pe: 2 M3x10 "
       "pelos furos das orelhas, porcas por baixo do pe. As pernas passam pelo furo do pe e os fios vao pelo canal de baixo ate a canaleta.",
    2: "Rosqueie as 2 bandeiras (M2x25) nos ressaltos atras da cabine, com uma porca de trava cada: a de baixo com a ponta "
       "para baixo, a de cima com a ponta para cima. Desca a cabine por cima da torre de baixo, um C em cada trilho.",
    3: "Polia de cima: rolamento 625ZZ em cada mancal (frente e tras), eixo de 5 mm por tras atravessando rolamento, polia e "
       "rolamento; a polia aperta no eixo. Acoplamento rigido no eixo do N20, N20 entra pela frente no berco e o acoplamento "
       "aperta no eixo de 5 mm (o motor fica solto: so nao gira). Sensor de cima no teto, fenda para baixo, 2 M3x10 + porca "
       "por cima do teto. Encaixe nos 3 pinos e aperte 2 M3x8 atras e 2 na esquerda.",
    4: "Uma ponta da correia desce da polia do motor, a outra sobe da polia de baixo; as duas se encontram no meio do bolso de "
       "tras da cabine. Fixador de aluminio por cima, dentes nos dentes da correia; porca M3 na fenda atras dele; M3x14 pela "
       "janela da parede direita (cabine embaixo). Depois puxe a polia de baixo para baixo no rasgo e aperte a porca do eixo.",
    5: "A torre fica encostada na parede direita: 2 parafusos de madeira na aba da frente (piso) e 2 em cada orelha. "
       "Os fios saem pela canaleta de tras, embaixo.",
    9: "Rampa: 4 M3x12 de frente nos pilares, porcas nas fendas que descem do teto da torre. Os furos da rampa sao rasgos de "
       "+-4 mm: acerte a altura com o carro A na pega (a bola quase encostando na arruela do ima). Blocos: KW10 da casa no braco "
       "do bloco esquerdo e KW10 de seguranca no do direito (2 M2x12 cada), na bancada. Cada bloco com 2 parafusos de madeira "
       "na parede, antes do perfil. Centro do perfil: Z 410 (cima) e Z 81 (baixo).",
    10: "Na bancada: corte os perfis em 400 mm e prenda o trilho MGN12 de 400 na fenda de tras com 16 M3x8 + porca martelo. "
        "O trilho fica para tras (lado da tela). Encaixe o perfil nas luvas e aperte 2 M5x10 + martelo pela frente de cada luva.",
    11: "Motor no bloco esquerdo na bancada (4 M3x8), polia GT2 20T no eixo. Bloco de cima: 3 parafusos de madeira a mais "
        "na aba do motor. Bloco de baixo: 2 no piso e 2 na parede. Tensora no bloco direito com M5x25 e porca nylon, solta no rasgo.",
    12: "Carro A: eletroima no copo com 1 M3x8 por cima, arruela M10 de aco colada na face. Cada carro leva 4 M3x8 no patim. "
        "Correia: as 2 pontas se encontram no meio do fixador de aluminio; M3x16 de frente, porca na fenda da presilha. "
        "Estique na tensora do bloco direito.",
    13: "Anel (ja vem no carro B): LED IR de um lado e receptor do outro, com cola quente. Prateleira: 2 parafusos de madeira "
        "no teto por gancho. Esteiras: ponta movel no carro, ponta fixa na prateleira (A) ou no piso (B).",
    14: "Fila esquerda encostada na direita em X -30. Bandejas: 2 parafusos de madeira cada, pelo furo da placa; depois cole o "
        "EVA 5 mm por cima (cobre os furos) e a tira de EVA no batente do bolso.",
}

FIRMWARE = [
    "Casa dos eixos: os dois carros andam para a esquerda devagar ate o KW10 da casa (patim em X -146).",
    "Seguranca: o KW10 do bloco direito so aperta se o carro passar do fim do curso (A: 0,8 mm alem da pega; B: no batedor, "
    "a +148). Se apertar, para o motor na hora e refaz a casa.",
    "Pega: o carro A vai ate X +166,3 (ima em X 192,3) so com a cabine parada em cima e o sensor do bolso vendo a bola. "
    "Liga o ima, espera 150 ms, volta para o jogo.",
    "Jogo: carro A em seno de +-120 em 2,4 s (ate 314 mm/s), carro B em +-120. O botao corta o ima (MOSFET + TVS 33 V).",
    "Acerto: a barreira IR do anel ve a bola. Sem IR em 400 ms depois de soltar = erro.",
    "Elevador: sobe ate o sensor de fenda de cima e desce ate o de baixo (sensor sem placa: LED com resistor de 220 ohm e "
    "fototransistor com resistor de 10 k para o 3,3 V; a entrada muda quando a bandeira corta o feixe). "
    "baixo. N20 a 50% nos ultimos 20 mm e corte em 1 s sem sensor; L9110S em freio na espera; servo SG90 no buck de 5 V.",
    "Ajuste fino das paradas: gire a bandeira (M2x25) da cabine. Meia volta = 0,25 mm. Trave com a porca.",
    "TMC2209: corrente 0,6 A e StallGuard desligado (os fins de curso fazem a casa). Aceleracao de no maximo 1500 mm/s2.",
]

RISCOS = [
    ("Pega do eletroima", "O ima chega a 0,6 mm da bola (a bola sobe e encaixa no furo da arruela). Se nao puxar sempre, suba a "
     "rampa nos rasgos dos pilares (ate 4 mm) em vez de mexer no eixo de cima."),
    ("Folga dos trilhos do elevador", "1 mm por lado entre o C da cabine e o T impresso. Se a impressao sair apertada, passe lixa "
     "400 na cabeca do T; se sair folgada demais, a cabine so balanca, nao trava (C de 50 mm de altura)."),
    ("Momento no patim MGN12H do carro B", "Na batida da bola na borda do anel, FS 1,7 contra o limite estatico do catalogo. "
     "E um pico curto; se o patim ficar com folga, troque o patim (o trilho continua)."),
    ("Sensor de fenda", "O desenho usa o sensor da foto (24,5 mm, 2 orelhas). Confira a distancia entre os furos (19 mm no "
     "desenho, os furos tem rasgo de +-1,5 mm), a largura da fenda (5 mm) e a altura total (11 mm). "
     "e o furo da placa pode cair em qualquer lugar do rasgo de 16 mm. Confira antes de imprimir se a fenda e de 5 mm."),
    ("Esteiras porta-cabo", "Medidas para 7x7 com raio 18-20. Se a de voces for maior, a de cima precisa de 2 mm a mais de prateleira."),
]


IMAGENS = [("01_geral.png", "Montagem completa"), ("02_frente.png", "De frente, como o jogador vê"),
           ("03_lado.png", "Lado direito (a tela fica à direita)"), ("04_pega.png", "Pega da bola no bolso"),
           ("05_elevador_topo.png", "Elevador no topo, entregando a bola"), ("06_comporta.png", "Comporta e cabine embaixo"),
           ("07_anel.png", "Carro B, anel e bandeja"), ("08_torre_baixo.png", "Pé da torre: polia de baixo e sensor de fenda"),
           ("09_torre_cima.png", "Topo da torre: motor N20, polia e sensor de fenda"),
           ("10_fixador_cabine.png", "Fixador de alumínio da correia, atrás da cabine")]

CABOS = [
    ("Motor N20 + sensor de fenda de cima", "pela janela de tras no topo da torre, para a canaleta", "desce a canaleta atras da torre ate o piso"),
    ("Sensor de fenda de baixo", "os pinos ja ficam dentro da canaleta", "canaleta atras da torre, no piso"),
    ("Sensor do bolso (TCRT5000)", "canal embaixo da rampa, furo de 7 mm na frente da torre (embaixo do pilar direito), sobe pelo "
     "corredor da direita ate a janela de tras no topo", "canaleta atras da torre"),
    ("Eletroímã (2 fios)", "dentro da esteira A até a ponta fixa, depois pela prateleira até a direita e pela lateral da torre",
     "canaleta atras da torre"),
    ("Fim de curso de segurança (2)", "dos bracos dos blocos direitos, pela parede direita", "atras da torre"),
    ("Motor NEMA 17 de cima + fim de curso da casa A", "furo da aba do suporte, desce pela parede esquerda atras da fila",
     "piso atras da fila, ate a torre"),
    ("Motor NEMA 17 de baixo + fim de curso da casa B", "furo da aba do suporte de baixo, pelo piso da frente (Y 44..50) ate X 36",
     "passa por baixo da bandeja e da fila em X 30..42 (entalhe de 9 mm no piso)"),
    ("Barreira IR do anel (4 fios)", "dentro da esteira B até a ponta fixa no piso, depois pelo piso da frente ate X 36",
     "passa por baixo da bandeja e da fila em X 30..42"),
    ("Servo da comporta", "pelo piso, embaixo da bandeja, ate X 36", "passa por baixo da fila em X 30..42"),
]

FAQ = [
    ("O que mudou na R2?",
     "Gabinete novo (440 × 430 × 230). Peças juntadas: o elevador virou uma torre de 2 peças (antes eram 8); cada bloco "
     "esquerdo já leva o motor NEMA 17; o anel é impresso com o carro B; o suporte do servo com a fila; a prateleira da "
     "esteira com os ganchos e a ponta fixa. De 29 para 19 arquivos de impressão. A cabine corre com 1 mm de folga por lado (era 0,5), a correia prende no "
     "mesmo fixador de alumínio dos carros, os fins de curso do elevador viraram sensores ópticos de fenda com ajuste fino por "
     "parafuso, a rampa sobe e desce em rasgos para acertar a pega, e a fila e a bandeja ganharam 1° a mais de queda."),
    ("Quais folgas a R2 usa?",
     "Peças compradas que entram em peças impressas: 0,4 mm por lado (era 0,25). Furos passantes: M3 3,5, M5 5,6, madeira 4,5. "
     "Porca M3 presa: sextavado de 6,3 entre faces e 3,2 de fundo. Pinos da emenda da torre: 0,3 por lado. Tudo o que anda "
     "fica a pelo menos 1 mm de tudo (era 0,5), checado no curso inteiro."),
    ("Os sensores e os cabos estão na montagem?",
     "Sensores: 4 fins de curso KW10 nos eixos (casa e segurança em cada um), 2 sensores ópticos de fenda no elevador, a "
     "barreira IR do anel e o TCRT5000 do bolso. Os cabos dos carros correm nas esteiras porta-cabo; os do elevador descem "
     "pela canaleta atrás da torre; os do lado esquerdo passam por um entalhe no piso, por baixo da bandeja e da fila "
     "(tabela abaixo). A eletrônica fica fora da caixa."),
    ("Onde as bolas ficam guardadas?",
     "Na fila, a calha do fundo. A máquina usa 8: 1 no carro A, 1 na cabine e até 6 na fila. A fila desce 5° para a direita "
     "até a comporta (4° na parte da esquerda)."),
    ("O que garante que a bola faz o caminho todo, igual toda vez?",
     "A bandeja cai 5° para o fundo e 3,5° para a esquerda (4° na parte da esquerda), então toda bola rola até a fila. A "
     "checagem testou mais de 300 pontos de queda e 98 trajetórias de soltura. Ela só entra na fila à esquerda de X 40, longe "
     "da comporta. O EVA de 5 mm corta o quique."),
    ("Como o eletroímã pega a bola?",
     "O elevador entrega a bola no bolso. O piso do bolso cai 1,5° para a direita e 6° para a frente, então a bola sempre para "
     "no mesmo ponto. O carro A para com a arruela do ímã 0,6 mm acima dela. Ao ligar, a bola sobe e encaixa no furo da "
     "arruela. Se precisar, a rampa sobe ou desce até 4 mm nos rasgos dos pilares."),
    ("Como a bola é solta?",
     "Um MOSFET corta o ímã, com um TVS de 33 V para o campo cair em poucos milissegundos. Ela cai 250 mm até o topo do anel."),
    ("Como o elevador segura a bola e solta lá em cima?",
     "A bola viaja no berço da cabine, inclinado 8° para a frente, encostada na frente da torre. No topo a frente acaba, o "
     "piso do berço fica 1 mm acima do começo da rampa e a bola rola sozinha. Embaixo o berço fica 1,5 mm abaixo do fim da "
     "fila. As duas paradas são ajustadas girando as bandeiras da cabine."),
    ("O que mais pode dar errado, e o que o programa faz?",
     "O carro A só vai buscar a bola depois que o sensor de fenda de cima avisa que a cabine chegou e o sensor do bolso vê a "
     "bola. Se depois de ligar o ímã o sensor ainda vir a bola, a pega falhou: o carro tenta de novo. Se um fim de curso de "
     "segurança apertar, o motor para e o eixo refaz a casa."),
]


def distribuir(linhas):
    fila = {k: [] for k, _, _ in IMPRESSORAS}
    horas = {k: 0.0 for k, _, _ in IMPRESSORAS}
    for l in sorted(linhas, key=lambda l: -l["horas"]):
        retas = [k for k, _, _ in IMPRESSORAS if any(c.startswith(k) and "diagonal" not in c for c in l["cabe"])]
        todas = [k for k, _, _ in IMPRESSORAS if any(c.startswith(k) for c in l["cabe"])]
        k = min(retas or todas, key=lambda k: horas[k])
        fila[k].append(l["peca"])
        horas[k] += l["horas"]
        l["impressora"] = k
    # dentro de cada impressora: na ordem da montagem (o elevador sai primeiro)
    etapa = lambda p: L.PECAS.get(p.split(" esquerda")[0].split(" direita")[0].split(" A (")[0].split(" B (")[0],
                                  ("", "", 99))[2]
    for k in fila:
        fila[k].sort(key=etapa)
    return fila, {k: round(v, 1) for k, v in horas.items()}


def cena(m):
    geo = []
    for e in L.geometria(m):
        if e["peca"] in ("Gabinete", "Tela"):
            continue
        geo.append(dict(n=e["nome"], c=e["corpo"], t=e["tipo"], s=[round(v, 3) for v in e["meio"]],
                        p=[round(v, 3) for v in e["pos"]], q=[round(v, 6) for v in e["quat"]], peca=e["peca"], cor=e["cor"]))
    est = {}
    for k, (a, b) in (("A", m.cA), ("B", m.cB)):
        est[k] = []
        for c in (a, (a + b) / 2, b):
            gk, info = L.esteira_caixas(m, k, c)
            est[k].append(dict(c=c, g=[dict(s=e["meio"], p=e["pos"], q=e["quat"]) for e in gk]))
    return dict(geo=geo, est=est)


def novidades(m):
    """Pecas novas/alteradas da R2 e pontos de vista para o botao 'O que mudou'."""
    import elevador2 as E
    el = m.el
    def f(nome, alvo, d, a, b, txt, z=None, dist=170):
        return dict(nome=nome, alvo=[round(v, 2) for v in alvo], dir=d, a=round(a, 2), b=round(b, 2), txt=txt,
                    z=None if z is None else round(z, 2), dist=dist)
    k0, k1 = el.fix_z
    zf = el.zc_min + (k0 + k1) / 2
    casa = m.c_casa
    return dict(
        compradas=["Sensor de fenda", "Bandeira", "Fixador da cabine", "Fim de curso"],
        alteradas=["Torre inferior", "Torre superior", "Cabine", "Rampa", "Fila", "Fila esquerda", "Bandeja esquerda",
                   "Bandeja do meio", "Bandeja direita", "Bloco direito", "Carro B", "Bloco esquerdo de cima",
                   "Bloco esquerdo de baixo", "Prateleira da esteira"],
        focos=[
            f("Torre do elevador", (192, 165, 215), (-1.0, -0.9, 0.35), -60, 0,
              "O elevador virou 2 peças: a torre de baixo (pé, trilhos, frente, polia de baixo, sensor) e a de cima (motor, "
              "sensor, pilares da rampa). Encaixam por 3 pinos e 4 M3.", z=el.zc_min + 150, dist=430),
            f("Fixador da correia na cabine", (196, 192, zf), (0.9, 0.5, 0.35), -60, 0,
              "Atrás da cabine: o mesmo fixador de alumínio dos carros, em pé, dentes nos dentes da correia. M3x14 pela direita "
              "e porca presa atrás do fixador.", z=el.zc_min, dist=110),
            f("Sensor de fenda de baixo", (E.X_BANDEIRA, E.Y_BANDEIRA, 14), (0.7, 0.8, 0.6), -60, 0,
              "Sensor de fenda (sem placa) preso pelas 2 orelhas no pé, fenda para cima. A bandeira (M2x25 da cabine) entra na fenda: girar o parafuso "
              "ajusta a parada.", z=el.zc_min, dist=110),
            f("Sensor de fenda de cima", (E.X_BANDEIRA, E.Y_BANDEIRA, 416), (0.7, 0.8, -0.3), -60, 0,
              "Igual ao de baixo, pendurado no teto da torre, fenda para baixo.", z=el.zc_max, dist=120),
            f("Motor N20 no topo", (191, 165, 419), (-0.5, -0.9, 0.4), -60, 0,
              "Face da caixa de redução presa por 2 M2 numa placa da própria torre, corpo num berço fechado (não torce).",
              z=el.zc_max, dist=140),
            f("Rampa ajustável", (190, 100, el.z_rampa), (-0.7, -1.0, 0.4), -60, 0,
              "Presa nos pilares da torre por 4 M3 em rasgos de ±4 mm: sobe ou desce para acertar a pega.", z=el.zc_max, dist=170),
            f("Fim de curso de segurança", (m.x_fdc_dir + 6, 36, m.zpA - 25), (0.1, -1.0, 0.5), m.cA[1] - 10, 0,
              "KW10 no braço do bloco direito. O carro A chega a 0,8 mm da alavanca na pega e só aperta se passar dela.",
              dist=110),
            f("Batedor do carro B", (m.cB_seg + 25, 36, m.zpB - 25), (0.1, -1.0, 0.5), casa + m.dA, m.cB_seg - 1.5,
              "O bloco direito é igual nos 2 eixos; o carro B aperta a mesma alavanca 21 mm antes, por este batedor.", dist=110),
            f("Bloco esquerdo + motor", (m.x_motor, 22, m.zpA - 30), (-0.3, -1.0, 0.5), casa + m.dA, 0,
              "Cada bloco esquerdo agora segura o perfil, o motor NEMA 17 e o fim de curso numa peça só.", dist=170),
            f("Anel no carro B", (0, m.y_bola, m.zb), (-0.5, -1.0, 0.7), casa + m.dA, 0,
              "O anel e a barreira infravermelha são impressos junto com o carro B: sem os 4 parafusos das costas.", dist=150),
            f("Passagem de cabos no piso", (36, 140, 5), (-0.4, -1.0, 0.6), -60, 0,
              "Entalhe de 9 mm na fila e na bandeja em X 30..42: os cabos da esquerda e da frente vão para o fundo por baixo.",
              z=el.zc_min, dist=120),
        ])


def main(saida):
    m = L.M()
    el = m.el
    val = json.loads((AQUI / "validacao.json").read_text(encoding="utf8"))
    res = json.loads((AQUI / "resistencia.json").read_text(encoding="utf8"))
    imp = json.loads((AQUI / "saida" / "impressao.json").read_text(encoding="utf8"))
    tst = json.loads((AQUI / "teste_stl.json").read_text(encoding="utf8"))
    var = json.loads((AQUI / "teste_variacoes.json").read_text(encoding="utf8"))
    pl = json.loads((AQUI / "saida" / "plano.json").read_text(encoding="utf8"))
    imp = pl["pecas"]
    fila, horas = pl["placas"], pl["total"]
    pecas = {k: dict(tipo=v[0], mat=v[1], etapa=v[2], fix=v[3]) for k, v in L.PECAS.items()}
    arquivo = {}
    for l in imp:
        base = l["peca"].split(" esquerda")[0].split(" direita")[0].split(" A (")[0].split(" B (")[0]
        arquivo.setdefault(l["peca"], l["arquivo"])
        arquivo.setdefault(base, l["arquivo"])
    fx = L.fixadores(m)
    contagem = {}
    for f in fx:
        contagem[f["tipo"]] = contagem.get(f["tipo"], 0) + 1
    par = val["parafusos"]
    resumo = dict(
        interf=val["interferencias"]["n_ruins"], pares=val["interferencias"]["pares"],
        par_ok=sum(p["ok"] for p in par), par_tot=len(par),
        varr=val["varredura"]["ok"], varr_pos=val["varredura"]["posicoes"],
        bola_ok=all(v.get("ok", True) for v in val["bola"].values()),
        res_ok=sum(c["ok"] for c in res["casos"]), res_tot=len(res["casos"]),
        stl_ok=sum(l["ok"] for l in imp), stl_tot=len(imp),
        malha_inter=len(tst["intersecoes"]["ruins"]), furos_ruins=len(tst["furos"]["ruins"]),
        horas_total=round(sum(l["horas"] for l in imp), 1), massa=round(sum(l["massa_g"] * l["quantidade"] for l in imp)),
    )
    dados = dict(
        cena=cena(m), pecas=pecas, arquivo=arquivo, imp=imp, plano=fila, horas=horas, resumo=resumo,
        bola=val["bola"], janela=val["janela"], res=res, tst=tst, contagem=contagem,
        etapas=[dict(n=k, t=v, nota=NOTAS_ETAPA.get(k, ""), pecas=[p for p, d in pecas.items() if d["etapa"] == k])
                for k, v in ETAPAS.items()],
        firmware=FIRMWARE, riscos=RISCOS, var=var,
        malhas=json.loads((AQUI / "saida" / "malhas.json").read_text(encoding="utf8")),
        imagens=[dict(t=t, src="data:image/png;base64," + base64.b64encode((AQUI / "saida" / "imagens" / a).read_bytes()).decode())
                 for a, t in IMAGENS],
        faq=FAQ, cabos=CABOS,
        novo=novidades(m),
        m=dict(cA=m.cA, cB=m.cB, dA=m.dA, zc=[el.zc_min, el.zc_max], piv=list(el.piv), ang=el.ang_baixa, zs=m.zs, zb=m.zb,
               yb=m.y_bola, r=L.R, x_pega=m.x_pega, bolso=m.bola_bolso.tolist(), curso=m.curso),
    )
    html = (AQUI / "pagina_m.html").read_text(encoding="utf8").replace("__DADOS__", json.dumps(dados, ensure_ascii=False))
    Path(saida).write_text(html, encoding="utf8")
    print("ok", saida, len(html) // 1024, "KB", resumo, horas)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(AQUI / "saida" / "picbox_compacta.html"))
