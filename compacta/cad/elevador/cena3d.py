"""Cinematica e distancias entre pecas sem dependencia nativa (substitui o MuJoCo nas checagens de montagem).

Cada geometria e uma caixa ou um cilindro (convexos). A distancia com sinal entre duas pecas convexas A e B e
  d = max sobre direcoes u de  -(h_A(u) + h_B(-u))
onde h e a funcao suporte. Testando as normais das faces, os produtos vetoriais entre arestas e os eixos dos
cilindros (teorema do eixo separador), o valor e exato no sinal para caixa x caixa e nunca MAIOR que a distancia
real: a checagem erra so para o lado da cautela (mostra folga menor). Negativo = interferencia.
"""
import math

import numpy as np

from modelo import geometria

MM = 1e-3
DENSIDADE = 800.0          # kg/m3, PETG com preenchimento
MASSA_FIXA = {"patim": 0.016}


def q2R(q):
    w, x, y, z = q
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def _fib(n=48):
    i = np.arange(n) + 0.5
    phi = np.arccos(1 - 2 * i / n)
    th = math.pi * (1 + 5 ** 0.5) * i
    return np.stack([np.cos(th) * np.sin(phi), np.sin(th) * np.sin(phi), np.cos(phi)], 1)


FIB = _fib()


class _Body:
    def __init__(self, i):
        self.id = i


class _M:
    """Imita o pouco do MjModel que a checagem usa: massa dos corpos."""
    def __init__(self, cena):
        self.cena = cena
        self._ids = {"carro": 0, "alavanca": 1}
        self.body_mass = np.zeros(2)

    def body(self, nome):
        return _Body(self._ids[nome])


class _D:
    def __init__(self):
        self.geom_xpos = None
        self.geom_xmat = None
        self.xipos = np.zeros((2, 3))


class Cena:
    def __init__(self, p):
        self.p = p
        self.g = geometria(p)
        self.id = {e["nome"]: i for i, e in enumerate(self.g)}
        self.corpo = {e["nome"]: e["corpo"] for e in self.g}
        self.peca = {e["nome"]: e["peca"] for e in self.g}
        self.loc = [(np.array(e["pos"], float), q2R(e["quat"])) for e in self.g]
        self.tipo = [e["tipo"] for e in self.g]
        self.meio = [np.array(e["meio"], float) for e in self.g]
        n = len(self.g)
        self.m = _M(self)
        self.d = _D()
        self.d.geom_xpos = np.zeros((n, 3))
        self.d.geom_xmat = np.zeros((n, 9))
        self._R = [np.eye(3)] * n
        self._c = [np.zeros(3)] * n
        self.pose(p.zc_min, 0.0)

    # ---------------------------------------------------------------- pose
    def pose(self, zc, th_deg):
        p = self.p
        piv = np.array(p.piv, float)
        a = math.radians(th_deg)
        Ry = np.array([[math.cos(a), 0, math.sin(a)], [0, 1, 0], [-math.sin(a), 0, math.cos(a)]])
        massa = {"carro": [0.0, np.zeros(3)], "alavanca": [0.0, np.zeros(3)]}
        for i, e in enumerate(self.g):
            c0, R0 = self.loc[i]
            if e["corpo"] == "carro":
                c, R = c0 + np.array([0, 0, zc]), R0
            elif e["corpo"] == "alavanca":
                c, R = piv + Ry @ c0, Ry @ R0
            else:
                c, R = c0, R0
            self._c[i], self._R[i] = c, R
            self.d.geom_xpos[i] = c * MM
            self.d.geom_xmat[i] = R.reshape(-1)
            if e["corpo"] in massa:
                h = self.meio[i]
                vol = 8 * h[0] * h[1] * h[2] if self.tipo[i] == "box" else math.pi * h[0] ** 2 * 2 * h[1]
                mk = MASSA_FIXA.get(e["nome"], DENSIDADE * vol * 1e-9)
                massa[e["corpo"]][0] += mk
                massa[e["corpo"]][1] = massa[e["corpo"]][1] + mk * c
        for k, j in (("carro", 0), ("alavanca", 1)):
            mt, mc = massa[k]
            self.m.body_mass[j] = mt
            self.d.xipos[j] = (mc / mt) * MM if mt > 0 else 0

    # ---------------------------------------------------------------- suporte
    def _h(self, i, U):
        """Funcao suporte da geometria i nas direcoes U (k x 3, unitarias)."""
        c, R, h = self._c[i], self._R[i], self.meio[i]
        if self.tipo[i] == "box":
            return U @ c + np.abs(U @ R) @ h
        r, hl = h
        ax = R[:, 2]
        ad = U @ ax
        return U @ c + hl * np.abs(ad) + r * np.sqrt(np.clip(1 - ad ** 2, 0, None))

    def _eixos(self, i):
        R = self._R[i]
        return [R[:, 0], R[:, 1], R[:, 2]] if self.tipo[i] == "box" else [R[:, 2]]

    def dist(self, a, b, dmax=None):
        i, j = self.id[a], self.id[b]
        la, ha = self.aabb_i(i)
        lb, hb = self.aabb_i(j)
        gap = np.maximum(0, np.maximum(lb - ha, la - hb))
        ga = float(np.linalg.norm(gap))
        if ga > 30:
            return ga
        ea, eb = self._eixos(i), self._eixos(j)
        dirs = ea + eb
        for u in ea:
            for v in eb:
                w = np.cross(u, v)
                n = np.linalg.norm(w)
                if n > 1e-6:
                    dirs.append(w / n)
        cc = self._c[j] - self._c[i]
        if np.linalg.norm(cc) > 1e-9:
            dirs.append(cc / np.linalg.norm(cc))
        # cilindros: direcoes perpendiculares ao eixo, apontando para o centro do outro
        for k, o in ((i, j), (j, i)):
            if self.tipo[k] == "cylinder":
                ax = self._R[k][:, 2]
                v = self._c[o] - self._c[k]
                v = v - (v @ ax) * ax
                if np.linalg.norm(v) > 1e-9:
                    dirs.append(v / np.linalg.norm(v))
        U = np.array(dirs)
        if "cylinder" in (self.tipo[i], self.tipo[j]):
            U = np.vstack([U, FIB])
        U = np.vstack([U, -U])
        s = -(self._h(i, U) + self._h(j, -U))
        return float(s.max())

    def nomes(self, corpo):
        return [e["nome"] for e in self.g if e["corpo"] == corpo and e["nome"] != "chao"]

    def aabb_i(self, i):
        c, R, h = self._c[i], self._R[i], self.meio[i]
        if self.tipo[i] == "box":
            e = np.abs(R) @ h
        else:
            r, hl = h
            ax = R[:, 2]
            e = np.abs(ax) * hl + r * np.sqrt(np.clip(1 - ax ** 2, 0, 1))
        return c - e, c + e

    def aabb(self, nome):
        return self.aabb_i(self.id[nome])
