#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera versoes single-file (autossuficientes) das 5 paginas na raiz do projeto,
para publicar direto no GitHub/Vercel sem pastas assets/ e data/."""
import re, subprocess, tempfile, os
from pathlib import Path

APP = Path(__file__).resolve().parent / "app"
ROOT = Path(__file__).resolve().parent


def r(p):
    return (APP / p).read_text(encoding="utf-8")


css = r("assets/css/styles.css")
summary = r("data/summary.js")
dashboard = r("data/dashboard.js")
europe = r("data/europe_benchmark.js")
mainjs = r("assets/js/main.js")
i18n = r("assets/js/i18n.js")
charts = r("assets/js/charts.js")

vessels = r("data/vessels.js")
vsearch = r("assets/js/vessel-search.js")
euvalid = r("data/europe_validation.js")
ets = r("data/ets_exposure.js")

CDN = "https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js"

def bundle(pg):
    """Bundle por pagina: o dataset de navios (grande) so entra no explorer."""
    dados = summary + "\n" + dashboard + "\n" + europe + "\n" + euvalid + "\n" + ets + "\n"
    logica = mainjs + "\n" + i18n + "\n" + charts + "\n"
    if pg == "vessel-explorer.html":
        dados += vessels + "\n"
        logica += vsearch + "\n"
    return ('<script src="' + CDN + '"></script>\n'
            + "<script>\n/* dados */\n" + dados
            + "/* logica */\n" + logica
            + "</" + "script>\n")

PAGES = ["index.html", "vessel-explorer.html", "port-call-analytics.html",
         "emissions.html", "data-quality.html"]

for pg in PAGES:
    h = (APP / pg).read_text(encoding="utf-8")
    h = h.replace('<link rel="stylesheet" href="assets/css/styles.css">',
                  "<style>\n" + css + "\n</" + "style>")
    h = re.sub(r'\s*<script src="assets/js/[^"]+"></' + 'script>', '', h)
    h = re.sub(r'\s*<script src="data/[^"]+"></' + 'script>', '', h)
    h = re.sub(r'\s*<script src="https://cdnjs\.cloudflare\.com/[^"]+"></' + 'script>', '', h)
    h = h.replace("</body>", bundle(pg) + "</body>")
    (ROOT / pg).write_text(h, encoding="utf-8")
    refs = re.findall(r'(?:src|href)="(assets/[^"]+|data/[^"]+)"', h)
    print(pg, round(len(h) / 1024, 1), "KB | refs locais:", refs)

# valida a sintaxe do JS embutido
for pg in PAGES:
    h = (ROOT / pg).read_text(encoding="utf-8")
    m = re.search(r"<script>\n/\* dados \*/(.*?)</" + "script>", h, re.S)
    js = m.group(1)
    f = tempfile.NamedTemporaryFile("w", suffix=".js", delete=False)
    f.write(js); f.close()
    rc = subprocess.run(["node", "--check", f.name], capture_output=True, text=True)
    print(pg, "JS:", "OK" if rc.returncode == 0 else "ERRO " + rc.stderr[:200])
    os.unlink(f.name)
