"""Bucha da polia do motor N20: polia GT2 20T furo 5 mm no eixo de 3 mm do N20.

  python bucha_n20.py  ->  saida/stl/bucha_da_polia_do_n20__x4.stl  (+ imagens e pagina)
                           compacta/pagina/PICBOX_bucha_polia_n20.html (copiada pelo publicar.py)

Medidas (N20): eixo de 3,0 mm (redondo ou com lado chato), 10 mm de comprimento. Furo redondo serve nos dois.
Polia GT2 20T furo 5: cubo de 7 mm com o parafuso sem cabeca M3 no meio do cubo.
"""
import base64
import io
import math
from pathlib import Path

import cadquery as cq

AQUI = Path(__file__).parent
S = AQUI / "saida"
IMG = S / "imagens_bucha"
ARQ = "bucha_da_polia_do_n20__x4.stl"

# bucha (impressa ja com a compensacao tipica: fora sai um pouco maior, furo sai um pouco menor)
L_B = 9.5          # comprimento (eixo do N20 tem 10)
R_FORA = 2.45      # 4,9 de diametro: entra no furo de 5 da polia
R_FURO = 1.6       # 3,2 de diametro: o eixo de 3 entra sem forcar
RASGO_W, RASGO_L = 3.3, 6.0   # rasgo aberto na ponta do motor: o parafuso da polia passa por ele e aperta no eixo


def bucha():
    furo = cq.Workplane("XY").circle(R_FURO).extrude(L_B)
    corpo = cq.Workplane("XY").circle(R_FORA).extrude(L_B).cut(furo)
    rasgo = cq.Workplane("XY").center(R_FORA, 0).rect(2 * R_FORA, RASGO_W).extrude(RASGO_L)
    return corpo.cut(rasgo)


def eixo():
    return (cq.Workplane("XY").circle(1.5).extrude(10.0)
            .intersect(cq.Workplane("XY").center(1.0 - 5, 0).rect(10, 10).extrude(10.0)))


def polia():
    cubo = cq.Workplane("XY").circle(6.5).extrude(7.0)
    dentes = cq.Workplane("XY").workplane(offset=7.0).polygon(40, 2 * 6.1).extrude(7.0)
    fl1 = cq.Workplane("XY").workplane(offset=7.0).circle(8.0).extrude(1.0)
    fl2 = cq.Workplane("XY").workplane(offset=13.0).circle(8.0).extrude(1.0)
    p = cubo.union(dentes).union(fl1).union(fl2)
    p = p.cut(cq.Workplane("XY").circle(2.5).extrude(14.0))
    p = p.cut(cq.Workplane("YZ").workplane(offset=0).center(0, 3.5).circle(1.5).extrude(8.0))   # rosca M3 do cubo
    return p


def parafuso():
    return cq.Workplane("YZ").workplane(offset=1.0).center(0, 3.5).circle(1.45).extrude(4.0)


def motor():
    return (cq.Workplane("XY").workplane(offset=-9.0).rect(12, 10).extrude(9.0)
            .union(cq.Workplane("XY").workplane(offset=-0.8).circle(2.0).extrude(0.8)))


def mesa_x4(b):
    """4 buchas em pe, ponta do rasgo para cima (sem suporte), 12 mm entre elas."""
    vira = b.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, L_B))
    out = None
    for i in range(4):
        c = vira.translate((R_FORA + (i % 2) * 12.0, R_FORA + (i // 2) * 12.0, 0))
        out = c if out is None else out.union(c)
    return out


def imagens(pecas):
    import pyvista as pv
    import tempfile
    pv.OFF_SCREEN = True
    IMG.mkdir(parents=True, exist_ok=True)
    mal = {}
    with tempfile.TemporaryDirectory() as d:
        for k, wp in pecas.items():
            p = Path(d) / f"{k}.stl"
            cq.exporters.export(wp, str(p), tolerance=0.01, angularTolerance=0.1)
            mal[k] = pv.read(str(p))
    COR = dict(bucha="#e07a22", eixo="#8d969b", polia="#b9c2c8", parafuso="#3b413e", motor="#d0d5d8")

    def foto(nome, itens, foco, direcao, escala, rot=(), titulo="", tam=(1400, 1000), up=(0, 0, 1)):
        pl = pv.Plotter(off_screen=True, window_size=tam)
        pl.set_background("#f4f6f4")
        for k, me, op in itens:
            pl.add_mesh(me, color=COR[k], opacity=op, smooth_shading=True, specular=0.3)
        if rot:
            pl.add_point_labels([r[1] for r in rot], [r[0] for r in rot], font_size=18, point_size=8,
                                point_color="#c23b6b", text_color="#111111", shape_color="#ffffff",
                                shape_opacity=0.85, always_visible=True)
        d = [v / math.sqrt(sum(x * x for x in direcao)) for v in direcao]
        pl.camera.focal_point = foco
        pl.camera.position = [foco[i] + d[i] * 500 for i in range(3)]
        pl.camera.up = up
        pl.camera.parallel_projection = True
        pl.camera.parallel_scale = escala
        if titulo:
            pl.add_text(titulo, position="upper_left", font_size=13, color="#111111")
        pl.enable_anti_aliasing("ssaa")
        pl.screenshot(str(IMG / nome))
        pl.close()

    b = mal["bucha"]
    foto("01_bucha.png", [("bucha", b, 1)], (0, 0, L_B / 2), (1, -0.9, 0.7), 7.5,
         [("Rasgo: o parafuso da polia passa aqui", (R_FORA, 0, 3.0)), ("Furo redondo 3,2 (eixo do N20)", (0, 0, L_B)),
          ("Fora 4,9 (furo da polia 5)", (-R_FORA, 0, 7.0))], "Bucha: fora 4,9 mm, furo 3,2 mm, 9,5 mm de altura")
    foto("02_topo.png", [("bucha", b, 1)], (0, 0, L_B), (0, 0, 1), 3.6,
         [("Furo 3,2: o eixo de 3 entra sem forcar", (1.6, 0, L_B))], "Vista de cima", up=(0, 1, 0))
    sobe = lambda me, dz=0, dx=0: me.translate((dx, 0, dz), inplace=False)
    foto("03_explodida.png", [("motor", mal["motor"], 1), ("eixo", mal["eixo"], 1), ("bucha", sobe(b, 14), 1),
                              ("polia", sobe(mal["polia"], 28), 1), ("parafuso", sobe(mal["parafuso"], 28, 9), 1)],
         (0, 0, 16), (1, -1.1, 0.45), 26,
         [("1. eixo do N20 (3 mm)", (1.5, 0, 9)), ("2. bucha: rasgo na ponta do motor", (R_FORA, 0, 16)),
          ("3. polia GT2 20T furo 5, cubo para baixo", (8, 0, 38)), ("4. parafuso sem cabeca M3", (14, 0, 31.5))],
         "Montagem: a bucha entra no eixo, a polia entra na bucha, o parafuso passa pelo rasgo e aperta no eixo")
    corte = lambda me: me.clip(normal=(0, -1, 0), origin=(0, 0, 0))
    foto("04_corte.png", [("motor", corte(mal["motor"]), 1), ("eixo", corte(mal["eixo"]), 1), ("bucha", corte(b), 1),
                          ("polia", corte(mal["polia"]), 1), ("parafuso", corte(mal["parafuso"]), 1)],
         (2, 0, 6), (0.25, -1, 0.15), 11,
         [("Parafuso aperta direto no eixo", (4.5, 0, 3.5)), ("Bucha entre eixo e polia", (-2.0, 0, 9.0)),
          ("Polia", (-7.5, 0, 12))], "Corte montado")


def pagina():
    img = lambda n: "data:image/png;base64," + base64.b64encode((IMG / n).read_bytes()).decode()
    stl = base64.b64encode((S / "stl" / ARQ).read_bytes()).decode()
    html = f"""<title>Bucha polia N20</title>
<meta name="claude:viewport-fit-sides" content="cover">
<style>
:root{{--bg:#f3f5f7;--papel:#fff;--tinta:#17202a;--suave:#5a6672;--linha:#d8dee4;--acento:#c25d12;
  --f:"Segoe UI",system-ui,sans-serif;--m:ui-monospace,Consolas,monospace}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#12171c;--papel:#1b2229;--tinta:#e6ebef;--suave:#9aa6b1;--linha:#2d3741;--acento:#f0913f;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#12171c;--papel:#1b2229;--tinta:#e6ebef;--suave:#9aa6b1;--linha:#2d3741;--acento:#f0913f;color-scheme:dark}}
body{{background:var(--bg);color:var(--tinta);font:15px/1.55 var(--f);padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:24px 48px}}
main{{max-width:960px;margin:0 auto;display:flex;flex-direction:column;gap:22px}}
h1{{margin:0;font-size:1.8rem}} h2{{margin:0;font-size:1.15rem}} p{{margin:0;max-width:68ch}}
.g{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}}
figure{{margin:0;background:#f4f6f4;border:1px solid var(--linha);border-radius:8px;overflow:hidden}}
figure img{{display:block;width:100%;height:auto}} figure.l{{grid-column:1/-1}}
.c{{background:var(--papel);border:1px solid var(--linha);border-radius:8px;padding:16px 18px;display:flex;flex-direction:column;gap:8px;min-width:0}}
table{{border-collapse:collapse;width:100%;font-size:.92rem}} td{{padding:6px 8px;border-bottom:1px solid var(--linha);vertical-align:top}}
td.n{{font-family:var(--m);white-space:nowrap;text-align:right}} tr:last-child td{{border-bottom:0}}
ol,ul{{margin:0;padding-left:1.2em;display:flex;flex-direction:column;gap:4px}}
.mono{{font-family:var(--m)}} .rot{{font-size:.75rem;letter-spacing:.08em;text-transform:uppercase;color:var(--suave)}}
button{{font:600 .9rem var(--f);background:var(--acento);color:#fff;border:0;border-radius:6px;padding:8px 14px;cursor:pointer;align-self:flex-start}}
</style>
<main>
<header style="display:flex;flex-direction:column;gap:8px"><span class="rot">PICBOX compacta · elevador</span>
<h1>Bucha da polia do motor N20</h1>
<p>Adapta a polia GT2 20T de furo 5 mm ao eixo de 3 mm do N20. O parafuso sem cabeça da polia passa pelo rasgo da bucha e aperta direto no eixo, então a polia não patina.</p></header>
<div class="g">
<figure class="l"><img src="{img('03_explodida.png')}" alt="Montagem explodida"></figure>
<figure><img src="{img('01_bucha.png')}" alt="Bucha"></figure>
<figure><img src="{img('04_corte.png')}" alt="Corte montado"></figure>
<figure><img src="{img('02_topo.png')}" alt="Vista de cima"></figure>
<div class="c"><h2>Medidas</h2><table>
<tr><td>Diâmetro de fora</td><td class="n">4,9 mm</td></tr>
<tr><td>Furo (eixo do N20 de 3 mm)</td><td class="n">3,2 mm</td></tr>
<tr><td>Altura</td><td class="n">9,5 mm</td></tr>
<tr><td>Rasgo do parafuso (largura × altura)</td><td class="n">3,3 × 6 mm</td></tr>
</table></div>
</div>
<div class="g">
<div class="c"><h2>Imprimir</h2><ul>
<li>Arquivo <span class="mono">{ARQ}</span>: 4 buchas em pé (2 de reserva), rasgo para cima, sem suporte.</li>
<li>PETG, bico 0,4, camada 0,12 ou 0,16, 100% de preenchimento, velocidade baixa, com aba (brim) de 5 mm para não soltar da mesa.</li>
<li>Peça muito pequena: imprima junto com outra peça na mesma mesa, para cada camada ter tempo de esfriar.</li>
<li>Se ficar justa na polia, lixe de leve por fora. Se o eixo não entrar, passe uma broca de 3 mm no furo.</li>
</ul></div>
<div class="c"><h2>Montar</h2><ol>
<li>Empurre a bucha no eixo do N20, com o rasgo na ponta do motor.</li>
<li>Empurre a polia na bucha, com o cubo (lado do parafuso) virado para o motor.</li>
<li>Gire a polia até o parafuso ficar alinhado com o rasgo.</li>
<li>Aperte o parafuso sem cabeça: ele passa pelo rasgo e trava direto no eixo (se o eixo tiver um lado chato, deixe o parafuso nele).</li>
</ol></div>
</div>
<div class="c"><h2>Arquivo</h2><p>O STL está dentro desta página.</p><button type="button" id="bx">Baixar {ARQ}</button>
<p class="rot" id="bx-msg"></p></div>
</main>
<script>
document.getElementById("bx").addEventListener("click", () => {{
  try {{
    const b = atob("{stl}"), u = new Uint8Array(b.length); for (let i = 0; i < b.length; i++) u[i] = b.charCodeAt(i);
    const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob([u], {{type: "model/stl"}})); a.download = "{ARQ}";
    document.body.appendChild(a); a.click(); a.remove();
    document.getElementById("bx-msg").textContent = "Se nada baixou, abra este arquivo salvo no computador.";
  }} catch (e) {{ document.getElementById("bx-msg").textContent = "Não deu para baixar aqui: " + e.message; }}
}});
</script>"""
    out = S / "bucha_n20.html"
    out.write_text(html, encoding="utf8")
    return out


def main():
    (S / "stl").mkdir(parents=True, exist_ok=True)
    b = bucha()
    cq.exporters.export(mesa_x4(b), str(S / "stl" / ARQ), tolerance=0.01, angularTolerance=0.1)
    imagens(dict(bucha=b, eixo=eixo(), polia=polia(), parafuso=parafuso(), motor=motor()))
    print("ok", ARQ, pagina())


if __name__ == "__main__":
    main()
