#!/usr/bin/env python3
"""Gera index.html a partir de conteudo.txt.

Formato de conteudo.txt:
  # Título da Parte | id        -> <h2>
  ## Título do Capítulo         -> <h3>
  ### Título da Seção           -> <h4>
  P: pergunta                   -> pergunta (numeração automática)
  R: resposta                   -> resposta (pode continuar em linhas seguintes)
  N: nota                       -> nota de rodapé (referências, ressalvas)
  T: texto livre                -> parágrafo
  (linhas começando com // são comentários)
"""
import html, pathlib, re
raiz = pathlib.Path(__file__).parent
esc = lambda s: html.escape(s.strip(), quote=False)

partes, n, aberto = [], 0, None
out, toc = [], []
def fechar():
    global aberto
    if aberto: out.append("</div>"); aberto = None
buf = None
def flush():
    global buf
    if buf:
        k, t = buf
        if k == "P":
            global n; n += 1
            out.append(f'<div class="qa"><span class="q">{n}) {esc(t)}</span>')
        elif k == "R": out.append(f'<div class="a">{esc(t)}</div></div>')
        elif k == "N": out.append(f'<div class="footnote">{esc(t)}</div>')
        elif k == "T": out.append(f'<p>{esc(t)}</p>')
    buf = None

for linha in (raiz/"conteudo.txt").read_text(encoding="utf-8").splitlines():
    if linha.startswith("//") or not linha.strip(): continue
    m = re.match(r"^(#{1,3}) (.*)$", linha)
    if m:
        flush()
        nivel, tit = len(m.group(1)), m.group(2)
        if nivel == 1:
            fechar(); out.append("</section>") if partes else None
            tit, _, pid = tit.partition("|"); pid = pid.strip() or f"p{len(partes)+1}"
            partes.append(pid); toc.append((pid, tit.strip()))
            out.append(f'<section id="{pid}"><h2>{esc(tit)}</h2>')
        elif nivel == 2:
            fechar(); out.append(f'<div class="chapter"><h3>{esc(tit)}</h3>'); aberto = True
        else: out.append(f"<h4>{esc(tit)}</h4>")
        continue
    m = re.match(r"^([PRNT]): ?(.*)$", linha)
    if m: flush(); buf = (m.group(1), m.group(2))
    elif buf: buf = (buf[0], buf[1] + " " + linha.strip())
flush(); fechar()
if partes: out.append("</section>")

sumario = "\n".join(f'  <div><a href="#{i}">{esc(t)}</a></div>' for i, t in toc)
topo = (raiz/"modelo/topo.html").read_text(encoding="utf-8")
rodape = (raiz/"modelo/rodape.html").read_text(encoding="utf-8")
titulo = '''<h1>Catecismo Maior<br>Anglo-Católico</h1>
<p class="center" style="font-size:1.1rem;">Segundo o método de São Pio X, para a Igreja Católica em sua vocação anglicana</p>
<p class="center" style="font-size:0.9rem;">Rascunho de trabalho · ✠ Ad majorem Dei gloriam</p>
<hr>
<div class="toc">
''' + sumario + "\n</div>\n"
(raiz/"index.html").write_text(topo + titulo + "\n".join(out) + "\n" + rodape, encoding="utf-8")
print(f"index.html gerado: {n} perguntas, {len(partes)} partes")
