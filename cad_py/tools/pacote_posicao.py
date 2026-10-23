"""STL e STEP nomeados pela posicao na maquina (sem o elevador) + STEP completo sem gabinete (com e sem elevador).
Uso (de dentro de cad_py/): python tools/pacote_posicao.py"""
import shutil
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cadquery as cq  # noqa: E402

from maquina_a import assembly as AS  # noqa: E402
from maquina_a import montagem as MT  # noqa: E402
from maquina_a.parts import A12_calco as A12  # noqa: E402

ELEV = ("A20", "A21", "A22", "A23", "A24", "A25")
OUT = Path(__file__).resolve().parents[1] / "maquina_a" / "out"
CALCO = {"0": "frente-esquerda", "1": "tras-esquerda", "2": "frente-centro", "3": "tras-centro",
         "4": "frente-centro-direita", "5": "tras-direita"}
POS = {
    ("A01", "B"): "eixoB-baixo_ponta-direita-motor", ("A01", "A"): "eixoA-cima_ponta-direita-motor",
    ("A02", "B"): "eixoB-baixo_ponta-esquerda-tensor", ("A02", "A"): "eixoA-cima_ponta-esquerda-tensor",
    ("A04", "B"): "eixoB-baixo_ponta-esquerda-tensor", ("A04", "A"): "eixoA-cima_ponta-esquerda-tensor",
    ("A05", "B"): "eixoB-baixo_carro", ("A05", "A"): "eixoA-cima_carro",
    ("A07", "B"): "eixoB-baixo_carro-correia", ("A07", "A"): "eixoA-cima_carro-correia",
    ("A09", "B"): "eixoB-baixo_carro-boca", ("A10", "A"): "eixoA-cima_carro-soltura",
    ("A11", "t"): "eixoA-cima_berco-portinhola-tras", ("A11", "f"): "eixoA-cima_berco-portinhola-frente",
    ("A36", "A"): "eixoA-cima_berco-solenoide", ("A08", "B"): "ferramenta_centragem-trilho",
    ("A15", "-"): "magazine_lateral-esquerda_saida-curva",
    ("A16", "-"): "magazine_lateral-esquerda_escapamento-servo",
    ("A26", "-"): "magazine_lateral-esquerda_curva-entrada-berco",
    ("A17", "-"): "magazine_lateral-esquerda_balancim-escapamento",
    ("A18", "-"): "magazine_lado-direito_entrada-funil",
    ("A19", "-"): "magazine_lateral-direita_suporte-entrada",
    ("A13", "e"): "bandeja_rodape-tras-esquerda", ("A13", "d"): "bandeja_rodape-tras-direita",
}
for v, p in CALCO.items():
    POS[("A12", v)] = f"bandeja_calco-{p}_h{A12.altura(v):.1f}mm".replace(".", ",")

for ext, pasta in (("stl", "stl_por_posicao"), ("step", "step_por_posicao")):
    dst = OUT / pasta
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir()
    linhas = ["arquivo;peca;posicao;qtd;impressora"]
    for pid in MT.PECAS:
        if pid in ELEV:
            continue
        m = MT.modulo(pid)
        for v, q in m.QTD.items():
            f = OUT / ext / (f"{pid}_{m.NOME}" + ("" if v == MT.var_principal(m) else f"_{v}") + f".{ext}")
            nome = f"{pid}_{m.NOME}__{POS[(pid, v)]}" + (f"__x{q}" if q > 1 else "") + f".{ext}"
            shutil.copy2(f, dst / nome)
            linhas.append(f"{nome};{m.TITULO};{POS[(pid, v)]};{q};{m.IMPRESSORA}")
    (dst / "LISTA.csv").write_text("\n".join(linhas) + "\n", encoding="utf-8-sig")
    with zipfile.ZipFile(OUT / f"{pasta}_sem_elevador.zip", "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(dst.iterdir()):
            zf.write(f, f.name)
    print(ext, len(linhas) - 1)

pecas = list(AS.pecas())
hw = {**AS.compradas(), **MT.hardware_fixo()}
band = {k: v for k, v in MT.corpos_bandeja().items() if k != "divisoria"}
for nome, com in (("maquina_a_sem_gabinete", True), ("maquina_a_sem_gabinete_sem_elevador", False)):
    a = cq.Assembly(name=nome)
    for n, w in pecas:
        if com or n[:3] not in ELEV:
            a.add(w, name=n, color=cq.Color(0.91, 0.54, 0.17))
    for n, w in hw.items():
        if com or not n.startswith("elev_"):
            vidro = n in ("tubo", "elev_acrilico")
            a.add(w, name="comprada_" + n.replace(".", "_"),
                  color=cq.Color(0.62, 0.83, 0.91, 0.5) if vidro else cq.Color(0.55, 0.55, 0.55))
    for n, w in band.items():
        a.add(w, name=n, color=cq.Color(0.2, 0.2, 0.2) if n == "bandeja_eva" else cq.Color(0.78, 0.66, 0.47))
    a.save(str(OUT / f"{nome}.step"))
print("ok")
