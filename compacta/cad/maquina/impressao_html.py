"""Gera saida/impressao.html: mesas por impressora na ordem, imagem de cada mesa, pecas e onde vao.
(rode depois de plano.py, render_mesas.py e render_m.py)"""
import base64
import io
import json
import zipfile
from pathlib import Path

AQUI = Path(__file__).parent
S = AQUI / "saida"
IMP = AQUI.parents[1] / "imprimir"          # compacta/imprimir (rode publicar.py antes)
PASTA = {"A": "A_impressora_grande", "B": "B_creality_1", "C": "C_creality_2"}


def zip64(arqs):
    """[(caminho no disco, nome dentro do zip)] -> zip em base64."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for f, nome in arqs:
            zf.write(f, nome)
    return base64.b64encode(buf.getvalue()).decode()


def b64(p):
    return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()


def main():
    plano = json.loads((S / "plano.json").read_text(encoding="utf8"))
    imgs = {p["arquivo"]: b64(S / "mesas" / p["arquivo"].replace(".stl", ".png"))
            for v in plano["placas"].values() for p in v}
    fotos = [(t, b64(S / "imagens" / a)) for a, t in (("01_geral.png", "Montagem completa"),
                                                      ("02_frente.png", "De frente, como o jogador vê"),
                                                      ("04_pega.png", "Pega da bola no bolso"),
                                                      ("05_elevador_topo.png", "Elevador no topo"),
                                                      ("06_comporta.png", "Comporta"), ("07_anel.png", "Anel no carro B"))]
    pecas = [dict(peca=p["peca"], arquivo=p["arquivo"], quantidade=p["quantidade"], placas=p["placas"],
                  posicao=p["posicao"], suporte=p["suporte"], horas=p["horas"], funcao=p["funcao"], por_que=p["por_que"])
             for p in plano["pecas"]]
    zips = {}
    tudo = [(IMP / "ORDEM_DE_IMPRESSAO.txt", "ORDEM_DE_IMPRESSAO.txt")]
    for k, pasta in PASTA.items():
        arqs = []
        for i, p in enumerate(plano["placas"][k], 1):
            nome = f"{i:02d}_placa_{p['n']}.stl"
            zips["mesa_" + p["n"]] = zip64([(IMP / pasta / nome, nome)])
            arqs.append((IMP / pasta / nome, f"{pasta}/{nome}"))
        arqs.append((IMP / pasta / "LEIA-ME.txt", f"{pasta}/LEIA-ME.txt"))
        zips["impressora_" + k] = zip64(arqs)
        tudo += arqs
    av = [(f, "pecas_avulsas/" + f.name) for f in sorted((IMP / "pecas_avulsas").glob("*.stl"))]
    zips["avulsas"] = zip64(av)
    zips["tudo"] = zip64(tudo + av)
    dados = dict(placas=plano["placas"], total=plano["total"], pecas=pecas, imgs=imgs, fotos=fotos, zips=zips)
    html = (AQUI / "impressao_tpl.html").read_text(encoding="utf8").replace("__DADOS__", json.dumps(dados, ensure_ascii=False))
    (S / "impressao.html").write_text(html, encoding="utf8")
    (IMP / "impressao.html").write_text(html, encoding="utf8")
    print("ok", len(html) // 1024, "KB")


if __name__ == "__main__":
    main()
