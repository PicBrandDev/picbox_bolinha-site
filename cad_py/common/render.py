"""Imagens de verificacao (checagem 11). pyvista offscreen."""
import numpy as np
import pyvista as pv

pv.OFF_SCREEN = True
COR_PECA = "#e8892b"
COR_REF = "#8fa3b0"
COR_HW = "#9a9a9a"
COR_MOVEL = "#4a8fd6"


def _pv(m):
    f = np.hstack([np.full((len(m.faces), 1), 3), m.faces]).astype(np.int64)
    return pv.PolyData(np.asarray(m.vertices), f)


def _cam(p, centro, direcao, dist, up=(0, 0, 1)):
    d = np.asarray(direcao, float)
    d /= np.linalg.norm(d)
    p.camera.focal_point = centro
    p.camera.position = np.asarray(centro) + d * dist
    p.camera.up = up
    p.camera.parallel_projection = True


def iso(caminho, peca, contexto=None, direcao=(-1, -1.3, 0.9), tamanho=(1200, 900), titulo="", escala=None, alvo=None):
    p = pv.Plotter(off_screen=True, window_size=tamanho)
    p.set_background("white")
    p.add_mesh(_pv(peca), color=COR_PECA, smooth_shading=False, specular=0.2)
    for nome, (m, cor, op) in (contexto or {}).items():
        p.add_mesh(_pv(m), color=cor, opacity=op)
    b = (alvo if alvo is not None else peca).bounds
    centro = (b[0] + b[1]) / 2
    r = float(np.linalg.norm(b[1] - b[0]))
    _cam(p, centro, direcao, r * 3)
    p.camera.parallel_scale = escala or r * 0.62
    if titulo:
        p.add_text(titulo, font_size=10, color="black")
    p.enable_eye_dome_lighting() if False else None
    p.screenshot(caminho)
    p.close()


def lado_a_lado(caminho, ref, nova, direcao=(-1, -1.3, 0.9), tamanho=(1600, 800), titulos=("referencia (simulacao)", "peca nova")):
    p = pv.Plotter(off_screen=True, window_size=tamanho, shape=(1, 2))
    b = np.vstack([ref.bounds, nova.bounds]) if ref is not None else nova.bounds
    lo, hi = b.min(0), b.max(0)
    centro = (lo + hi) / 2
    r = float(np.linalg.norm(hi - lo))
    for k, (m, cor, t) in enumerate(((ref, COR_REF, titulos[0]), (nova, COR_PECA, titulos[1]))):
        p.subplot(0, k)
        p.set_background("white")
        if m is not None:
            p.add_mesh(_pv(m), color=cor, specular=0.2)
        p.add_text(t, font_size=11, color="black")
        _cam(p, centro, direcao, r * 3)
        p.camera.parallel_scale = r * 0.55
    p.screenshot(caminho)
    p.close()


def mesa(caminho, m, impressora_xy, tamanho=(1000, 800)):
    p = pv.Plotter(off_screen=True, window_size=tamanho)
    p.set_background("white")
    p.add_mesh(_pv(m), color=COR_PECA, specular=0.2)
    w, d = impressora_xy
    c = (m.bounds[0][:2] + m.bounds[1][:2]) / 2
    p.add_mesh(pv.Plane(center=(c[0], c[1], -0.2), direction=(0, 0, 1), i_size=w, j_size=d), color="#d9dde0")
    b = m.bounds
    _cam(p, (b[0] + b[1]) / 2, (1, -1.4, 1.1), 600)
    p.camera.parallel_scale = max(w, d) * 0.42
    p.add_text(f"orientacao de impressao (mesa {w:.0f} x {d:.0f})", font_size=10, color="black")
    p.screenshot(caminho)
    p.close()
