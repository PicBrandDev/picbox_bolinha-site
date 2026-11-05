"""Gera saidas/visualizador.html: a Maquina A montada (sem gabinete) com a lista de pecas ao lado.
Clicar numa peca destaca ela na montagem; modo "peca a peca" mostra so ela. A montagem vai embutida (abre com dois
cliques, sem servidor); os links de STL/STEP apontam para os arquivos em saidas/.
Uso (de dentro de cad_pecas/, depois do verifica e do assembly): python ferramentas/visualizador.py"""
import base64
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from maquina_a import montagem as MT  # noqa: E402

S = Path(__file__).resolve().parents[1] / "saidas"
GLB = S / "montagem" / "maquina_a.glb"


def itens():
    out = []
    for g, ids in MT.GRUPOS.items():
        for pid in ids:
            mod = MT.modulo(pid)
            for v in MT.variantes(mod):
                nome = MT.nome_arquivo(pid, v)
                f = S / "relatorios" / f"{nome}.json"
                r = json.loads(f.read_text(encoding="utf8")) if f.exists() else {}
                fat = r.get("12_fatiamento", {})
                out.append(dict(no=nome, id=pid, titulo=mod.TITULO, grupo=g, posicao=MT.POSICAO[(pid, v)].replace("_", " · "),
                                qtd=mod.QTD[v], impressora=f"{mod.IMPRESSORA}x{mod.IMPRESSORA}", horas=fat.get("horas"),
                                gramas=fat.get("gramas"), aprovada=r.get("aprovada"), ferramenta=getattr(mod, "FERRAMENTA", False),
                                stl=f"stl_para_imprimir/{g}/{nome}.stl", step=f"step/{g}/{nome}.step",
                                imagem=f"imagens/pecas/{nome}_mesa.png"))
    return out


HTML = r"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PICBOX · Máquina A · peças</title>
<style>
:root{--bg:#f4f2ee;--painel:#ffffff;--texto:#1d1d1f;--fraco:#6b6b70;--linha:#e3e0da;--acento:#e8892b;--acento2:#fff1e3;--ok:#2e9e4f;--ruim:#c0392b}
@media (prefers-color-scheme: dark){:root{--bg:#141416;--painel:#1d1d20;--texto:#ececef;--fraco:#9a9aa2;--linha:#2c2c31;--acento:#f0a050;--acento2:#3a2a1a}}
*{box-sizing:border-box}
html,body{margin:0;height:100%;background:var(--bg);color:var(--texto);font:14px/1.4 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
#app{display:grid;grid-template-columns:360px 1fr;height:100vh}
aside{background:var(--painel);border-right:1px solid var(--linha);display:flex;flex-direction:column;min-height:0}
header{padding:16px 16px 10px;border-bottom:1px solid var(--linha)}
h1{font-size:16px;margin:0 0 2px}
.sub{color:var(--fraco);font-size:12px}
.barra{display:flex;gap:6px;margin-top:10px;flex-wrap:wrap}
button,.chip{font:inherit;font-size:12px;border:1px solid var(--linha);background:transparent;color:var(--texto);border-radius:6px;padding:5px 9px;cursor:pointer}
button.ativo{background:var(--acento);border-color:var(--acento);color:#fff}
input[type=search]{width:100%;margin-top:10px;padding:7px 9px;border:1px solid var(--linha);border-radius:6px;background:var(--bg);color:var(--texto);font:inherit}
label.opc{font-size:12px;color:var(--fraco);display:inline-flex;gap:4px;align-items:center;margin-right:10px;margin-top:8px}
#lista{overflow:auto;flex:1;padding:6px 0 12px}
.grupo{margin-top:6px}
.grupo>h2{font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--fraco);margin:10px 16px 4px;font-weight:600}
.item{padding:7px 16px;cursor:pointer;border-left:3px solid transparent}
.item:hover{background:var(--acento2)}
.item.sel{background:var(--acento2);border-left-color:var(--acento)}
.l1{display:flex;gap:8px;align-items:baseline}
.id{font-weight:700;font-variant-numeric:tabular-nums}
.nome{flex:1}
.qtd{color:var(--fraco);font-size:12px}
.l2{color:var(--fraco);font-size:12px;margin-top:1px}
.l3{margin-top:4px;display:none;gap:8px;font-size:12px}
.item.sel .l3{display:flex}
.l3 a{color:var(--acento);text-decoration:none}
.l3 a:hover{text-decoration:underline}
main{position:relative;min-width:0}
canvas{display:block;width:100%;height:100%}
#ficha{position:absolute;right:16px;bottom:16px;max-width:340px;background:var(--painel);border:1px solid var(--linha);border-radius:10px;padding:12px 14px;box-shadow:0 6px 24px rgba(0,0,0,.12);display:none}
#ficha h3{margin:0 0 4px;font-size:14px}
#ficha .k{color:var(--fraco)}
#dica{position:absolute;left:16px;bottom:16px;color:var(--fraco);font-size:12px;background:var(--painel);border:1px solid var(--linha);border-radius:8px;padding:6px 9px}
.st-ok{color:var(--ok)}.st-ruim{color:var(--ruim)}
@media (max-width:760px){#app{grid-template-columns:1fr;grid-template-rows:45vh 55vh}aside{order:2;border-right:0;border-top:1px solid var(--linha)}}
</style>
</head>
<body>
<div id="app">
  <aside>
    <header>
      <h1>PICBOX · Máquina A</h1>
      <div class="sub">Peças impressas na posição de montagem · sem gabinete · __DATA__</div>
      <div class="barra">
        <button id="m-tudo" class="ativo">Ver tudo</button>
        <button id="m-peca">Peça a peça</button>
        <button id="limpar">Limpar seleção</button>
      </div>
      <input id="busca" type="search" placeholder="Buscar peça (ID, nome ou posição)">
      <label class="opc"><input id="v-hw" type="checkbox" checked> compradas</label>
      <label class="opc"><input id="v-bj" type="checkbox" checked> bandeja</label>
    </header>
    <div id="lista"></div>
  </aside>
  <main>
    <div id="dica">Arraste para girar · roda para zoom · clique numa peça para selecionar</div>
    <div id="ficha"></div>
  </main>
</div>
<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}</script>
<script type="module">
import * as THREE from 'three';
import {OrbitControls} from 'three/addons/controls/OrbitControls.js';
import {GLTFLoader} from 'three/addons/loaders/GLTFLoader.js';

const ITENS = __ITENS__;
const GRUPOS = __GRUPOS__;
const GLB64 = "__GLB__";

const main = document.querySelector('main');
const renderer = new THREE.WebGLRenderer({antialias:true, alpha:true});
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
main.prepend(renderer.domElement);
const cena = new THREE.Scene();
const cam = new THREE.PerspectiveCamera(35, 1, 5, 20000);
const ctl = new OrbitControls(cam, renderer.domElement);
ctl.enableDamping = true;
cena.add(new THREE.HemisphereLight(0xffffff, 0x8a8070, 1.6)); cena.add(new THREE.AmbientLight(0xffffff, 0.35));
const sol = new THREE.DirectionalLight(0xffffff, 1.4); sol.position.set(600, 1800, 1200); cena.add(sol);
const sol2 = new THREE.DirectionalLight(0xffffff, 0.5); sol2.position.set(-800, 600, -900); cena.add(sol2);

function tamanho(){ const r = main.getBoundingClientRect(); renderer.setSize(r.width, r.height, false); cam.aspect = r.width / Math.max(r.height, 1); cam.updateProjectionMatrix(); }
new ResizeObserver(tamanho).observe(main); tamanho();

const nos = {};            // nome do no -> mesh
const original = new Map(); // mesh -> material original
const bytes = Uint8Array.from(atob(GLB64), c => c.charCodeAt(0));
new GLTFLoader().parse(bytes.buffer, '', gltf => {
  gltf.scene.traverse(o => { if (o.isMesh){
    nos[o.name] = o; if (!o.geometry.attributes.normal) o.geometry.computeVertexNormals();
    o.material = o.material.clone(); o.material.side = THREE.DoubleSide; o.material.metalness = 0; o.material.roughness = 0.75;
    if (/acrilico|comprada_tubo/.test(o.name)){ o.material.transparent = true; o.material.opacity = 0.25; o.material.depthWrite = false; }
    original.set(o, o.material); } });
  cena.add(gltf.scene);
  enquadrar(Object.values(nos).filter(m => !m.name.startsWith('bandeja')), new THREE.Vector3(0.55, 0.35, 1));
  aplicar();
});

function caixa(meshes){ const b = new THREE.Box3(); meshes.forEach(m => b.expandByObject(m)); return b; }
function enquadrar(meshes, dir){
  const b = caixa(meshes); if (b.isEmpty()) return;
  const c = b.getCenter(new THREE.Vector3()), r = b.getSize(new THREE.Vector3()).length() / 2;
  const d = (dir || cam.position.clone().sub(ctl.target)).clone().normalize();
  const dist = Math.max(r, 60) / Math.sin(THREE.MathUtils.degToRad(cam.fov / 2)) * 1.6;
  alvo = {c, p: c.clone().add(d.multiplyScalar(dist))};
}
let alvo = null;

const fantasma = new THREE.MeshStandardMaterial({color:0x9a9aa0, transparent:true, opacity:0.12, depthWrite:false});
const destaque = new THREE.MeshStandardMaterial({color:0xff8a2a, emissive:0x8a3a00, roughness:0.6, metalness:0, side:THREE.DoubleSide});
let modo = 'tudo', sel = null;

function tipo(nome){ return nome.startsWith('comprada_') ? 'hw' : nome.startsWith('bandeja') ? 'bj' : 'peca'; }
function aplicar(){
  const verHw = document.getElementById('v-hw').checked, verBj = document.getElementById('v-bj').checked;
  for (const [nome, m] of Object.entries(nos)){
    const t = tipo(nome);
    let vis = t === 'peca' || (t === 'hw' && verHw) || (t === 'bj' && verBj);
    if (modo === 'peca' && sel) vis = nome === sel;
    m.visible = vis;
    if (!sel) m.material = original.get(m);
    else m.material = nome === sel ? destaque : (modo === 'tudo' ? fantasma : original.get(m));
  }
}

function selecionar(nome, doLista){
  sel = nome;
  document.querySelectorAll('.item').forEach(e => e.classList.toggle('sel', e.dataset.no === nome));
  if (doLista){ const e = document.querySelector(`.item[data-no="${CSS.escape(nome)}"]`); if (e) e.scrollIntoView({block:'nearest'}); }
  aplicar();
  const it = ITENS.find(i => i.no === nome);
  const f = document.getElementById('ficha');
  if (it){
    const st = it.aprovada === true ? '<span class="st-ok">aprovada nas 13 checagens</span>' : it.aprovada === false ? '<span class="st-ruim">reprovada</span>' : '—';
    f.innerHTML = `<h3>${it.id} · ${it.titulo}</h3><div><span class="k">Posição:</span> ${it.posicao}</div>
      <div><span class="k">Quantidade:</span> ${it.qtd} · <span class="k">Impressora:</span> ${it.impressora}</div>
      <div><span class="k">Impressão:</span> ${it.horas ?? '—'} h · ${it.gramas ?? '—'} g (estimativa)</div>
      <div><span class="k">Verificação:</span> ${st}</div>
      <div style="margin-top:6px"><a href="${it.stl}" download>STL (para imprimir)</a> · <a href="${it.step}" download>STEP (montagem)</a> · <a href="${it.imagem}" target="_blank">imagem na mesa</a></div>`;
    f.style.display = 'block';
  } else f.style.display = nome ? 'block' : 'none';
  if (nome && nos[nome]) enquadrar([nos[nome]]);
  else if (!nome) enquadrar(Object.values(nos).filter(m => m.visible && !m.name.startsWith('bandeja')));
  if (!nome) f.style.display = 'none';
}

function lista(){
  const q = document.getElementById('busca').value.trim().toLowerCase();
  const el = document.getElementById('lista'); el.innerHTML = '';
  for (const [g, titulo] of Object.entries(GRUPOS)){
    const its = ITENS.filter(i => i.grupo === g && (!q || (i.id + ' ' + i.titulo + ' ' + i.posicao).toLowerCase().includes(q)));
    if (!its.length) continue;
    const div = document.createElement('div'); div.className = 'grupo';
    div.innerHTML = `<h2>${titulo}</h2>`;
    for (const it of its){
      const d = document.createElement('div'); d.className = 'item' + (it.no === sel ? ' sel' : ''); d.dataset.no = it.no;
      d.innerHTML = `<div class="l1"><span class="id">${it.id}</span><span class="nome">${it.titulo}</span><span class="qtd">×${it.qtd}</span></div>
        <div class="l2">${it.posicao}${it.ferramenta ? ' · ferramenta (não fica na máquina)' : ''}</div>
        <div class="l3"><a href="${it.stl}" download>STL</a><a href="${it.step}" download>STEP</a></div>`;
      d.onclick = ev => { if (ev.target.tagName === 'A') return; selecionar(it.no === sel ? null : it.no, false); };
      div.appendChild(d);
    }
    el.appendChild(div);
  }
}
lista();
document.getElementById('busca').oninput = lista;
document.getElementById('v-hw').onchange = aplicar;
document.getElementById('v-bj').onchange = aplicar;
document.getElementById('limpar').onclick = () => selecionar(null);
for (const [id, m] of [['m-tudo','tudo'],['m-peca','peca']]) document.getElementById(id).onclick = () => {
  modo = m; document.getElementById('m-tudo').classList.toggle('ativo', m === 'tudo'); document.getElementById('m-peca').classList.toggle('ativo', m === 'peca');
  if (m === 'peca' && !sel){ const p = ITENS.find(i => !i.ferramenta); if (p) selecionar(p.no, true); else aplicar(); } else { aplicar(); if (sel) enquadrar([nos[sel]]); }
};
addEventListener('keydown', e => {           // setas: proxima/anterior no modo peca a peca
  if (!['ArrowDown','ArrowUp'].includes(e.key) || document.activeElement.tagName === 'INPUT') return;
  const vis = [...document.querySelectorAll('.item')].map(x => x.dataset.no);
  const k = Math.max(0, vis.indexOf(sel) + (e.key === 'ArrowDown' ? 1 : -1));
  if (vis[k]) { selecionar(vis[Math.min(k, vis.length - 1)], true); e.preventDefault(); }
});

const ray = new THREE.Raycaster(), ptr = new THREE.Vector2(); let baixo = null;
renderer.domElement.addEventListener('pointerdown', e => baixo = [e.clientX, e.clientY]);
renderer.domElement.addEventListener('pointerup', e => {
  if (!baixo || Math.hypot(e.clientX - baixo[0], e.clientY - baixo[1]) > 4) return;
  const r = renderer.domElement.getBoundingClientRect();
  ptr.set((e.clientX - r.left) / r.width * 2 - 1, -(e.clientY - r.top) / r.height * 2 + 1);
  ray.setFromCamera(ptr, cam);
  const hit = ray.intersectObjects(Object.values(nos).filter(m => m.visible && tipo(m.name) === 'peca'), false)[0];
  if (hit) selecionar(hit.object.name, true);
});

(function loop(){
  requestAnimationFrame(loop);
  if (alvo){ ctl.target.lerp(alvo.c, 0.15); cam.position.lerp(alvo.p, 0.15); if (cam.position.distanceTo(alvo.p) < 1) alvo = null; }
  ctl.update(); renderer.render(cena, cam);
})();
</script>
</body>
</html>
"""


def main():
    from datetime import date
    its = itens()
    html = (HTML.replace("__ITENS__", json.dumps(its, ensure_ascii=False))
            .replace("__GRUPOS__", json.dumps(MT.GRUPO_TITULO, ensure_ascii=False))
            .replace("__GLB__", base64.b64encode(GLB.read_bytes()).decode("ascii"))
            .replace("__DATA__", f"{date.today():%d/%m/%Y}"))
    (S / "visualizador.html").write_text(html, encoding="utf8")
    print(S / "visualizador.html", round(len(html) / 1e6, 1), "MB,", len(its), "pecas")


if __name__ == "__main__":
    main()
