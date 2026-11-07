"""Pagina das novidades da R1.1 (imagens de render_novo.py embutidas).

  python render_novo.py && python novidades_html.py  ->  compacta/pagina/PICBOX_novidades_R1.1.html
"""
import base64
import io
from pathlib import Path

from PIL import Image

import layout as L

AQUI = Path(__file__).parent
IMG = AQUI / "saida" / "imagens_novo"


def jpg(nome):
    b = io.BytesIO()
    Image.open(IMG / nome).convert("RGB").save(b, "JPEG", quality=84, optimize=True)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()


CSS = """
:root{
  /* layout: coluna unica de fichas; cada ficha = imagem + onde/como/comprar */
  --bg:#f3f5f7; --papel:#ffffff; --tinta:#17202a; --suave:#5a6672; --linha:#d8dee4;
  --nova:#d6246e; --alt:#c98a06; --altfundo:#fff3d6; --novafundo:#fde6ef;
  --f-tit:"IBM Plex Sans Condensed",system-ui,sans-serif; --f-txt:"IBM Plex Sans",system-ui,sans-serif;
  --f-num:"IBM Plex Mono",ui-monospace,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#12171c; --papel:#1b2229; --tinta:#e6ebef; --suave:#9aa6b1; --linha:#2d3741;
  --nova:#ff5c9a; --alt:#f2b636; --altfundo:#3a2f12; --novafundo:#3d1a2a; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#12171c; --papel:#1b2229; --tinta:#e6ebef; --suave:#9aa6b1; --linha:#2d3741;
  --nova:#ff5c9a; --alt:#f2b636; --altfundo:#3a2f12; --novafundo:#3d1a2a; color-scheme:dark}
body{background:var(--bg);color:var(--tinta);font:15px/1.55 var(--f-txt);
  padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));padding-block:28px 56px}
main{max-width:980px;margin:0 auto;display:flex;flex-direction:column;gap:28px}
h1,h2{font-family:var(--f-tit);text-wrap:balance;margin:0;line-height:1.15}
h1{font-size:2rem;font-weight:600}
h2{font-size:1.35rem;font-weight:600}
p{margin:0;max-width:68ch}
.topo{display:flex;flex-direction:column;gap:10px}
.rev{font-family:var(--f-num);font-size:.8rem;letter-spacing:.06em;text-transform:uppercase;color:var(--suave)}
.legenda{display:flex;flex-wrap:wrap;gap:8px 18px;font-size:.9rem;color:var(--suave)}
.chip{display:inline-flex;align-items:center;gap:7px}
.chip i{width:14px;height:14px;border-radius:3px;display:inline-block}
.ficha{background:var(--papel);border:1px solid var(--linha);border-radius:10px;overflow:hidden}
.ficha figure{margin:0;background:#f4f6f4;border-bottom:1px solid var(--linha)}
.ficha img{display:block;width:100%;height:auto}
.corpo{padding:18px 20px 20px;display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px 28px}
.corpo>div{min-width:0;display:flex;flex-direction:column;gap:6px}
.corpo h2{grid-column:1/-1}
.rot{font-family:var(--f-num);font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;color:var(--suave)}
ul{margin:0;padding-left:1.1em;display:flex;flex-direction:column;gap:3px}
.tag{font-family:var(--f-num);font-size:.75rem;padding:1px 7px;border-radius:4px;white-space:nowrap}
.tag.n{background:var(--novafundo);color:var(--nova)} .tag.a{background:var(--altfundo);color:var(--alt)}
.tabela{overflow-x:auto;background:var(--papel);border:1px solid var(--linha);border-radius:10px}
table{border-collapse:collapse;width:100%;font-size:.92rem}
th,td{text-align:left;padding:9px 14px;border-bottom:1px solid var(--linha);vertical-align:top}
th{font-family:var(--f-num);font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;color:var(--suave);font-weight:500}
tr:last-child td{border-bottom:0}
td.num{font-family:var(--f-num);font-variant-numeric:tabular-nums;white-space:nowrap}
.semmuda{color:var(--suave)}
"""


def ficha(img, titulo, onde, como, compra):
    def lista(xs):
        return "<ul>" + "".join(f"<li>{x}</li>" for x in xs) + "</ul>"
    return f"""<section class="ficha"><figure><img src="{jpg(img)}" alt="{titulo}"></figure>
<div class="corpo"><h2>{titulo}</h2>
<div><span class="rot">Onde fica</span>{lista(onde)}</div>
<div><span class="rot">Como montar</span>{lista(como)}</div>
<div><span class="rot">Comprar / separar</span>{lista(compra)}</div></div></section>"""


def main():
    m = L.M()
    casa = f"{m.c_casa:.0f}".replace("-", "−")
    N = '<span class="tag n">nova</span>'
    A = '<span class="tag a">alterada</span>'
    fichas = [
        ficha("02_presilha.png", "Fixador de alumínio na presilha dos carros",
              ["Atrás de cada carro (A em cima, B embaixo), na altura da correia.",
               "O fixador fica em pé, na frente do ramo de trás da correia, com a face dentada encostada na face dentada da correia."],
              ["Encaixe a porca M3 por baixo, na fenda da presilha.", "Encoste as costas lisas da correia na parede da presilha e o fixador por cima, dentes nos dentes.",
               "As duas pontas da correia se encontram no meio: 20 mm de dente para cada ponta.",
               "Passe o M3x16 de frente pelo furo do meio do fixador, entre as pontas, e aperte firme. Faça isso com a tensora solta, afastando o ramo da frente com o dedo; depois estique na tensora."],
              ["2 fixadores GT2 de alumínio 40 × 9 × 5 (os da foto)", "2 M3x16 + 2 porcas M3"]),
        ficha("03_fim_de_curso.png", "Fim de curso dos eixos A e B",
              [f"No braço novo do bloco esquerdo, ao lado do motor. Um para cada eixo.",
               f"Casa (home) em X = {casa} mm: a face esquerda da presilha aperta a alavanca."],
              ["KW10 de lado no braço, alavanca virada para o carro.", "2 M2x12 por fim de curso.",
               "No firmware: homing no mínimo de X, devagar."],
              ["4 KW10 (2 nos eixos + 2 no elevador)", "8 M2x12"]),
        ficha("04_arruela.png", "Arruela de aço no ímã do carro A",
              ["Embaixo do eletroímã, dentro do copo impresso novo do carro A."],
              ["Cole a arruela na face do ímã (epóxi ou cola instantânea), centrada no copo.",
               "A bola para 0,6 mm abaixo da arruela. Ligando o ímã, ela sobe e encaixa 1,1 mm no furo, centrada.",
               "Quando chegar o eletroímã mais forte, ele entra no mesmo copo se tiver 20 mm de diâmetro."],
              ["1 arruela M10 lisa de AÇO comum (inox não gruda)"]),
        ficha("05_barreira_ir.png", "Barreira infravermelha no anel",
              ["Nos dois furos laterais do anel, um de frente para o outro."],
              ["Emissor de um lado, receptor do outro. Os furos não mudaram.",
               "Saída digital do receptor vai direto no microcontrolador: a bola corta o feixe e conta o acerto."],
              ["1 par de barreira IR 5 mm pronto (emissor + receptor com saída digital)"]),
    ]
    tabela = f"""<div class="tabela"><table>
<tr><th>Peça</th><th>Status</th><th>O que mudou</th><th>Impressora</th></tr>
<tr><td>Carro A</td><td>{A}</td><td>Presilha com parede de aperto e porca presa do fixador; copo do ímã; prateleira 2 mm mais alta (arruela)</td><td class="num">A · com suporte</td></tr>
<tr><td>Carro B</td><td>{A}</td><td>Presilha com parede de aperto e porca presa do fixador</td><td class="num">A</td></tr>
<tr><td>Anel</td><td>{A}</td><td>0,7 mm mais alto (bola 1,1 mm mais alta no ímã)</td><td class="num">A</td></tr>
<tr><td>Bloco esquerdo ×2</td><td>{A}</td><td>Braço para o fim de curso</td><td class="num">A</td></tr>
<tr><td>Fixador de correia ×2</td><td>{N}</td><td>Comprado, alumínio 40 × 9 × 5</td><td class="num">—</td></tr>
<tr><td>Arruela M10 de aço</td><td>{N}</td><td>Comprada</td><td class="num">—</td></tr>
<tr><td>Fim de curso KW10 ×4</td><td>{N}</td><td>2 nos eixos (novos) + 2 no elevador</td><td class="num">—</td></tr>
<tr><td>Barreira IR 5 mm</td><td>{N}</td><td>Par pronto no lugar do LED solto</td><td class="num">—</td></tr>
<tr class="semmuda"><td>Elevador</td><td>sem mudança</td><td>Continua com as presilhas dentadas impressas na cabine e KW10 embaixo e em cima</td><td class="num">—</td></tr>
</table></div>"""
    html = f"""<title>PICBOX R1.1 novidades</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans+Condensed:wght@600&family=IBM+Plex+Sans:wght@400;600&display=swap">
<style>{CSS}</style>
<main>
<header class="topo"><span class="rev">PICBOX compacta · revisão R1.1</span>
<h1>Onde fica cada coisa nova</h1>
<p>Correia presa com fixador de alumínio, fim de curso nos dois eixos, arruela de aço no ímã e barreira infravermelha pronta no anel. Todas as checagens passaram: 0 interferências, 128 de 128 parafusos com acesso, varredura dos dois eixos limpa.</p>
<div class="legenda"><span class="chip"><i style="background:#d6246e"></i>comprada nova</span>
<span class="chip"><i style="background:#f2a516"></i>impressa alterada</span>
<span class="chip"><i style="background:#c9d0d6"></i>sem mudança</span></div></header>
<section class="ficha"><figure><img src="{jpg('01_onde_fica.png')}" alt="Máquina inteira com as novidades destacadas"></figure></section>
{tabela}
{''.join(fichas)}
</main>"""
    for p in (AQUI / "saida" / "novidades.html", AQUI.parents[1] / "pagina" / "PICBOX_novidades_R1.1.html"):
        p.write_text(html, encoding="utf8")
    print("ok", len(html) // 1024, "KB")


if __name__ == "__main__":
    main()
