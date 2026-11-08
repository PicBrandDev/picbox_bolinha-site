"""Copia o que interessa para fora da pasta de codigo, ja organizado (rode depois de pecas.py, plano.py, render_m.py e pagina_m.py).

  compacta/imprimir/ORDEM_DE_IMPRESSAO.txt
  compacta/imprimir/A_impressora_grande/01_placa_A1.stl ...   (+ LEIA-ME.txt de cada impressora)
  compacta/imprimir/B_creality_1/ ...
  compacta/imprimir/C_creality_2/ ...
  compacta/imprimir/pecas_avulsas/*.stl                         (uma peca por arquivo, para reimprimir)
  compacta/pagina/picbox_compacta.html                          (3D, montagem, checagens)
  compacta/imagens/*.png                                         (montagem com as pecas reais)
  compacta/step/*.step                                           (pecas na posicao de montagem, para editar)
"""
import json
import shutil
from pathlib import Path

AQUI = Path(__file__).resolve().parent
S = AQUI / "saida"
C = AQUI.parents[1]                     # .../compacta
PASTA = {"A": "A_impressora_grande", "B": "B_creality_1", "C": "C_creality_2"}
NOME = {"A": "A - impressora grande (a melhor): pecas de precisao e as que ficam a vista",
        "B": "B - Creality 220 x 220", "C": "C - Creality 220 x 220"}
CONFIG = ["Configuracao: PETG, bico 0,4, camada 0,2, 4 perimetros, 25% de preenchimento.",
          "Os arquivos ja vem com as pecas arrumadas na mesa e na posicao certa: NAO use orientacao automatica.",
          "Se o fatiador juntar tudo num objeto so, use 'Dividir em objetos' (Split to objects).",
          "Placas COM SUPORTE: suporte em arvore so onde precisa e aba (brim) de 5 mm."]


def limpa(p):
    if p.exists():
        shutil.rmtree(p)
    p.mkdir(parents=True)


def main():
    import bucha_n20
    bucha_n20.main()                        # bucha da polia do N20 (peca pequena, fora das mesas)
    plano = json.loads((S / "plano.json").read_text(encoding="utf8"))
    imp = C / "imprimir"
    limpa(imp)
    geral = ["PICBOX COMPACTA - ORDEM DE IMPRESSAO", "", *CONFIG, "",
             "As 3 impressoras trabalham ao mesmo tempo. Em cada uma, imprima na ordem dos numeros.", ""]
    for k in ("A", "B", "C"):
        d = imp / PASTA[k]
        d.mkdir()
        txt = [f"IMPRESSORA {NOME[k]}  -  total {plano['total'][k]} h", "", *CONFIG, ""]
        geral.append(f"IMPRESSORA {NOME[k]}  -  total {plano['total'][k]} h   (pasta {PASTA[k]})")
        for i, p in enumerate(plano["placas"][k], 1):
            arq = f"{i:02d}_placa_{p['n']}.stl"
            shutil.copy2(S / "placas" / p["arquivo"], d / arq)
            linha = f"  {arq:<20} {p['horas']:>5} h  altura {p['altura']:.0f} mm{'  COM SUPORTE' if p['suporte'] else ''}"
            txt.append(linha)
            geral.append(linha)
            for x in p["pecas"]:
                txt.append(f"        - {x}")
                geral.append(f"        - {x}")
        geral.append("")
        (d / "LEIA-ME.txt").write_text("\n".join(txt), encoding="utf8")
    geral += ["Pecas avulsas (uma por arquivo, para reimprimir so uma): pasta pecas_avulsas.",
              "No nome, __x2 / __x3 = imprimir 2 / 3 copias."]
    (imp / "ORDEM_DE_IMPRESSAO.txt").write_text("\n".join(geral), encoding="utf8")
    av = imp / "pecas_avulsas"
    av.mkdir()
    for f in sorted((S / "stl").glob("*.stl")):
        shutil.copy2(f, av / f.name)
    for nome, origem, padrao in (("imagens", S / "imagens", "*.png"), ("step", S / "step", "*.step")):
        limpa(C / nome)
        for f in sorted(origem.glob(padrao)):
            shutil.copy2(f, C / nome / f.name)
    if (S / "impressao.html").exists():
        shutil.copy2(S / "impressao.html", imp / "PICBOX_compacta_impressao.html")
    limpa(C / "pagina")
    shutil.copy2(S / "picbox_compacta_r1.html", C / "pagina" / "PICBOX_compacta_visualizacao.html")
    for orig, dest in (("explica.html", "PICBOX_como_funciona.html"), ("novidades.html", "PICBOX_novidades_R1.1.html"),
                       ("bucha_n20.html", "PICBOX_bucha_polia_n20.html")):
        if (S / orig).exists():
            shutil.copy2(S / orig, C / "pagina" / dest)
    import alteradas
    alteradas.main()
    print("\n".join(geral))


if __name__ == "__main__":
    main()
