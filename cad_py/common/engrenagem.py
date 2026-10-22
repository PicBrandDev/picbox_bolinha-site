"""Engrenagem de dentes retos com perfil evolvente (para impressao FDM)."""
import math

import cadquery as cq


def _evolvente(rb, t):
    return (rb * (math.cos(t) + t * math.sin(t)), rb * (math.sin(t) - t * math.cos(t)))


def perfil_2d(modulo, dentes, angulo_pressao=20.0, folga_flanco=0.3, n=8):
    """Pontos (u, v) do contorno da engrenagem completa, centro na origem; dente 0 centrado no eixo +u."""
    rp = modulo * dentes / 2
    rb = rp * math.cos(math.radians(angulo_pressao))
    ra = rp + modulo
    rf = max(rp - 1.25 * modulo, rb * 0.95)
    # meia espessura angular do dente no primitivo, descontada a folga de flanco
    inv = lambda a: math.tan(a) - a
    alfa = math.radians(angulo_pressao)
    meia = math.pi / (2 * dentes) - folga_flanco / (2 * rp)
    t_a = math.sqrt((ra / rb) ** 2 - 1)
    pts = []
    for k in range(dentes):
        c = 2 * math.pi * k / dentes
        flanco = []
        for i in range(n + 1):
            t = t_a * i / n
            x, y = _evolvente(rb, t)
            r = math.hypot(x, y)
            if r < rf:
                continue
            ang = math.atan2(y, x)
            # gira para que o flanco fique a +meia no primitivo
            fi = meia + inv(alfa) - ang
            flanco.append((r, fi))
        # percurso anti-horario: pe -> flanco de baixo (base->ponta) -> flanco de cima (ponta->base) -> pe;
        # o flanco desce radialmente do circulo de base ate o pe (alivio para a ponta do dente par)
        a_base = flanco[0][1]
        pol = lambda r, ang: (r * math.cos(ang), r * math.sin(ang))
        pts.append(pol(rf, c - a_base))
        pts.extend(pol(r, c - a) for r, a in flanco)
        pts.extend(pol(r, c + a) for r, a in reversed(flanco))
        pts.append(pol(rf, c + a_base))
    return pts


def engrenagem(modulo, dentes, espessura, plano, fase_graus=0.0):
    """Solido da engrenagem completa no 'plano' (cq.Plane), extrudada ao longo da normal."""
    pts = perfil_2d(modulo, dentes)
    f = math.radians(fase_graus)
    pts = [(u * math.cos(f) - v * math.sin(f), u * math.sin(f) + v * math.cos(f)) for u, v in pts]
    return cq.Workplane(plano).polyline(pts).close().extrude(espessura)


def setor(modulo, dentes, espessura, plano, a0, a1, r_cubo, fase_graus=0.0):
    """Engrenagem cortada num setor angular [a0, a1] (graus, no plano), unida a um cubo de raio r_cubo."""
    g = engrenagem(modulo, dentes, espessura, plano, fase_graus)
    ra = modulo * dentes / 2 + modulo + 1
    a0r, a1r = math.radians(a0), math.radians(a1)
    m = max(2, int(abs(a1 - a0) / 10))
    cunha = [(0, 0)] + [(ra * 1.2 * math.cos(a0r + (a1r - a0r) * i / m), ra * 1.2 * math.sin(a0r + (a1r - a0r) * i / m)) for i in range(m + 1)]
    w = cq.Workplane(plano).polyline(cunha).close().extrude(espessura)
    cubo = cq.Workplane(plano).circle(r_cubo).extrude(espessura)
    return g.intersect(w).union(cubo)
