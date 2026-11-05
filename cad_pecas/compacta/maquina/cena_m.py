"""Distancia entre pecas convexas (caixa, cilindro, esfera) por eixo separador, para a maquina inteira.

Corpos: mundo (fixo), carro (cabine, sobe em Z), alavanca (gira no pivo da comporta), carroA / carroB (andam em X),
esteiraA / esteiraB (recalculadas com a posicao do carro). Aneis viram 24 segmentos de caixa.
Mesma conta do elevador (cena3d.py): o valor nunca e maior que a distancia real (erra para o lado da cautela).
"""
import math

import numpy as np

import layout as L

FIB = None


def _fib(n=64):
    i = np.arange(n) + 0.5
    phi = np.arccos(1 - 2 * i / n)
    th = math.pi * (1 + 5 ** 0.5) * i
    return np.stack([np.cos(th) * np.sin(phi), np.sin(th) * np.sin(phi), np.cos(phi)], 1)


FIB = _fib()


def q2R(q):
    w, x, y, z = q
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def expandir_aneis(g, n=24):
    out = []
    for e in g:
        if e["tipo"] != "anel":
            out.append(e)
            continue
        r0, r1, hz = e["meio"]
        cx, cy, cz = e["pos"]
        t = r1 * math.tan(math.pi / n)
        for i in range(n):
            a = 2 * math.pi * i / n
            rm = (r0 + r1) / 2
            Rm = L.rot(rz=math.degrees(a))
            d = dict(e)
            d.update(nome=f"{e['nome']}#{i}", tipo="box", meio=[(r1 - r0) / 2, t, hz],
                     pos=[cx + rm * math.cos(a), cy + rm * math.sin(a), cz], quat=L.EL.quat(Rm), pai=e["nome"])
            out.append(d)
    return out


class Cena:
    def __init__(self, m: L.M, extra=()):
        self.m = m
        self.el = m.el
        self.g0 = L.geometria(m) + list(extra)
        self.g = expandir_aneis(self.g0)
        self._est = {}
        for k in ("A", "B"):
            gk, _ = L.esteira_caixas(m, k, 0.0)
            self._est[k] = [e["nome"] for e in gk]
            self.g += gk
        self.id = {e["nome"]: i for i, e in enumerate(self.g)}
        self.corpo = {e["nome"]: e["corpo"] for e in self.g}
        self.peca = {e["nome"]: e["peca"] for e in self.g}
        self.pai = {e["nome"]: e.get("pai", e["nome"]) for e in self.g}
        n = len(self.g)
        self.tipo = [e["tipo"] for e in self.g]
        self.loc = [(np.array(e["pos"], float), q2R(e["quat"])) for e in self.g]
        self.meio = [np.array(e["meio"], float) for e in self.g]
        self._c = [None] * n
        self._R = [None] * n
        self.estado = None
        self.pose()

    def nomes(self, corpo):
        return [e["nome"] for e in self.g if e["corpo"] == corpo]

    def pose(self, zc=None, th=0.0, cA=0.0, cB=0.0):
        el, m = self.el, self.m
        zc = el.zc_min if zc is None else zc
        piv = np.array(el.piv, float)
        a = math.radians(th)
        Ry = np.array([[math.cos(a), 0, math.sin(a)], [0, 1, 0], [-math.sin(a), 0, math.cos(a)]])
        for k, c in (("A", cA), ("B", cB)):
            gk, _ = L.esteira_caixas(m, k, c)
            for e in gk:
                i = self.id[e["nome"]]
                self.loc[i] = (np.array(e["pos"], float), q2R(e["quat"]))
                self.meio[i] = np.array(e["meio"], float)
        for i, e in enumerate(self.g):
            c0, R0 = self.loc[i]
            cp = e["corpo"]
            if cp == "carro":
                c, R = c0 + np.array([0, 0, zc]), R0
            elif cp == "alavanca":
                c, R = piv + Ry @ c0, Ry @ R0
            elif cp == "carroA":
                c, R = c0 + np.array([cA, 0, 0]), R0
            elif cp == "carroB":
                c, R = c0 + np.array([cB, 0, 0]), R0
            else:
                c, R = c0, R0
            self._c[i], self._R[i] = c, R
        self.estado = (zc, th, cA, cB)

    # ------------------------------------------------------------ geometria
    def _h(self, i, U):
        c, R, h, t = self._c[i], self._R[i], self.meio[i], self.tipo[i]
        if t == "box":
            return U @ c + np.abs(U @ R) @ h
        if t == "sphere":
            return U @ c + h[0]
        r, hl = h
        ad = U @ R[:, 2]
        return U @ c + hl * np.abs(ad) + r * np.sqrt(np.clip(1 - ad ** 2, 0, None))

    def _eixos(self, i):
        R = self._R[i]
        t = self.tipo[i]
        return [R[:, 0], R[:, 1], R[:, 2]] if t == "box" else ([R[:, 2]] if t == "cylinder" else [])

    def aabb_i(self, i):
        c, R, h, t = self._c[i], self._R[i], self.meio[i], self.tipo[i]
        if t == "box":
            e = np.abs(R) @ h
        elif t == "sphere":
            e = np.full(3, h[0])
        else:
            r, hl = h
            ax = R[:, 2]
            e = np.abs(ax) * hl + r * np.sqrt(np.clip(1 - ax ** 2, 0, 1))
        return c - e, c + e

    def aabb(self, nome):
        return self.aabb_i(self.id[nome])

    def dist(self, a, b, corte=30.0):
        i, j = self.id[a], self.id[b]
        return self.dist_i(i, j, corte)

    def dist_i(self, i, j, corte=30.0):
        la, ha = self.aabb_i(i)
        lb, hb = self.aabb_i(j)
        gap = np.maximum(0, np.maximum(lb - ha, la - hb))
        ga = float(np.linalg.norm(gap))
        if ga > corte:
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
        curvo = False
        for k, o in ((i, j), (j, i)):
            if self.tipo[k] in ("cylinder", "sphere"):
                curvo = True
                v = self._c[o] - self._c[k]
                if self.tipo[k] == "cylinder":
                    ax = self._R[k][:, 2]
                    v = v - (v @ ax) * ax
                if np.linalg.norm(v) > 1e-9:
                    dirs.append(v / np.linalg.norm(v))
        U = np.array(dirs) if dirs else np.zeros((0, 3))
        if curvo or len(dirs) < 3:
            U = np.vstack([U, FIB]) if len(U) else FIB
        U = np.vstack([U, -U])
        s = -(self._h(i, U) + self._h(j, -U))
        d = float(s.max())
        if curvo and d > 0:
            # refina a direcao de separacao (esfera e cilindro: o maximo pode cair entre as direcoes testadas)
            u = U[int(s.argmax())]
            for passo in (0.2, 0.05, 0.01):
                for _ in range(6):
                    cand = u + passo * np.random.default_rng(0).normal(size=(24, 3))
                    cand /= np.linalg.norm(cand, axis=1, keepdims=True)
                    sc = -(self._h(i, cand) + self._h(j, -cand))
                    if sc.max() > d:
                        d = float(sc.max())
                        u = cand[int(sc.argmax())]
        return d

    # ------------------------------------------------------------ esfera solta (bola)
    def com_bola(self, nome, centro, r=L.R):
        """Insere (ou move) uma esfera no mundo."""
        if nome not in self.id:
            self.g.append(dict(nome=nome, corpo="bola", tipo="sphere", meio=[r], pos=list(centro), quat=[1, 0, 0, 0],
                               peca="Bola", grupo="bola", cor="bola"))
            i = len(self.g) - 1
            self.id[nome] = i
            self.corpo[nome], self.peca[nome], self.pai[nome] = "bola", "Bola", nome
            self.tipo.append("sphere")
            self.loc.append((np.array(centro, float), np.eye(3)))
            self.meio.append(np.array([r], float))
            self._c.append(np.array(centro, float))
            self._R.append(np.eye(3))
        i = self.id[nome]
        self._c[i] = np.array(centro, float)
        self.meio[i] = np.array([r], float)
        return i

    def contem(self, i, P):
        """Pontos P (k x 3) dentro da geometria i."""
        c, R, h, t = self._c[i], self._R[i], self.meio[i], self.tipo[i]
        q = (P - c) @ R
        if t == "box":
            return np.all(np.abs(q) <= h, axis=1)
        if t == "sphere":
            return np.linalg.norm(P - c, axis=1) <= h[0]
        r, hl = h
        return (q[:, 0] ** 2 + q[:, 1] ** 2 <= r * r) & (np.abs(q[:, 2]) <= hl)
