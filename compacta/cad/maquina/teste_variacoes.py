"""Tolerancias: repete as checagens da bola e das pecas paradas com o modelo deslocado (erro de impressao/montagem)."""
import json
from dataclasses import replace
from pathlib import Path

import layout as L
from cena_m import Cena
import checagem as C

CASOS = {
    "nominal": {},
    "ima 0,5 mm mais perto": dict(gap_pega=0.5),
    "ima 1,5 mm mais longe": dict(gap_pega=1.5),
    "ima 0,5 mm para a esquerda": dict(x_pega=191.8),
    "ima 0,5 mm para a direita": dict(x_pega=192.8),
    "ima 0,5 mm para a frente": dict(y_bola=73.2),
    "ima 0,5 mm para tras": dict(y_bola=74.2),
    "rampa 1 grau de queda para a direita": dict(incl_rampa_x=1.0),
    "rampa 2 graus de queda para a direita": dict(incl_rampa_x=2.0),
    "queda 248 (perfil de cima 2 mm abaixo)": dict(queda=248.0),
    "anel 1 mm mais alto (queda 249)": dict(queda=249.0),
    "folga limpa 5,8": dict(folga_limpa=5.8),
}


def main():
    out = {}
    for nome, kw in CASOS.items():
        m = replace(L.M(), **kw)
        c = Cena(m)
        it = C.interferencias(c)
        b = C.bola(c)
        linha = dict(interferencias=it["n_ruins"], **{k: bool(v["ok"]) for k, v in b.items()},
                     pega_mm=b["pega"]["ima_ate_bola"], levando_mm=b["levando"]["folga_min"],
                     anel_ok=b["anel"]["casos"], folga_bola_anel=b["bandeja"]["folga_bola_anel"])
        out[nome] = linha
        ok = it["n_ruins"] == 0 and all(v["ok"] for v in b.values())
        print(("OK  " if ok else "RUIM"), nome, {k: v for k, v in linha.items() if k not in ("anel_ok",)}, flush=True)
    Path(__file__).with_name("teste_variacoes.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=float),
                                                                encoding="utf8")


if __name__ == "__main__":
    main()
