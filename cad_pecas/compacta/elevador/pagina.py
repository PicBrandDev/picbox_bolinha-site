"""Gera a pagina 3D de validacao a partir de cena*.json e validacao*.json (rode montagem.py antes).

  python pagina.py SAIDA.html [mgn9|eixos]
"""
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent

POLIA = ("<b>Polia:</b> as presilhas ficam na cabine, e a cabine nunca chega a menos de 0,5 mm das polias em todo o "
         "curso. Por elas passa so correia.")
COMPORTA = ("<b>Comporta:</b> a versao passiva com contrapeso foi reprovada na checagem, porque a bola seguinte avancava "
            "antes de a lamina subir. Com servo, a lamina sobe antes de a cabine sair.")
CORREIA = ("Prenda uma ponta na presilha de baixo. Passe pela polia de baixo, suba pelo lado livre, contorne a polia do "
           "motor e prenda na presilha de cima. A tensao se da na presilha de cima.")
BANCADA = ("Fila, suporte do servo com o braco e rampa vao na bancada. Ajuste a lamina pelos furos oblongos ate ela ficar "
           "entre as duas bolas.")

TXT = {
    "mgn9": dict(
        sobre="PICBOX compacta · elevador R0.2 · trilho MGN9 · validacao de montagem · 03/11/2026",
        lead="Uma cabine sobe e desce num trilho MGN9 levando uma bola por vez. A correia é aberta e as duas pontas ficam "
             "presas na cabine, então nada rigido passa pelas polias. Embaixo, uma lamina movida por servo libera uma bola "
             "de cada vez. Todas as pecas, parafusos e movimentos abaixo foram checados por programa, no mesmo modelo que "
             "aparece em 3D.",
        guia_tit="Cabine num trilho entrou",
        guia_itens=[POLIA, "<b>Trilho:</b> o patim fica sempre com pelo menos 3 mm de trilho sobrando. Nem batendo no topo "
                    "ele sai do trilho.", COMPORTA],
        guia_min=3, guia_chip="Patim: trilho sobrando embaixo / em cima", guia_linha="Trilho sobrando embaixo / em cima",
        compras="Compras que mudam com esta versao:<br>Entram: trilho MGN9 cortado em 380 mm com patim MGN9H, N20 com "
                "encoder, servo MG90S, 1 m de correia GT2 6 mm aberta e cerca de 40 insertos M3.<br>Sai: a correia "
                "fechada de 760 mm.",
        etapas=[
            ["Base e espinha", "As duas espinhas assentam na base. Entram 2 M3x12 por baixo, em insertos na espinha de baixo.", [0, 0, 0]],
            ["Trilho com patim", "Trilho MGN9 de 380 mm, ja com o patim, preso por 19 M3x10 pela frente em insertos. Deslize o patim para alcancar cada furo.", [0, -1, 0]],
            ["Cabine", "Entram 4 M3x6 pela frente nos furos roscados do patim. A chave passa pelos furos de acesso no fundo do berco.", [0, -1, 0]],
            ["Polia de baixo", "Um M3x35 entra por tras da espinha e passa pelo espacador e pela polia, com porca autotravante na frente.", [0, 1, 0]],
            ["Motor no topo", "O suporte abraca o N20 e entra no topo da espinha com 2 M3x12 de cima. A polia vai no eixo, com o parafuso sem cabeca no lado chato.", [0, 0, 1]],
            ["Correia", CORREIA, [0, 0, 0]],
            ["Tubo", "O tubo de baixo e o de cima entram pela frente. Cada um leva 4 M3x8 de cabeca chata pelas laterais, na espinha.", [0, -1, 0]],
            ["Fila, comporta e rampa", BANCADA, [-1, 0, 0]],
        ]),
    "eixos": dict(
        sobre="PICBOX compacta · elevador R0.3 · versao barata com eixos de 8 mm · validacao de montagem · 03/11/2026",
        lead="Uma cabine sobe e desce em dois eixos de 8 mm, correndo em dois rolamentos LM8UU, levando uma bola por vez. "
             "A correia é aberta e as duas pontas ficam presas na cabine, então nada rigido passa pelas polias. Embaixo, uma "
             "lamina movida por servo libera uma bola de cada vez. Todas as pecas, parafusos e movimentos abaixo foram "
             "checados por programa, no mesmo modelo que aparece em 3D.",
        guia_tit="Cabine em dois eixos de 8 mm (versao barata)",
        guia_itens=[POLIA,
                    "<b>Eixos:</b> dois eixos de 8 x 400 mm, sem cortar, presos num pe embaixo e numa cabeca em cima. A "
                    "cabine para 1 mm acima do pe no fundo e 1,1 mm abaixo da cabeca no topo; a cabeca serve de batente "
                    "de cima.",
                    "<b>Sem espinha:</b> pe, eixos, cabeca, suporte do motor e tubo formam a estrutura. Sao 13 parafusos, "
                    "contra 36 da versao com trilho.",
                    COMPORTA],
        guia_min=1, guia_chip="Cabine ate o pe / ate a cabeca", guia_linha="Cabine ate o pe (fundo) / ate a cabeca (topo)",
        compras="Versao mais barata:<br>Entram: 2 eixos retificados de 8 x 400 mm, 2 rolamentos LM8UU, N20 sem encoder "
                "(a posicao vem dos sensores TCRT5000 e do batente), servo SG90, 1 m de correia GT2 6 mm aberta e "
                "cerca de 10 insertos M3.<br>Saem: o trilho MGN9 com patim, o N20 com encoder e a correia fechada de 760 mm.",
        etapas=[
            ["Base e pe dos eixos", "O pe assenta na base e leva 2 M3x12 por baixo, em insertos.", [0, 0, 0]],
            ["Eixos com a cabine", "Prense os 2 LM8UU na cabine. Passe a cabine nos eixos e encaixe os eixos no pe; trave cada um com um parafuso sem cabeca M3 por tras.", [0, 0, 1]],
            ["Cabeca dos eixos", "Encaixe a cabeca no topo dos eixos. Antes de travar, corra a cabine de ponta a ponta para os eixos ficarem paralelos.", [0, 0, 1]],
            ["Polia de baixo", "Um M3x35 entra por tras do pe e passa pelo espacador e pela polia, com porca autotravante na frente.", [0, 1, 0]],
            ["Motor no topo", "O suporte abraca o N20 e prende na cabeca dos eixos com 2 M3x25 de cima. A polia vai no eixo do motor.", [0, 0, 1]],
            ["Correia", CORREIA, [0, 0, 0]],
            ["Tubo", "O tubo de baixo entra pela frente e prende na base com 2 M3x8 na aba. O de cima encaixa nele por 2 pinos e prende no suporte do motor com 2 M3x12.", [0, -1, 0]],
            ["Fila, comporta e rampa", BANCADA, [-1, 0, 0]],
        ]),
    "impressa": dict(
        sobre="PICBOX compacta \u00b7 elevador R0.6 \u00b7 guia impressa, reforcada \u00b7 para aprovar \u00b7 04/11/2026",
        lead="Uma cabine sobe e desce numa guia impressa: dois trilhos em T que saem da mesma peca do pe e da cabeca, e a "
             "cabine abraca cada trilho com um alojamento em C. Nao tem trilho nem eixo comprado. A correia é aberta e as duas "
             "pontas ficam presas na cabine, então nada rigido passa pelas polias. Embaixo, uma lamina movida por servo libera "
             "uma bola de cada vez. Todas as pecas, parafusos e movimentos abaixo foram checados por programa, no mesmo modelo "
             "que aparece em 3D.",
        guia_tit="Guia impressa em T (versao sem trilho comprado)",
        guia_itens=[POLIA,
                    "<b>Guia:</b> 2 trilhos em T de 8 mm, impressos em 2 pecas (195 e 210 mm) junto com o pe e a cabeca. O C da "
                    "cabine tem 0,5 mm de folga por lado e 40 mm de altura.",
                    "<b>Atrito:</b> para subir, a cabine pede 1,0 N com PETG lubrificado e 1,3 N com PETG seco. O motor dá 8 N. "
                    "O indice de travamento (efeito gaveta) fica entre 0,11 e 0,35; trava so a partir de 1.",
                    "<b>Folga:</b> os pesos ficam na frente da guia, então a cabine sempre encosta do mesmo lado. O piso "
                    "do berco fica no maximo 1,3 mm mais baixo na frente, dentro das tolerancias testadas na comporta.",
                    "<b>Fins de curso:</b> 2 microchaves, uma num rebaixo do pe e outra na cabeca. O C da cabine aperta a "
                    "alavanca no fundo e no topo. A altura de espera e por tempo, calibrado a cada subida completa, 20 mm "
                    "abaixo do topo; um erro de 6 mm ainda deixa a bola presa.",
                    COMPORTA],
        guia_min=1, guia_chip="Cabine ate o pe / ate a cabeca", guia_linha="Cabine ate o pe (fundo) / ate a cabeca (topo)",
        compras="Compras desta versao (o que esta no seu carrinho):<br>8 bolas de aco de 1 pol, eletroima P20/15 12 V, motor "
                "N20 12 V 100 rpm, polia GT2 20 dentes furo 5 mm (com bucha impressa para o eixo de 3 mm), polia tensora GT2 "
                "20 dentes furo 5 mm (com calco impresso para o M3), 1 m de correia GT2 6 mm aberta, ponte H L9110S, MOSFET "
                "IRLZ44N e diodo 1N4007.<br>Ja tem: servo SG90, fins de curso, parafusos (confira: 1 M3x40, 4 M2x12, 3 de madeira "
                "3,5x16), filamento.<br>Nao precisa: trilho, "
                "eixos, rolamentos lineares, insertos (o M3 rosqueia direto no PETG).",
        etapas=[
            ["Base e guia de baixo", "Na bancada: aparafuse o fim de curso de baixo no rebaixo do pe com 2 M2x12 de lado e "
             "ponha a porca M3 no rasgo da bochecha da base. A guia de baixo (pe + 2 trilhos em T) assenta na base e leva 2 M3x12 "
             "por baixo. Leve ao gabinete e prenda a base no piso com 2 parafusos de madeira 3,5x16 na frente.", [0, 0, 0]],
            ["Cabine", "Passe um pouco de vaselina ou grafite nos trilhos. Encaixe a cabine pelo topo da guia de baixo; os dois C "
             "abracam os trilhos em T.", [0, 0, 1]],
            ["Guia de cima", "Na bancada, aparafuse o fim de curso de cima no rebaixo da cabeca (2 M2x12). Encaixe a guia de cima na de baixo "
             "pelos 2 pinos impressos e lixe a emenda ate a cabine passar sem degrau.", [0, 0, 1]],
            ["Polia de baixo", "Um M3x40 entra por tras do pe e passa pelo espacador, pelo calco dentro do rolamento da tensora "
             "de 5 mm e pela polia, e rosqueia na porca presa na bochecha. Para esticar a correia, empurre a polia para baixo no "
             "rasgo de 2 mm e aperte.", [0, 1, 0]],
            ["Motor no topo", "O suporte abraca o N20 e prende no topo da guia de cima com 2 M3x16 de cima. Ele tambem segura as "
             "duas guias juntas. A polia de 5 mm entra no eixo de 3 mm com a bucha impressa. A orelha da frente leva 1 parafuso "
             "de madeira 3,5x16 na parede direita do gabinete.", [0, 0, 1]],
            ["Correia", CORREIA, [0, 0, 0]],
            ["Tubo", "O tubo de baixo entra pela frente e prende na base com 2 M3x10 na aba. O de cima encaixa nele por 2 pinos e "
             "prende no suporte do motor com 2 M3x12.", [0, -1, 0]],
            ["Fila, comporta e rampa", BANCADA, [-1, 0, 0]],
        ]),
}


REFORCOS = [
    "<b>Polia de baixo:</b> a polia de 18 mm entrava 1,5 mm na base. A base ganhou uma janela embaixo dela.",
    "<b>Esticador:</b> o furo do parafuso da polia virou rasgo de 2 mm no pe e na bochecha. Testado nas duas pontas do rasgo, sem folga ruim.",
    "<b>Coluna:</b> 419 mm presa so na base balancava 8 mm com um esbarrao de 10 N, e a emenda abria. O suporte do motor "
    "ganhou uma orelha com 1 parafuso de madeira na parede direita do gabinete; com ela o balanco cai para 0,5 mm.",
    "<b>Batente:</b> passou de 2,5 para 3 mm, mais comprido, e ganhou um reforco de lado.",
    "<b>Fila:</b> entrava 0,5 mm no canto da base; ganhou um recorte.",
    "<b>Fins de curso:</b> M2x12 no lugar do M2x10 para pegar 4,5 mm. Aparafuse-os na bancada: no gabinete, a parede tapa a chave.",
    "<b>Tubo na base:</b> M3x10 no lugar do M3x8, para pegar 5 mm no PETG.",
]


ACENTOS = {"berco": "berço", "cabeca": "cabeça", "Cabeca": "Cabeça", "pe": "pé", "Pe": "Pé", "lamina": "lâmina",
           "Braco": "Braço", "braco": "braço", "espacador": "espaçador", "Espacador": "Espaçador", "posicao": "posição",
           "tensao": "tensão", "abracado": "abraçado", "abraca": "abraça", "abracadeira": "abraçadeira", "reducao": "redução",
           "nao": "não", "ate": "até", "so": "só", "tras": "trás", "ja": "já", "metalica": "metálica", "proprio": "próprio",
           "maquina": "máquina", "peca": "peça", "tambem": "também", "indice": "índice", "maximo": "máximo", "tolerancias": "tolerâncias", "abracam": "abraçam", "ja": "já", "esta": "está", "calco": "calço", "eletroima": "eletroímã", "aco": "aço", "microchaves": "microchaves", "subida": "subida", "rebaixo": "rebaixo", "Nao": "Não", "sairem": "saírem", "travamento": "travamento", "pes": "pés", "Sao": "São", "versao": "versão", "validacao": "validação", "pecas": "peças",
           "rigido": "rígido", "Calco": "Calço", "reforcada": "reforçada", "reforco": "reforço", "balanco": "balanço", "esbarrao": "esbarrão", "flambagem": "flambagem", "camadas": "camadas", "camada": "camada", "fluencia": "fluência", "aco": "aço", "pescoco": "pescoço", "bochecha": "bochecha", "presilha": "presilha", "abracadeira": "abraçadeira", "pendulo": "pêndulo", "minimo": "mínimo", "rosqueia": "rosqueia", "diagonal": "diagonal", "cabeca": "cabeça", "tempo-limite": "tempo-limite", "ultimos": "últimos", "programa": "programa", "deitada": "deitada", "impressao": "impressão", "aparafuse": "aparafuse", "orelha": "orelha", "nervuras": "nervuras", "rasgo": "rasgo", "porca": "porca", "avancava": "avançava", "alcancar": "alcançar", "vao": "vão", "da": "dá", "vao": "vão",
           "Eixos 8 mm": "Eixos 8 mm"}
NAO_MEXER = {"a", "b", "n", "nome", "c", "t", "cor"}


def acentuar(v, chave=None):
    import re
    if isinstance(v, str):
        if chave in NAO_MEXER:
            return v
        v = re.sub(r"\bse da\b", "se dá", v)
        return re.sub(r"\b(" + "|".join(k for k in ACENTOS if k != "da") + r")\b", lambda m: ACENTOS[m.group(1)], v)
    if isinstance(v, list):
        return [acentuar(x, chave) for x in v]
    if isinstance(v, dict):
        return {acentuar(k) if chave == "pecas" or chave == "casos" else k: acentuar(x, k) for k, x in v.items()}
    return v


def main(saida, guia="mgn9"):
    suf = "" if guia == "mgn9" else "_" + guia
    cena = json.loads((AQUI / f"cena{suf}.json").read_text(encoding="utf8"))
    val = json.loads((AQUI / f"validacao{suf}.json").read_text(encoding="utf8"))
    cena["p"]["ang_baixa"] = 7.5
    html = (AQUI / "pagina_modelo.html").read_text(encoding="utf8")
    cena, val, txt = acentuar(cena), acentuar(val), acentuar(TXT[guia])
    arq = AQUI / "resistencia.json"
    res = json.loads(arq.read_text(encoding="utf8")) if guia == "impressa" and arq.exists() else None
    if res:
        res["reforcos"] = REFORCOS
        res = acentuar(res)
    for k, v in (("__CENA__", cena), ("__VAL__", val), ("__TXT__", txt), ("__RES__", res)):
        html = html.replace(k, json.dumps(v, ensure_ascii=False))
    Path(saida).write_text(html, encoding="utf8")
    print(saida, len(html))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "mgn9")
