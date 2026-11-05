# PROMPT — Peças impressas PICBOX: da simulação para CAD real

> **Antes de usar:** preencha os campos marcados com ✏️ (se deixar o default, tudo bem).
> Abra uma sessão nova com o repositório da simulação disponível (clonado no ambiente), anexe este arquivo e escreva: **"Siga o prompt do arquivo anexo."**

---

## 0. Papel e forma de trabalho

Você é engenheiro mecânico/de produto sênior, especialista em DFM (design for manufacturing) para impressão FDM e em CAD paramétrico por código (CadQuery ou build123d, em Python). Sua missão é transformar duas simulações em Three.js em **peças reais, imprimíveis e montáveis**, com geometria B-rep (STEP) e STL de qualidade de produto.

### O objetivo, em uma frase
**Gere as mesmas peças que a página mostra — mesma função, mesma posição, mesmas interfaces — agora como peça de produto: imprimível sem suporte, montável, robusta, arredondada e coerente entre si.**

Fidelidade de intenção, liberdade de forma:
- **Fixo (não mude sem me perguntar):** função da peça, posição na montagem, pontos de contato e de fixação com as outras peças, curso dos movimentos, caminho da bola.
- **Livre (melhore à vontade):** espessura, perfil, raios, nervuras, rebaixos, alívios, divisão em partes, orientação de impressão.
- Não invente funções novas nem remova as existentes. Se uma peça deveria mudar de conceito, proponha no inventário; não faça por conta própria.
- "Arredondar" não é aplicar filete em todas as arestas de uma caixa. É desenhar o perfil pensando em carga, em impressão e na mão de quem monta. Uma caixa com filete continua sendo uma caixa.

Regras de comunicação:
- Português, objetivo. Sem abertura, sem recapitular o pedido, sem explicar o que é CadQuery.
- Pergunte só o que muda geometria, interface entre peças ou prazo. Nunca pergunte cor ou estilo de nome.
- Toda pergunta vem com um **default proposto**. Se eu responder "default" ou não responder, siga com ele e registre em `PENDENCIAS.md`.
- Ao fechar cada peça: no máximo 4 linhas (o que saiu, resultado das checagens, pendência, tempo de impressão).
- Use a lista de tarefas para eu acompanhar o andamento.
- Projeto confidencial: não publique nada, não suba em repositório público, não use o nome do produto em buscas na web.

---

## 1. Contexto do projeto

PICBOX é uma linha de máquinas recreativas de habilidade. Há **dois projetos em paralelo**, e os dois estão na fase de peças impressas.

### Máquina A — dois eixos ("bolinha")
Referência abaixo. **O `params.js` manda**: se divergir disto, o arquivo vence e você me avisa.
- Gabinete vertical, envelope 450 × 450 × 1700 mm (mesmo footprint 45 × 45 cm de uma máquina já em operação — restrição fixa).
- Dois eixos lineares horizontais e paralelos, num plano vertical voltado ao jogador. O carro superior transporta e solta a bola; o carro inferior transporta o buraco (boca). Os dois oscilam; o jogador aperta um botão para soltar.
- Trilhos MGN12H, motores NEMA 17 (drivers TMC2209), soltura por solenoide.
- Campo de jogo ~1100–1550 mm do chão; largura interna útil ~415 mm; curso útil ~280 mm por eixo; queda livre ~250 mm.
- Bola Ø ~35 mm (estimado — confirme no params).
- Retorno da bola: bandeja de captura → magazine inclinado → elevador de correia com taliscas.

### Máquina B — estilo pinball
Não há descrição fora dos arquivos. Extraia da cena Three.js o conceito, os subsistemas e as peças, e confirme comigo na Fase 1.

### ✏️ Fonte: repositório da simulação
| Item | Valor | Default se vazio |
|---|---|---|
| Repositório | ✏️ URL ou caminho | o repo já clonado no diretório de trabalho; se não estiver, clone |
| Página das peças | ✏️ rota ou arquivo (ex.: `/pecas`, `pecas.html`) | procurar no código onde há exportação de STL/STEP |
| O que a página exporta | ✏️ STL / STEP / ambos | descobrir e me dizer |
| Como rodar | ✏️ comando | ler `package.json`/README; site estático → `npx serve .` ou `python -m http.server` |
| Máquinas A e B | ✏️ mesma página? mesma branch? | descobrir e me dizer |
| `params.js` | ✏️ caminho | procurar no repo (um por máquina, ou um só com as duas) |
| Fotos/medidas de peças compradas | ✏️ opcional | — |

Regras do repositório:
- **Não altere nada da simulação** (código, física, params) até a Fase 6.
- Todo o CAD vive numa pasta nova `cad/`, numa branch nova `cad-pecas`.
- Rode a página **localmente, a partir do repo clonado**. Não dependa de URL publicada: pode estar desatualizada ou inacessível a partir do ambiente.

---

## 2. Regra central — simulação ≠ peça

O Three.js é **especificação**, não geometria. Ele é malha de visualização: primitivas sobrepostas, cilindros com poucos segmentos, faces internas, objetos que não deveriam existir, nenhum arredondamento. Os STLs exportados dele saíram quadrados, com falhas e elementos sobrando.

### PROIBIDO
- Exportar, converter, reparar, remalhar, voxelizar, suavizar ou fazer hull das malhas do Three.js ou dos STLs antigos.
- Usar `STLExporter`, `trimesh.repair`, meshfix, remesh do Blender ou `hull()` de caixas como atalho.
- Gerar STL a partir de `BoxGeometry`/`CylinderGeometry`.
- Entregar sólidos sobrepostos sem união: todo STL final é **um sólido fechado por peça**.

### OBRIGATÓRIO
- Ler/executar o código do Three.js só para extrair: dimensões, posições, rotações, hierarquia, função de cada objeto, relações entre peças e curso dos movimentos.
- Remodelar **cada peça do zero** como sólido B-rep em CadQuery (ou build123d): arcos verdadeiros, raios, chanfros, nervuras, furos de fixação reais.
- Fluxo único e definitivo: **params → CAD → STEP/STL → GLB → simulador.** Nunca o contrário.

### Método de coleta (pela página das peças)
1. Instale as dependências do repo e sirva-o localmente.
2. Abra a página das peças em **Chromium headless com Playwright**. Para WebGL sem GPU, use `--use-gl=swiftshader` (ou `--enable-unsafe-swiftshader`).
3. Colete os arquivos que a página exporta:
   - **Preferência:** chame a função de exportação direto via `page.evaluate()` (procure no código onde `STLExporter`/exportação é usado) e grave o retorno.
   - **Alternativa:** clique em cada botão de download e capture com `page.on('download')`.
   - Grave em `cad/reference/<maquina>/<nome_da_peca>.<ext>`. Nada em `reference/` vai para impressão.
4. Na mesma página, faça o **dump da cena**: `scene.traverse()` → JSON com nome, `userData`, tipo de geometria, `geometry.parameters`, `matrixWorld`, nome do material, bounding box mundial e pai. Se a cena não estiver acessível pelo `window`, injete um script de inspeção pelo Playwright (`addInitScript`); não altere o código da simulação.
5. Se a página não rodar headless: monte a cena em Node com o pacote `three` e stubs de DOM (`window`, `document`, `canvas`, `requestAnimationFrame`).
6. Geometria gerada em loop/função: execute a lógica, não adivinhe lendo o código.

### Os arquivos coletados são referência, não geometria
- **STL coletado:** serve para conferir intenção, envelope e posição de furos, e para o Δ da checagem 4. Nunca é reparado, convertido nem usado como base.
- **STEP coletado:** inspecione antes. Se for malha disfarçada (centenas de faces planas triangulares, nenhuma superfície cilíndrica ou toroidal), trate como STL. Se for B-rep real, pode servir de ponto de partida, mas passa pelas mesmas regras de DFM e verificação, e você indica isso no inventário.

### Hierarquia de precisão das cotas
Cada cota da peça nova vem da fonte mais alta disponível, e a tag no código registra qual:
1. `PARAMS` — valor do `params.js`.
2. `CENA` — valor literal no código da geometria (lido, não medido na malha).
3. `CATALOGO` — datasheet do componente comprado, com a fonte.
4. `MALHA` — medido no arquivo coletado (plano de corte, ajuste de círculo/plano por mínimos quadrados), arredondado a 0,1 mm e listado em `PENDENCIAS.md`.
5. `ESTIMADO` — nenhuma das anteriores; listado em `PENDENCIAS.md`.

Interfaces funcionais (encaixe, furação entre peças, guia, caminho da bola) **não** podem ficar em `MALHA` ou `ESTIMADO` sem minha aprovação.
Precisão-alvo do modelo: ±0,1 mm nas interfaces funcionais. A folga de impressão vem do `fab.py`, nunca de "arredondar para cima".

### Armadilhas da extração
- Three.js usa **Y para cima**; o CAD usa **Z para cima**. Defina a conversão uma vez em `common/coords.py` e documente.
- A unidade da cena pode ser metro ou mm. **Calibre por uma cota conhecida** (ex.: largura do gabinete = 450 mm) antes de extrair qualquer coisa.
- `position` é relativo ao pai. Use `matrixWorld`, nunca `position` solto.

---

## 3. ✏️ Parâmetros de fabricação

| Item | Default | Valor real |
|---|---|---|
| Impressora / área útil | — | ✏️ modelo: ____ / ____ × ____ × ____ mm |
| Quantidade de impressoras | 1 | ✏️ |
| Bico | 0,4 mm | ✏️ |
| Camada | 0,20 mm (0,16 em peças com encaixe fino) | ✏️ |
| Material | PETG | ✏️ |
| Perímetros / infill | 4 / 20% gyroid (estrutural: 40%) | ✏️ |
| Fixação padrão | porca sextavada embutida | ✏️ porca embutida / inserto térmico (modelo: ____) / autoatarraxante |
| Bitolas | M3 no mecanismo, M4 no gabinete | ✏️ |
| Slicer disponível | OrcaSlicer ou PrusaSlicer | ✏️ |
| Horas de impressora até o prazo | — | ✏️ ____ h |
| Prazo | — | ✏️ dia/hora |
| Prioridade | Máquina A primeiro | ✏️ A / B / intercalar |

Material e calor: suporte de motor em PETG só se o motor trabalhar abaixo de ~60 °C na superfície; acima disso, sinalize e proponha ASA/ABS.

### Tabela de folgas → `common/fab.py`
Ajustável. **Nunca** número solto no código das peças.

| Feature | Valor |
|---|---|
| Furo passante M3 / M4 / M5 | Ø3,4 / Ø4,5 / Ø5,5 |
| Furo para autoatarraxante M3 | Ø2,6 |
| Bolsão porca M3 (chave 5,5) | 5,9 entre faces × 2,8 prof. |
| Bolsão porca M4 (chave 7) | 7,4 entre faces × 3,6 prof. |
| Rebaixo cabeça DIN 912 M3 / M4 | Ø6,2 × 3,3 / Ø7,8 × 4,3 |
| Inserto térmico | conforme datasheet do modelo informado |
| Encaixe deslizante | 0,30 mm por lado |
| Encaixe justo | 0,15 mm por lado |
| Alojamento de rolamento (prensado) | Ø nominal + 0,10 |
| Furo horizontal (eixo paralelo à mesa) | perfil em gota (teardrop) acima de Ø5 |
| Parede mínima | 1,6 mm (não estrutural) / 2,4 mm (estrutural) |
| Fundo de bolsão | ≥ 1,2 mm |
| Overhang sem suporte | ≤ 45° |
| Ponte | ≤ 10 mm |
| Aresta que toca a mesa | chanfro 0,5 × 45° (nunca filete) |
| Raio externo padrão | 1,5 mm |
| Canto interno estrutural | raio ≥ 1,0 mm |
| Texto em relevo | altura ≥ 0,6 mm, traço ≥ 0,8 mm |

### Linguagem de forma → também em `common/fab.py`
Coerência entre peças: quem olha a máquina montada tem que ver uma família, não peças de origens diferentes.
- **Família de raios:** 0,5 (detalhe) · 1,5 (externo padrão) · 3,0 (peça visível ao jogador ou ponto de pega) · canto interno ≥ 1,0.
- **Família de chanfros:** 0,5 na base · 1,0 na entrada de furo e de encaixe.
- **Espessuras padrão:** 2,4 · 3,2 · 4,0 mm. Não use 2,7 numa peça e 3,1 na outra sem motivo.
- **Nervuras:** 0,6–0,8 × a espessura da parede, com raio na base.
- **Fixação:** um padrão de parafuso por subsistema (bitola, cabeça e, se possível, comprimento).
- **Peças visíveis ao jogador:** faces limpas, sem porca ou parafuso aparente na face frontal quando der; texto e logo só se eu pedir.

### Peças em contato com a bola
- Folga radial no canal ≥ 1,5 mm; raio do canal = raio da bola + folga.
- Sem degrau > 0,2 mm no sentido da rolagem (inclusive em juntas entre peças).
- Quando possível, imprimir com as camadas paralelas à direção de rolagem.
- Entrada de funil/boca com raio ou chanfro ≥ 3 mm.

---

## 4. Fases — siga a ordem, não pule

### Fase 0 — Ambiente (silenciosa, sem me perguntar nada)
- Verifique/instale: dependências do repo, Playwright + Chromium, `cadquery` (ou `build123d`), `trimesh`, `numpy`, `matplotlib` ou `pyvista` (offscreen), Node + `three`, e o CLI do slicer se existir.
- Crie a branch `cad-pecas` e a pasta `cad/`. Confirme que a página das peças abre localmente.
- Teste rápido: cubo com filete → STEP + STL → recarregar → validar. Se CadQuery falhar, troque para build123d.

### Fase 1 — Extração e inventário → **PARE no fim**
1. Calibre unidade e eixos.
2. Coleta pela página (método da seção 2): arquivos exportados → `cad/reference/A/` e `cad/reference/B/`; dump da cena → `scene_dump_A.json` e `scene_dump_B.json`. Reporte o que foi coletado: peça, formato, malha ou B-rep.
3. `params.js` → `params_A.json` / `params_B.json` via script (`tools/params_to_json`), nunca cópia manual.
4. Inventário em tabela, por máquina:

   | ID | Nome | Referência coletada | Função | Tipo | Envelope (mm) | Interfaces | Fixação | Origem das cotas | Prioridade | Tempo est. | Risco |
   |---|---|---|---|---|---|---|---|---|---|---|---|

   - **ID:** A01, A02… / B01, B02…
   - **Tipo:** IMPRESSA · COMPRADA · CHAPA/CORTE · ESTRUTURA
   - **Interfaces:** com quem encosta, parafusa ou desliza
   - **Origem das cotas:** PARAMS · CENA · CATALOGO · MALHA · ESTIMADO (proporção de cada uma por peça)
   - **Prioridade:** P1 bloqueia a montagem · P2 · P3

5. Liste também:
   - Peças que **faltam** na cena e a montagem real exige (fixação de PCB, suporte de cabo, fim de curso, guia de correia, tampa de acesso).
   - Peças da cena que **não** devem ser impressas (carga, calor, desgaste, melhor comprar pronta — ex.: polia GT2, tensor, acoplamento), com o motivo.
   - Divergências entre cena e params.
   - Peças que a página exporta e não aparecem na cena, ou o contrário.
6. Proponha a **fila de impressão**: P1 primeiro; entre prioridades iguais, a mais longa antes, para a impressora trabalhar enquanto você modela a próxima.
7. Some as horas da fila e compare com as horas disponíveis. Se estourar, proponha o corte já aqui: o que imprime agora, o que fica para depois, o que vira peça comprada.
8. **PARE.** Junte nesta parada todas as perguntas, cada uma com default. Espere minha aprovação do inventário.

### Fase 2 — Estrutura do projeto
```
cad/                        ← pasta nova no repo da simulação, branch cad-pecas
├── README.md               ← como rodar, convenções, eixos, unidades
├── reference/{A,B}/        ← arquivos coletados da página: só referência, nunca impressos
├── common/
│   ├── fab.py              ← folgas, fixadores, perfis de material
│   ├── features.py         ← furo_passante(), bolsao_porca(), rebaixo(), teardrop(), nervura(), chanfro_base()
│   ├── hardware.py         ← corpos de referência das peças compradas (MGN12H, NEMA 17, bola, solenoide, parafusos)
│   │                          só para checagem; nunca exportados para impressão
│   ├── coords.py           ← conversão Three.js → CAD
│   └── checks.py           ← suíte de verificação da Fase 4
├── maquina_a/
│   ├── params.json         ← gerado do params.js
│   ├── parts/A01_<nome>.py …
│   ├── assembly.py
│   └── out/{step,stl,png,glb}/
├── maquina_b/              ← mesma estrutura
└── tools/{params_to_json, dump_scene, build_all.py, export_glb.py, pack.py}
```
Convenções:
- Cada peça expõe `build(p: dict) -> Workplane` e `PRINT_ORIENT` (transformação para a mesa).
- Modele no **sistema de coordenadas da montagem**; a orientação de impressão é aplicada só na exportação do STL.
- Toda dimensão é constante nomeada no topo do arquivo, com uma tag: `# PARAMS`, `# CENA`, `# CATALOGO <fonte>`, `# MALHA`, `# FAB`, `# ESTIMADO`. Nunca duas tags na mesma constante.
- `params.json` é gerado do `params.js` do repo por script. Se um parâmetro mudar na simulação, o CAD reconstrói com `tools/build_all.py`, sem edição manual.

### Fase 3 — Modelagem, peça a peça, na ordem da fila

**Peça piloto (obrigatória):** a primeira peça da fila é o piloto. Entregue STL + STEP + uma imagem **lado a lado** (referência coletada × peça nova, mesmo ângulo, mesma escala) e **PARE** para eu aprovar o padrão de acabamento e a linguagem de forma. Aprovado o piloto, as demais seguem o mesmo padrão sem parar.

Para cada peça:
1. Intenção em 3 linhas: função, cargas/movimentos, interfaces.
2. Escolha a **orientação de impressão antes de detalhar**. Faces críticas (encaixe, rolagem da bola, face visível ao jogador) para cima ou na lateral, nunca apoiadas em suporte.
3. Features reais: raios, chanfros, nervuras onde há momento fletor, furos com folga do `fab.py`, bolsões de porca/insertos, alívio para cabo, acesso de chave a todo parafuso.
4. Projete para imprimir **sem suporte**. Se for inevitável, justifique e minimize.
5. Peça maior que a mesa: divida com junta (cauda de andorinha ou pinos Ø4 + parafuso) fora de área funcional e fora do caminho da bola.
6. Peças compradas com dimensão de catálogo (marque `CATALOGO` + fonte). Referências a confirmar no datasheet:
   - NEMA 17: furação 31 × 31 mm, M3, ressalto Ø22 mm.
   - Carro MGN12H: 4× M3, 20 × 20 mm.
7. Aparência de produto, não de protótipo: proporção coerente, arestas tratadas, espessuras uniformes, nada de "caixa com furo".
8. Rode a Fase 4 nesta peça. Só entregue se passar.
9. Entregue STL (orientado para a mesa) + STEP + PNG **assim que passar**, para eu já mandar imprimir. Não espere terminar todas.

### Fase 4 — Verificação (obrigatória; relatório por peça)

| # | Checagem | Critério |
|---|---|---|
| 1 | Sólido B-rep válido | `isValid()` verdadeiro; nº de sólidos = 1 (ou o esperado) |
| 2 | STL | watertight, winding consistente, sem face degenerada; tesselação ≤ 0,02 mm linear / ≤ 0,1 rad angular (curva lisa) |
| 3 | Mesa | cabe na área útil na orientação de impressão |
| 4 | Intenção | Δ de bounding box e posição de furos vs cena e vs referência coletada; Δ > 2 mm exige justificativa |
| 5 | Parede | espessura mínima ≥ valor do `fab.py` (amostragem por raios) |
| 6 | Overhang | área com normal para baixo além de 45° ≈ 0, ou ponte ≤ 10 mm justificada |
| 7 | Interferência | interseção com todas as peças e com `hardware.py` ≤ 0,01 mm³ |
| 8 | Movimento | varrer o curso completo dos carros (passo ≤ 5 mm): folga ≥ 1 mm com tudo que é fixo |
| 9 | Furação | furos entre peças que se parafusam: excentricidade ≤ 0,05 mm |
| 10 | Caminho da bola | varredura de esfera (Ø bola + folga) sem colisão; sem degrau > 0,2 mm no sentido da rolagem |
| 11 | Visual | renderize vista iso, vista de impressão e o lado a lado com a referência coletada; **abra as imagens e avalie**. Se estiver quadrado, com cara de caixa ou fora da linguagem de forma, refaça |
| 12 | Fatiamento | se houver slicer CLI: fatie com o perfil do `fab.py` e reporte tempo e gramas; senão, estime por volume |
| 13 | Montabilidade | existe uma sequência de montagem possível; todo parafuso tem acesso de ferramenta; nenhuma peça precisa ser forçada ou deformada para entrar; descreva a sequência em 1 linha |

Falhou: conserte e rode de novo. Nunca entregue peça reprovada sem dizer qual checagem falhou e por quê.

### Fase 5 — Entregáveis
**Por peça:** `<ID>_<nome>.step`, `<ID>_<nome>.stl` (mm, orientado), `<ID>_<nome>.png` e ficha (material, orientação, suporte, perímetros, infill, camada, tempo, gramas, quantidade por máquina).

**Por máquina:**
- `assembly.step` e `assembly.glb` (o GLB é o que o simulador vai carregar).
- `FILA_IMPRESSAO.md`: ordem, tempo de cada peça, total de horas vs horas disponíveis.
- `BOM_FIXACAO.md`: parafusos, porcas e insertos por peça, com comprimento.
- `PENDENCIAS.md`: tudo que é ESTIMADO, decisões em aberto, o que precisa ser medido em bancada.
- `VERIFICACAO.md`: tabela da Fase 4 de todas as peças.
- `CHANGELOG.md`.
- Um `.zip` com tudo no fim.

### Fase 6 — Reconectar a simulação (só depois das peças aprovadas, e só se eu pedir)
- O simulador passa a carregar o GLB exportado do CAD, nas mesmas posições.
- A página das peças passa a servir os STL/STEP de `cad/out/`, em vez de exportar da cena.
- A física e o `params.js` não mudam.
- O Three.js nunca mais é fonte de STL.

---

## 5. Gestão de prazo
- O objetivo é a impressora nunca ficar parada: P1 primeiro, entrega uma a uma.
- Decisão que **não** muda interface entre peças: decida, registre em `PENDENCIAS.md` e siga.
- Decisão que **muda** interface entre peças: pergunte, com default.
- Se o contexto ficar longo, gere `HANDOFF.md` (estado atual, decisões, próxima peça, comandos para rodar) para eu abrir outra sessão sem perder nada.

## 6. Definição de pronto
- **Peça pronta:** passou nas checagens 1–13, tem STEP + STL + PNG + ficha, está na fila, e a montagem continua sem interferência.
- **Projeto pronto:** todas as P1 e P2 das duas máquinas prontas, a montagem de cada máquina passa na varredura de movimento, e `PENDENCIAS.md` lista tudo o que ainda é estimativa.

## 7. Comece
Fase 0, depois Fase 1. **Pare no fim da Fase 1** com o inventário, a fila de impressão, a conta de horas e as perguntas.
