"""Verificacao e exportacao de uma peca da Maquina A (Fases 4 e 5).

Uso: python -m maquina_a.verifica A01 [A02 ...]   (de dentro de cad_py/)
Saida: maquina_a/out/{step,stl,png}/ e maquina_a/out/relatorios/<ID>_<nome>.json
"""
import importlib
import json
import sys
import time
from pathlib import Path

import cadquery as cq
import numpy as np

from common import checks as C, fab, hardware as hw, render as R
from common import referencia as REF
from common.features import caixa
from common.malha import para_trimesh, _shape
from maquina_a import layout as L
from maquina_a import eixo as E
from maquina_a import montagem as MT

OUT = Path(__file__).resolve().parent / "out"
for d in ("step", "stl", "png", "relatorios"):
    (OUT / d).mkdir(parents=True, exist_ok=True)

HEX = {"M2": 1.5, "M3": 2.5, "M4": 3.0, "M5": 3.0}


def gabinete():
    a, m, h = L.GAB_LADO / 2, L.MDF_GAB, L.GAB_ALTURA
    return {
        "lateral_dir": caixa(a - m, a, -a, a, 0, h),
        "lateral_esq": caixa(-a, -a + m, -a, a, 0, h),
        "fundo": caixa(-a + m, a - m, a - m, a, 0, h),
    }


def hardware_eixo(eixo):
    return {f"{eixo}.{k}": E.para_maquina(v, eixo) for k, v in E.fixos(eixo, E.lados_fc(eixo)).items()}


_CARRO = {}


def carro_em(eixo, x):
    """Corpos que andam com o carro do eixo, na posicao x (trimesh, maquina)."""
    if eixo not in _CARRO:
        base = {f"{eixo}.patim": para_trimesh(E.para_maquina(hw.patim(0.0), eixo), 0.05, 0.2)}
        for nome, mod, var in MT.moveis(eixo):
            base[nome] = MT.malha_maquina(mod, var)
        base.update(MT.referencias_moveis(eixo))
        base.update({k: para_trimesh(v, 0.05, 0.2) for k, v in MT.hardware_carro(eixo).items()})
        _CARRO[eixo] = base
    out = {}
    for k, m in _CARRO[eixo].items():
        mm = m.copy()
        mm.apply_translation((x, 0, 0))
        out[k] = mm
    return out


def fixadores_maquina(mod, var):
    fs = []
    for f in mod.fixadores(var) if _aceita_var(mod.fixadores) else mod.fixadores():
        local_eixo = MT.no_eixo(mod) and not getattr(mod, "COORD_MAQUINA", False)
        p = E.ponto_para_maquina(f["ponto"], MT.eixo_de(mod, var)) if local_eixo else f["ponto"]
        d = E.dir_para_maquina(f["dir"], MT.eixo_de(mod, var)) if local_eixo else f["dir"]
        fs.append(dict(f, ponto=p, dir=d))
    return fs


def _aceita_var(fn):
    import inspect
    return len(inspect.signature(fn).parameters) >= 1


def corpos_fixadores(fs):
    out, chaves = {}, {}
    for k, f in enumerate(fs):
        fn = hw.parafuso_iso7380 if f["tipo"] == "ISO7380" else hw.parafuso_din912
        out[f"fix{k}_{f['nome']}"] = fn(f["bitola"], f.get("comp_modelo", f["comp"]), f["ponto"], f["dir"])
        n = cq.Vector(*f["dir"]).normalized()
        hc = (hw.ISO7380 if f["tipo"] == "ISO7380" else hw.DIN912)[f["bitola"]][1]
        base = cq.Vector(*f["ponto"]) - n * (hc + 0.3)
        from common.features import cilindro
        chaves[f"chave{k}_{f['nome']}"] = (cilindro(HEX[f["bitola"]] * 1.6, f.get("chave", 60), base.toTuple(), (-n).toTuple()),
                                            tuple(f.get("antes_de", ())))
    return out, chaves


def verificar(pid, var):
    mod = MT.modulo(pid)
    t0 = time.time()
    nome = f"{mod.ID}_{mod.NOME}" + ("" if var == MT.var_principal(mod) else f"_{var}")
    rel = dict(id=mod.ID, nome=mod.NOME, variante=var, titulo=mod.TITULO)

    peca = mod.build(None, var)
    mesa = mod.impressao(var)
    rel["1_brep"] = C.c1_brep(peca, getattr(mod, "ESPERADO_SOLIDOS", 1))
    rel["2_stl"], m_mesa = C.c2_stl(mesa)
    rel["3_mesa"] = C.c3_mesa(m_mesa, mod.IMPRESSORA)

    ref_nome = MT.referencia(mod, var)
    ref = REF.malha(*ref_nome) if ref_nome else None
    rel["4_intencao"] = C.c4_intencao(peca, ref, getattr(mod, "JUSTIFICATIVA", ""))
    rel["5_parede"] = C.c5_parede(m_mesa, getattr(mod, "PAREDE_MINIMA", fab.PAREDE_MIN))
    rel["6_overhang"] = C.c6_overhang(m_mesa, brep=mesa)

    # contexto fixo: gabinete, compradas do(s) eixo(s), outras pecas novas fixas
    fixos = dict(gabinete())
    fixos.update({k: v for k, v in MT.hardware_fixo().items() if mod.ID not in ("A17",) or k != "sg90"})
    if "A12" in MT.PECAS:
        fixos.update(MT.corpos_bandeja())
    for e in MT.eixos_contexto(mod, var):
        fixos.update(hardware_eixo(e))
    for outro, ovar, obj in MT.pecas_fixas(excluir=(mod.ID, var)):
        fixos[f"{outro}{'' if ovar == '-' else '.' + ovar}"] = obj
    fs = fixadores_maquina(mod, var)
    corpos_fix, chaves = corpos_fixadores(fs)

    esperado = getattr(mod, "CONTATO_ESPERADO", ())
    ignorar = {k for k in fixos if any(e in k for e in esperado)}
    rel["7_interferencia"] = C.c7_interferencia(peca, fixos, ignorar=ignorar)
    # pecas do proprio carro (paradas juntas, carro em x=0)
    eixo_mov0 = MT.eixo_de(mod, var) if MT.no_eixo(mod) else None
    if getattr(mod, "MOVEL", False) and eixo_mov0:
        from common import hardware as _hw
        carro = {f"{eixo_mov0}.patim": E.para_maquina(_hw.patim(0.0), eixo_mov0), **MT.hardware_carro(eixo_mov0)}
        for nome_c, m2, v2 in MT.moveis(eixo_mov0):
            if (m2.ID, v2) != (mod.ID, var):
                carro[nome_c] = m2.build(None, v2)
        ign = {k for k in carro if any(e in k for e in esperado)}
        rc = C.c7_interferencia(peca, carro, ignorar=ign)
        rel["7_interferencia"]["carro"] = rc
        rel["7_interferencia"]["ok"] = rel["7_interferencia"]["ok"] and rc["ok"]
    # parafusos da propria peca: so contra a peca e o hardware (paredes/perfil recebem o parafuso de proposito)
    hw_sem_receptor = {k: v for k, v in fixos.items() if not any(s in k for s in ("lateral", "fundo", "perfil", "nema"))}
    inter_fix = (C.c7_interferencia(cq.Workplane().add([_shape(v) for v in corpos_fix.values()]), {"peca": peca, **hw_sem_receptor})
                 if corpos_fix else dict(ok=True, colisoes={}))
    rel["7_interferencia"]["parafusos"] = inter_fix
    rel["7_interferencia"]["ok"] = rel["7_interferencia"]["ok"] and inter_fix["ok"]

    # movimento: carro(s) do eixo varrendo o curso ate o fim de curso
    eixo_mov = MT.eixo_de(mod, var) if MT.no_eixo(mod) else None
    eixos_varrer = [eixo_mov] if eixo_mov else ([] if getattr(mod, "FERRAMENTA", False) else list(getattr(mod, "EIXOS_CONTEXTO", [])))
    if eixos_varrer:
        e0 = eixos_varrer[0]
        c0, c1 = MT.CURSO[e0]
        xs = list(np.arange(c0, c1 + 1e-6, fab.PASSO_VARREDURA)) + [c1]
        if getattr(mod, "MOVEL", False):
            fixos_mov = {k: para_trimesh(v, 0.05, 0.2) for k, v in fixos.items() if not any(t in k for t in ("trilho", "correia"))}
            # a alavanca do FC e tocada de proposito: fica fora da folga e ganha checagem propria
            fc = {k: v for k, v in fixos_mov.items() if ".fc" in k}
            fixos_mov = {k: v for k, v in fixos_mov.items() if ".fc" not in k}
            rel["8_movimento"] = C.c8_movimento(fixos_mov, lambda x: carro_em(eixo_mov, x), xs)
            if fc and mod.ID == "A05":
                rel["8_movimento"]["fim_de_curso"] = C.contato_fc(para_trimesh(peca, 0.05, 0.2), fc, L.CURSO_JOGO, L.CURSO_REF)
                rel["8_movimento"]["ok"] = rel["8_movimento"]["ok"] and rel["8_movimento"]["fim_de_curso"]["ok"]
        else:
            rel["8_movimento"] = C.c8_movimento({mod.ID: para_trimesh(peca, 0.05, 0.2)}, lambda x: carro_em(e0, x), xs)
    else:
        rel["8_movimento"] = dict(ok=True, nota="peca fora dos eixos")

    pares = mod.pares_furos(var) if hasattr(mod, "pares_furos") else []
    rel["9_furos"] = C.c9_furos(pares) if pares else dict(ok=True, nota="sem furacao entre pecas")
    rel["10_bola"] = mod.checa_bola(var) if hasattr(mod, "checa_bola") else dict(ok=True, nota="peca fora do caminho da bola")

    # 13: acesso de chave com o carro no lado oposto
    obst = dict(fixos)
    obst["peca"] = peca
    if eixo_mov:
        lado = -np.sign(np.mean([f["ponto"][0] for f in fs])) if fs else -1
        for k, m in carro_em(eixo_mov, lado * L.CURSO_REF).items():
            obst[k] = cq.Workplane().add(_trimesh_para_cq(m))
    rel["13_montagem"] = C.c13_acesso(chaves, obst)
    rel["13_montagem"]["sequencia"] = mod.FICHA.get("montagem", "")

    rel["12_fatiamento"] = C.c12_estimativa(m_mesa, getattr(mod, "ESTRUTURAL", False))

    # exporta
    cq.exporters.export(peca, str(OUT / "step" / f"{nome}.step"))
    m_mesa.export(OUT / "stl" / f"{nome}.stl")

    # 11: imagens
    m_peca = para_trimesh(peca, 0.05, 0.2)
    ctx = {}
    for k, v in fixos.items():
        if k.startswith(tuple(f"{e}." for e in MT.eixos_contexto(mod, var))):
            ctx[k] = (para_trimesh(v, 0.1, 0.3), R.COR_HW, 1.0)
    pv_dir = getattr(mod, "VISTA", (-1, -1.3, 0.9))
    R.iso(str(OUT / "png" / f"{nome}.png"), m_peca, direcao=pv_dir, titulo=f"{mod.ID} {mod.TITULO} ({var})")
    R.iso(str(OUT / "png" / f"{nome}_contexto.png"), m_peca, ctx, direcao=pv_dir, alvo=m_peca,
          escala=float(np.linalg.norm(m_peca.extents)) * 1.1, titulo=f"{mod.ID} na montagem ({var})")
    R.mesa(str(OUT / "png" / f"{nome}_mesa.png"), m_mesa, fab.IMPRESSORAS[mod.IMPRESSORA][:2])
    R.lado_a_lado(str(OUT / "png" / f"{nome}_lado_a_lado.png"), ref, m_peca, direcao=pv_dir)
    rel["11_visual"] = dict(ok=None, imagens=[f"png/{nome}{s}.png" for s in ("", "_contexto", "_mesa", "_lado_a_lado")],
                            nota="avaliar abrindo as imagens")

    rel["aprovada"] = all(v.get("ok") is not False for k, v in rel.items() if isinstance(v, dict) and k[0].isdigit())
    rel["tempo_verificacao_s"] = round(time.time() - t0, 1)
    rel["fixadores"] = [dict(nome=f["nome"], tipo=f["tipo"], bitola=f["bitola"], comp=f["comp"], extra=f.get("extra", ""))
                        for f in fs]
    (OUT / "relatorios" / f"{nome}.json").write_text(json.dumps(rel, indent=1, ensure_ascii=False, default=str), encoding="utf8")
    return rel


def _trimesh_para_cq(m):
    """Malha -> solido OCC (so para obstaculos de checagem)."""
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeFace, BRepBuilderAPI_Sewing
    from OCP.gp import gp_Pnt
    sew = BRepBuilderAPI_Sewing(1e-3)
    V = m.vertices
    for f in m.faces:
        poly = BRepBuilderAPI_MakePolygon(*[gp_Pnt(*map(float, V[i])) for i in f], True)
        sew.Add(BRepBuilderAPI_MakeFace(poly.Wire()).Face())
    sew.Perform()
    sh = cq.Shape.cast(sew.SewedShape())
    try:
        return cq.Solid.makeSolid(cq.Shell(sh.wrapped)) if sh.ShapeType() == "Shell" else sh
    except Exception:
        return sh


def resumo(rel):
    linhas = []
    for k, v in rel.items():
        if isinstance(v, dict) and k[0].isdigit():
            st = "ok" if v.get("ok") else ("?" if v.get("ok") is None else "FALHOU")
            extra = {kk: vv for kk, vv in v.items() if kk not in ("ok", "imagens", "sequencia", "furos")}
            linhas.append(f"  {k:16s} {st:6s} {json.dumps(extra, ensure_ascii=False, default=str)[:220]}")
    return "\n".join(linhas)


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        pid, _, var = arg.partition(":")
        mod = MT.modulo(pid)
        for v in ([var] if var else MT.variantes(mod)):
            r = verificar(pid, v)
            print(f"{pid} {v}: {'APROVADA' if r['aprovada'] else 'REPROVADA'} ({r['tempo_verificacao_s']} s)")
            print(resumo(r))
