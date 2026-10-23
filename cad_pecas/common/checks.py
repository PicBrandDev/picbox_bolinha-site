"""Suite de verificacao (Fase 4). Cada funcao devolve dict(ok=bool, ...)."""
import math

import numpy as np
import cadquery as cq
import trimesh

from . import fab
from .malha import para_trimesh, para_manifold, _shape


def c1_brep(obj, esperado=1):
    sh = _shape(obj)
    n = len(cq.Workplane("XY").add(sh).solids().vals())
    return dict(ok=bool(sh.isValid()) and n == esperado, valido=bool(sh.isValid()), solidos=n,
                volume_mm3=round(sh.Volume(), 1))


def c2_stl(obj_mesa):
    m = para_trimesh(obj_mesa, fab.TOL_LINEAR, fab.TOL_ANGULAR)
    areas = m.area_faces
    degeneradas = int((areas < 1e-8).sum())
    ok = m.is_watertight and m.is_winding_consistent and degeneradas == 0 and m.body_count == 1
    return dict(ok=bool(ok), estanque=bool(m.is_watertight), winding=bool(m.is_winding_consistent),
                degeneradas=degeneradas, corpos=int(m.body_count), triangulos=len(m.faces),
                tol_linear=fab.TOL_LINEAR, tol_angular=fab.TOL_ANGULAR), m


def c3_mesa(m, impressora=fab.MESA_PADRAO):
    lim = fab.IMPRESSORAS[impressora]
    ext = m.extents
    xy = sorted(ext[:2])
    cabe = xy[1] <= max(lim[:2]) and xy[0] <= min(lim[:2]) and ext[2] <= lim[2] and abs(m.bounds[0][2]) < 1e-3
    return dict(ok=bool(cabe), impressora=impressora, tamanho=[round(float(v), 1) for v in ext], mesa=list(lim))


def c4_intencao(obj_maq, ref, justificativa=""):
    if ref is None:
        return dict(ok=True, nota="sem referencia coletada (peca nova)")
    bb = _shape(obj_maq).BoundingBox()
    novo = np.array([[bb.xmin, bb.ymin, bb.zmin], [bb.xmax, bb.ymax, bb.zmax]])
    d = novo - ref.bounds
    dmax = float(np.abs(d).max())
    ok = dmax <= fab.DELTA_INTENCAO or bool(justificativa)
    return dict(ok=ok, delta_min=[round(float(v), 1) for v in d[0]], delta_max=[round(float(v), 1) for v in d[1]],
                delta_abs_max=round(dmax, 1), justificativa=justificativa)


def c5_parede(m, minimo=fab.PAREDE_MIN, n=3000, seed=1):
    pts, idx = trimesh.sample.sample_surface_even(m, n, seed=seed)
    nrm = m.face_normals[idx]
    orig = pts - nrm * 1e-3
    loc, ri, _ = m.ray.intersects_location(orig, -nrm, multiple_hits=False)
    d = np.full(len(pts), np.inf)
    d[ri] = np.linalg.norm(loc - orig[ri], axis=1)
    finitos = d[np.isfinite(d)]
    # arestas de filete/chanfro dao leituras falsas muito curtas; usa o percentil 1
    p1 = float(np.percentile(finitos, 1)) if len(finitos) else float("inf")
    finos = int((finitos < minimo * 0.9).sum())
    return dict(ok=p1 >= minimo * 0.9, percentil1_mm=round(p1, 2), minimo=minimo,
                amostras_abaixo=finos, amostras=len(finitos))


def _area_overhang_brep(obj, z0, lim):
    """Area virada para baixo alem do limite, por face B-rep; furos cilindricos ate fab.TEARDROP_ACIMA_DE sao
    aceitos sem gota (tabela de folgas) e nao entram na conta."""
    area = 0.0
    for f in _shape(obj).Faces():
        if f.geomType() == "CYLINDER":
            from OCP.BRepAdaptor import BRepAdaptor_Surface
            if BRepAdaptor_Surface(f.wrapped).Cylinder().Radius() * 2 <= fab.TEARDROP_ACIMA_DE + 0.2:
                continue
        v, t = f.tessellate(0.05, 0.2)
        if not t:
            continue
        P = np.array([p.toTuple() for p in v])
        T = np.array(t)
        a, b, c = P[T[:, 0]], P[T[:, 1]], P[T[:, 2]]
        cr = np.cross(b - a, c - a)
        ar = np.linalg.norm(cr, axis=1)
        ok = ar > 1e-12
        nz = np.zeros(len(T))
        nz[ok] = cr[ok, 2] / ar[ok]
        cz = (a[:, 2] + b[:, 2] + c[:, 2]) / 3
        sel = ok & (nz < lim) & (nz >= -0.999) & (cz > z0 + 0.05)
        area += float(ar[sel].sum() / 2)
    return area


def c6_overhang(m, lim_graus=fab.OVERHANG_MAX_GRAUS, ponte_max=fab.PONTE_MAX, brep=None):
    z0 = m.bounds[0][2]
    n = m.face_normals
    cz = m.triangles_center[:, 2]
    fora_mesa = cz > z0 + 0.05
    lim = -math.cos(math.radians(lim_graus)) - 0.02
    over = (n[:, 2] < lim) & fora_mesa
    plano = (n[:, 2] < -0.999) & fora_mesa
    area_over = _area_overhang_brep(brep, z0, lim) if brep is not None else float(m.area_faces[over & ~plano].sum())
    # pontes: regioes horizontais viradas para baixo; vao = menor lado do retangulo minimo
    vaos = []
    if plano.any():
        sub = m.submesh([np.where(plano)[0]], append=True)
        for comp in sub.split(only_watertight=False):
            pts2 = comp.vertices[:, :2]
            if len(pts2) < 3:
                continue
            try:
                _, ext = trimesh.bounds.oriented_bounds_2D(pts2)
                vaos.append(float(min(ext)))
            except Exception:
                pass
    vao_max = max(vaos) if vaos else 0.0
    return dict(ok=area_over < 25.0 and vao_max <= ponte_max, area_overhang_mm2=round(area_over, 1),
                ponte_max_mm=round(vao_max, 1), limite_graus=lim_graus)


def _vol_inter(a, b):
    try:
        return float(_shape(a).intersect(_shape(b)).Volume())
    except Exception:
        return float("nan")


def c7_interferencia(obj, outros, ignorar=()):
    sh = _shape(obj)
    bb = sh.BoundingBox()
    res = {}
    for nome, o in outros.items():
        if nome in ignorar:
            continue
        ob = _shape(o).BoundingBox()
        if (ob.xmin > bb.xmax or ob.xmax < bb.xmin or ob.ymin > bb.ymax or ob.ymax < bb.ymin
                or ob.zmin > bb.zmax or ob.zmax < bb.zmin):
            continue
        v = _vol_inter(sh, o)
        if not (v <= fab.INTERFERENCIA_MAX_MM3):
            res[nome] = round(v, 3)
    return dict(ok=not res, colisoes=res)


def c8_movimento(fixos, moveis_em, posicoes, folga=fab.FOLGA_MOVIMENTO, ignorar_pares=()):
    """fixos: nome -> trimesh/cq; moveis_em(pos) -> nome -> trimesh (posicionado). Folga minima por par."""
    F = {k: para_manifold(v if isinstance(v, trimesh.Trimesh) else para_trimesh(v, 0.05, 0.2)) for k, v in fixos.items()}
    piores = {}
    for pos in posicoes:
        M = moveis_em(pos)
        for km, vm in M.items():
            mm = para_manifold(vm)
            for kf, mf_ in F.items():
                if (km, kf) in ignorar_pares:
                    continue
                g = mm.min_gap(mf_, folga + 5.0)
                if (km, kf) not in piores or g < piores[(km, kf)][0]:
                    piores[(km, kf)] = (g, pos)
    ruins = {f"{a} x {b}": dict(folga=round(g, 2), pos=p) for (a, b), (g, p) in piores.items() if g < folga}
    menor = min(piores.items(), key=lambda kv: kv[1][0]) if piores else None
    if menor and menor[1][0] >= folga + 5.0 - 1e-6:
        menor = ((menor[0][0], menor[0][1]), (float("inf"), menor[1][1]))
    return dict(ok=not ruins, abaixo_da_folga=ruins, folga_exigida=folga,
                menor=(f"{menor[0][0]} x {menor[0][1]}", round(menor[1][0], 2), menor[1][1]) if menor else None,
                passos=len(posicoes))


def _dist_retas(p1, d1, p2, d2):
    p1, d1, p2, d2 = map(lambda v: np.asarray(v, float), (p1, d1, p2, d2))
    d1, d2 = d1 / np.linalg.norm(d1), d2 / np.linalg.norm(d2)
    ang = math.degrees(math.acos(min(1.0, abs(float(d1 @ d2)))))
    w = p2 - p1
    c = np.cross(d1, d2)
    if np.linalg.norm(c) < 1e-9:
        dist = float(np.linalg.norm(np.cross(w, d1)))
    else:
        dist = float(abs(w @ c) / np.linalg.norm(c))
    return dist, ang


def c9_furos(pares):
    """pares: lista (nome, (p, d) da peca, (p, d) do par)."""
    res = []
    for nome, (pa, da), (pb, db) in pares:
        dist, ang = _dist_retas(pa, da, pb, db)
        res.append(dict(furo=nome, excentricidade=round(dist, 3), angulo=round(ang, 3),
                        ok=dist <= fab.EXCENTRICIDADE_MAX and ang < 0.5))
    return dict(ok=all(r["ok"] for r in res), furos=res)


def c12_estimativa(m, estrutural=False):
    P = fab.PERFIL_IMPRESSAO
    v = abs(m.volume) / 1000.0
    casca = min(v, m.area / 100.0 * 0.16)
    infill = 0.4 if estrutural else 0.2
    g = P["densidade_g_cm3"] * (casca + infill * (v - casca))
    h = g / P["vazao_g_h"] + P["preparo_h"]
    return dict(ok=True, gramas=round(g, 1), horas=round(h, 2), metodo="estimado por volume (sem slicer CLI)")


def c13_acesso(chaves, obstaculos):
    """chaves: nome -> (volume do acesso (cq), nomes montados DEPOIS deste parafuso). obstaculos: nome -> cq."""
    ruins = {}
    for k, (vol, depois) in chaves.items():
        r = c7_interferencia(vol, {n: o for n, o in obstaculos.items() if not any(d in n for d in depois)})
        if not r["ok"]:
            ruins[k] = r["colisoes"]
    return dict(ok=not ruins, bloqueados=ruins, n=len(chaves))


def contato_fc(placa, fcs, curso_jogo, curso_ref, passo=0.1):
    """Posicao do carro em que a placa toca cada fim de curso: tem que ser depois do curso de jogo e antes do fundo."""
    res = {}
    P = para_manifold(placa)
    for nome, m in fcs.items():
        F = para_manifold(m if isinstance(m, trimesh.Trimesh) else para_trimesh(m, 0.05, 0.2))
        c = F.bounding_box()
        s = 1 if (c[0] + c[3]) / 2 > 0 else -1
        toque = None
        x = curso_jogo - 5.0
        while x <= curso_ref + 2.0:
            if P.translate((s * x, 0, 0)).min_gap(F, 0.5) <= 0.01:
                toque = round(x, 1)
                break
            x += passo
        res[nome] = dict(toque_em=toque, ok=toque is not None and curso_jogo < toque <= curso_ref - 1.0)
    return dict(ok=all(v["ok"] for v in res.values()), **res)
