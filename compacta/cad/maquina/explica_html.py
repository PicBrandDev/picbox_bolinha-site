"""Gera saida/explica.html (e compacta/pagina/PICBOX_como_funciona.html): elevador, correias, bolso, anel, sensores."""
import json
from pathlib import Path

import layout as L

AQUI = Path(__file__).parent


def main():
    m = L.M()
    e = m.el
    dados = dict(zc=[e.zc_min, e.zc_max], zp=[e.z_polia_baixo, e.z_polia_cima], x_bola=e.x_bola, y_fila=e.y_bola,
                 bolso=m.bola_bolso.tolist(), zs=m.zs, zb=m.zb, r=L.R, y_bola=m.y_bola, S=m.s_bandeja(0, m.y_bola),
                 f40=m.f_fila(40), f150=m.f_fila(150), x_motor=m.x_motor, x_tens=m.x_tensora, cA=list(m.cA), dA=m.dA)
    html = (AQUI / "explica_tpl.html").read_text(encoding="utf8").replace("__M__", json.dumps(dados))
    (AQUI / "saida" / "explica.html").write_text(html, encoding="utf8")
    (AQUI.parents[1] / "pagina" / "PICBOX_como_funciona.html").write_text(html, encoding="utf8")
    print("ok", len(html) // 1024, "KB")


if __name__ == "__main__":
    main()
