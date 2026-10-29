"""Visão geral da Máquina A para o README: renders de saidas/montagem/maquina_a.glb.

Cena = peças do CadQuery (impressas + compradas + bandeja) e, só como contexto, o gabinete de MDF do CAD antigo
(../montagem/modelos/gab_*.glb, mesmas coordenadas).

Uso (da pasta cad_pecas, depois do build_all.py):
    cd ferramentas/visao_geral && npm install && cd ../..
    python ferramentas/visao_geral/gerar.py                 # saidas/imagens/visao_geral/*.png + giro.gif
    python ferramentas/visao_geral/gerar.py --painel ARQ    # também a cena num glTF só (JSON com o buffer embutido)

Requer: Python com playwright e Pillow, e ffmpeg no PATH.
"""
import argparse, base64, functools, glob, http.server, json, os, re, shutil, subprocess, sys, tempfile, threading

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

AQUI = os.path.dirname(os.path.abspath(__file__))
CP = os.path.abspath(os.path.join(AQUI, '..', '..'))
RAIZ = os.path.dirname(CP)
SAIDA = os.path.join(CP, 'saidas', 'imagens', 'visao_geral')

MODULOS = [('A', 'Eixo A (bola)'), ('sol', 'Soltura (berço)'), ('mag', 'Magazine e carga'), ('elev', 'Elevador de fuso'),
           ('B', 'Eixo B (buraco)'), ('boca', 'Boca e detecção'), ('bj', 'Bandeja'), ('tras', 'Vista de trás')]


def mapa_ids():
    """nome do arquivo da peça -> ID curto (A09, A01-B, A12-3...), como no painel do Maker Lab."""
    rs = [json.load(open(f, encoding='utf-8')) for f in glob.glob(os.path.join(CP, 'saidas', 'relatorios', '*.json'))]
    nvar = {}
    for r in rs:
        nvar.setdefault(r['id'], set()).add(r['variante'])
    return {os.path.basename(r['arquivos']['stl'])[:-4]: (r['id'] if len(nvar[r['id']]) == 1 else f"{r['id']}-{r['variante']}")
            for r in rs}


def fonte(tam):
    for f in ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 'C:/Windows/Fonts/arialbd.ttf', '/Library/Fonts/Arial Bold.ttf'):
        if os.path.exists(f):
            return ImageFont.truetype(f, tam)
    return ImageFont.load_default()


def grade(tmp):
    tw, th, cols, pad, head = 800, 600, 4, 24, 64
    rows = (len(MODULOS) + cols - 1) // cols
    W, H = cols * tw + (cols + 1) * pad, rows * (th + head) + (rows + 1) * pad
    img = Image.new('RGB', (W, H), (238, 240, 236))
    d, f = ImageDraw.Draw(img), fonte(34)
    for i, (k, t) in enumerate(MODULOS):
        x, y = pad + (i % cols) * (tw + pad), pad + (i // cols) * (th + head + pad)
        d.rounded_rectangle([x, y, x + tw, y + th + head], radius=18, fill=(246, 247, 244))
        img.paste(Image.open(os.path.join(tmp, f'mod_{k}.png')).convert('RGB'), (x, y + head))
        d.rounded_rectangle([x, y, x + tw, y + th + head], radius=18, outline=(214, 218, 210), width=2)
        d.text((x + 28, y + head / 2 + 4), t, font=f, fill=(28, 35, 33), anchor='lm')
    img.resize((W // 2, H // 2), Image.LANCZOS).save(os.path.join(SAIDA, 'modulos.png'), optimize=True)


def chromium(p):
    exe = os.environ.get('CHROME')
    if not exe and os.path.exists('/opt/pw-browsers/chromium-1243/chrome-linux64/chrome'):
        exe = '/opt/pw-browsers/chromium-1243/chrome-linux64/chrome'
    args = ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist']
    return p.chromium.launch(executable_path=exe, args=args) if exe else p.chromium.launch(args=args)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--painel', metavar='ARQ', help='grava a cena inteira como glTF com o buffer embutido (fora do git)')
    a = ap.parse_args()
    if not os.path.isdir(os.path.join(AQUI, 'node_modules', 'three')):
        sys.exit('Falta o three.js: rode "npm install" em ferramentas/visao_geral.')
    os.makedirs(SAIDA, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix='picbox_vg_')
    vistas = json.load(open(os.path.join(AQUI, 'vistas.json'), encoding='utf-8'))

    class Q(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *x): pass
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Q, directory=RAIZ))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f'http://127.0.0.1:{srv.server_address[1]}/cad_pecas/ferramentas/visao_geral/render.html'

    with sync_playwright() as p:
        b = chromium(p)
        pg = b.new_page(viewport={'width': 800, 'height': 600})
        pg.goto(url)
        pg.evaluate('m => monta(m)', mapa_ids())
        for v in vistas:
            png = pg.evaluate('o => quadro(o)', v['o'])
            destino = tmp if v['nome'].startswith(('mod_', 'giro_')) else SAIDA
            open(os.path.join(destino, v['nome']), 'wb').write(base64.b64decode(png.split(',', 1)[1]))
            print(v['nome'], flush=True)
        if a.painel:
            open(os.path.join(tmp, 'bruto.glb'), 'wb').write(base64.b64decode(pg.evaluate('exporta()')))
        b.close()
    srv.shutdown()

    grade(tmp)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', '10', '-i', os.path.join(tmp, 'giro_%02d.png'),
                    '-vf', 'scale=560:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128:stats_mode=diff[p];'
                           '[s1][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle',
                    '-loop', '0', os.path.join(SAIDA, 'giro.gif')], check=True)
    if a.painel:
        cli = os.path.join(AQUI, 'node_modules', '.bin', 'gltf-transform')
        win = os.name == 'nt'
        subprocess.run([cli, 'optimize', os.path.join(tmp, 'bruto.glb'), os.path.join(tmp, 'q.glb'), '--compress', 'quantize',
                        '--texture-compress', 'false', '--simplify', 'false', '--instance', 'false', '--join', 'false',
                        '--flatten', 'false', '--palette', 'false'], check=True, shell=win)
        subprocess.run([cli, 'copy', os.path.join(tmp, 'q.glb'), os.path.join(tmp, 'q.gltf')], check=True, shell=win)
        j = json.load(open(os.path.join(tmp, 'q.gltf'), encoding='utf-8'))
        for buf in j['buffers']:
            buf['uri'] = 'data:application/octet-stream;base64,' + base64.b64encode(open(os.path.join(tmp, buf['uri']), 'rb').read()).decode()
        open(a.painel, 'w', encoding='utf-8').write(json.dumps(j, separators=(',', ':')))
        print('cena para o painel:', a.painel, os.path.getsize(a.painel) // 1024, 'KB')
    shutil.rmtree(tmp, ignore_errors=True)
    print('Pronto:', SAIDA)


if __name__ == '__main__':
    main()
