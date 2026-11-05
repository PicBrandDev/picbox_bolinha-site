"""Resistencia e impressao das pecas do elevador (versao guia impressa).

Contas de mao, conservadoras, para os pontos que carregam: cada caso diz a carga, a tensao, o que o material
aguenta na direcao em que a peca foi impressa e o fator de seguranca (FS). Dois regimes de carga:
- normal: pretensao da correia + subir a bola (o que a peca sente sempre)
- falha: o motor trava contra o batente ou a cabeca com o torque maximo (fim de curso falhou); dura ate o
  tempo-limite do programa, entao conta como carga curta.
Uso: python resistencia.py  ->  resistencia.json
"""
import json
import math
from pathlib import Path

import numpy as np

import modelo
from cena3d import q2R

AQUI = Path(__file__).parent

# ------------------------------------------------------------------ material e cargas
PETG = dict(E=1800.0,            # MPa, modulo impresso
            sr_xy=45.0,          # MPa, ruptura no plano da camada
            sr_z=25.0,           # MPa, ruptura entre camadas
            tau_z=15.0,          # MPa, cisalhamento entre camadas
            fluencia=10.0)       # MPa, limite para carga permanente (PETG flui acima disso)
ACO_M3_48 = 340.0                # MPa, escoamento do parafuso classe 4.8 (o mais fraco que se compra)
ACO_EIXO = 355.0                 # MPa, eixo do N20 (aco 45 sem tempera)
G = 9.80665
M_BOLA = 0.067
M_CABINE = 0.0193
R_POLIA = 20 * 2.0 / (2 * math.pi)          # raio primitivo da GT2 20 dentes, 6,37 mm
T0 = 5.0                                     # N, pretensao por ramo (correia "esticada sem cantar")
T0_MAX = 10.0
TRAVA_KGCM = 2.4                             # N20 12 V 100 rpm: 1,5-2,4 kgf.cm travado (pior catalogo)
F_TRAVA = TRAVA_KGCM * G / 100 / (R_POLIA / 1000)    # forca na correia com o motor travado
F_SUBIR = 1.31 + (M_BOLA + M_CABINE) * G     # atrito pior caso (montagem.checar_atrito) + pesos
F_ESBARRAO = 10.0                            # N, alguem esbarra no topo da coluna


def caso(peca, ponto, regime, carga_N, tensao, limite, direcao, nota=""):
    fs = limite / tensao if tensao > 0 else float("inf")
    minimo = 3.0 if regime == "normal" else 1.5
    return dict(peca=peca, ponto=ponto, regime=regime, carga_N=round(carga_N, 1), tensao_MPa=round(tensao, 1),
                limite_MPa=limite, direcao=direcao, fs=round(fs, 1), fs_min=minimo, ok=fs >= minimo, nota=nota)


def secao(retangulos, eixo):
    """I e distancia maxima para flexao. retangulos: (x0, x1, y0, y1). eixo 'y' = forca em Y."""
    A = sum((x1 - x0) * (y1 - y0) for x0, x1, y0, y1 in retangulos)
    if eixo == "y":
        c = sum((x1 - x0) * (y1 - y0) * (y0 + y1) / 2 for x0, x1, y0, y1 in retangulos) / A
        I = sum((x1 - x0) * (y1 - y0) ** 3 / 12 + (x1 - x0) * (y1 - y0) * ((y0 + y1) / 2 - c) ** 2
                for x0, x1, y0, y1 in retangulos)
        cmax = max(max(abs(y0 - c), abs(y1 - c)) for x0, x1, y0, y1 in retangulos)
    else:
        c = sum((x1 - x0) * (y1 - y0) * (x0 + x1) / 2 for x0, x1, y0, y1 in retangulos) / A
        I = sum((y1 - y0) * (x1 - x0) ** 3 / 12 + (x1 - x0) * (y1 - y0) * ((x0 + x1) / 2 - c) ** 2
                for x0, x1, y0, y1 in retangulos)
        cmax = max(max(abs(x0 - c), abs(x1 - c)) for x0, x1, y0, y1 in retangulos)
    return A, I, cmax


def casos_resistencia(p, g):
    out = []
    caixas = {e["nome"]: e for e in g}

    def lim(n):
        e = caixas[n]
        return [(c - m, c + m) for c, m in zip(e["pos"], e["meio"])]

    # 1. coluna (guia inferior + superior): secao no meio, flexao por esbarrao no topo
    rets = []
    for n in ("placa_inf", "trilho_esq_inf", "pescoco_esq_inf", "trilho_dir_inf", "pescoco_dir_inf"):
        (x0, x1), (y0, y1), _ = lim(n)
        rets.append((x0, x1, y0, y1))
    A, Iy, cy = secao(rets, "y")
    _, Ix, cx = secao(rets, "x")
    L = p.topo_cabeca
    E = PETG["E"]
    M_balanco = F_ESBARRAO * L
    flecha_balanco = F_ESBARRAO * L ** 3 / (3 * E * Iy)
    # com a orelha na parede: apoiada na base e no topo, emenda no meio vira articulacao -> cada metade em balanco
    Lm = L / 2
    flecha_orelha = (F_ESBARRAO / 2) * Lm ** 3 / (3 * E * Iy)
    M_orelha = (F_ESBARRAO / 2) * Lm
    out.append(caso("Guias impressas", "coluna inteira, esbarrao de 10 N no topo, SEM a orelha", "normal",
                    F_ESBARRAO, M_balanco * cy / Iy, PETG["sr_xy"], "ao longo da camada (guia deitada)",
                    f"aguenta, mas balanca {flecha_balanco:.1f} mm no topo e a emenda abre: por isso a orelha"))
    out.append(caso("Guias impressas", "coluna com a orelha na parede, esbarrao de 10 N", "normal",
                    F_ESBARRAO, M_orelha * cy / Iy, PETG["sr_xy"], "ao longo da camada (guia deitada)",
                    f"topo parado; a emenda mexe {flecha_orelha:.2f} mm"))
    # pinos da emenda: o corte do esbarrao
    a_pino = math.pi * 2.5 ** 2
    out.append(caso("Guias impressas", "2 pinos de 5 mm da emenda, corte", "normal", F_ESBARRAO / 2,
                    (F_ESBARRAO / 2) / (2 * a_pino), PETG["tau_z"], "pino deitado na impressao", ""))

    # 2. trilho em T e C da cabine: binario da correia (14 mm atras do peso) no motor travado
    e = 14.0
    h_c = p.alt_caixa
    par = F_TRAVA * e / h_c / 2                          # por trilho
    out.append(caso("Guias impressas", "pescoco do T (4 mm) puxado pela aba do C, motor travado", "falha", par,
                    par / (4.0 * h_c), PETG["sr_z"], "entre camadas (guia deitada de costas)", ""))
    out.append(caso("Cabine", "aba do C (2,5 mm) dobrando, motor travado", "falha", par,
                    par * 2.5 / (h_c * 2.5 ** 2 / 6), PETG["sr_xy"], "no plano (cabine em pe)", ""))

    # 3. presilhas da correia na cabine: 4 dentes pegos (8 mm)
    F = F_TRAVA + T0_MAX
    area_dente = 6.0 * 1.2
    out.append(caso("Cabine", "dentes da presilha da correia (4 dentes)", "falha", F,
                    F / (4 * area_dente), PETG["tau_z"], "corte entre camadas (cabine em pe)",
                    "a ponta da correia volta dobrada e presa com abracadeira"))

    # 4. batente: motor travado empurrando a cabine para baixo
    (x0, x1), (y0, y1), (z0, z1) = lim("batente")
    b, t, hb = y1 - y0, x1 - x0, z1 - z0
    F = F_TRAVA + (M_CABINE + M_BOLA) * G
    out.append(caso("Base", "batente comprimido, motor travado", "falha", F, F / (b * t), PETG["sr_z"],
                    "compressao entre camadas", ""))
    Pcr = math.pi ** 2 * E * (b * t ** 3 / 12) / (4 * hb ** 2)
    out.append(dict(peca="Base", ponto="batente, flambagem", regime="falha", carga_N=round(F, 1),
                    tensao_MPa=None, limite_MPa=None, direcao="", fs=round(Pcr / F, 1), fs_min=1.5,
                    ok=Pcr / F >= 1.5, nota=f"carga critica {Pcr:.0f} N"))
    # pancada de lado na montagem (20 N no topo), com o reforco
    (rx0, rx1), (ry0, ry1), (rz0, rz1) = lim("batente_reforco")
    W = (b * (t + (rx1 - rx0)) ** 2 / 6)
    out.append(caso("Base", "batente levando 20 N de lado na montagem (com o reforco)", "falha", 20.0,
                    20.0 * hb / W, PETG["sr_z"], "entre camadas (base deitada)", ""))

    # 5. parafuso da polia de baixo: apoiado no pe e na bochecha
    y_pe, y_boch, y_pol = 176.5, 163.5, sum(p.y_correia) / 2
    vao = y_pe - y_boch
    a, bb = y_pe - y_pol, y_pol - y_boch
    W_m3 = math.pi * 2.39 ** 3 / 32
    for regime, Tr in (("normal", T0 + F_SUBIR), ("falha", F_TRAVA + T0)):
        F = 2 * Tr
        out.append(caso("Parafuso da polia de baixo", "M3 dobrando entre o pe e a bochecha", regime, F,
                        F * a * bb / vao / W_m3, ACO_M3_48, "aco classe 4.8", ""))
    F = 2 * (F_TRAVA + T0)
    out.append(dict(peca="Parafuso da polia de baixo", ponto="sem a bochecha (como era)", regime="falha",
                    carga_N=round(F, 1), tensao_MPa=round(F * (y_pe - y_pol) / W_m3), limite_MPa=ACO_M3_48,
                    direcao="aco", fs=round(ACO_M3_48 / (F * (y_pe - y_pol) / W_m3), 1), fs_min=1.5,
                    ok=False, antes=True, nota="o parafuso entortava: por isso a bochecha"))
    out.append(caso("Calco da polia de baixo", "calco de PETG esmagado pelo rolamento", "normal", 2 * (T0 + F_SUBIR),
                    2 * (T0 + F_SUBIR) / (3.2 * 8.0), PETG["fluencia"], "carga permanente", ""))
    R_boch = F * a / vao
    (bx0, bx1), (by0, by1), _ = lim("bochecha")
    out.append(caso("Base", "bochecha puxada para cima pela polia", "falha", R_boch,
                    R_boch / ((bx1 - bx0) * (by1 - by0)), PETG["sr_z"], "tracao entre camadas", ""))
    # ponte da base em frente a janela, segurando a bochecha
    (mx0, mx1), (my0, my1), (mz0, mz1) = lim("base_meio")
    vao_m = mx1 - mx0
    W_meio = (my1 - my0) * (mz1 - mz0) ** 2 / 6
    out.append(caso("Base", "faixa da base na frente da janela", "falha", R_boch,
                    R_boch * vao_m / 4 / W_meio, PETG["sr_xy"], "no plano (base deitada)", ""))

    # 6. eixo do N20: polia em balanco a 11,5 mm da caixa de reducao
    braco = sum(p.y_correia) / 2 - 157.0
    W_eixo = math.pi * 2.5 ** 3 / 32            # eixo de 3 mm com lado chato
    for regime, F in (("normal", 2 * T0 + F_SUBIR), ("falha", F_TRAVA + 2 * T0)):
        out.append(caso("Motor N20", "eixo de 3 mm dobrando com a polia", regime, F, F * braco / W_eixo, ACO_EIXO,
                        "aco", "eixo no limite: o programa tem que impedir o travamento"
                        if regime == "falha" else "pretensao baixa: 5 N por ramo"))
    F = 0.5 * F_TRAVA + 2 * T0
    out.append(caso("Motor N20", "eixo, travado com PWM de 50% nos ultimos 20 mm (regra do programa)", "falha", F,
                    F * braco / W_eixo, ACO_EIXO, "aco", "devagar perto do fim + tempo-limite de 1 s"))

    # 7. suporte do motor: placa de 4 mm + 2 nervuras, do motor ate a cabeca da guia
    y_motor = 140.75
    braco = 176.5 - y_motor
    rets = [(172, 209, 415, 419)]                 # placa (x, z)
    for n in ("sup_nervura_esq", "sup_nervura_dir"):
        (x0, x1), _, (z0, z1) = lim(n)
        rets.append((x0, x1, z0, z1))
    _, I_sup, c_sup = secao(rets, "y")            # aqui o 2o par e Z
    for regime, F in (("normal", 2 * T0 + F_SUBIR), ("falha", F_TRAVA + 2 * T0)):
        lim_sup = PETG["fluencia"] if regime == "normal" else PETG["sr_xy"]
        out.append(caso("Suporte do motor", "placa com nervuras, mesmo se o tubo nao ajudar", regime, F,
                        F * braco * c_sup / I_sup, lim_sup, "no plano (suporte de cabeca para baixo)",
                        "carga permanente: comparada com o limite de fluencia" if regime == "normal" else ""))
    W_placa = 37 * 4 ** 2 / 6
    F = F_TRAVA + 2 * T0
    out.append(dict(peca="Suporte do motor", ponto="so a placa de 4 mm (como era)", regime="falha",
                    carga_N=round(F, 1), tensao_MPa=round(F * braco / W_placa, 1), limite_MPa=PETG["sr_xy"],
                    direcao="no plano", fs=round(PETG["sr_xy"] / (F * braco / W_placa), 1), fs_min=1.5,
                    ok=PETG["sr_xy"] / (F * braco / W_placa) >= 1.5,
                    antes=True, nota=f"normal {(2 * T0 + F_SUBIR) * braco / W_placa:.1f} MPa permanente, perto do limite de fluencia"))

    # 8. comporta: bola da fila batendo na lamina (Newton: a fila passa o choque para a bola da frente)
    h_fila = (p.x_fila_fim - p.x_fila_ini - 25.4) / 1000 * math.sin(math.radians(p.incl_fila))
    v = math.sqrt(10 / 7 * G * h_fila)
    E_choque = 0.5 * M_BOLA * v ** 2 * 1000            # mJ
    a_lam = (p.zf_fim + p.lamina_topo) - 14.0          # da barra de baixo ate o topo da lamina
    b_ef = 20.0
    k = 3 * E * (b_ef * 1.5 ** 3 / 12) / a_lam ** 3 * 2      # presa na barra e na ponte: ~2x mais rigida
    F_imp = math.sqrt(2 * k * E_choque)
    sig = F_imp / 2 * a_lam / (b_ef * 1.5 ** 2 / 6)    # metade do choque vai por cada apoio
    out.append(caso("Braco da comporta", f"lamina levando o choque de uma bola que rolou a fila vazia ({v:.2f} m/s)",
                    "falha", F_imp, sig, PETG["sr_z"], "pior direcao (entre camadas)",
                    "antes, so presa na ponte, era o dobro"))
    sig_p = F_imp * p.ponta_h / (8.0 * 1.2 ** 2 / 6)
    out.append(caso("Braco da comporta", "degrau da ponta (1,2 mm) no mesmo choque", "falha", F_imp, sig_p,
                    PETG["sr_z"], "entre camadas", "a ponta de 0,8 so tem 0,5 mm de altura"))
    sig_p_antigo = F_imp * 3.0 / (8.0 * 0.8 ** 2 / 6)
    out.append(dict(peca="Braco da comporta", ponto="ponta de 0,8 x 3 mm (como era)", regime="falha",
                    carga_N=round(F_imp, 1), tensao_MPa=round(sig_p_antigo, 1), limite_MPa=PETG["sr_z"],
                    direcao="entre camadas", fs=round(PETG["sr_z"] / sig_p_antigo, 1), fs_min=1.5, ok=False,
                    antes=True, nota="quebrava no choque"))
    # bola da frente pular a lamina: o choque chega sem giro (passa pela fila como no pendulo de Newton) e a bola
    # gira em volta da quina da lamina; momento angular na quina -> energia para subir o degrau
    r, hd = 12.7, 6.46
    d = r - hd
    frac = 5 * d ** 2 / (7 * r ** 2)
    E_pular = M_BOLA * G * hd                          # mJ (g*mm)
    fs_pulo = E_pular / (frac * E_choque)
    v_lim = math.sqrt(2 * (E_pular / 1.5) / frac / M_BOLA / 1000)
    out.append(dict(peca="Comporta", ponto="bola da frente pular a lamina com o choque", regime="falha",
                    carga_N=None, tensao_MPa=None, limite_MPa=None, direcao="", fs=round(fs_pulo, 1), fs_min=1.5,
                    ok=fs_pulo >= 1.5, nota=f"precisa de {E_pular:.1f} mJ, chegam {frac * E_choque:.2f} mJ. Regra para a "
                                            f"bandeja de retorno: a bola chega na fila a menos de {v_lim:.1f} m/s"))

    # 9. parafusos M3 rosqueados direto no PETG (furo 2,7): arrancamento ~60 N por mm de rosca
    for nome, pega, carga, desc in (
            ("base_guia", 7.0, F_ESBARRAO * L / 19.0 / 2, "M3x12 base-guia, sem a orelha (pior)"),
            ("suporte_guia", 10.0, (F_TRAVA + 2 * T0) / 2, "M3x16 suporte-guia, motor travado"),
            ("tubo_base", 5.0, 5.0, "M3x10 tubo-base (so posiciona)")):
        Fr = 60.0 * pega
        out.append(dict(peca="Parafusos", ponto=desc, regime="falha", carga_N=round(carga, 1), tensao_MPa=None,
                        limite_MPa=None, direcao="rosca no PETG", fs=round(Fr / carga, 1), fs_min=1.5,
                        ok=Fr / carga >= 1.5, nota=f"{pega:.0f} mm de rosca, arranca com ~{Fr:.0f} N"))
    return out, dict(F_trava=round(F_TRAVA, 1), F_subir=round(F_SUBIR, 2), T0=T0, v_choque=round(v, 2),
                     E_choque_mJ=round(E_choque, 1), Iy_coluna=round(Iy), flecha_sem_orelha=round(flecha_balanco, 1),
                     flecha_com_orelha=round(flecha_orelha, 2))


# ------------------------------------------------------------------ impressao: posicao, impressora, tempo
IMPRESSORAS = {"A (260 x 260)": (260, 260, 250), "B (220 x 220)": (220, 220, 250), "C (220 x 220)": (220, 220, 250)}
MARGEM = 5.0
POSICAO = {   # peca: (como deitar, eixo que fica em pe, suportes)
    "Base": ("deitada, face de baixo na mesa", "z", "nao"),
    "Guia impressa inferior": ("deitada de costas (face de tras, a da tela, na mesa); trilhos para cima", "y", "nao (aba do T de 2 mm sai sem suporte)"),
    "Guia impressa superior": ("deitada de costas, igual a de baixo", "y", "nao"),
    "Cabine": ("em pe, como monta", "z", "so embaixo do bloco da correia"),
    "Espacador": ("em pe", "y", "nao"),
    "Suporte do motor": ("de cabeca para baixo (placa na mesa)", "z", "nao (teto do motor em ponte de 12 mm)"),
    "Tubo inferior": ("deitado, bordas de tras das paredes na mesa (abertura para baixo)", "y", "nao (frente em ponte de 32 mm)"),
    "Tubo superior": ("deitado, abertura para baixo, igual ao de baixo", "y", "nao"),
    "Fila": ("em pe, como monta; camada de 0,16 no piso", "z", "nao"),
    "Rampa": ("em pe, como monta", "z", "nao"),
    "Suporte do servo": ("em pe, como monta", "z", "nao"),
    "Braco da comporta": ("de cabeca para baixo (topo do braco na mesa)", "z", "nao"),
}
EXTRAS = [  # pecas pequenas que nao estao no 3D como caixa propria
    ("Bucha da polia do motor (5 -> 3 mm em D)", (5, 5, 10), "em pe", 3),
    ("Calco da polia de baixo (5 -> 3,2 mm)", (5, 5, 8), "em pe", 3),
    ("Braco da comporta (reserva)", None, "igual ao braco", 2),
]


def volumes(p, g):
    pecas = {}
    for e in g:
        if modelo.PECAS_IMPRESSA.get(e["peca"], ("",))[0] == "impressa" or e["peca"] == "Batente":
            pc = "Base" if e["peca"] == "Batente" else e["peca"]
            pecas.setdefault(pc, []).append(e)
    furos = [e for e in g if e["peca"] in ("Motor N20", "Fim de curso")]
    res = {}
    h = 0.5
    for pc, es in pecas.items():
        lo = np.full(3, 1e9)
        hi = np.full(3, -1e9)
        for e in es:
            R = q2R(e["quat"])
            m = np.array(e["meio"] if e["tipo"] == "box" else [e["meio"][0], e["meio"][0], e["meio"][1]])
            ext = np.abs(R) @ m
            lo = np.minimum(lo, np.array(e["pos"]) - ext)
            hi = np.maximum(hi, np.array(e["pos"]) + ext)
        ax = [np.arange(lo[i] + h / 2, hi[i], h) for i in range(3)]
        P = np.stack(np.meshgrid(*ax, indexing="ij"), -1).reshape(-1, 3)
        dentro = np.zeros(len(P), bool)
        corpo = es[0]["corpo"]

        def teste(e):
            R = q2R(e["quat"])
            q = (P - np.array(e["pos"])) @ R
            if e["tipo"] == "box":
                return np.all(np.abs(q) <= np.array(e["meio"]), axis=1)
            r, hm = e["meio"]
            return (q[:, 0] ** 2 + q[:, 1] ** 2 <= r * r) & (np.abs(q[:, 2]) <= hm)
        for e in es:
            dentro |= teste(e)
        if corpo == "mundo":
            for e in furos:
                dentro &= ~teste(e)
        res[pc] = dict(vol_cm3=round(dentro.sum() * h ** 3 / 1000, 1), dims=(hi - lo).round(1).tolist())
    return res


def impressao(p, g):
    vol = volumes(p, g)
    linhas = []
    for pc, (como, em_pe, sup) in POSICAO.items():
        d = dict(zip("xyz", vol[pc]["dims"]))
        altura = d[em_pe]
        a, b = [d[k] for k in "xyz" if k != em_pe]
        a, b = max(a, b), min(a, b)
        cabe = []
        for nome, (X, Y, Z) in IMPRESSORAS.items():
            reto = a <= X - 2 * MARGEM and b <= Y - 2 * MARGEM
            diag = (a + b) / math.sqrt(2) <= X - 2 * MARGEM          # girada a 45 graus
            if altura <= Z - 5 and (reto or diag):
                cabe.append(nome if reto else nome + " na diagonal")
        horas = vol[pc]["vol_cm3"] * 0.75 / 11.0 + 0.2
        linhas.append(dict(peca=pc, posicao=como, suporte=sup, mesa_mm=[round(a), round(b)], altura_mm=round(altura),
                           vol_cm3=vol[pc]["vol_cm3"], horas=round(horas, 1), cabe=cabe, ok=bool(cabe)))
    return linhas


def distribuir(linhas):
    """Peca longa (>200) vai na A; o resto equilibra as horas entre B e C."""
    fila = {k: [] for k in IMPRESSORAS}
    horas = {k: 0.0 for k in IMPRESSORAS}
    for l in sorted(linhas, key=lambda l: -l["horas"]):
        opcoes = [k for k in IMPRESSORAS if any(c.startswith(k) for c in l["cabe"])]
        retas = [k for k in opcoes if k in l["cabe"]]
        k = min(retas or opcoes, key=lambda k: horas[k])
        fila[k].append(l["peca"])
        horas[k] += l["horas"]
        l["impressora"] = k
    return fila, {k: round(v, 1) for k, v in horas.items()}


def main():
    p = modelo.P(guia="impressa")
    g = modelo.geometria(p)
    casos, base = casos_resistencia(p, g)
    linhas = impressao(p, g)
    fila, horas = distribuir(linhas)
    out = dict(material=PETG, cargas=base, casos=casos, impressao=linhas, fila=fila, horas=horas,
               extras=[dict(peca=n, posicao=c, quantidade=q) for n, _, c, q in EXTRAS])
    (AQUI / "resistencia.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf8")
    print("CARGAS", base)
    atuais = [c for c in casos if not c.get("antes")]
    print("CASOS ATUAIS ruins:", [c["ponto"] for c in atuais if not c["ok"]], "de", len(atuais))
    for c in casos:
        print(f"{'antes' if c.get('antes') else ('OK  ' if c['ok'] else 'RUIM')} FS {c['fs']:>5} (min {c['fs_min']}) {c['regime']:6s} {c['peca']}: {c['ponto']}"
              f" | {c['tensao_MPa']} MPa / {c['limite_MPa']} | {c['nota']}")
    for l in linhas:
        print(f"{l['peca']:24s} {l['mesa_mm']} h{l['altura_mm']:>4} {l['vol_cm3']:>6} cm3 {l['horas']:>4} h -> {l['impressora']} | {l['cabe']}")
    print("HORAS", horas)


if __name__ == "__main__":
    main()
