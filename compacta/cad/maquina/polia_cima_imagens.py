"""Imagens da polia de cima R2.2 (vao junto com os STL em imprimir/polia_de_cima):
  adaptador_corte.png  - corte do adaptador N20 -> M5
  montagem_r2.2.png    - montado no corte da torre de cima (malha real) + ordem explodida
Chamado por polia_cima.main()."""
import base64
import json
from pathlib import Path

import matplotlib
import numpy as np
import trimesh

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import PathPatch, Rectangle  # noqa: E402
from matplotlib.path import Path as MPath  # noqa: E402

import elevador2 as E  # noqa: E402

AQUI = Path(__file__).resolve().parent
Z0 = 419.0
C = dict(motor="#8a8f98", ad="#e8833a", polia="#c9ccd1", esp="#f2b134", rol="#4a78c2", arr="#f2b134", cab="#5b5f66",
         m5="#3a3d42", correia="#222")


def corte_adaptador(stl, out):
    m = trimesh.load(stl)
    a = sorted(m.split(only_watertight=False), key=lambda p: p.bounds[0][0])[0]
    a.apply_translation(-a.bounds.mean(0) * [1, 1, 0])
    fig, ax = plt.subplots(figsize=(7, 8))
    s = a.section(plane_origin=(0, 0, 0), plane_normal=(0, 1, 0))
    p2, _ = s.to_2D(to_2D=np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1]]))
    for poly in p2.polygons_full:
        x, y = poly.exterior.xy
        ax.fill(x, y, color=C["ad"], ec="k", lw=1)
        for h in poly.interiors:
            x, y = h.xy
            ax.fill(x, y, color="white", ec="k", lw=1)

    def t(z, txt, zt=None):
        ax.annotate(txt, (4, z), (8, z if zt is None else zt), fontsize=10, va="center",
                    arrowprops=dict(arrowstyle="-", lw=.6))
    t(23.6, "furo em D do N20: Ø3,2, chato a 1,1, 7,15 de fundo", 25.5)
    t(21.35, "M3 sem cabeça (aperta no chato)", 21.0)
    t(17.1, "parede de 1,25 entre os furos", 16.6)
    t(8, "rosca M5 Ø4,2, 16,45 de fundo (pega 16 mm de rosca)")
    t(1.9, "flange Ø14 x 3,85: encosta no cubo da polia")
    ax.annotate("Ø11", (-5.5, 12), (-11, 12), fontsize=10, va="center", arrowprops=dict(arrowstyle="-", lw=.6))
    ax.text(0, -2.2, "MESA (imprimir assim, sem suporte)", ha="center", fontsize=9)
    ax.text(0, 27.3, "lado do motor N20", ha="center", fontsize=9)
    ax.text(0, -4.2, "lado da polia", ha="center", fontsize=9)
    ax.set_aspect("equal"); ax.set_xlim(-13, 30); ax.set_ylim(-5, 28.5); ax.axis("off")
    ax.set_title("Adaptador reforçado N20 → M5 (corte pelo meio)", fontsize=12)
    plt.savefig(out, dpi=130, bbox_inches="tight")
    plt.close(fig)


def _torre():
    for o in json.loads((AQUI / "saida" / "malhas.json").read_text(encoding="utf8")):
        if o["nome"] == "Torre superior":
            V = np.frombuffer(base64.b64decode(o["v"]), np.float32).reshape(-1, 3).astype(float) + np.array(o["copias"][0])
            T = np.frombuffer(base64.b64decode(o["t"]), np.uint32).reshape(-1, 3)
            return trimesh.Trimesh(V, T)


def _rect(ax, y0, y1, r, cor, z=3, alpha=1):
    ax.add_patch(Rectangle((y0, Z0 - r), y1 - y0, 2 * r, fc=cor, ec="k", lw=.8, zorder=z, alpha=alpha))


def _pecas(ax, d=None):
    d = d or {}
    g = d.get
    o = g("motor", 0)
    _rect(ax, 122 + o, 154.5 + o, 5, C["motor"]); _rect(ax, 154.5 + o, 162.65 + o, 1.5, C["m5"])
    o = g("ad", 0)
    _rect(ax, E.PC_ACOPL[0] + o, E.PC_AD_FL[0] + o, E.PC_ACOPL_R, C["ad"]); _rect(ax, *(v + o for v in E.PC_AD_FL), E.PC_AD_FL_R, C["ad"])
    o = g("polia", 0)
    y0, y1 = E.PC_POLIA
    _rect(ax, E.PC_CUBO[0] + o, E.PC_CUBO[1] + o, 8, C["polia"]); _rect(ax, y0 + o, y0 + .85 + o, 8, C["polia"])
    _rect(ax, y0 + .85 + o, y1 - .85 + o, 6.1, C["polia"]); _rect(ax, y1 - .85 + o, y1 + o, 8, C["polia"])
    ax.plot([184 + o, 184 + o], [Z0 + 8, Z0 + 9.3], color="k", lw=2, zorder=4)          # parafusinho da polia
    o = g("esp", 0)
    _rect(ax, E.PC_ESP_T[0] + o, E.PC_ESP_T[1] + o, 3.2, C["esp"])
    o = g("rol", 0)
    _rect(ax, 203.15 + o, 208.15 + o, 8, C["rol"]); _rect(ax, 203.15 + o, 208.15 + o, 4, "#9db7e3")
    o = g("arr", 0)
    _rect(ax, 208.15 + o, 209.15 + o, 3.75, C["arr"])
    o = g("m5", 0)
    _rect(ax, 209.15 + o, 214.15 + o, 4.25, C["cab"]); _rect(ax, 164.15 + o, 209.15 + o, 2.5, C["m5"], z=2)


def montagem(out):
    s = _torre().section(plane_origin=(E.P().x_polia, 0, 0), plane_normal=(1, 0, 0))
    verts, codes = [], []
    for li in s.discrete:
        yz = li[:, [1, 2]]
        verts += yz.tolist(); codes += [MPath.MOVETO] + [MPath.LINETO] * (len(yz) - 2) + [MPath.CLOSEPOLY]
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(15, 11.5), gridspec_kw=dict(height_ratios=[1.25, 1]))
    a1.add_patch(PathPatch(MPath(verts, codes), fc="#d9d9d9", ec="#555", lw=.6, zorder=1))
    a1.add_patch(Rectangle((189, 380), 6, Z0 - 6.37 - 380, fc=C["correia"], alpha=.25, zorder=0))
    _pecas(a1)
    a1.add_patch(Rectangle((164.15, Z0 - 2.5), 45, 5, fc="none", ec="k", lw=1.3, ls="--", zorder=8))
    a1.add_patch(Rectangle((182, 425), 4.5, 4, fc="#ff3b30", ec="#b00", lw=1.5, hatch="////", alpha=.75, zorder=6))
    lab = [((140, Z0), "motor N20 (no berço)", (140, 437)), ((166, Z0 + 5.5), "ADAPTADOR (imprimir)", (160, 440)),
           ((184, Z0 + 8), "polia 16 mm (cubo para o motor)\nparafusinho dela no M5", (160, 446)),
           ((199.5, Z0 + 3.2), "ESPAÇADOR 6,8 (imprimir)\natravessa o furo de 7 da parede", (214, 446)),
           ((205.6, Z0 + 8), "rolamento 625ZZ\n(colado, encostado no degrau)", (222, 437)),
           ((208.65, Z0 - 3.75), "arruela", (212, 404)), ((211.6, Z0 - 4.25), "cabeça do M5", (218, 409)),
           ((184.25, 429), "CORTAR esta tira do teto\n(4,5 mm, largura da janela)", (187, 457)),
           ((192, 400), "correia", (198, 392)), ((172, Z0), "M5 x 45 (eixo, tracejado)", (168, 400))]
    for p, t, q in lab:
        a1.annotate(t, p, q, fontsize=10, ha="center", arrowprops=dict(arrowstyle="-", lw=.7), zorder=9,
                    color="#b00" if "CORTAR" in t else "k", fontweight="bold" if t.isupper() or "CORTAR" in t else None)
    a1.text(178.9, 413.3, "encaixe da\nfrente (vazio)", fontsize=8, ha="center", color="#444")
    a1.text(202, 404, "parede", fontsize=8, ha="center", color="#444")
    a1.set_xlim(118, 226); a1.set_ylim(388, 462); a1.set_aspect("equal"); a1.axis("off")
    a1.set_title("MONTADO - corte pelo meio da torre de cima (vista de lado: frente à esquerda, trás à direita)", fontsize=12)
    _pecas(a2, dict(motor=-14, ad=-7, polia=0, esp=6, rol=12, arr=18, m5=58))
    for x, t in [(138, "1 motor N20"), (159, "2 adaptador"), (188, "3 polia"), (205, "4 espaçador"), (217.5, "5 rolamento"),
                 (228, "6 arruela"), (250, "7 M5 x 45: entra por trás\ne rosqueia no adaptador")]:
        a2.text(x, Z0 - 13, t, ha="center", fontsize=10)
    a2.annotate("", (160, Z0 + 11), (262, Z0 + 11), arrowprops=dict(arrowstyle="->", lw=1.4))
    a2.text(211, Z0 + 12.5, "o M5 aperta tudo num bloco só: cabeça → arruela → pista de dentro do rolamento → espaçador → "
            "polia → adaptador", ha="center", fontsize=10)
    a2.set_xlim(104, 278); a2.set_ylim(400, 436); a2.set_aspect("equal"); a2.axis("off")
    a2.set_title("ORDEM (explodido)", fontsize=12)
    plt.tight_layout(); plt.savefig(out, dpi=120)
    plt.close(fig)
