"""Coleta da pagina /montagem (Fase 1): arquivos que a pagina oferece para download
e dump da cena Three.js de cada modulo. Nada aqui altera a simulacao: a cena e
capturada por um gancho em WebGLRenderer.render injetado com addInitScript.

Uso: python cad_pecas/ferramentas/dump_scene.py [url_base]   (default http://localhost:8765)
Saida: cad_pecas/reference/A/{fabricar/*, scene_dump_A.json, coleta.json}
"""
import json
import sys
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright

RAIZ = Path(__file__).resolve().parents[2]
REF = RAIZ / "cad_pecas" / "saidas" / "referencia_cad_antigo"   # fora do git (so consulta)
BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8765").rstrip("/") + "/"

GANCHO = """
(() => {
  // o UMD do three.min.js faz window.THREE = {} e exporta as classes no fim;
  // quando Object3D e exportado, o primeiro scene.add() da pagina entrega a cena
  let T;
  Object.defineProperty(window, 'THREE', {
    configurable: true,
    get() { return T; },
    set(v) {
      T = v;
      let O;
      Object.defineProperty(v, 'Object3D', {
        configurable: true, enumerable: true,
        get() { return O; },
        set(c) {
          O = c;
          const add = c.prototype.add;
          c.prototype.add = function (...x) { if (this.isScene) window.__cena = this; return add.apply(this, x); };
        }
      });
    }
  });
})();
"""

DUMP = """
() => {
  const out = [];
  // userData so com valores simples (a pagina guarda objetos three la dentro)
  const simples = v => v === null || ['string', 'number', 'boolean'].includes(typeof v);
  const ud = u => Object.fromEntries(Object.entries(u || {}).map(([k, v]) =>
    [k, simples(v) ? v : Array.isArray(v) && v.every(simples) ? v : '[obj]']));
  const cena = window.__cena;
  cena.updateMatrixWorld(true);
  const box = new THREE.Box3();
  cena.traverse(o => {
    const g = o.geometry;
    let bb = null;
    if (o.isMesh || o.isGroup || o.isObject3D) {
      box.makeEmpty(); box.expandByObject(o);
      if (!box.isEmpty()) bb = [box.min.toArray(), box.max.toArray()];
    }
    out.push({
      uuid: o.uuid, nome: o.name, tipo: o.type, pai: o.parent ? o.parent.uuid : null,
      userData: ud(o.userData), visivel: o.visible,
      geometria: g ? { tipo: g.type, parametros: g.parameters || null,
                       vertices: g.attributes && g.attributes.position ? g.attributes.position.count : 0 } : null,
      material: o.material ? (Array.isArray(o.material) ? o.material.map(m => m.name) : o.material.name) : null,
      matrixWorld: o.matrixWorld.toArray(), bboxMundo: bb,
    });
  });
  return out;
}
"""


def main():
    REF.mkdir(parents=True, exist_ok=True)
    (REF / "fabricar").mkdir(exist_ok=True)
    with sync_playwright() as pw:
        nav = pw.chromium.launch(args=["--use-gl=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
        pag = nav.new_page(viewport={"width": 1400, "height": 900})
        pag.add_init_script(GANCHO)
        erros = []
        pag.on("pageerror", lambda e: erros.append(str(e)))
        pag.goto(BASE + "montagem.html#imprimir", wait_until="networkidle")
        guia = pag.evaluate("fetch('montagem/guia.json').then(r => r.json())")

        # 1) arquivos que a pagina oferece (links de download das paginas Pecas e Imprimir)
        hrefs = set()
        for aba in ("imprimir", "pecas"):
            pag.goto(BASE + "montagem.html?a=" + aba + "#" + aba, wait_until="networkidle")
            pag.wait_for_timeout(500)
            hrefs |= set(pag.eval_on_selector_all("a[download]", "as => as.map(a => a.getAttribute('href'))"))
        coletados = []
        for h in sorted(hrefs):
            r = pag.request.get(urljoin(BASE, h))
            nome = Path(h).name
            (REF / "fabricar" / nome).write_bytes(r.body())
            coletados.append({"href": h, "arquivo": "fabricar/" + nome, "bytes": len(r.body()), "status": r.status})

        # 2) dump da cena de cada modulo
        cenas = {}
        for m in guia["modulos"]:
            pag.goto(BASE + "montagem.html?m=" + m["id"] + "#" + m["id"], wait_until="networkidle")
            pag.wait_for_function("window.__cena && document.querySelector('#carregando') && "
                                  "document.querySelector('#carregando').style.opacity === '0'",
                                  timeout=120000)
            pag.wait_for_timeout(300)
            cenas[m["id"]] = pag.evaluate(DUMP)
            print(m["id"], len(cenas[m["id"]]), "objetos")
        nav.close()

    (REF / "scene_dump_A.json").write_text(json.dumps({"base": BASE, "unidade_cena": "?", "modulos": cenas}), encoding="utf8")
    (REF / "coleta.json").write_text(json.dumps({"arquivos": coletados, "erros_pagina": erros}, indent=1), encoding="utf8")
    print(len(coletados), "arquivos coletados;", len(erros), "erros de pagina")


if __name__ == "__main__":
    main()
