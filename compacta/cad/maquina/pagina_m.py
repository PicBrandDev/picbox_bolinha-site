"""Gera a pagina da maquina completa (3D + pecas + impressao + checagens + montagem).

  python pagina_m.py saida/picbox_compacta_r1.html
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
    1: "Base e guia de baixo do elevador (na bancada, depois no piso do gabinete)",
    2: "Cabine nos trilhos impressos",
    3: "Guia de cima do elevador",
    4: "Polia de baixo do elevador",
    5: "Suporte do motor N20 e orelha na parede direita",
    6: "Correia do elevador",
    7: "Tubos do elevador",
    8: "Fila, comporta (servo) e rampa com o bolso de pega",
    9: "Blocos de ponta dos eixos nas paredes (com os fins de curso)",
    10: "Perfis 2020 com trilho MGN12 nos blocos",
    11: "Motores NEMA 17 com suporte e polias tensoras",
    12: "Carros A e B nos patins, correias nas presilhas, eletroima",
    13: "Anel no carro B, esteiras porta-cabo, prateleira e ganchos",
    14: "Fila esquerda, bandejas e EVA",
}

NOTAS_ETAPA = {
    9: "Aparafuse o fim de curso KW10 no braco do bloco esquerdo na bancada (2 M2x12). Prenda cada bloco na parede com "
       "2 parafusos de madeira por dentro do bloco, antes de entrar o perfil. Altura do centro do perfil: 405 (cima) e 81 (baixo).",
    10: "Na bancada: corte os perfis em 400 mm e prenda o trilho MGN12 de 400 na fenda de tras com 16 M3x8 + porca martelo, "
        "usando o gabarito do trilho. O trilho fica para tras (lado da tela). Encaixe o perfil nas luvas e aperte 2 M5x10 + "
        "martelo pela frente de cada luva.",
    11: "Motor no suporte na bancada (4 M3x8), polia GT2 20T no eixo com a face de cima 2 mm abaixo do perfil. Suporte de cima: "
        "3 parafusos de madeira na parede esquerda. Suporte de baixo: 2 parafusos de madeira no piso. Tensora no bloco direito "
        "com M5x25 e porca nylon, solta no rasgo.",
    12: "Carro A: eletroima por baixo da prateleira com 1 M3x8 por cima, kapton na face. Cada carro leva 4 M3x8 no patim. "
        "Correia: ponta da esquerda na fenda dentada vindo do motor, contorna a tensora, ponta da direita na mesma fenda. "
        "Estique puxando a tensora no rasgo e aperte; 1 abracadeira de nylon em volta da presilha.",
    13: "Anel: LED IR de um lado e fototransistor do outro (cola quente). Costas do anel na placa do carro B com 4 M3x12 + "
        "porca. Esteiras: ponta movel no carro, ponta fixa na prateleira (A) ou no piso (B).",
    14: "Fila esquerda encostada na direita em X -30. Bandejas: 2 parafusos de madeira cada, pelo furo de 9 mm da placa; "
        "depois cole o EVA 5 mm por cima (cobre os furos) e a tira de EVA 5 mm no batente do bolso.",
}

FIRMWARE = [
    "Casa dos eixos: os dois carros andam para a esquerda devagar ate o fim de curso KW10. A posicao zero e o patim em X -165.",
    "Pega: o carro A vai ate X +166,3 (ima em X 192,3) so com a cabine do elevador ja parada em cima e a bola no bolso. "
    "Liga o ima, espera 150 ms, volta para o jogo. O elevador so entrega a proxima bola depois que o carro A saiu.",
    "Jogo: carro A em seno de +-120 em 2,4 s (ate 314 mm/s), carro B em +-120 em 3,1 s. O botao corta o ima "
    "(MOSFET + TVS 33 V). Soltar so com o ima entre -120 e +120.",
    "Acerto: a barreira IR do anel (Z 95,4) ve a bola. Sem IR em 400 ms depois de soltar = erro.",
    "Elevador (do R0.6): N20 a no maximo 50% nos ultimos 20 mm e corte em 1 s sem fim de curso; L9110S em freio na espera; "
    "servo SG90 no buck de 5 V.",
    "TMC2209: corrente 0,6 A e StallGuard desligado (os fins de curso fazem a casa). Aceleracao de no maximo 1500 mm/s2.",
]

RISCOS = [
    ("Pega do eletroima a 1 mm", "Ima P20/15 com kapton puxando a bola de 1 mm de distancia. Teste na bancada primeiro, com a "
     "rampa e o carro A montados: se nao puxar sempre, baixe o perfil de cima 0,5 mm (furos dos blocos tem folga) ou tire o kapton."),
    ("Momento no patim MGN12H do carro B", "Na batida da bola na borda do anel, FS 1,7 contra o limite estatico do catalogo. "
     "E um pico curto; se o patim ficar com folga, troque o patim (o trilho continua)."),
    ("Ruido e quique da bola de aco", "EVA 5 mm na bandeja e no batente do bolso. Bola que bate na borda do anel pode pular "
     "longe: o labio da frente tem 18 mm e a parede de tras da fila vai ate Z 105."),
    ("Esteiras porta-cabo", "Medidas para 7x7 com raio 18-20. Se a de voces for maior, a de baixo ainda cabe; a de cima precisa "
     "de 2 mm a mais de prateleira."),
    ("Fins de curso", "Sao 4 KW10 no total (2 no elevador, 2 nos eixos). Voces tinham 3: falta 1 (ou use o fim de curso da maquina antiga)."),
]


IMAGENS = [("01_geral.png", "Montagem completa"), ("02_frente.png", "De frente, como o jogador vê"),
           ("03_lado.png", "Lado direito (a tela fica à direita)"), ("04_pega.png", "Pega da bola no bolso"),
           ("05_elevador_topo.png", "Elevador no topo, entregando a bola"), ("06_comporta.png", "Comporta e cabine embaixo"),
           ("07_anel.png", "Carro B, anel e bandeja")]

CABOS = [
    ("Motor NEMA 17 de cima", "sai pelo furo da aba do suporte", "parede esquerda, Y 22, Z 312, Ø10"),
    ("Fim de curso do eixo de cima", "do bloco esquerdo de cima", "parede esquerda, Y 52, Z 385, Ø8"),
    ("Eletroímã (2 fios)", "dentro da esteira A até a ponta fixa (X −13), depois pela prateleira até a esquerda",
     "parede esquerda, Y 92, Z 404, Ø8"),
    ("Motor NEMA 17 de baixo + fim de curso do eixo de baixo", "furo na aba do suporte de baixo", "parede esquerda, Y 47, Z 25, Ø8"),
    ("Barreira IR do anel (4 fios)", "dentro da esteira B até a ponta fixa no piso (X −2,5), depois pelo piso da frente",
     "piso, X −150, Y 6, Ø10"),
    ("Servo da comporta", "pelo piso, embaixo da bandeja", "piso, X 100, Y 84, Ø8"),
    ("Motor N20 + fim de curso de cima do elevador", "do topo da coluna", "parede direita, Y 162, Z 404, Ø10"),
    ("Sensor do bolso (TCRT5000)", "desce pelo canal embaixo da rampa", "parede direita, Y 72, Z 334, Ø6"),
    ("Fim de curso de baixo do elevador", "do pé da guia", "parede direita, Y 174,5, Z 10, Ø8"),
]

FAQ = [
    ("O suporte do motor é robusto?",
     "Sim. Suporte do NEMA de cima: aba de 4,5 mm na parede com 3 parafusos de madeira e uma nervura de 35 mm. O parafuso mais "
     "carregado tem FS 5,7 no uso e 1,8 com o motor travado; a primeira vibração fica perto de 390 Hz, longe do motor. "
     "Suporte de baixo: antes eram só 2 parafusos no piso (FS 1,3 com o motor travado); agora tem mais 2 na parede (FS 3,5). "
     "O N20 do elevador foi conferido no R0.6."),
    ("Os sensores e os cabos estão na montagem?",
     "Sensores: 4 fins de curso KW10 (2 no elevador, 1 em cada eixo), a barreira IR do anel e um sensor novo no bolso, "
     "que confirma que a bola chegou e que o ímã a levou. Os cabos dos carros correm dentro das esteiras porta-cabo. O "
     "resto sai por furos nas paredes e no piso, perto de cada componente, porque a eletrônica fica fora da caixa (tabela abaixo)."),
    ("Onde as bolas ficam guardadas?",
     "Na fila, a calha do fundo. Cabem 14 bolas e a máquina usa 8: 1 no carro A, 1 na cabine e até 6 na fila. A fila "
     "desce 4° para a direita até a comporta."),
    ("O que garante que a bola faz o caminho todo, igual toda vez?",
     "A bandeja cai 4° para o fundo e 2,5° para a esquerda, então toda bola rola até a fila. A checagem testou 287 pontos "
     "de queda e 98 trajetórias de soltura, e todas chegaram. Ela só entra na fila à esquerda de X 40, longe da comporta. "
     "O lábio da frente tem 18 mm, a parede de trás da fila vai até Z 105 e o EVA de 5 mm corta o quique. "
     "Risco: se a frente do gabinete não tiver vidro, uma bola que bate na borda do anel pode pular para fora."),
    ("Como o eletroímã pega a bola?",
     "O elevador entrega a bola no bolso. O piso do bolso cai 1,5° para a direita e 6° para a frente, então a bola sempre para "
     "no mesmo ponto, encostada na parede da direita e no EVA da frente. O carro A para com o ímã 1 mm acima dela, 1 mm à "
     "esquerda e 1 mm atrás. Ao ligar, o ímã puxa a bola 1 mm para cima e ela desencosta das duas paredes. O sensor do bolso "
     "confirma que a bola saiu."),
    ("Como a bola é solta?",
     "Um MOSFET corta o ímã, com um TVS de 33 V para o campo cair em poucos milissegundos. A película de kapton na face do ímã "
     "evita que a bola fique grudada pelo magnetismo que sobra. Ela cai 250 mm até o topo do anel."),
    ("O curso dos eixos alcança a pega e o jogo?",
     "Sim. O patim do carro A anda de X −165 (fim de curso) a X +166,3, o que leva o ímã de X −139 a X +192,3: cobre o jogo "
     "(±120) e a pega (X 192,3). O carro B anda de −165 a +120. A varredura conferiu 112 posições do A e 97 do B sem nada encostar."),
    ("Como o elevador segura a bola e solta lá em cima?",
     "A bola viaja no berço da cabine, que é inclinado 8° para a frente. Na subida, a parede da frente do tubo segura a bola. "
     "No topo o tubo acaba, o piso do berço fica 0,5 mm acima do começo da rampa e a bola rola sozinha para a rampa e dela "
     "para o bolso. A comporta embaixo só deixa entrar uma bola por vez."),
    ("O que mais pode dar errado, e o que o programa faz?",
     "O carro A só vai buscar a bola depois que o fim de curso de cima do elevador avisa que a cabine chegou e o sensor do bolso "
     "vê a bola. Se depois de ligar o ímã o sensor ainda vir a bola, a pega falhou: o carro tenta de novo. Se a barreira IR "
     "do anel não vê a bola em 400 ms depois de soltar, é erro. Os eixos fazem a casa nos fins de curso a cada ligação."),
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
    """Pecas novas/alteradas da R1.1 e pontos de vista para o botao 'Novidades R1.1'."""
    casa, xe, yf = m.c_casa, m.c_casa + L.FIX[0] - 2, 28.37 - 0.7 - 4.5
    zcA, zcB = m.zpA - 22, m.zpB - 22
    f = lambda nome, alvo, d, a, b, txt: dict(nome=nome, alvo=[round(v, 2) for v in alvo], dir=d, a=round(a, 2), b=round(b, 2), txt=txt)
    return dict(
        compradas=["Fixador de correia", "Arruela M10 de aco", "Fim de curso", "LED IR / fototransistor 5 mm"],
        alteradas=["Carro A", "Carro B", "Anel", "Bloco esquerdo"],
        focos=[
            f("Fixador carro A", (casa - 6, yf, zcA), (-0.3, -0.8, 1.0), casa + m.dA, 0,
              "Fixador de alumínio 40 × 9 × 5 deitado no bolso da presilha; a correia passa entre ele e a parede, as duas pontas se encontram no meio; M3x12 + porca."),
            f("Fixador carro B", (casa - 6, yf, zcB), (-0.3, -0.8, 1.0), 0, casa,
              "Igual ao do carro A, no eixo de baixo."),
            f("Fim de curso A", (xe, 36, m.zpA - 20), (0.25, -1.0, 0.55), casa + m.dA, 0,
              f"KW10 no braço do bloco esquerdo (2 M2x12). Na casa (X {casa:.0f}) a presilha aperta a alavanca."),
            f("Fim de curso B", (xe, 36, m.zpB - 20), (0.25, -1.0, 0.55), 0, casa,
              "Igual ao do eixo A, no bloco esquerdo de baixo."),
            f("Arruela no ímã", (m.x_pega, m.y_bola, m.face_ima), (-0.45, -1.0, 0.12), m.x_pega, 0,
              "Arruela M10 de aço colada embaixo do ímã, dentro do copo impresso. A bola sobe e encaixa 1,1 mm no furo."),
            f("Barreira IR", (0, m.y_bola, m.zb - 14.5), (-0.5, -1.0, 0.7), casa + m.dA, 0,
              "Par emissor/receptor 5 mm pronto, nos dois furos laterais do anel (os mesmos de antes)."),
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
    main(sys.argv[1] if len(sys.argv) > 1 else str(AQUI / "saida" / "picbox_compacta_r1.html"))
