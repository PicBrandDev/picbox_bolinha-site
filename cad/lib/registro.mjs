/* Registro de pecas. Cada peca tem UMA ficha e UM gerador de geometria.

   tipo:  'comprado'  item da planilha de compras (Plano 1)
          'falta'     item que a montagem exige e NAO esta na planilha
          'impresso'  desenhado aqui, sai em STL/STEP para a impressora 3D
          'cortar'    chapa/perfil/tubo cortado na medida
          'fixador'   parafuso, porca, arruela (kit de ferragens)
   src:   'cat'   cota de catalogo/datasheet do fabricante
          'est'   cota de projeto (desenhada aqui)
          'medir' cota de anuncio generico: CONFERIR com paquimetro antes de imprimir
                  a peca que encaixa nela. A ficha lista quais cotas medir. */
export const PECAS = {};

export function peca(id, meta, gera) {
  if (PECAS[id]) throw new Error('peca duplicada: ' + id);
  PECAS[id] = Object.assign({ id, tipo: 'comprado', src: 'cat', notas: [], conferir: [] }, meta, { gera });
  return id;
}

/* instancias de uma montagem: { id, peca, T, rotulo? } */
export function inst(id, pecaId, T, extra) {
  if (!PECAS[pecaId]) throw new Error('peca inexistente: ' + pecaId + ' (instancia ' + id + ')');
  return Object.assign({ id, peca: pecaId, T }, extra || {});
}
