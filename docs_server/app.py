"""Servidor asíncrono de lectura para la documentación Markdown del proyecto."""
from pathlib import Path

import markdown
from quart import Quart, abort, render_template_string

ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = (ROOT / "docs").resolve()
app = Quart(__name__)

PAGE = """<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ title }} · SITRA-CGE UNL</title>
<style>
:root{font-family:Inter,system-ui,sans-serif;color:#172033;background:#f4f6fa}body{max-width:1050px;margin:2rem auto;padding:0 1.25rem;line-height:1.65}
header,main{background:white;border:1px solid #dce2ec;border-radius:12px;padding:1.5rem 2rem;margin-bottom:1rem}a{color:#1456a0}nav ul{columns:2;padding-left:1.2rem}
pre{overflow:auto;background:#101827;color:#e5ecf6;padding:1rem;border-radius:8px}code{font-family:ui-monospace,monospace}table{border-collapse:collapse;width:100%}th,td{border:1px solid #dce2ec;padding:.5rem;text-align:left}blockquote{border-left:4px solid #3974b8;margin-left:0;padding-left:1rem;color:#526078}
</style><script type="module">
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
document.querySelectorAll('pre code.language-mermaid').forEach(code => {
  const diagram = document.createElement('div');
  diagram.className = 'mermaid';
  diagram.textContent = code.textContent;
  code.closest('pre').replaceWith(diagram);
});
mermaid.initialize({ startOnLoad: true, theme: 'neutral' });
</script></head><body><header><a href="/">SITRA-CGE UNL · Documentación</a><h1>{{ title }}</h1></header><main>{{ body|safe }}</main></body></html>"""


def render_document(path: Path):
    if not path.is_file() or path.suffix.lower() != ".md":
        abort(404)
    source = path.read_text(encoding="utf-8")
    body = markdown.markdown(source, extensions=["fenced_code", "tables", "toc"])
    title = path.stem.replace("_", " ").replace("-", " ").title()
    return render_template_string(PAGE, title=title, body=body)


@app.get("/")
async def index():
    files = sorted(DOCS_DIR.rglob("*.md"))
    links = "<h2>Documentos</h2><ul>" + "".join(
        f'<li><a href="/{path.relative_to(DOCS_DIR).as_posix()}">{path.relative_to(DOCS_DIR).as_posix()}</a></li>'
        for path in files
    ) + "</ul>"
    return await render_template_string(PAGE, title="Documentación", body=links)


@app.get("/<path:doc_name>")
async def document(doc_name: str):
    requested = (DOCS_DIR / doc_name).resolve()
    if not requested.is_relative_to(DOCS_DIR):
        abort(404)
    return await render_document(requested)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
