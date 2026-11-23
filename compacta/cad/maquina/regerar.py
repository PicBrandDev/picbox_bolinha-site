"""Regera TUDO da compacta, na ordem certa, e para no primeiro erro.

  python regerar.py            (pelo PowerShell: o pecas.py usa CadQuery)
  python regerar.py malhas     (comeca a partir de um passo)
Depois: compacta/imprimir, pagina, imagens e step atualizados (publicar.py e o ultimo).
"""
import subprocess
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PASSOS = [
    "checagem",          # modelo: bola, interferencias, parafusos, varredura -> saida/validacao.json
    "resistencia_m",     # contas de resistencia
    "pecas",             # STL + STEP de cada peca impressa (CadQuery)
    "teste_stl",         # testes na malha real que vai para a impressora
    "plano",             # mesas das 3 impressoras
    "plano_unica",       # mesas para uma impressora so (SparkX i7)
    "malhas",            # malhas reais para o 3D e as imagens
    "render_m",          # imagens da montagem
    "render_polias",     # imagens das polias
    "render_sensores",   # imagens dos sensores
    "render_elevador",   # imagem do elevador com nomes
    "render_mesas",      # imagem de cada mesa
    "impressao_html",    # ficha de impressao (3 impressoras)
    "explica_html",      # pagina "como funciona"
    "pagina_m",          # pagina da maquina (3D, pecas, montagem, checagens)
    "publicar",          # copia tudo para compacta/ + polia de cima, SparkX i7, alteradas, visualizador, elevador 3D e montagem
]


def main():
    ini = sys.argv[1] if len(sys.argv) > 1 else PASSOS[0]
    t0 = time.time()
    for p in PASSOS[PASSOS.index(ini):]:
        t = time.time()
        print(f"\n===== {p}", flush=True)
        r = subprocess.run([sys.executable, f"{p}.py"], cwd=AQUI)
        print(f"===== {p}: {'ok' if r.returncode == 0 else 'ERRO'} em {time.time() - t:.0f} s", flush=True)
        if r.returncode:
            sys.exit(f"parou em {p} (rode de novo com: python regerar.py {p})")
    print(f"\ntudo ok em {(time.time() - t0) / 60:.1f} min")


if __name__ == "__main__":
    main()
