"""Registro das pecas novas da Maquina A e do contexto de montagem usado nas checagens."""
import importlib
from functools import lru_cache

from common import referencia as REF
from common.malha import para_trimesh

# ID -> modulo em maquina_a/parts. Ordem = fila de modelagem.
PECAS = {
    "A01": "A01_bloco_motor",
    "A02": "A02_bloco_tensor",
    "A04": "A04_deslizador",
    "A05": "A05_placa_carro",
    "A07": "A07_presilha",
    "A09": "A09_boca",
    "A10": "A10_berco",
    "A11": "A11_portinhola",
    "A36": "A36_garfo",
    "A08": "A08_gabarito",
    "A15": "A15_saida_magazine",
    "A16": "A16_escapamento",
    "A26": "A26_entrada_berco",
    "A17": "A17_balancim",
    "A18": "A18_entrada_magazine",
    "A19": "A19_suporte_entrada",
    "A12": "A12_calco",
    "A13": "A13_rodape",
    "A20": "A20_base_elevador",
    "A24": "A24_suporte_motor_elevador",
    "A21": "A21_fuso",
    "A27": "A27_cabeca_elevador",
    "A22": "A22_tampa_elevador",
    "A25": "A25_saida_elevador",
    "A23": "A23_calha_elevador",
}

# curso real de cada carro: o eixo A so tem fim de curso do lado do motor; no lado do tensor para na carga (-140)
CURSO = {"A": (-141.0, 144.2), "B": (-144.2, 144.2)}

# carro: pecas antigas que andam com cada carro (referencia ate a nova existir): (peca antiga, prefixo, ID novo)
CARRO_REF = {
    "B": [("eixo_placa_carro", "B.", "A05"), ("eixo_garra", "B.", "A06"), ("eixo_presilha", "B.", "A07"),
          ("boca_alvo", "boca.", "A09")],
    "A": [("eixo_placa_carro", "A.", "A05"), ("eixo_garra", "A.", "A06"), ("eixo_presilha", "A.", "A07"),
          ("soltura_berco", "sol.", "A10"), ("soltura_batente", "sol.", "A11")],
}


# grupo de cada peca na maquina (pasta dos arquivos gerados)
GRUPOS = {
    "1_eixos": ("A01", "A02", "A04", "A05", "A07", "A08"),
    "2_boca_e_soltura": ("A09", "A10", "A11", "A36"),
    "3_magazine_e_carga": ("A15", "A16", "A26", "A17", "A18", "A19"),
    "4_bandeja": ("A12", "A13"),
    "5_elevador": ("A20", "A24", "A21", "A27", "A22", "A25", "A23"),
}
GRUPO_TITULO = {"1_eixos": "Eixos lineares (A em cima: bola; B embaixo: buraco)", "2_boca_e_soltura": "Boca e soltura",
                "3_magazine_e_carga": "Magazine e carga do berco", "4_bandeja": "Bandeja", "5_elevador": "Elevador de fuso"}

# onde cada variante vai na maquina (entra no nome do arquivo)
POSICAO = {
    ("A01", "B"): "eixoB-baixo_ponta-direita-motor", ("A01", "A"): "eixoA-cima_ponta-direita-motor",
    ("A02", "B"): "eixoB-baixo_ponta-esquerda-tensor", ("A02", "A"): "eixoA-cima_ponta-esquerda-tensor",
    ("A04", "B"): "eixoB-baixo_ponta-esquerda-tensor", ("A04", "A"): "eixoA-cima_ponta-esquerda-tensor",
    ("A05", "B"): "eixoB-baixo_carro", ("A05", "A"): "eixoA-cima_carro",
    ("A07", "B"): "eixoB-baixo_carro-correia", ("A07", "A"): "eixoA-cima_carro-correia",
    ("A08", "B"): "ferramenta_centragem-trilho",
    ("A09", "B"): "eixoB-baixo_carro", ("A10", "A"): "eixoA-cima_carro",
    ("A11", "t"): "eixoA-cima_berco-tras", ("A11", "f"): "eixoA-cima_berco-frente", ("A36", "A"): "eixoA-cima_berco-solenoide",
    ("A15", "-"): "lateral-esquerda_tras", ("A16", "-"): "lateral-esquerda_meio", ("A26", "-"): "lateral-esquerda_frente",
    ("A17", "-"): "lateral-esquerda_no-servo", ("A18", "-"): "direita_tras", ("A19", "-"): "lateral-direita_tras",
    ("A12", "0"): "frente-esquerda", ("A12", "1"): "tras-esquerda", ("A12", "2"): "frente-centro", ("A12", "3"): "tras-centro",
    ("A12", "4"): "frente-centro-direita", ("A12", "5"): "tras-direita",
    ("A13", "e"): "tras-esquerda", ("A13", "d"): "tras-direita",
    ("A20", "-"): "pe-sob-divisoria", ("A24", "-"): "motor-no-pedestal", ("A21", "1"): "segmento-1-de-baixo",
    ("A21", "2"): "segmento-2-do-meio", ("A21", "3"): "segmento-3-de-cima", ("A27", "-"): "topo-do-tubo",
    ("A22", "-"): "tampa", ("A25", "-"): "saida-do-topo", ("A23", "-"): "calha-ate-o-magazine",
}


def grupo(pid):
    return next(g for g, ids in GRUPOS.items() if pid in ids)


def nome_arquivo(pid, var):
    """Nome dos arquivos gerados: ID_peca__posicao[__xN] (sem extensao)."""
    m = modulo(pid)
    q = m.QTD[var]
    base = f"{pid}_{m.NOME.replace('_', '-')}__{POSICAO[(pid, var)]}"
    if pid == "A12":
        base += f"_h{m.altura(var):.1f}mm".replace(".", ",")
    return base + (f"__x{q}" if q > 1 else "")


@lru_cache(maxsize=None)
def modulo(pid):
    return importlib.import_module(f"maquina_a.pecas.{PECAS[pid]}")


def variantes(mod):
    return list(mod.QTD.keys())


def var_principal(mod):
    return variantes(mod)[0]


def no_eixo(mod):
    return getattr(mod, "NO_EIXO", True)


def eixo_de(mod, var):
    return getattr(mod, "EIXO", var) if no_eixo(mod) else None


def eixos_contexto(mod, var):
    return [eixo_de(mod, var)] if no_eixo(mod) else getattr(mod, "EIXOS_CONTEXTO", [])


def referencia(mod, var):
    """(peca antiga, indice da instancia) para comparar intencao; None se nao houver."""
    ref = getattr(mod, "REF", None)
    if not ref:
        return None
    if isinstance(ref, dict):
        ref = ref.get(var)
        if not ref:
            return None
    nomes = [i["id"] for i in REF.instancias(ref)]
    pref = f"{eixo_de(mod, var)}." if no_eixo(mod) else ""
    idx = next((k for k, n in enumerate(nomes) if n.startswith(pref)), 0)
    return (ref, idx)


@lru_cache(maxsize=None)
def _build(pid, var):
    return modulo(pid).build(None, var)


@lru_cache(maxsize=None)
def malha_maquina(mod, var):
    return para_trimesh(mod.build(None, var), 0.05, 0.2)


def pecas_fixas(excluir=()):
    for pid in PECAS:
        mod = modulo(pid)
        if getattr(mod, "MOVEL", False) or getattr(mod, "FERRAMENTA", False):
            continue
        for v in variantes(mod):
            if (pid, v) == tuple(excluir):
                continue
            yield pid, v, _build(pid, v)


def moveis(eixo):
    out = []
    for pid in PECAS:
        mod = modulo(pid)
        if not getattr(mod, "MOVEL", False):
            continue
        if getattr(mod, "EIXO", None) == eixo:
            out += [(f"{pid}.{v}", mod, v) for v in variantes(mod)]
        elif not hasattr(mod, "EIXO") and eixo in mod.QTD:
            out.append((f"{pid}.{eixo}", mod, eixo))
    return out


@lru_cache(maxsize=None)
def referencias_moveis(eixo):
    out = {}
    for peca, pref, novo in CARRO_REF[eixo]:
        if novo in PECAS:
            continue
        for k, inst in enumerate(REF.instancias(peca)):
            if inst["id"].startswith(pref):
                out[f"ref:{inst['id']}"] = REF.malha(peca, k)
    return out


def pares_movimento_ignorados(eixo):
    return ()


def hardware_carro(eixo):
    """Compradas que andam com o carro (coordenadas da maquina, carro em x=0), alem do patim."""
    out = {}
    if eixo == "A" and "A10" in PECAS:
        from common import hardware as hw
        from maquina_a import soltura as S
        exposto = S.Z_SOL_BASE - (S.Z_PINO_FECHADO + S.GARFO_H / 2) + 4.0
        out["A.solenoide"] = hw.solenoide(S.X_SOL_FACE, S.Y_PINO, S.Z_SOL_BASE, exposto)
    return out


def hardware_fixo():
    """Compradas fixas fora dos eixos (coordenadas da maquina)."""
    from common import hardware as hw
    from maquina_a import magazine as M
    out = {}
    if "A16" in PECAS:
        out["sg90"] = hw.sg90(M.X_PAREDE, M.Y_PIVO, M.Z_PIVO, +1)
    if "A15" in PECAS:
        a, b = M.eixo_tubo(M.X_TUBO[0]), M.eixo_tubo(M.X_TUBO[1])
        out["tubo"] = hw.tubo(a[0], b[0], M.Y_MAG, a[2], b[2], M.TUBO_D, M.TUBO_DI)
    if "A20" in PECAS:
        out.update(_hw_elevador())
    return out


@lru_cache(maxsize=None)
def _hw_elevador():
    from maquina_a import elevador as EL
    return EL.hardware()


def corpos_magazine():
    """Apoios da bola no caminho do magazine (o que a bola toca de proposito)."""
    out = {pid: modulo(pid).build(None, var_principal(modulo(pid))) for pid in ("A15", "A16", "A26", "A18") if pid in PECAS}
    out.update({k: v for k, v in hardware_fixo().items() if k == "tubo"})
    return out


def corpos_contexto_caminho(carro_a=-140.0):
    """Tudo o que nao e apoio, com o carro A na posicao de carga (para a checagem do caminho da bola)."""
    import cadquery as cq
    from common import hardware as hw
    from maquina_a import eixo as E
    out = {}
    for pid, v, obj in pecas_fixas():
        if pid not in ("A15", "A16", "A26", "A18"):
            out[f"{pid}.{v}"] = obj
    for e in ("A", "B"):
        for k, w in E.fixos(e, E.lados_fc(e)).items():
            out[f"{e}.{k}"] = E.para_maquina(w, e)
    out.update({k: v for k, v in hardware_fixo().items() if k != "tubo"})
    carro = {"A.patim": E.para_maquina(hw.patim(0.0), "A"), **hardware_carro("A")}
    for nome, m, v in moveis("A"):
        carro[nome] = m.build(None, v)
    for k, w in carro.items():
        sh = (w.val() if isinstance(w, cq.Workplane) else w).translate((carro_a, 0, 0))
        out[f"carro:{k}"] = cq.Workplane("XY").add(sh)
    return out


def corpos_bandeja():
    """Corte (MDF da bandeja, EVA) e divisoria com o furo do tubo do elevador (referencia, coordenadas da maquina)."""
    import math
    import cadquery as cq
    from common.features import caixa, cilindro
    from maquina_a import bandeja as B
    from maquina_a import layout as L
    n = cq.Vector(math.tan(B.INCL_X), -math.tan(B.INCL_Y), 1.0).normalized()
    xd = (1, 0, -math.tan(B.INCL_X))

    def acima(zfun):
        x, y = 0.0, -100.0
        return cq.Workplane(cq.Plane(origin=(x, y, zfun(x, y)), xDir=xd, normal=n.toTuple())).rect(2000, 2000).extrude(500)

    base = caixa(B.X_BAND[0], B.X_BAND[1], B.Y_BAND[0], B.Y_BAND[1], 1050, 1250)
    mdf = base.cut(acima(lambda x, y: B.z_eva(x, y) - B.EVA)).intersect(acima(B.z_mdf_baixo))
    from maquina_a import elevador as EL
    furo = cilindro(EL.D_FURO_DIVISORIA, 400, (*EL.C, 900), (0, 0, 1)).union(caixa(EL.C[0], 300, -300, EL.C[1], 900, 1300))
    mdf = mdf.cut(furo)
    eva = caixa(B.X_BAND[0], B.X_BAND[1], B.Y_BAND[0], B.Y_RODAPE[0], 1050, 1250)
    eva = eva.cut(acima(B.z_eva)).intersect(acima(lambda x, y: B.z_eva(x, y) - B.EVA))
    eva = eva.cut(furo)
    for sx in (-1, 1):                                     # recorte nos cantos de tras: pes dos blocos dos eixos (x>=|200|)
        canto = caixa(sx * B.X_RECORTE[0], sx * 300, B.Y_RECORTE, 0, 900, 1300) if sx > 0 else caixa(-300, -B.X_RECORTE[0], B.Y_RECORTE, 0, 900, 1300)
        mdf = mdf.cut(canto)
        eva = eva.cut(canto)
    a, m = L.GAB_LADO / 2, L.MDF_GAB
    div = caixa(-a + m, a - m, -a + m, a - m, L.Z_DIVISORIA - m, L.Z_DIVISORIA)
    div = div.cut(furo)                                    # tubo do elevador (furo Ø101 + recorte ate o canto)
    if "A20" in PECAS:                                     # furos dos parafusos da base do elevador
        a20 = modulo("A20")
        for ang in a20.FUROS_FLANGE:
            div = div.cut(cilindro(4.0, 40, EL.p(a20.R_FURO_FLANGE, ang, L.Z_DIVISORIA - 30), (0, 0, 1)))
    return {"bandeja_mdf": mdf, "bandeja_eva": eva, "divisoria": div}


def corpos_carro(eixo):
    """Pecas e compradas que andam com o carro (carro em x=0, coordenadas da maquina)."""
    from common import hardware as hw
    from maquina_a import eixo as E
    out = {f"{eixo}.patim": E.para_maquina(hw.patim(0.0), eixo), **hardware_carro(eixo)}
    for nome, m, v in moveis(eixo):
        out[nome] = m.build(None, v)
    return out


def corpos_contexto_bandeja():
    """O que e fixo em volta da bandeja: pecas fixas (menos as da propria bandeja), compradas do eixo B, divisoria."""
    from maquina_a import eixo as E
    out = {}
    for pid, v, obj in pecas_fixas():
        if pid != "A12":
            out[f"{pid}.{v}"] = obj
    for k, w in E.fixos("B", E.lados_fc("B")).items():
        out[f"B.{k}"] = E.para_maquina(w, "B")
    out["divisoria"] = corpos_bandeja()["divisoria"]
    return out
