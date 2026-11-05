"""Validacao da montagem do elevador de cabine.

  python montagem.py            # roda todas as checagens e grava validacao.json + cena.json (visualizacao)

Checagens:
  1. folgas: cabine x pecas fixas em todo o curso (0,5 mm), alavanca na posicao que a cabine impoe
  2. parafusos: atravessa a peca que prende, pega o suficiente na que rosca, nao fura mais nada,
     inserto com parede >= 1,2 mm, cabeca assenta e a chave chega (corredor livre na etapa em que entra)
  3. correia: comprimento, nada rigido chega nas polias, ramo livre longe da cabine
  4. comporta: abre no fundo, fecha ao subir, empurrao da fila fecha em vez de abrir, contrapeso, lamina
     entrando entre as bolas
  5. impressao: cada peca cabe numa das impressoras; tudo dentro de 420 x 420 x 200
"""
import json
import math
from pathlib import Path

import numpy as np

import modelo
from modelo import P, geometria, fixadores, ancoras, R_BOLA
PECAS = modelo.PECAS

AQUI = Path(__file__).resolve().parent
MM = 1e-3
FOLGA = 0.5
IMPRESSORAS = {"260 x 260 x 250": (260, 260, 250), "220 x 220 x 250": (220, 220, 250)}
CONTATO_PREVISTO = {("patim", "trilho"): "o patim abraca o trilho",
                    ("bloco_dir", "batente"): "batente de baixo: e onde a cabine para",
                    ("alav_chifre", "servo"): "chifre montado no eixo do servo",
                    ("bucha_esq", "eixo_esq"): "o LM8UU corre no eixo",
                    ("bucha_dir", "eixo_dir"): "o LM8UU corre no eixo",
                    ("aloj_dir_b", "fdc_baixo_alav"): "fim de curso de baixo: a cabine aperta a alavanca no batente",
                    ("aloj_dir_b", "fdc_cima_alav"): "fim de curso de cima: a cabine aperta a alavanca no topo"}


from cena3d import Cena  # noqa: E402  (sem MuJoCo: o Windows bloqueou a DLL dele)


# ------------------------------------------------------------------ 1. folgas em movimento
def checar_folgas(c: Cena):
    """Cabine x fixas em todo o curso; braco da comporta x fixas em todo o giro; cabine x braco em TODAS as
    combinacoes (curso x giro): se nunca encostam, a ordem dos comandos nao pode causar batida."""
    p = c.p
    fixos = c.nomes("mundo")
    carro, alav = c.nomes("carro"), c.nomes("alavanca")
    minimo = {}

    def guarda(a, b, zc, th):
        dd = c.dist(a, b)
        if (a, b) not in minimo or dd < minimo[(a, b)][0]:
            minimo[(a, b)] = (dd, zc, th)

    for zc in np.arange(p.zc_min, p.zc_max + 0.01, 0.5):
        c.pose(zc, 0.0)
        for a in carro:
            for b in fixos:
                guarda(a, b, zc, 0.0)
    angs = np.arange(0, 8.01, 0.25)
    for th in angs:
        c.pose(p.zc_max, th)
        for a in alav:
            for b in fixos:
                guarda(a, b, p.zc_max, th)
    for zc in np.arange(p.zc_min, p.zc_min + 60.01, 0.5):
        for th in angs:
            c.pose(zc, th)
            for a in carro:
                for b in alav:
                    guarda(a, b, zc, th)
    linhas = []
    for (a, b), (dd, zc, th) in sorted(minimo.items(), key=lambda kv: kv[1][0]):
        prev = CONTATO_PREVISTO.get((a, b))
        ok = dd >= FOLGA - 1e-6 or prev is not None
        if dd < 3 or not ok:
            linhas.append(dict(a=a, pa=c.peca[a], b=b, pb=c.peca[b], folga=round(float(dd), 2), zc=round(float(zc), 1),
                               ang=round(float(th), 2), ok=bool(ok), nota=prev or ""))
    return linhas, []


# ------------------------------------------------------------------ 2. parafusos
def intervalo(p0, d, L, lo, hi, r):
    """Trecho [t0, t1] do segmento p0 + t d (0..L) dentro da caixa alinhada [lo, hi] engordada pelo raio
    nas direcoes perpendiculares (o corpo do parafuso inteiro dentro). None se nao cruza."""
    t0, t1 = 0.0, L
    for k in range(3):
        if abs(d[k]) > 0.5:
            a, b = sorted(((lo[k] - p0[k]) / d[k], (hi[k] - p0[k]) / d[k]))
            t0, t1 = max(t0, a), min(t1, b)
        else:
            if p0[k] + r <= lo[k] + 1e-6 or p0[k] - r >= hi[k] - 1e-6:
                return None
    return (t0, t1) if t1 - t0 > 1e-6 else None


def borda(p0, d, lo, hi):
    return min(min(p0[k] - lo[k], hi[k] - p0[k]) for k in range(3) if abs(d[k]) < 0.5)


def checar_parafusos(c: Cena):
    p = c.p
    ZC = 150.0
    c.pose(ZC, 0.0)                      # cabine no meio do curso durante a montagem
    caixas = {n: c.aabb(n) for n in c.id}          # inclui o piso: os parafusos de madeira pegam nele
    etapa = {n: PECAS.get(c.peca[n], ("", "", 99))[2] for n in caixas}
    res = []
    for f in fixadores(p):
        p0, d, L = np.array(f["p0"], float), np.array(f["dir"], float), f["L"]
        if f["corpo"] == "carro":
            p0[2] += ZC
        problemas, notas = [], []
        dentro = {}
        for n, (lo, hi) in caixas.items():
            iv = intervalo(p0, d, L, lo, hi, 1.4)
            if iv:
                pc = c.peca[n]
                dentro.setdefault(pc, []).append((n, iv))
        prende = sum(iv[1] - iv[0] for _, iv in dentro.get(f["prende"], []))
        rosca = sum(iv[1] - iv[0] for _, iv in dentro.get(f["rosca"], []))
        if prende < 1.0:
            problemas.append(f"nao atravessa {f['prende']} ({prende:.1f} mm)")
        auto = p.guia == "impressa"          # sem insertos: M3 rosqueia direto no PETG (furo 2,7)
        if f["rosca"] in ("Bancada", "Gabinete"):
            minimo = 8.0
        elif f["insert"]:
            minimo = 5.0 if auto else 4.0
        else:
            minimo = 1.0 if "Polia" in f["rosca"] else 2.5
        if rosca < minimo:
            problemas.append(f"pega so {rosca:.1f} mm em {f['rosca']} (minimo {minimo})")
        for pc in dentro:
            if pc not in (f["prende"], f["rosca"], "Bancada") and pc not in f["atravessa"] and pc not in f["acesso"]:
                problemas.append(f"fura {pc}")
        if f["insert"]:
            for n, iv in dentro.get(f["rosca"], []):
                lo, hi = caixas[n]
                b = borda(p0, d, lo, hi)
                r_f = 1.5 if auto else 2.3     # raio da rosca (auto) ou do inserto
                p_min = 1.5 if auto else 1.2
                if b < r_f + p_min:
                    problemas.append(f"furo a {b:.1f} mm da borda de {n} (parede {b - r_f:.1f} mm)")
                notas.append(f"parede em volta da rosca {b - r_f:.1f} mm")
        # cabeca e corredor da chave: para tras da cabeca, ate 120 mm
        rc = f["cab"] / 2 + 0.5
        livres = set([f["prende"]] + f["acesso"] + ["Bancada"])
        for n, (lo, hi) in caixas.items():
            pc = c.peca[n]
            if pc in livres or etapa[n] > f["etapa"]:
                continue
            iv = intervalo(p0, -d, 120.0, lo, hi, rc)
            if iv and iv[0] < 119:
                problemas.append(f"chave bate em {pc} ({n}) a {iv[0]:.0f} mm da cabeca")
        res.append(dict(nome=f["nome"], tipo=f["tipo"], etapa=f["etapa"], prende=f["prende"], rosca=f["rosca"],
                        pega=round(rosca, 1), acesso=f["acesso"], ok=not problemas, problemas=problemas, notas=notas,
                        p0=f["p0"], dir=f["dir"], L=L, corpo=f["corpo"]))
    return res


# ------------------------------------------------------------------ 3. correia
def checar_correia(c: Cena, folgas):
    p = c.p
    zb, zt, r = p.z_polia_baixo, p.z_polia_cima, p.r_pitch
    pega = 8.0
    comp = 2 * (zt - zb) - (29 - 21) + 2 * math.pi * r + 2 * pega
    pol = [l for l in folgas if l["b"] in ("polia_cima", "polia_baixo", "cubo_cima", "correia_volta")]
    menor = {}
    for l in pol:
        k = l["b"]
        if k not in menor or l["folga"] < menor[k]["folga"]:
            menor[k] = l
    return dict(comprimento=round(comp, 0), compra="GT2 6 mm aberta, 1 m (corta em ~835 mm)",
                pega_presilha=pega, presilhas_z=[[13, 21], [29, 37]],
                curso=[round(p.zc_min, 2), round(p.zc_max, 2)],
                folga_polia_cima=menor.get("polia_cima", {}).get("folga"),
                folga_polia_baixo=menor.get("polia_baixo", {}).get("folga"),
                folga_ramo_livre=menor.get("correia_volta", {}).get("folga"),
                trilho_sobra_cima=round(p.z_trilho[1] - (p.zc_max + p.patim_z[1]), 2) if p.guia == "mgn9" else
                round(p.fundo_cabeca - (p.zc_max + p.caixa_z[1]), 2),
                trilho_sobra_baixo=round((p.zc_min + p.patim_z[0]) - p.z_trilho[0], 2) if p.guia == "mgn9" else
                round((p.zc_min + p.caixa_z[0]) - p.z_pe, 2))


# ------------------------------------------------------------------ 4. comporta
def _pen_caixa(c, nome, centro, r):
    """Quanto uma esfera (centro, r) entra na caixa 'nome' na pose atual (positivo = entra)."""
    i = c.id[nome]
    pos = c.d.geom_xpos[i] / MM
    R = c.d.geom_xmat[i].reshape(3, 3)
    h = np.array(next(x for x in c.g if x["nome"] == nome)["meio"])
    loc = R.T @ (np.array(centro) - pos)
    q = np.clip(loc, -h, h)
    return r - float(np.linalg.norm(loc - q))


def bolas_no_fundo(p, r2, r3):
    """Bola 2 no berco (cabine no fundo) e bola 3 empurrada pela fila contra ela."""
    z2 = p.zc_min + p.z_piso_berco(p.x_parede_dir - r2, p.y_bola) + r2 / math.cos(math.radians(p.incl_berco_x))
    x2 = p.x_parede_dir - r2
    tf = math.tan(math.radians(p.incl_fila))
    zf = lambda x: p.zf_fim + (p.x_fila_fim - min(x, p.x_fila_fim)) * tf
    x3 = p.x_fila_ini
    for x in np.arange(x2 - 2 * (r2 + r3), x2, 0.02):
        if math.hypot(x - x2, zf(x) + r3 - z2) >= r2 + r3:
            x3 = x
        else:
            break
    return (x2, p.y_bola, z2), (x3, 130 + p.larg_fila / 2, zf(x3) + r3)


def checar_comporta_caso(p, r2=R_BOLA, r3=R_BOLA):
    c = Cena(p)
    out = {}
    th_b = p.ang_baixa
    c.pose(p.zc_max, th_b)
    lo, hi = c.aabb("alav_ponta_topo")
    out["lamina_baixa_topo_vs_fila"] = round(float(hi[2] - p.zf_fim), 2)
    c.pose(p.zc_max, 0.0)
    lo, hi = c.aabb("alav_ponta_topo")
    out["lamina_alta_topo_vs_fila"] = round(float(hi[2] - p.zf_fim), 2)
    b2, b3 = bolas_no_fundo(p, r2, r3)
    out["bola2"] = [round(float(v), 2) for v in b2]
    out["bola3"] = [round(float(v), 2) for v in b3]
    # servo levanta a lamina com a cabine parada no fundo: a lamina nao pode tocar nenhuma das duas
    pior2 = pior3 = -99.0
    for th in np.arange(th_b, -0.001, -0.1):
        c.pose(p.zc_min, th)
        for n in ("alav_lamina", "alav_ponta2", "alav_ponta", "alav_ponta_topo"):
            pior2 = max(pior2, _pen_caixa(c, n, b2, r2))
            pior3 = max(pior3, _pen_caixa(c, n, b3, r3))
    out["folga_lamina_bola_no_berco"] = round(-pior2, 2)
    out["folga_lamina_bola_seguinte"] = round(-pior3, 2)
    # se a lamina encosta, ela afasta a bola seguinte (a do berco esta presa na parede): forca do servo na ponta
    out["afastar_bola_seguinte_mm"] = round(max(0.0, pior2) + max(0.0, pior3), 2)
    f_ponta = 216.0 / (p.x_contato - p.piv[0])
    out["forca_ponta_servo_N"] = round(f_ponta, 2)
    # cabine sobe: a bola seguinte avanca ate encostar na lamina; degrau que ela teria que pular
    c.pose(p.zc_max, 0.0)
    lo, hi = c.aabb("alav_ponta_topo")
    tf = math.tan(math.radians(p.incl_fila))
    zf = lambda x: p.zf_fim + (p.x_fila_fim - min(x, p.x_fila_fim)) * tf
    x3 = b3[0]
    while max(_pen_caixa(c, n, (x3 + 0.02, b3[1], zf(x3 + 0.02) + r3), r3) for n in ("alav_lamina", "alav_ponta2", "alav_ponta", "alav_ponta_topo")) < 0 and x3 < p.x_bola:
        x3 += 0.02
    base = zf(x3)
    h = float(hi[2] - base)
    m_g = 0.067 * 9.80665
    f_sub = float("inf") if h >= r3 else m_g * math.sqrt(2 * r3 * h - h * h) / (r3 - h)
    fila = 6 * m_g * math.sin(math.radians(p.incl_fila + 1))
    out["degrau_mm"] = round(h, 2)
    out["forca_para_pular_N"] = round(f_sub, 2)
    out["empurrao_fila_N"] = round(fila, 2)
    out["fs_segurar"] = round(f_sub / fila, 1)
    z_ct = min(float(hi[2]), base + r3)
    braco = abs(z_ct - p.piv[2])
    bid = c.m.body("alavanca").id
    massa = float(c.m.body_mass[bid])
    com = c.d.xipos[bid] / MM
    tau = fila * braco + massa * 9.80665 * abs(com[0] - p.piv[0])
    out["torque_servo_Nmm"] = round(tau, 2)
    out["fs_servo"] = round(216.0 / tau, 0)          # MG90S: 2,2 kgf.cm a 4,8 V
    out["fs_afastar"] = round(out["forca_ponta_servo_N"] * math.cos(math.radians(45)) / fila, 1)
    return out


def checar_comporta(c: Cena, tab):
    from dataclasses import replace
    casos = {
        "nominal": (P(), R_BOLA, R_BOLA),
        "lamina ajustada +0,3, bolas grandes": (replace(P(), lamina_dx=0.0), 12.75, 12.75),
        "lamina ajustada -0,3, bolas pequenas": (replace(P(), lamina_dx=-0.6), 12.65, 12.65),
        "berco grande, seguinte pequena, lamina +0,3": (replace(P(), lamina_dx=0.0, x_parede_dir=203.2), 12.75, 12.65),
        "berco pequena, seguinte grande, lamina -0,3": (replace(P(), lamina_dx=-0.6, x_parede_dir=203.8), 12.65, 12.75),
        "sem ajuste: lamina +0,6": (replace(P(), lamina_dx=0.3), 12.75, 12.75),
        "sem ajuste: lamina -0,6": (replace(P(), lamina_dx=-0.9), 12.65, 12.65),
        "degrau 0,4 / fila 3 graus": (replace(P(), degrau=0.4, incl_fila=3.0), R_BOLA, R_BOLA),
        "degrau 1,2 / fila 5 graus": (replace(P(), degrau=1.2, incl_fila=5.0), R_BOLA, R_BOLA),
        "berco 7 graus / 1,3 graus": (replace(P(), incl_berco_y=7.0, incl_berco_x=1.3), R_BOLA, R_BOLA),
    }
    res = {k: checar_comporta_caso(*v) for k, v in casos.items()}
    return dict(casos=res,
                pior_folga=round(min(min(r["folga_lamina_bola_no_berco"], r["folga_lamina_bola_seguinte"]) for r in res.values()), 2),
                pior_fs_segurar=min(r["fs_segurar"] for r in res.values()),
                pior_afastar=max(r["afastar_bola_seguinte_mm"] for r in res.values()),
                sequencia=["cabine no fundo, lamina baixa: uma bola rola para o berco (sensor confirma)",
                           "servo levanta a lamina no vao entre a bola do berco e a seguinte",
                           "cabine sobe; a fila fica presa na lamina",
                           "cabine volta ao fundo; servo baixa a lamina; a proxima bola entra"])


# ------------------------------------------------------------------ 4b. pecas paradas entre si
SOBREPOSICAO_PREVISTA = {
    frozenset(("Suporte do motor", "Motor N20")): "o suporte abraca o motor (bolsao no lugar do motor)",
    frozenset(("Guia impressa inferior", "Fim de curso")): "fim de curso dentro do rebaixo do pe",
    frozenset(("Guia impressa superior", "Fim de curso")): "fim de curso dentro do rebaixo da cabeca",
    frozenset(("Polia de baixo", "Correia")): "a correia abraca a polia",
    frozenset(("Polia do motor", "Correia")): "a correia abraca a polia",
}


def checar_interferencias(c: Cena):
    """Pecas fixas (impressas e compradas) nao podem entrar umas nas outras, fora os encaixes previstos."""
    import itertools
    p = c.p
    c.pose(p.zc_min, 0.0)
    fixos = [n for n in c.id if c.corpo[n] == "mundo"] if hasattr(c, "corpo") else [n for n in c.id]
    ruins, previstas = [], []
    for a, b in itertools.combinations(fixos, 2):
        pa, pb = c.peca[a], c.peca[b]
        if pa == pb:
            continue
        d = c.dist(a, b)
        if d >= -0.2:          # encostar (ou 0,2 de ajuste de apoio, como a rampa no tubo) e permitido
            continue
        k = frozenset((pa, pb))
        item = dict(a=a, pa=pa, b=b, pb=pb, entra=round(-d, 2))
        (previstas if k in SOBREPOSICAO_PREVISTA else ruins).append(item)
    return dict(ruins=ruins, previstas=len(previstas), ok=not ruins)


# ------------------------------------------------------------------ 5. impressao e envelope
def checar_impressao(c: Cena):
    c.pose(0.0, 0.0)
    por = {}
    for n in c.id:
        if n == "chao":
            continue
        pc = c.peca[n]
        lo, hi = c.aabb(n)
        if pc in por:
            por[pc] = (np.minimum(por[pc][0], lo), np.maximum(por[pc][1], hi))
        else:
            por[pc] = (lo, hi)
    res = []
    for pc, (lo, hi) in por.items():
        tipo = PECAS.get(pc, ("?",))[0]
        if tipo != "impressa":
            continue
        dims = sorted((hi - lo).tolist())
        cabe = [k for k, v in IMPRESSORAS.items() if all(a <= b for a, b in zip(dims, sorted(v)))]
        res.append(dict(peca=pc, dims=[round(x, 1) for x in sorted((hi - lo).tolist(), reverse=True)], cabe=cabe, ok=bool(cabe)))
    return res


def checar_envelope(c: Cena):
    p = c.p
    bancada = {"Fila", "Rampa", "Braco da comporta", "Servo", "Servo MG90S", "Suporte do servo", "Bancada", "Gabinete"}
    lo_t, hi_t = np.full(3, 1e9), np.full(3, -1e9)
    for zc in (p.zc_min, p.zc_max):
        c.pose(zc, 0.0)
        for n in c.id:
            if n == "chao" or c.peca[n] in bancada:
                continue
            lo, hi = c.aabb(n)
            lo_t, hi_t = np.minimum(lo_t, lo), np.maximum(hi_t, hi)
    ok = lo_t[0] >= 172 - 1e-6 and hi_t[0] <= 210 + 1e-6 and lo_t[2] >= -1e-6 and hi_t[2] <= 420 + 1e-6 and hi_t[1] <= 200
    return dict(min=[round(x, 1) for x in lo_t], max=[round(x, 1) for x in hi_t], ok=bool(ok),
                limite="X 172..210 (faixa direita, fora da janela), Y ate 200 (tela), Z 0..420")


def checar_atrito(c: Cena):
    """Guia impressa: forca para subir e risco de travar (efeito gaveta). Os pesos ficam na frente da guia e a
    correia puxa entre os dois; o momento que sobra vira um par de forcas nas pontas do C, que geram atrito."""
    p = c.p
    m, d = c.m, c.d
    c.pose(p.zc_min, 0.0)
    bc = m.body("carro").id
    mc = float(m.body_mass[bc])
    yc = float(d.xipos[bc][1] / MM)
    xc = float(d.xipos[bc][0] / MM)
    g = 9.80665
    mb = 0.067
    ye, h = p.y_eixos, p.alt_caixa
    xg = sum(p.x_eixos) / 2
    y_cor = sum(p.y_correia) / 2
    e = ye - y_cor                       # braco da correia ate a linha da guia
    out = dict(massa_cabine_g=round(mc * 1000, 1), altura_C_mm=h, braco_correia_mm=round(e, 1),
               folga_por_lado_mm=p.folga_guia)
    W = (mc + mb) * g
    casos = []
    for mu, nome in ((0.15, "PETG com spray de PTFE ou grafite"), (0.3, "PETG liso, lubrificado com vaselina"),
                     (0.5, "PETG seco, pior caso")):
        F = W
        for _ in range(20):
            Mx = mb * g * (ye - p.y_bola) + mc * g * (ye - yc) - F * e          # momento no plano Y-Z
            My = F * (p.x_ida - xg) - (mc * g * (xc - xg) + mb * g * (p.x_bola - xg))  # no plano X-Z
            N = abs(Mx) / h + abs(My) / h
            F = W + mu * 2 * N
        trava = mu * 2 * e / h
        casos.append(dict(mu=mu, situacao=nome, forca_subir_N=round(F, 2), fs_motor=round(8.0 / F, 1),
                          indice_trava=round(trava, 2), trava=trava >= 1))
    out["casos"] = casos
    out["inclinacao_max_graus"] = round(math.degrees(2 * p.folga_guia / h), 2)
    out["balanco_na_frente_do_berco_mm"] = round((ye - 130) * 2 * p.folga_guia / h, 2)
    return out


def cena_json(c: Cena, tab, val):
    p = c.p
    geo = []
    for e in c.g:
        if e["nome"] == "chao":
            continue
        pc = e["peca"]
        geo.append(dict(n=e["nome"], c=e["corpo"], t=e["tipo"], s=[round(v, 3) for v in e["meio"]],
                        p=[round(v, 3) for v in e["pos"]], q=[round(v, 6) for v in e["quat"]], peca=pc,
                        cor=e["cor"], etapa=PECAS.get(pc, ("", "", 0))[2]))
    return dict(geo=geo, fix=[dict(n=f["nome"], p0=f["p0"], d=f["dir"], L=f["L"], etapa=f["etapa"], tipo=f["tipo"],
                                    ok=f["ok"], c=f["corpo"]) for f in val["parafusos"]],
                anc=ancoras(p), piv=list(p.piv), r=p.r_bola, tab=tab,
                p=dict(zf_fim=p.zf_fim, x_fila_fim=p.x_fila_fim, x_fila_ini=p.x_fila_ini, incl_fila=p.incl_fila,
                       y_bola=p.y_bola, z_rampa=p.z_rampa, incl_rampa=p.incl_rampa, x_ida=p.x_ida, x_volta=p.x_volta,
                       y_correia=list(p.y_correia), zb=p.z_polia_baixo, zt=p.z_polia_cima,
                       incl_berco_y=p.incl_berco_y, incl_berco_x=p.incl_berco_x, z_piso_bola=p.z_piso_berco(p.x_bola, p.y_bola)),
                pecas={k: dict(tipo=v[0], mat=v[1], etapa=v[2], fix=v[3]) for k, v in PECAS.items()})


def _js(o):
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def main():
    import sys
    from dataclasses import replace
    global PECAS
    guia = sys.argv[1] if len(sys.argv) > 1 else "mgn9"
    suf = "" if guia == "mgn9" else "_" + guia
    if guia == "eixos":
        PECAS = modelo.PECAS_EIXOS
    if guia == "impressa":
        PECAS = modelo.PECAS_IMPRESSA
    _P0 = P
    globals()["P"] = lambda **kw: _P0(guia=guia, **kw)
    p = P()
    c = Cena(p)
    folgas, tab = checar_folgas(c)
    val = dict(ancoras={k: round(v, 2) for k, v in ancoras(p).items()},
               folgas=folgas, parafusos=checar_parafusos(c), correia=checar_correia(c, folgas),
               comporta=checar_comporta(c, tab), impressao=checar_impressao(c), envelope=checar_envelope(c),
               interferencias=checar_interferencias(c))
    if guia == "impressa":
        val["atrito"] = checar_atrito(c)
        print("ATRITO", val["atrito"])
    (AQUI / f"validacao{suf}.json").write_text(json.dumps(val, indent=1, ensure_ascii=False, default=_js), encoding="utf8")
    (AQUI / f"cena{suf}.json").write_text(json.dumps(cena_json(c, tab, val), ensure_ascii=False, default=_js), encoding="utf8")
    ruins = [l for l in folgas if not l["ok"]]
    print("ancoras", val["ancoras"])
    print("FOLGAS ruins:", len(ruins))
    for l in folgas[:25]:
        print("  ", l)
    pr = [f for f in val["parafusos"] if not f["ok"]]
    print("PARAFUSOS ruins:", len(pr), "de", len(val["parafusos"]))
    for f in pr:
        print("  ", f["nome"], f["problemas"])
    print("CORREIA", val["correia"])
    print("COMPORTA pior folga", val["comporta"]["pior_folga"], "pior FS segurar", val["comporta"]["pior_fs_segurar"])
    for k, v in val["comporta"]["casos"].items():
        print("   ", k, v)
    print("IMPRESSAO", [(i["peca"], i["dims"], i["ok"]) for i in val["impressao"]])
    print("ENVELOPE", val["envelope"])
    print("INTERFERENCIAS ruins:", len(val["interferencias"]["ruins"]), val["interferencias"]["ruins"][:8],
          "previstas:", val["interferencias"]["previstas"])


if __name__ == "__main__":
    main()
