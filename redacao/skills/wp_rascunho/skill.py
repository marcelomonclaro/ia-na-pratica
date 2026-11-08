"""Monta o rascunho do WordPress a partir de uma matéria já validada.

Converte o Markdown em blocos do Gutenberg e gera o JSON que o navegador envia
à API REST do site. O status é sempre 'draft': publicar é decisão humana.
"""
from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path

import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "materia_validador", Path(__file__).parent.parent / "materia_validador" / "skill.py")
_validador = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_validador)
ler_materia, validar = _validador.ler_materia, _validador.validar


class GateError(RuntimeError):
    pass


def inline(md: str) -> str:
    s = html.escape(md, quote=False)
    s = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", s)
    return s


def p(t): return f"<!-- wp:paragraph -->\n<p>{t}</p>\n<!-- /wp:paragraph -->"


def h(t, nivel=2):
    attr = "" if nivel == 2 else f' {{"level":{nivel}}}'
    return f'<!-- wp:heading{attr} -->\n<h{nivel} class="wp-block-heading">{t}</h{nivel}>\n<!-- /wp:heading -->'


def lista(itens, ordenada=False):
    li = "\n\n".join(f"<!-- wp:list-item -->\n<li>{i}</li>\n<!-- /wp:list-item -->" for i in itens)
    if ordenada:
        return f'<!-- wp:list {{"ordered":true}} -->\n<ol class="wp-block-list">{li}</ol>\n<!-- /wp:list -->'
    return f'<!-- wp:list -->\n<ul class="wp-block-list">{li}</ul>\n<!-- /wp:list -->'


def md_para_gutenberg(corpo: str) -> str:
    out = []
    for b in [x.strip() for x in re.split(r"\n\s*\n", corpo) if x.strip()]:
        linhas = b.splitlines()
        if b.startswith("### "):
            out.append(h(inline(b[4:].strip()), 3))
        elif b.startswith("## "):
            out.append(h(inline(b[3:].strip()), 2))
        elif all(re.match(r"^[-*] ", l) for l in linhas):
            out.append(lista([inline(l[2:].strip()) for l in linhas]))
        elif all(re.match(r"^\d+\. ", l) for l in linhas):
            out.append(lista([inline(re.sub(r"^\d+\. ", "", l).strip()) for l in linhas], True))
        else:
            out.append(p(inline(" ".join(l.strip() for l in linhas))))
    return "\n\n".join(out)


def montar(params: dict) -> dict:
    arq = params["arquivo"]
    if params.get("status", "draft") != "draft":
        raise GateError("Este pacote só cria rascunhos. Publicar é feito por uma pessoa no painel.")
    laudo = validar({"arquivo": arq})
    if not laudo["ok"]:
        raise GateError("Matéria reprovada no validador: " + "; ".join(laudo["erros"]))
    meta, corpo = ler_materia(arq)
    partes = [md_para_gutenberg(corpo)]
    if meta.get("leia_tambem"):
        partes.append(h("Leia também", 3))
        partes.append(lista([f'<a href="{x["url"]}">{html.escape(x["titulo"], quote=False)}</a>' for x in meta["leia_tambem"]]))
    if meta.get("estudo"):
        partes.append(p(f"<em>{inline(meta['estudo'])}</em>"))
    foto = meta["foto"]
    pagina = meta.get("tipo", "post") == "pagina"
    return {
        "rota": "pages" if pagina else "posts",
        "post": {
            "title": meta["titulo"],
            "slug": meta["slug"],
            "status": "draft",
            "excerpt": meta["linha_fina"],
            "content": "\n\n".join(partes),
            **({} if pagina else {"categories": [int(c) for c in meta["categorias"]]}),
            "meta": {
                **({} if pagina else {"mf_format": meta.get("formato", "noticia")}),
                "_yoast_wpseo_focuskw": meta["seo"]["palavra_chave"],
                "_yoast_wpseo_metadesc": meta["seo"]["metadesc"],
            },
        },
        "tags": [] if pagina else meta.get("tags", []),
        "foto": {
            "url": foto["url"],
            # Sufixo "-foto": no WordPress a mídia ocupa o endereço do nome do arquivo e, nas páginas,
            # disputa o slug com elas (foi assim que uma página saiu com "-2" no endereço).
            "arquivo": foto.get("arquivo", meta["slug"] + "-foto.jpg"),
            "titulo": foto.get("titulo", foto["legenda"].split(". Foto:")[0]),
            "legenda": foto["legenda"],
            "alt": foto["alt"],
        },
        "laudo": laudo,
    }


if __name__ == "__main__":
    try:
        r = montar({"arquivo": sys.argv[1]})
    except GateError as e:
        print("BLOQUEADO:", e)
        sys.exit(1)
    destino = Path(sys.argv[1]).with_suffix(".payload.json")
    destino.write_text(json.dumps(r, ensure_ascii=False), encoding="utf-8")
    print(f"ok -> {destino} ({len(r['post']['content'])} caracteres de conteúdo)")
