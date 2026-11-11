"""Ficha de impressao para UMA impressora (SparkX i7): imagens das mesas + HTML de arquivo unico (para mandar no WhatsApp).

  python plano_unica.py && python impressao_unica.py
  -> compacta/imprimir/SparkX_i7/ (mesas, LEIA-ME) e compacta/imprimir/PICBOX_R2_SparkX_i7.html
"""
import base64
import io
import json
import shutil
import zipfile
from pathlib import Path

import numpy as np
import pyvista as pv

pv.OFF_SCREEN = True
AQUI = Path(__file__).parent
S = AQUI / "saida"
U = AQUI / "saida_unica"
IMP = AQUI.parents[1] / "imprimir"
PASTA = "SparkX_i7"
LADO = 260
CORES = ["#2f6fd6", "#e07a22", "#3f8f5f", "#b8457a", "#7a5cc7", "#c9a227", "#2b9aa6", "#a0522d"]


def render(plano):
    out = U / "mesas"
    out.mkdir(exist_ok=True)
    for p in plano["placas"]["S"]:
        me = pv.read(str(U / "placas" / p["arquivo"]))
        partes = me.connectivity(extraction_mode="all").split_bodies()
        pl = pv.Plotter(off_screen=True, window_size=(900, 700))
        pl.set_background("#f4f6f4")
        pl.add_mesh(pv.Box(bounds=(-LADO / 2, LADO / 2, -LADO / 2, LADO / 2, -2.0, 0.0)), color="#c9cfcb")
        pl.add_mesh(pv.Box(bounds=(-LADO / 2 + 5, LADO / 2 - 5, -LADO / 2 + 5, LADO / 2 - 5, -0.05, 0.0)),
                    style="wireframe", color="#7d8a83", line_width=1)
        for i, b in enumerate(partes):
            pl.add_mesh(b.extract_surface(algorithm="dataset_surface"), color=CORES[i % len(CORES)], specular=0.15)
        alt = max(p["altura"], 40)
        pl.camera.focal_point = (0, 0, alt * 0.35)
        pl.camera.position = (-LADO * 0.9, -LADO * 1.5, LADO * 1.25 + alt)
        pl.camera.up = (0, 0, 1)
        pl.camera.parallel_projection = True
        pl.camera.parallel_scale = LADO * 0.62 + alt * 0.25
        pl.enable_anti_aliasing("ssaa")
        pl.screenshot(str(out / p["arquivo"].replace(".stl", ".png")))
        pl.close()
        print(p["arquivo"], len(partes), flush=True)


def zip64(arqs):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for f, nome in arqs:
            zf.write(f, nome)
    return base64.b64encode(buf.getvalue()).decode()


def b64(p):
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()


def main():
    plano = json.loads((U / "plano.json").read_text(encoding="utf8"))
    render(plano)
    # pasta de entrega
    d = IMP / PASTA
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    for p in plano["placas"]["S"]:
        shutil.copy2(U / "placas" / p["arquivo"], d / p["arquivo"])
    shutil.copy2(U / "placas" / "LEIA-ME.txt", d / "LEIA-ME.txt")
    imgs = {p["arquivo"]: b64(U / "mesas" / p["arquivo"].replace(".stl", ".png")) for p in plano["placas"]["S"]}
    fotos = [(t, b64(S / "imagens" / a)) for a, t in (("01_geral.png", "Montagem completa"),
                                                      ("02_frente.png", "De frente, como o jogador vê"),
                                                      ("04_pega.png", "Pega da bola no bolso"),
                                                      ("05_elevador_topo.png", "Elevador no topo"),
                                                      ("08_torre_baixo.png", "Pé da torre do elevador"),
                                                      ("s1_sensores_geral.png", "Onde ficam os sensores"))]
    pecas = [dict(peca=p["peca"], arquivo=p["arquivo"], quantidade=p["quantidade"], placas=p["placas"],
                  posicao=p["posicao"], suporte=p["suporte"], horas=p["horas"], funcao=p["funcao"], por_que=p["por_que"])
             for p in plano["pecas"]]
    zips = {}
    arqs = []
    for p in plano["placas"]["S"]:
        zips["mesa_" + p["n"]] = zip64([(d / p["arquivo"], p["arquivo"])])
        arqs.append((d / p["arquivo"], f"{PASTA}/{p['arquivo']}"))
    arqs += [(d / "LEIA-ME.txt", f"{PASTA}/LEIA-ME.txt"), (IMP / "LEIA-ME_R2.txt", "LEIA-ME_R2.txt")]
    zips["impressora_S"] = zip64(arqs)
    av = [(f, "pecas_avulsas/" + f.name) for f in sorted((IMP / "pecas_avulsas").glob("*.stl"))]
    zips["avulsas"] = zip64(av)
    pc = [(f, "polia_de_cima/" + f.name) for f in sorted((IMP / "polia_de_cima").glob("*")) if f.suffix in (".stl", ".txt")]
    zips["tudo"] = zip64(arqs + av + pc)
    dados = dict(placas=plano["placas"], total=plano["total"], pecas=pecas, imgs=imgs, fotos=fotos, zips=zips)
    longa = max(plano["placas"]["S"], key=lambda p: p["horas"])
    h = (AQUI / "impressao_tpl.html").read_text(encoding="utf8")
    i0, i1 = h.index("const IMP = {"), h.index("const ler = ")
    h = h[:i0] + '''const IMP = {S: {pasta: "SparkX_i7", nome: "Creality SparkX i7", mesa: "260 × 260", sub: "Todas as peças, na menor quantidade de mesas", cor: "var(--a)"}};
''' + h[i1:]
    for a, b in [
        ('"picbox-impresso-"', '"picbox-sparkx-"'),
        ('grid-template-columns:repeat(4,minmax(0,1fr))}', 'grid-template-columns:repeat(auto-fit,minmax(210px,1fr))}'),
        ('let atual = "A";', 'let atual = "S";'),
        ('arq = `${nn}_placa_${p.n}.stl`', 'arq = p.arquivo'),
        ('try { atual = localStorage.getItem("picbox-aba") || "A"; } catch (e) {}', ''),
        ('["A", "B", "C"].map(k =>', '["S"].map(k =>'),
        ('"Baixar tudo (.zip): 3 impressoras + peças avulsas"', '"Baixar tudo (.zip): as mesas + peças avulsas"'),
        ('`Baixar as ${lista.length} mesas da ${atual} (.zip)`', '`Baixar as ${lista.length} mesas (.zip)`'),
        ('<h1>PICBOX Compacta R2</h1>', '<h1>PICBOX Compacta R2 · SparkX i7</h1>'),
        ('"picbox_compacta_impressao_completa.zip"', '"picbox_R2_sparkx_i7_completa.zip"'),
        ('<span class="muted">Pasta <span class="mono">compacta/imprimir/${I.pasta}/</span></span>', ''),
        ('.abas{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}', '.abas{display:grid;grid-template-columns:minmax(0,1fr);gap:12px}'),
        ('<div><b>R2: imprima tudo</b><span>O gabinete mudou de tamanho: todas as peças são novas. As 2 torres do elevador levam ~22 h cada, sem suporte e com aba (brim) de 5 mm.</span></div>',
         f'<div><b>Uma impressora só</b><span>Tudo em {len(plano["placas"]["S"])} mesas na SparkX i7 (260 × 260). Aba (brim) de 5 mm em todas. '
         f'A mesa mais longa ({longa["n"]}) leva ~{round(longa["horas"])} h seguidas.</span></div>'),
        ('<div><b>Mesa 01 primeiro</b><span>É o teste de encaixe: monte com as peças compradas antes de seguir.</span></div>',
         '<div><b>Mesa 01 primeiro</b><span>Tem a cabine e os carros (teste de encaixe). Suporte em árvore só nessas 3 peças.</span></div>'),
        ('Arquivos avulsos em <span class="mono">compacta/imprimir/pecas_avulsas/</span>, para reimprimir uma peça só.',
         'Cada peça também vem sozinha no botão abaixo, para reimprimir uma só.'),
    ]:
        assert a in h, a
        h = h.replace(a, b)
    h = h.replace("<title>Impressão PICBOX Compacta</title>", "<title>Impressão PICBOX R2 · SparkX i7</title>")
    h = h.replace("__DADOS__", json.dumps(dados, ensure_ascii=False))
    out = IMP / "PICBOX_R2_SparkX_i7.html"
    out.write_text(h, encoding="utf8")
    print("ok", out, len(h) // 1024, "KB")


if __name__ == "__main__":
    main()
