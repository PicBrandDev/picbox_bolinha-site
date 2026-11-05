"""Simulacao fisica (MuJoCo) do elevador de cabine: monta o modelo a partir de modelo.geometria(),
roda o firmware de controle e conta falhas. Unidades internas do MuJoCo em metros.

Uso:
  python sim.py checar            # folgas entre pecas em todo o curso
  python sim.py campanha 20 50    # 20 conjuntos de tolerancia x 50 entregas = 1000 ciclos
  python sim.py gravar            # grava 2 ciclos para a visualizacao
"""
import json
import math
import sys
import time
from dataclasses import replace
from pathlib import Path

import numpy as np
import mujoco

from modelo import P, geometria, R_BOLA

AQUI = Path(__file__).resolve().parent
MM = 1e-3
DT = 0.0002
SUB = 5                       # passos por ciclo de controle (1 ms)
BITS = {"fixa": (1, 0), "visual": (0, 0), "carro": (4, 0), "carro_vis": (0, 0), "alavanca": (8, 4)}
N_BOLAS = 7


def fmt(v):
    return " ".join(f"{x:.6g}" for x in v)


def mjcf(p: P, fis: dict, raios):
    g = geometria(p)
    corpos = {"mundo": [], "carro": [], "alavanca": []}
    for e in g:
        ct, ca = BITS[e["grupo"]]
        if e["tipo"] == "box":
            tam = [s * MM for s in e["meio"]]
        else:
            tam = [e["meio"][0] * MM, e["meio"][1] * MM]
        extra = ""
        if e["nome"] == "alav_contrapeso":
            extra = f' mass="{fis["contrapeso"]:.4f}"'
        elif e["nome"] == "patim":
            extra = ' mass="0.016"'
        elif e["grupo"] in ("fixa", "visual", "carro_vis") and e["corpo"] == "mundo":
            extra = ""
        else:
            extra = ' density="800"'
        atr = (f'<geom name="{e["nome"]}" type="{e["tipo"]}" size="{fmt(tam)}" pos="{fmt([c * MM for c in e["pos"]])}" '
               f'quat="{fmt(e["quat"])}" contype="{ct}" conaffinity="{ca}" friction="{fis["mu_plast"]:.3f} 0.005 0.0001" '
               f'solref="0.002 {fis["amort"]:.3f}" solimp="0.95 0.99 0.0005"{extra} '
               f'group="{0 if ct else 3}"/>')
        corpos[e["corpo"]].append(atr)
    px, py, pz = p.piv
    bolas = []
    for i in range(N_BOLAS):
        bolas.append(
            f'<body name="b{i}" pos="0 0 1"><freejoint name="bj{i}"/>'
            f'<geom name="bola{i}" type="sphere" size="{raios[i] * MM:.6f}" mass="0.067" contype="2" conaffinity="15" '
            f'condim="6" friction="0.15 0.002 0.00002" solref="0.002 {fis["amort"]:.3f}" solimp="0.95 0.99 0.0005"/></body>')
    return f"""<mujoco model="elevador_cabine">
  <option timestep="{DT}" integrator="implicitfast" cone="elliptic" impratio="5" gravity="0 0 -9.80665"/>
  <default><geom margin="0.0002"/></default>
  <worldbody>
    {''.join(corpos['mundo'])}
    <body name="carro" pos="0 0 0">
      <joint name="cz" type="slide" axis="0 0 1" limited="true" range="{p.zc_min * MM:.6f} {p.zc_max * MM:.6f}"
             armature="{fis['armadura']:.3f}" frictionloss="{fis['atrito_trilho']:.3f}" damping="0.5"/>
      {''.join(corpos['carro'])}
    </body>
    <body name="alavanca" pos="{px * MM} {py * MM} {pz * MM}">
      <joint name="aj" type="hinge" axis="0 1 0" limited="true" range="0 8" damping="0.00002"/>
      {''.join(corpos['alavanca'])}
    </body>
    {''.join(bolas)}
  </worldbody>
  <actuator><motor name="m" joint="cz" ctrllimited="true" ctrlrange="-60 60"/></actuator>
</mujoco>"""


def sortear(rng, k):
    """Conjunto de tolerancias. k < 4 sao os cantos piores escolhidos a mao."""
    u = lambda a, b: float(rng.uniform(a, b))
    if k == 0:   # bola grande, fila estreita, pouca inclinacao, muito atrito, lamina para dentro, contrapeso leve
        geo = dict(larg_fila=26.2, incl_fila=3.0, incl_berco_y=7.0, incl_berco_x=1.3, degrau=0.4, x_parede_dir=203.2,
                   lamina_dx=0.6, lamina_topo=6.5, contrapeso_g=11.0)
        fis = dict(mu_plast=0.5, amort=0.4, Fs=20.0, v0=0.058, armadura=6.0, atrito_trilho=0.5)
        raio = (12.75, 12.75)
    elif k == 1:  # bola pequena, larga, muita inclinacao, pouco atrito, quica
        geo = dict(larg_fila=26.8, incl_fila=5.0, incl_berco_y=9.0, incl_berco_x=2.7, degrau=1.2, x_parede_dir=203.8,
                   lamina_dx=-0.6, lamina_topo=7.5, contrapeso_g=19.0)
        fis = dict(mu_plast=0.2, amort=0.4, Fs=33.0, v0=0.075, armadura=1.0, atrito_trilho=0.1)
        raio = (12.65, 12.65)
    elif k == 2:  # fila rapida e bola quicando contra a lamina deslocada
        geo = dict(incl_fila=5.0, lamina_dx=0.6, lamina_topo=6.5, contrapeso_g=11.0, degrau=1.2, incl_berco_x=1.3)
        fis = dict(mu_plast=0.2, amort=0.4, Fs=27.0, v0=0.067, armadura=3.0, atrito_trilho=0.3)
        raio = (12.65, 12.75)
    elif k == 3:  # fila lenta, muito atrito, lamina para fora
        geo = dict(incl_fila=3.0, lamina_dx=-0.6, lamina_topo=7.5, contrapeso_g=11.0, degrau=0.4, incl_berco_y=7.0)
        fis = dict(mu_plast=0.5, amort=1.0, Fs=20.0, v0=0.058, armadura=6.0, atrito_trilho=0.5)
        raio = (12.65, 12.75)
    else:
        geo = dict(larg_fila=u(26.2, 26.8), incl_fila=u(3, 5), incl_berco_y=u(7, 9), incl_berco_x=u(1.3, 2.7),
                   degrau=u(0.4, 1.2), x_parede_dir=u(203.2, 203.8), lamina_dx=u(-0.6, 0.6), lamina_topo=u(6.5, 7.5),
                   contrapeso_g=u(11, 19), piv=(100 + u(-0.5, 0.5), 122 + u(-0.5, 0.5), 24 + u(-0.5, 0.5)))
        fis = dict(mu_plast=u(0.2, 0.5), amort=u(0.4, 1.0), Fs=u(20, 33), v0=u(0.058, 0.075), armadura=u(1, 6),
                   atrito_trilho=u(0.1, 0.5))
        raio = (12.65, 12.75)
    fis["contrapeso"] = geo.pop("contrapeso_g") / 1000
    fis["erro_topo"] = u(-0.6, 0.6) if k >= 4 else (0.6 if k % 2 else -0.6)
    fis["erro_casa"] = u(0.0, 0.3)
    raios = [float(rng.uniform(*raio)) for _ in range(N_BOLAS)]
    return geo, fis, raios


class Bancada:
    """Modelo + firmware + carro A de mentira (retira a bola do bolso e devolve na fila)."""

    def __init__(self, p: P, fis, raios, rng, gravar=False):
        self.p, self.fis, self.rng = p, fis, rng
        self.m = mujoco.MjModel.from_xml_string(mjcf(p, fis, raios))
        self.d = mujoco.MjData(self.m)
        self.raios = raios
        self.qadr = [self.m.jnt_qposadr[self.m.joint(f"bj{i}").id] for i in range(N_BOLAS)]
        self.vadr = [self.m.jnt_dofadr[self.m.joint(f"bj{i}").id] for i in range(N_BOLAS)]
        self.jz = self.m.jnt_qposadr[self.m.joint("cz").id]
        self.vz = self.m.jnt_dofadr[self.m.joint("cz").id]
        self.ja = self.m.jnt_qposadr[self.m.joint("aj").id]
        self.d.qpos[self.jz] = (p.zc_min + 40) * MM
        tf = math.tan(math.radians(p.incl_fila))
        self.reserva = []
        for i in range(N_BOLAS):
            if i < 6:
                x = p.x_fila_fim - p.r_bola - 0.5 - i * 25.6
                self.por(i, x, 130 + p.larg_fila / 2, p.zf_fim + (p.x_fila_fim - x) * tf + raios[i] + 0.2)
            else:
                self.estacionar(i)
        mujoco.mj_forward(self.m, self.d)
        self.t_ctrl = 0.0
        self.estado, self.t_estado = "desce", 0.0
        self.alvo = p.zc_min
        self.ev = dict(entregas=0, duplas=0, vazamentos=0, pega_dupla=0, perdidas=0, travamentos=0,
                       falhas_trav=0, sem_entrega=0, sem_pega=0)
        self.passou = [False] * N_BOLAS
        self.no_bolso = {}
        self.ciclos = []
        self.t_pedido = None
        self.saidas_janela = 0
        self.quieto = 0.0
        self.trav_ciclo = 0
        self.rev_ate = None
        self.gravar = gravar
        self.quadros = []
        self.t_quadro = 0.0
        self.log = []

    # ------------------------------------------------------------- utilidades
    def por(self, i, x, y, z):
        a = self.qadr[i]
        self.d.qpos[a:a + 3] = [x * MM, y * MM, z * MM]
        self.d.qpos[a + 3:a + 7] = [1, 0, 0, 0]
        self.d.qvel[self.vadr[i]:self.vadr[i] + 6] = 0

    def estacionar(self, i):
        self.por(i, 240 + 30 * i, 215, R_BOLA + 0.5)
        self.reserva.append(i)

    def pos(self, i):
        a = self.qadr[i]
        return self.d.qpos[a:a + 3] / MM

    def vel(self, i):
        a = self.vadr[i]
        return np.linalg.norm(self.d.qvel[a:a + 3]) / MM

    def zc(self):
        return self.d.qpos[self.jz] / MM

    def vc(self):
        return self.d.qvel[self.vz] / MM

    def ativas(self):
        return [i for i in range(N_BOLAS) if i not in self.reserva]

    def no_berco(self, i):
        p, x = self.p, self.pos(i)
        return abs(x[0] - p.x_bola) < 4 and 128 < x[1] < 158 and abs(x[2] - (self.zc() + p.r_bola + 0.3)) < 4

    def regiao_ok(self, x):
        p = self.p
        fila = p.x_fila_ini - 1 < x[0] < 178.5 and 127 < x[1] < 159 and -1 < x[2] < 62
        coluna = 175 < x[0] < 208.5 and 127 < x[1] < 159 and 0 < x[2] < 400
        rampa = 175 < x[0] < 208.5 and 57 < x[1] < 131 and 330 < x[2] < 390
        return fila or coluna or rampa

    # ------------------------------------------------------------- firmware
    def mudar(self, e):
        self.estado, self.t_estado = e, self.d.time

    def motor(self):
        p, f = self.p, self.fis
        z, v = self.zc(), self.vc()
        if self.estado in ("baixo",) and z < p.zc_min + 0.5:
            u = 0.0
        else:
            alvo = self.alvo
            if self.rev_ate is not None:
                alvo = self.rev_alvo
            u = float(np.clip((alvo - z) / 3.0, -1, 1))
        F = f["Fs"] * (u - v * MM / f["v0"])
        F = float(np.clip(F, -10.0, 10.0))           # limite de corrente do DRV8871
        if u == 0.0:
            F = 0.0
        self.d.ctrl[0] = F

    def firmware(self):
        p, t = self.p, self.d.time
        z, v = self.zc(), self.vc()
        e = self.estado
        topo = p.zc_topo + self.fis["erro_topo"]
        espera = p.zc_espera + self.fis["erro_topo"]
        # travamento: parado longe do alvo
        if e in ("sobe_espera", "sobe_topo", "desce") and self.rev_ate is None:
            if abs(v) < 2 and abs(self.alvo - z) > 1.5 and t - self.t_estado > 0.3:
                self.quieto += 0.001
            else:
                self.quieto = 0.0
            if self.quieto > 0.6:
                self.ev["travamentos"] += 1
                self.trav_ciclo += 1
                self.log.append((round(t, 2), "travou", e, round(z, 1)))
                self.rev_alvo = z + (5 if self.alvo < z else -5)
                self.rev_ate = t + 0.5
                self.quieto = 0.0
        if self.rev_ate is not None and t > self.rev_ate:
            self.rev_ate = None
            if self.trav_ciclo >= 3:
                self.ev["falhas_trav"] += 1
                self.log.append((round(t, 2), "falha_trav", e))
                self.reiniciar()
                return
        if e == "baixo":
            self.alvo = p.zc_min
            dentro = [i for i in self.ativas() if self.no_berco(i) and self.vel(i) < 5]
            if dentro and z < p.zc_min + 0.5:
                if t - self.t_estado > 0.3 and self.pega_desde is not None and t - self.pega_desde > 0.3:
                    self.mudar("sobe_espera")
                elif self.pega_desde is None:
                    self.pega_desde = t
            else:
                self.pega_desde = None
            if t - self.t_estado > 8:
                self.ev["sem_pega"] += 1
                self.log.append((round(t, 2), "sem_pega"))
                self.mudar("baixo")
        elif e == "sobe_espera":
            self.alvo = espera
            if abs(z - espera) < 0.3 and abs(v) < 1:
                self.mudar("espera")
        elif e == "espera":
            self.alvo = espera
            if self.pedido():
                self.saidas_janela = 0
                self.t_saida = None
                self.mudar("sobe_topo")
        elif e == "sobe_topo":
            self.alvo = topo
            if self.saidas_janela >= 1 and self.t_saida is not None and t - self.t_saida > 0.3:
                self.mudar("desce")
            elif t - self.t_estado > 4:
                self.ev["sem_entrega"] += 1
                self.log.append((round(t, 2), "sem_entrega"))
                self.mudar("desce")
        elif e == "desce":
            self.alvo = p.zc_min - 1.0
            if z < p.zc_min + 0.3 and abs(v) < 1:
                self.trav_ciclo = 0
                self.pega_desde = None
                self.mudar("baixo")

    def pedido(self):
        if self.t_pedido is None:
            return False
        return not self.no_bolso and not any(self.na_rampa(i) for i in self.ativas())

    def na_rampa(self, i):
        x = self.pos(i)
        return x[1] < 127 and x[2] > 330

    def reiniciar(self):
        """Falha sem recuperacao: tecnico abre a maquina, recoloca as bolas e manda para casa."""
        p = self.p
        tf = math.tan(math.radians(p.incl_fila))
        self.reserva = []
        for k, i in enumerate(range(N_BOLAS)):
            if k < 6:
                x = p.x_fila_fim - p.r_bola - 0.5 - k * 25.6
                self.por(i, x, 130 + p.larg_fila / 2, p.zf_fim + (p.x_fila_fim - x) * tf + self.raios[i] + 0.2)
            else:
                self.estacionar(i)
        self.d.qpos[self.jz] = (p.zc_min + 40) * MM
        self.d.qvel[self.vz] = 0
        self.no_bolso = {}
        self.trav_ciclo = 0
        self.rev_ate = None
        self.passou = [False] * N_BOLAS
        self.pega_desde = None
        self.mudar("desce")

    # ------------------------------------------------------------- bancada (carro A + retorno pela bandeja)
    def bancada(self):
        p, t = self.p, self.d.time
        for i in self.ativas():
            x = self.pos(i)
            if not self.regiao_ok(x):
                self.ev["perdidas"] += 1
                self.log.append((round(t, 2), "perdida", i, [round(c, 1) for c in x]))
                self.estacionar(i)
                continue
            if x[1] < 122 and x[2] > 330 and not self.passou[i]:
                self.passou[i] = True
                self.saidas_janela += 1
                self.t_saida = t
                if self.saidas_janela > 1:
                    self.ev["duplas"] += 1
                    self.log.append((round(t, 2), "dupla"))
            if x[1] < 75 and x[2] > 330 and self.vel(i) < 20 and i not in self.no_bolso:
                self.no_bolso[i] = t + float(self.rng.uniform(0.3, 3.0))
                self.ev["entregas"] += 1
                if self.t_pedido is not None:
                    self.ciclos.append(t - self.t_pedido)
                self.t_pedido = None
            # vazamento: bola no bolso de baixo com a cabine fora
            if self.zc() > p.zc_min + 30 and x[0] > p.x_berco_ini - 0.5 and x[2] < p.zf_fim + 20 and 128 < x[1] < 158:
                if not getattr(self, "vazou", False):
                    self.ev["vazamentos"] += 1
                    self.log.append((round(t, 2), "vazou", i, [round(c, 1) for c in x]))
                    self.vazou = True
        if self.zc() < p.zc_min + 5:
            self.vazou = False
        # pega dupla: ao sair do fundo
        if self.estado == "sobe_espera" and abs(self.zc() - (p.zc_min + 30)) < 0.2:
            n = sum(1 for i in self.ativas() if self.no_berco(i))
            if n > 1 and not getattr(self, "contou_pega", False):
                self.ev["pega_dupla"] += 1
                self.log.append((round(t, 2), "pega_dupla", n))
            self.contou_pega = True
        if self.estado != "sobe_espera":
            self.contou_pega = False
        # carro A leva a bola; ela volta pela bandeja para o inicio da fila
        for i, tl in list(self.no_bolso.items()):
            if t > tl:
                del self.no_bolso[i]
                self.passou[i] = False
                self.estacionar(i)
        if self.reserva:
            tf = math.tan(math.radians(p.incl_fila))
            x0 = p.x_fila_ini + p.r_bola + 1
            livre = all(abs(self.pos(j)[0] - x0) > 2 * p.r_bola + 1 or self.pos(j)[2] > 70 for j in self.ativas())
            if livre:
                i = self.reserva.pop(0)
                self.por(i, x0, 130 + p.larg_fila / 2 + float(self.rng.uniform(-0.5, 0.5)),
                         p.zf_fim + (p.x_fila_fim - x0) * tf + self.raios[i] + 0.3)
        if self.t_pedido is None and not self.no_bolso and self.estado in ("espera", "sobe_espera", "baixo", "desce"):
            self.t_pedido = t

    def quadro(self):
        b = []
        for i in range(N_BOLAS):
            x = self.pos(i)
            b.append([round(float(c), 2) for c in x])
        self.quadros.append(dict(t=round(self.d.time, 3), zc=round(self.zc(), 3),
                                 a=round(float(math.degrees(self.d.qpos[self.ja])), 3), b=b, e=self.estado))

    def rodar(self, entregas=None, t_max=1e9):
        self.pega_desde = None
        while True:
            self.firmware()
            self.motor()
            mujoco.mj_step(self.m, self.d, nstep=SUB)
            if int(self.d.time * 1000) % 20 == 0:
                self.bancada()
            if self.gravar and self.d.time >= self.t_quadro:
                self.quadro()
                self.t_quadro += 1 / 30
            if entregas is not None and self.ev["entregas"] >= entregas:
                break
            if self.d.time > t_max:
                break
            if self.t_pedido is not None and self.d.time - self.t_pedido > 40:
                self.ev["sem_entrega"] += 1
                self.log.append((round(self.d.time, 2), "parou"))
                self.reiniciar()
                self.t_pedido = self.d.time
        return self


# ----------------------------------------------------------------- campanha
def episodio(args):
    k, n, semente = args
    rng = np.random.default_rng(semente)
    geo, fis, raios = sortear(rng, k)
    p = replace(P(), **geo)
    t0 = time.time()
    b = Bancada(p, fis, raios, rng).rodar(entregas=n, t_max=n * 40)
    ciclos = b.ciclos
    return dict(k=k, geo={kk: (list(vv) if isinstance(vv, tuple) else round(vv, 3)) for kk, vv in geo.items()},
                fis={kk: round(vv, 4) for kk, vv in fis.items()}, raios=[round(r, 3) for r in raios],
                ev=b.ev, t_sim=round(b.d.time, 1), t_real=round(time.time() - t0, 1),
                ciclo_med=round(float(np.mean(ciclos)), 2) if ciclos else None,
                ciclo_max=round(float(np.max(ciclos)), 2) if ciclos else None, log=b.log[:40])


def campanha(n_ep, n_ent, semente=7):
    from multiprocessing import Pool
    tarefas = [(k, n_ent, semente * 1000 + k) for k in range(n_ep)]
    with Pool() as pool:
        res = pool.map(episodio, tarefas)
    tot = {}
    for r in res:
        for kk, vv in r["ev"].items():
            tot[kk] = tot.get(kk, 0) + vv
    out = dict(episodios=res, total=tot, n_ep=n_ep, n_ent=n_ent)
    (AQUI / "resultado_campanha.json").write_text(json.dumps(out, indent=1), encoding="utf8")
    return out


# ----------------------------------------------------------------- folgas
def checar(p: P = None):
    """Distancia minima entre pecas que se movem e todo o resto, em todo o curso. Pares que DEVEM
    encostar (pe da alavanca x piso do berco) sao reportados a parte."""
    p = p or P()
    fis = dict(mu_plast=0.3, amort=0.7, armadura=3, atrito_trilho=0.3, contrapeso=0.015)
    m = mujoco.MjModel.from_xml_string(mjcf(p, fis, [R_BOLA] * N_BOLAS))
    d = mujoco.MjData(m)
    for i in range(N_BOLAS):
        a = m.jnt_qposadr[m.joint(f"bj{i}").id]
        d.qpos[a:a + 3] = [5 + i * 0.1, 5, 5]
    jz, ja = m.jnt_qposadr[m.joint("cz").id], m.jnt_qposadr[m.joint("aj").id]
    gid = {m.geom(i).name: i for i in range(m.ngeom) if m.geom(i).name}
    corpo = {n: m.body(m.geom_bodyid[i]).name for n, i in gid.items()}
    moveis = [n for n in gid if corpo[n] in ("carro", "alavanca")]
    fixos = [n for n in gid if corpo[n] == "world" and n != "chao"]
    esperado = {("alav_pe", "berco_piso")}
    minimo = {}
    ft = np.zeros(6)
    zs = np.arange(p.zc_min, p.zc_max + 0.01, 0.5)
    angs = np.radians(np.arange(0, 8.01, 0.25))

    def medir(mv, alvos, z, a, dmax=0.02):
        for fx in alvos:
            dist = mujoco.mj_geomDistance(m, d, gid[mv], gid[fx], dmax, ft) / MM
            chave = (mv, fx)
            if chave not in minimo or dist < minimo[chave][0]:
                minimo[chave] = (round(dist, 2), round(z, 1), round(math.degrees(a), 2))

    carro = [n for n in moveis if corpo[n] == "carro"]
    alav = [n for n in moveis if corpo[n] == "alavanca"]
    for z in zs:
        d.qpos[jz] = z * MM
        d.qpos[ja] = 0
        mujoco.mj_kinematics(m, d)
        for mv in carro:
            medir(mv, fixos, z, 0)
    d.qpos[jz] = p.zc_max * MM
    for a in angs:
        d.qpos[ja] = a
        mujoco.mj_kinematics(m, d)
        for mv in alav:
            medir(mv, fixos, p.zc_max, a)
    # carro x alavanca: so a combinacao real (angulo imposto pelo contato) importa; mede com a alavanca fechada
    for z in zs:
        d.qpos[jz] = z * MM
        d.qpos[ja] = 0
        mujoco.mj_kinematics(m, d)
        for mv in [n for n in moveis if corpo[n] == "carro"]:
            for al in [n for n in moveis if corpo[n] == "alavanca"]:
                dist = mujoco.mj_geomDistance(m, d, gid[mv], gid[al], 0.05, ft) / MM
                chave = (mv, al)
                if chave not in minimo or dist < minimo[chave][0]:
                    minimo[chave] = (round(dist, 2), round(z, 1), 0.0)
    linhas = sorted(((v[0], k[0], k[1], v[1], v[2]) for k, v in minimo.items()), key=lambda r: r[0])
    return linhas, esperado


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "checar"
    if cmd == "checar":
        p = P()
        print({k: round(v, 2) for k, v in dict(zc_min=p.zc_min, zc_espera=p.zc_espera, zc_topo=p.zc_topo,
                                                x_bola=p.x_bola, x_contato=p.x_contato).items()})
        linhas, esp = checar(p)
        for l in linhas[:40]:
            print(l)
    elif cmd == "campanha":
        n_ep, n_ent = int(sys.argv[2]), int(sys.argv[3])
        t0 = time.time()
        out = campanha(n_ep, n_ent)
        print("total", out["total"], "tempo", round(time.time() - t0, 1))
        for r in out["episodios"]:
            print(r["k"], r["ev"], r["ciclo_med"], r["ciclo_max"], r["t_real"])
    elif cmd == "um":
        r = episodio((int(sys.argv[2]), int(sys.argv[3]), 1))
        print(json.dumps({k: v for k, v in r.items()}, indent=1))
