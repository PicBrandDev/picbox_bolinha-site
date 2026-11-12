"""Visualizador 3D de arquivo unico da PICBOX compacta (estilo CAD): pecas reais, sensores, mudancas da R2, por que de cada
peca, posicao de impressao, montagem passo a passo. Mouse como o SolidWorks.

  python visualizador.py  ->  compacta/pagina/PICBOX_R2_visualizador_3D.html
(rode depois de pecas.py, plano.py, plano_unica.py, malhas.py e checagem.py)
"""
import json
import math
from pathlib import Path

import numpy as np

import layout as L
import elevador2 as E
import pagina_m as PM

AQUI = Path(__file__).resolve().parent
S = AQUI / "saida"
SAIDA = AQUI.parents[1] / "pagina" / "PICBOX_R2_visualizador_3D.html"

GRUPOS = [
    ("Elevador", ("Torre inferior", "Torre superior", "Cabine", "Rampa", "Motor N20", "Polia do motor", "Polia de baixo",
                  "Adaptador N20-M5", "Parafuso sem cabeca M3", "Parafuso M5 da polia", "Arruela impressa",
                  "Espacador da parede", "Rolamento 625ZZ",
                  "Correia", "Fixador da cabine", "Bandeira", "Sensor de fenda", "Sensor do bolso", "EVA 5 mm")),
    ("Fila e comporta", ("Fila", "Fila esquerda", "Braco da comporta", "Servo")),
    ("Eixo de cima (A)", ("Bloco esquerdo de cima", "Perfil 2020 A", "Trilho MGN12 A", "Patim MGN12H A", "NEMA 17 A",
                          "Polia GT2 20T A", "Polia tensora A", "Correia A", "Carro A", "Eletroima P20/15",
                          "Arruela M10 de aco", "Prateleira da esteira", "Esteira A")),
    ("Eixo de baixo (B)", ("Bloco esquerdo de baixo", "Perfil 2020 B", "Trilho MGN12 B", "Patim MGN12H B", "NEMA 17 B",
                           "Polia GT2 20T B", "Polia tensora B", "Correia B", "Carro B", "LED IR / fototransistor 5 mm",
                           "Ponta fixa da esteira", "Esteira B")),
    ("Os 2 eixos", ("Bloco direito", "Fim de curso", "Fixador de correia")),
    ("Bandeja", ("Bandeja esquerda", "Bandeja do meio", "Bandeja direita")),
]


def r(v, n=2):
    return [round(float(x), n) for x in v]


def sensores(m):
    el = m.el
    xb, yb = E.X_BANDEIRA, E.Y_BANDEIRA
    zA, zB = m.zpA, m.zpB
    sx, sy = L.SENSOR_BOLSO
    return [
        dict(id="fdc_casa_A", nome="Fim de curso da casa · eixo A", tipo="Microchave KW10", corpo="mundo",
             pos=[-181, 35, zA - 20], dir=[1, 0, 0],
             onde="Braço do bloco esquerdo de cima, 2 M2x12. Alavanca virada para +X (para a direita).",
             aciona="A face esquerda da presilha do carro A aperta a alavanca quando o carro chega na casa (patim em X −146).",
             uso="Zero do eixo A a cada ligação (casa devagar para a esquerda)."),
        dict(id="fdc_seg_A", nome="Fim de curso de segurança · eixo A", tipo="Microchave KW10", corpo="mundo",
             pos=[m.x_fdc_dir + 7, 35, zA - 25], dir=[-1, 0, 0],
             onde="Braço do bloco direito de cima, 2 M2x12. Alavanca virada para −X (para a esquerda).",
             aciona="Na pega a presilha fica 0,8 mm da alavanca; só aperta se o carro passar do curso.",
             uso="Para o motor na hora e refaz a casa. Nunca aperta no jogo normal."),
        dict(id="fdc_casa_B", nome="Fim de curso da casa · eixo B", tipo="Microchave KW10", corpo="mundo",
             pos=[-181, 35, zB - 20], dir=[1, 0, 0],
             onde="Braço do bloco esquerdo de baixo. Alavanca para +X.",
             aciona="A presilha do carro B aperta a alavanca na casa (X −146).", uso="Zero do eixo B."),
        dict(id="fdc_seg_B", nome="Fim de curso de segurança · eixo B", tipo="Microchave KW10", corpo="mundo",
             pos=[m.x_fdc_dir + 7, 35, zB - 25], dir=[-1, 0, 0],
             onde="Braço do bloco direito de baixo (o bloco direito é igual nos 2 eixos).",
             aciona=f"O batedor do carro B aperta a alavanca se o carro passar de X +{m.cB_seg - 1.5:.0f} (o jogo vai até +120).",
             uso="Segurança do eixo B."),
        dict(id="fenda_baixo", nome="Sensor de fenda de baixo · elevador", tipo="Sensor de fenda sem placa (tipo ITR9608)", corpo="mundo",
             pos=[xb, yb, E.P.Z_FEIXE_BAIXO], dir=[0, 0, 1],
             onde="No pé da torre, canto de trás à direita, fenda para CIMA, orelhas presas com 2 M3x10 + porca. Feixe ao longo de Y. "
                  "Fios pelo furo do pé e pelo canal de baixo até a canaleta.",
             aciona="A bandeira (parafuso M2x25) embaixo da cabine desce e corta o feixe.",
             uso="Cabine embaixo: o berço fica 1,5 mm abaixo do fim da fila. Girar a bandeira ajusta a parada (meia volta = 0,2 mm)."),
        dict(id="fenda_cima", nome="Sensor de fenda de cima · elevador", tipo="Sensor de fenda sem placa (tipo ITR9608)", corpo="mundo",
             pos=[xb, yb, E.P.Z_FEIXE_CIMA], dir=[0, 0, -1],
             onde="Preso pelas orelhas no teto da torre, fenda para BAIXO, mesmo canto do de baixo. Fios pelo furo e pelo canal do teto.",
             aciona="A bandeira de cima da cabine sobe e corta o feixe.",
             uso="Cabine no topo: o berço fica 1 mm acima do começo da rampa e a bola rola para o bolso."),
        dict(id="bolso", nome="Sensor do bolso", tipo="TCRT5000 (reflexivo)", corpo="mundo",
             pos=[sx, sy, m.z_rampa(sx, sy) - 4], dir=[0, 0, 1],
             onde="Embaixo do piso do bolso da rampa, olhando para CIMA pela janela. Fio pelo canal embaixo da rampa.",
             aciona="Vê a bola parada no bolso.", uso="Só manda o carro A buscar com bola no bolso; confirma que o ímã levou a bola."),
        dict(id="ir_anel", nome="Barreira infravermelha do anel", tipo="Par LED IR + receptor 5 mm", corpo="carroB",
             pos=[0, m.y_bola, m.zb - 14.5], dir=[1, 0, 0],
             onde="Nos 2 furos laterais do anel (carro B), 14,5 mm abaixo da borda. Feixe ao longo de X, atravessando o furo.",
             aciona="A bola que passa dentro do anel corta o feixe.", uso="Conta o acerto. Sem corte em 400 ms depois de soltar = erro."),
    ]


def main():
    m = L.M()
    el = m.el
    plano = json.loads((S / "plano.json").read_text(encoding="utf8"))
    unica = json.loads((S.parent / "saida_unica" / "plano.json").read_text(encoding="utf8"))
    mesa_u = {}
    for p in unica["placas"]["S"]:
        for x in p["pecas"]:
            mesa_u.setdefault(x, [])
            if p["n"] not in mesa_u[x]:
                mesa_u[x].append(p["n"])
    impr = {l["peca"]: l for l in plano["pecas"]}
    # malhas reais
    malhas = []
    for o in json.loads((S / "malhas.json").read_text(encoding="utf8")):
        pc = o["nome"] if o["nome"] in L.PECAS else o["peca"]
        malhas.append(dict(peca=pc, nome=o["nome"], corpo=o["corpo"], copias=o["copias"], v=o["v"], t=o["t"]))
    reais = {x["peca"] for x in malhas}
    # compradas e o resto em caixas
    geo = []
    for e in L.geometria(m):
        tp = L.PECAS.get(e["peca"], ("?",))[0]
        if e["peca"] in ("Gabinete", "Tela") or (tp == "impressa" and e["peca"] in reais):
            continue
        geo.append(dict(n=e["nome"], c=e["corpo"], t=e["tipo"], s=r(e["meio"], 3), p=r(e["pos"], 3), q=r(e["quat"], 6),
                        peca=e["peca"], cor=e["cor"]))
    # fichas das pecas
    grupo = {p: g for g, ps in GRUPOS for p in ps}
    pecas = {}
    for k, (tipo, mat, etapa, fix) in L.PECAS.items():
        if k in ("Gabinete", "Tela"):
            continue
        d = dict(tipo=tipo, mat=mat, etapa=etapa, fix=fix, grupo=grupo.get(k, "Outros"))
        cands = [l for n, l in impr.items() if n == k or n.startswith(k + " ")]
        if cands:
            l = cands[0]
            d.update(funcao=l["funcao"], por_que=l["por_que"], posicao=l["posicao"], suporte=l["suporte"],
                     arquivos=[c["arquivo"] for c in cands], horas=round(sum(c["horas"] for c in cands), 1),
                     massa=round(sum(c["massa_g"] * c["quantidade"] for c in cands)),
                     qtd=sum(c["quantidade"] for c in cands),
                     mesas=sorted({x for c in cands for x in mesa_u.get(c["peca"], [])}))
        pecas[k] = d
    val = json.loads((AQUI / "validacao.json").read_text(encoding="utf8"))
    res = json.loads((AQUI / "resistencia.json").read_text(encoding="utf8"))
    var = json.loads((AQUI / "teste_variacoes.json").read_text(encoding="utf8"))
    resumo = dict(
        interf=val["interferencias"]["n_ruins"], par_ok=sum(p["ok"] for p in val["parafusos"]), par=len(val["parafusos"]),
        varr=val["varredura"]["ok"], bola=all(v.get("ok", True) for v in val["bola"].values()),
        res_ok=sum(c["ok"] for c in res["casos"]), res=len(res["casos"]),
        stl_ok=sum(l["ok"] for l in plano["pecas"]), stl=len(plano["pecas"]),
        var_ok=sum(1 for d in var.values() if d["interferencias"] == 0 and all(d[x] for x in ("bolso", "pega", "levando", "queda", "anel", "bandeja", "fila"))),
        var=len(var), mesas=len(unica["placas"]["S"]), horas=unica["total"]["S"],
        fixadores=len(L.fixadores(m)))
    novo = PM.novidades(m)
    etapas = [dict(n=k, t=v, nota=PM.NOTAS_ETAPA.get(k, ""), pecas=[p for p, d in pecas.items() if d["etapa"] == k])
              for k, v in PM.ETAPAS.items()]
    # etapa 0 (gabinete) e etapas sem nome recebem as pecas que nao estao em nenhuma
    usadas = {p for e in etapas for p in e["pecas"]}
    sobra = [p for p in pecas if p not in usadas]
    if sobra:
        for p in sobra:
            et = min(PM.ETAPAS, key=lambda k: abs(k - pecas[p]["etapa"]))
            next(e for e in etapas if e["n"] == et)["pecas"].append(p)
            pecas[p]["etapa"] = et
    dados = dict(
        malhas=malhas, geo=geo, pecas=pecas, grupos=[g for g, _ in GRUPOS] + ["Outros"], sensores=sensores(m),
        etapas=etapas, novo=novo, resumo=resumo, cabos=PM.CABOS, firmware=PM.FIRMWARE, riscos=PM.RISCOS, faq=PM.FAQ,
        m=dict(cA=r(m.cA), cB=r(m.cB), dA=m.dA, zc=r([el.zc_min, el.zc_max]), piv=r(el.piv), ang=el.ang_baixa, zs=round(m.zs, 2),
               zb=round(m.zb, 2), yb=m.y_bola, r=L.R, bolso=r(m.bola_bolso), curso=m.curso, dZ=m.dZ, gab=[L.GX, L.GY, L.GZ],
               RcA=m.RcA, RcB=m.RcB, est_h=m.est_h, est_w=m.est_w,
               ida=dict(x=round(el.x_ida, 2), y=r(el.y_correia), zb=el.z_polia_baixo, zt=el.z_polia_cima, k=r(el.fix_z))))
    html = (AQUI / "visualizador_tpl.html").read_text(encoding="utf8").replace("__DADOS__", json.dumps(dados, ensure_ascii=False))
    SAIDA.write_text(html, encoding="utf8")
    print("ok", SAIDA, len(html) // 1024, "KB")


if __name__ == "__main__":
    main()
