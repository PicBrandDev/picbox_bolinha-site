"""Resistencia das pecas novas (contas de mao), no mesmo criterio do elevador (../elevador/resistencia.py).

PETG impresso: 45 MPa no plano da camada, 25 entre camadas, 15 de cisalhamento entre camadas, 10 para carga permanente.
normal = o que a peca sente sempre ou a cada jogada (FS >= 3); falha = motor travado, esbarrao, fim de curso falhou
(FS >= 1,5). A direcao de cada tensao foi conferida contra a posicao de impressao (pecas.POS).
Impactos: F = v * raiz(k * m), com k em serie (contato, peca, trilho, perfil) - limite superior (a bola quica).
"""
import json
import math
import sys
from pathlib import Path

import layout as L

AQUI = Path(__file__).parent
sys.path.insert(0, str(AQUI.parent / "elevador"))
import resistencia as RE  # noqa: E402

PETG = RE.PETG
caso, secao = RE.caso, RE.secao
G = 9.80665
M_BOLA = 0.067
T0 = 15.0                                   # N, tensao de montagem por ramo da GT2 6 dos eixos
R_P = 20 * 2 / (2 * math.pi) / 1000         # m
TORQUE_NEMA = 0.42                          # N.m, 17HS4401 segurando (pior caso: travado)
F_TRAVA = TORQUE_NEMA / R_P                 # N na correia com o motor travado
E_AL, I_2020, W_2020, SY_AL = 69000.0, 6900.0, 690.0, 145.0     # perfil 2020 6063-T5
MGN12H_M = 23.7                             # N.m, momento estatico de catalogo (MP/MY)
PULL_M3_PETG = 60.0                         # N por mm de rosca, M3 rosqueado em PETG (furo 2,7)
PULL_MADEIRA = 40.0                         # N por mm, 3,5 mm em MDF


def impacto(v, k_lista, m=M_BOLA):
    k = 1 / sum(1 / x for x in k_lista)     # N/mm em serie
    return v * math.sqrt(k * 1000 * m), k


def casos(m: L.M):
    out = []
    w = 2 * math.pi / 2.4
    a = m.curso * w ** 2 / 1000                          # m/s2
    m_carroA = 0.015 + 0.030 + M_BOLA + 0.025
    F_norm = T0 + m_carroA * a
    F_falha = T0 + F_TRAVA
    # 1. dentes da presilha (4 dentes de cada lado, 8 mm de correia)
    area = 4 * 0.9 * 6.0
    for k in ("A", "B"):
        out.append(caso(f"Carro {k}", "dentes da presilha da correia", "normal", F_norm, F_norm / area, PETG["fluencia"],
                        "cisalhamento entre camadas", "carga permanente da correia: compara com 10 MPa"))
        out.append(caso(f"Carro {k}", "dentes da presilha da correia", "falha", F_falha, F_falha / area, PETG["tau_z"],
                        "cisalhamento entre camadas", f"NEMA travado ({TORQUE_NEMA} N.m) puxa {F_TRAVA:.0f} N"))
        # bloco da presilha em balanco da placa (16 x 14, braco 12,6 ate a correia)
        A_, I, c = secao([(-8, 8, 0, 14.1)], "x")
        out.append(caso(f"Carro {k}", "raiz do bloco da presilha", "falha", F_falha, F_falha * 12.6 * c / I, PETG["sr_z"],
                        "flexao, pior caso entre camadas"))
    # 2. prateleira do eletroima (24 x 5, balanco de 27,7 ate o ima) e esbarrao de 10 N
    A_, I, c = secao([(0, 24, 0, 5)], "y")
    peso = (0.030 + M_BOLA) * G
    out.append(caso("Carro A", "prateleira do eletroima", "normal", peso, peso * 27.7 * c / I, PETG["fluencia"],
                    "flexao no plano da camada (impressa de lado)"))
    out.append(caso("Carro A", "prateleira do eletroima", "falha", 10.0, 10.0 * 27.7 * c / I, PETG["sr_xy"],
                    "flexao no plano da camada", "esbarrao de 10 N no ima"))
    # 3. anel: bola de 250 mm batendo na borda (acontece em todo erro de raspao)
    v = math.sqrt(2 * G * m.queda / 1000)
    ri, rt, rf, h = m.r_furo, m.r_tubo, m.r_flange, m.h_anel
    A_, Ia, ca = secao([(ri, rt, 0, h - 6), (ri, rf, h - 6, h)], "y")
    k_anel = 6 * PETG["E"] * Ia / (2 * rf) ** 3
    k_perfil = 48 * E_AL * I_2020 / m.L_perfil ** 3
    F_anel, k = impacto(v, [k_anel, k_perfil, 1000.0])
    out.append(caso("Anel", "borda do anel (bola caindo 250 mm)", "normal", F_anel, F_anel / 2 * 2 * rf * ca / Ia,
                    PETG["sr_xy"], "flexao no plano da camada (anel impresso deitado)",
                    f"k em serie {k:.0f} N/mm; FS 3 tambem cobre a fadiga de muitas batidas"))
    braco = m.y_bola + rf - 46
    A_, Ib, cb = secao([(0, 24, 0, h - 6)], "y")
    out.append(caso("Anel", "raiz do braco do anel", "normal", F_anel, F_anel * braco * cb / Ib, PETG["sr_xy"],
                    "flexao no plano da camada"))
    zs = (60.0, m.zb - 10.0)
    F_par = F_anel * braco / (zs[1] - zs[0] + 6) / 2
    area_arruela = math.pi / 4 * (7.0 ** 2 - 3.4 ** 2)
    out.append(caso("Anel", "porca do parafuso das costas (esmaga a placa)", "normal", F_par, F_par / area_arruela,
                    PETG["sr_z"], "compressao embaixo da porca com arruela 7 mm", "M3 passante com porca e arruela"))
    out.append(caso("Anel", "parafuso M3 das costas", "normal", F_par, F_par / 5.03, RE.ACO_M3_48, "tracao no aco 4.8"))
    M_pat = F_anel * (m.y_bola + rf - 36) / 1000
    out.append(caso("Patim MGN12H B", "momento no patim na batida", "falha", F_anel, M_pat, MGN12H_M,
                    "momento estatico de catalogo (N.m)", "impacto curto; o patim aguenta 23,7 N.m parado"))
    M_pf = F_anel * m.L_perfil / 4
    out.append(caso("Perfil 2020 B", "perfil no meio, batida no anel", "normal", F_anel, M_pf / W_2020, SY_AL,
                    "flexao do aluminio", f"flecha {F_anel / k_perfil:.2f} mm durante a batida"))
    # 4. bandeja: bola caindo ate 310 mm sobre EVA 5 mm e placa de 5 mm entre nervuras a 36 mm
    v_b = math.sqrt(2 * G * (m.zs - 45) / 1000)
    k_eva = 5.0 * 100 / m.eva
    F_b, _ = impacto(v_b, [k_eva])
    vao = 36.0
    Mb = F_b * vao / 6
    A_, Ip, cp = secao([(0, vao, 0, m.e_placa)], "y")
    out.append(caso("Bandeja", "placa entre nervuras (bola caindo 310 mm)", "normal", F_b, Mb * cp / Ip, PETG["sr_xy"],
                    "flexao em X, no plano da camada (impressa em pe)", f"EVA {m.eva:.0f} mm amortece: {F_b:.0f} N"))
    out.append(caso("Bandeja", "placa entre nervuras, direcao Y", "normal", F_b, 0.5 * Mb * cp / Ip, PETG["sr_z"],
                    "flexao em Y, entre camadas (metade da de X: placa em faixa)"))
    # 5. batente do bolso: bola chegando a 0,32 m/s no EVA 5 mm
    v_r = math.sqrt(10 / 7 * G * (68 * math.sin(math.radians(6)) / 1000))
    A_, Iw, cw = secao([(0, 17, 0, 4)], "y")
    k_w = 3 * PETG["E"] * Iw / 13 ** 3
    F_r, _ = impacto(v_r, [5.0 * 50 / m.eva, k_w])
    out.append(caso("Rampa", "batente do bolso (com EVA 5 mm)", "normal", F_r, F_r * 13 * cw / Iw, PETG["sr_z"],
                    "flexao entre camadas (rampa em pe)", f"bola a {v_r:.2f} m/s"))
    # 6. suporte do NEMA de cima: correia puxa a polia 15 mm acima da placa
    for regime, F in (("normal", 2 * T0), ("falha", T0 + F_falha)):
        A_, Is, cs = secao([(0, 42.3, 0, 4.5)], "y")
        A2, In, cn = secao([(0, 3.85, 0, 35.5)], "y")
        W = Is / cs + In / cn
        lim = PETG["fluencia"] if regime == "normal" else PETG["sr_xy"]
        out.append(caso("Suporte do NEMA de cima", "canto aba/placa", regime, F, F * 17 / W, lim,
                        "flexao no plano da camada (aba na mesa)"))
        d = [10.0, 10.0, 22.0]
        Mp = F * (15 + 72)
        Fp = Mp * max(d) / sum(x * x for x in d)
        out.append(caso("Suporte do NEMA de cima", "parafuso de madeira mais carregado", regime, Fp, Fp / 12,
                        PULL_MADEIRA, "arrancamento (N por mm de rosca)", "12 mm no MDF"))
    # 6b. suporte do NEMA de baixo: correia a 59 mm do piso; 2 parafusos na parede (Z 14 e 36) seguram o tombo
    for regime, F in (("normal", 2 * T0), ("falha", T0 + F_falha)):
        Mb = F * (m.zpB + m.dz_correia)
        Fp = Mb * 36.0 / (14.0 ** 2 + 36.0 ** 2)
        out.append(caso("Suporte do NEMA de baixo", "parafuso de madeira da parede (o de cima)", regime, Fp, Fp / 12,
                        PULL_MADEIRA, "arrancamento (N por mm de rosca)", "12 mm no MDF; os 2 do piso ajudam e nao entram"))
    # 7. tensora: bracos do bloco direito (o de baixo, 5,5 mm, leva quase tudo), rasgo no fim (8 mm)
    t1, t2 = 3.0, 5.5
    parte = t2 ** 3 / (t1 ** 3 + t2 ** 3)
    for regime, F in (("normal", 2 * T0), ("falha", T0 + F_falha)):
        A_, Ia2, ca2 = secao([(0, 17, 0, t2)], "y")
        lim = PETG["fluencia"] if regime == "normal" else PETG["sr_z"]
        out.append(caso("Bloco direito", "braco de baixo da tensora", regime, F * parte, F * parte * 8 * ca2 / Ia2, lim,
                        "flexao entre camadas (bloco impresso de lado)"))
    # 8. bloco nas paredes: 2 parafusos de madeira em cisalhamento
    out.append(caso("Bloco direito", "parafusos de madeira na parede", "falha", T0 + F_falha, (T0 + F_falha) / 2 / 12,
                    PULL_MADEIRA * 2, "cisalhamento no MDF (N por mm)"))
    return out, dict(F_trava=round(F_TRAVA), T0=T0, F_anel=round(F_anel), F_bandeja=round(F_b), F_batente=round(F_r),
                     v_anel=round(v, 2), a_carro=round(a, 2))


def main():
    m = L.M()
    cs, cargas = casos(m)
    for c in cs:
        print(("OK  " if c["ok"] else "RUIM"), c["peca"], "|", c["ponto"], "|", c["regime"], c["carga_N"], "N",
              c["tensao_MPa"], "/", c["limite_MPa"], "FS", c["fs"])
    print(cargas)
    (AQUI / "resistencia.json").write_text(json.dumps(dict(casos=cs, cargas=cargas), indent=1, ensure_ascii=False),
                                           encoding="utf8")


if __name__ == "__main__":
    main()
