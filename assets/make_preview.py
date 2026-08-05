"""Rebuild preview.html from README.md using GitHub's own markdown renderer.

The point of the preview is fidelity: it must show exactly what github.com will
show, so the README is rendered by the GitHub markdown API (via `gh api`), not
by a local markdown library that disagrees with it in a hundred small ways.
Mermaid is the one thing the API returns as a plain code block, because GitHub
renders it client-side; this script converts those blocks to
<pre class="mermaid"> and the page footer loads mermaid.js the same way.

    python assets/make_preview.py
Then serve the repo root (python -m http.server 8766) and open /preview.html.
"""
import html
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
OUT = ROOT / "preview.html"

HEAD = """<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>scaffold-bench README preview</title><style>
:root{--bg:#ffffff;--fg:#1f2328;--muted:#59636e;--border:#d1d9e0;--panel:#f6f8fa;--link:#0969da}
@media (prefers-color-scheme:dark){
 :root{--bg:#0d1117;--fg:#e6edf3;--muted:#9198a1;--border:#30363d;--panel:#161b22;--link:#4493f8}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);
 font:16px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}
.wrap{max-width:1012px;margin:0 auto;padding:32px 24px 120px}
.bar{max-width:1012px;margin:0 auto;padding:14px 24px;color:var(--muted);font-size:13px;
 border-bottom:1px solid var(--border)}
h1,h2,h3{line-height:1.25;margin:24px 0 16px;font-weight:600}
h1{font-size:2em;padding-bottom:.3em;border-bottom:1px solid var(--border)}
h2{font-size:1.5em;padding-bottom:.3em;border-bottom:1px solid var(--border)}
h3{font-size:1.25em}
p,li{color:var(--fg)}
a{color:var(--link);text-decoration:none}a:hover{text-decoration:underline}
img{max-width:100%}
hr{height:1px;background:var(--border);border:0;margin:24px 0}
code{background:var(--panel);padding:.2em .4em;border-radius:6px;font-size:85%;
 font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
pre{background:var(--panel);padding:16px;border-radius:6px;overflow:auto}
pre code{background:none;padding:0}
table{border-collapse:collapse;display:block;overflow:auto;max-width:100%;margin:16px 0}
th,td{border:1px solid var(--border);padding:6px 13px}
tr:nth-child(2n){background:var(--panel)}
blockquote{border-left:.25em solid var(--border);padding:0 1em;color:var(--muted);margin:16px 0}
details{margin:8px 0;border:1px solid var(--border);border-radius:6px;padding:12px 16px}
summary{cursor:pointer;font-weight:600}
.markdown-alert{border-left:.25em solid var(--border);padding:8px 16px;margin:16px 0;
 background:var(--panel);border-radius:0 6px 6px 0}
.markdown-alert-title{font-weight:600;display:block;margin-bottom:4px}
.mermaid{margin:16px 0;background:none}
.mermaid svg{max-width:100%;height:auto}
</style></head><body><div class='bar'>local preview &middot; rendered by GitHub's own markdown API &middot; mermaid rendered below via mermaid.js, as GitHub does client-side</div><div class='wrap'>"""

FOOT = """</div><script type='module'>import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';const dark=matchMedia('(prefers-color-scheme:dark)').matches;mermaid.initialize({startOnLoad:true,theme:dark?'dark':'default'});</script></body></html>"""


def render(md_text):
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                     encoding="utf-8") as f:
        json.dump({"text": md_text, "mode": "gfm"}, f)
        body = f.name
    try:
        out = subprocess.run(["gh", "api", "markdown", "--input", body],
                             capture_output=True, text=True, encoding="utf-8", check=True)
        return out.stdout
    finally:
        Path(body).unlink(missing_ok=True)


def main():
    md = README.read_text(encoding="utf-8")
    rendered = render(md)

    # GitHub renders mermaid client-side; the API hands the source back as a
    # highlighted code block. Swap each one for a <pre class="mermaid"> holding
    # the raw source, in order, so mermaid.js can pick them up.
    sources = re.findall(r"```mermaid\n(.*?)```", md, flags=re.S)
    def sub_mermaid(m, _it=iter(sources)):
        return ('<pre class="mermaid">' + html.escape(next(_it)) + "</pre>")
    rendered = re.sub(
        r'<div class="highlight highlight-source-mermaid"[^>]*>.*?</div>',
        sub_mermaid, rendered, flags=re.S)

    OUT.write_text(HEAD + rendered + FOOT, encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
