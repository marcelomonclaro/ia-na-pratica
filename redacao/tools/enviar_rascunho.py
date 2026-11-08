"""Envia uma matéria validada ao WordPress como RASCUNHO, pela API REST.

Credenciais vêm de variáveis de ambiente (nunca do código):
  WP_URL           ex.: https://seusite.com.br
  WP_USER          usuário da automação (ex.: automacao)
  WP_APP_PASSWORD  senha de aplicativo desse usuário

Uso:
  python tools/enviar_rascunho.py materias/arquivo.md            # envia
  python tools/enviar_rascunho.py materias/arquivo.md --simular  # só mostra o que faria
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import requests

RAIZ = Path(__file__).resolve().parent.parent
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location("wp_rascunho", RAIZ / "skills" / "wp_rascunho" / "skill.py")
montador = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(montador)

UA = "redacao-automatizada/0.1"


class Cliente:
    def __init__(self, base: str, usuario: str, senha: str, sessao=None):
        self.base = base.rstrip("/") + "/wp-json/wp/v2"
        self.s = sessao or requests.Session()
        self.s.auth = (usuario, senha)
        self.s.headers["User-Agent"] = UA

    def get(self, rota, **params):
        r = self.s.get(f"{self.base}/{rota}", params=params, timeout=30)
        if r.status_code >= 400:
            raise RuntimeError(f"{rota}: HTTP {r.status_code} {r.text[:300]}")
        return r.json()

    def post(self, rota, **kw):
        r = self.s.post(f"{self.base}/{rota}", timeout=60, **kw)
        if r.status_code >= 400:
            raise RuntimeError(f"{rota}: HTTP {r.status_code} {r.text[:300]}")
        return r.json()


def resolver_tags(cli: Cliente, nomes: list[str]) -> tuple[list[int], list[str]]:
    """Usa tags existentes; tenta criar as que faltam. O papel Autor não cria tags: essas voltam como pendentes."""
    ids, pendentes = [], []
    for nome in nomes:
        achadas = cli.get("tags", search=nome, per_page=20)
        hit = next((t for t in achadas if t["name"].lower() == nome.lower()), None)
        if hit:
            ids.append(hit["id"])
            continue
        try:
            ids.append(cli.post("tags", json={"name": nome})["id"])
        except RuntimeError:
            pendentes.append(nome)
    return ids, pendentes


def subir_foto(cli: Cliente, foto: dict) -> int:
    img = requests.get(foto["url"], timeout=60, headers={"User-Agent": UA})
    img.raise_for_status()
    m = cli.post("media", data=img.content, headers={
        "Content-Disposition": f'attachment; filename="{foto["arquivo"]}"',
        "Content-Type": img.headers.get("Content-Type", "image/jpeg").split(";")[0],
    })
    cli.post(f"media/{m['id']}", json={"title": foto["titulo"], "caption": foto["legenda"], "alt_text": foto["alt"]})
    return m["id"]


def enviar(arquivo: str, cli: Cliente | None, simular: bool = False) -> dict:
    pl = montador.montar({"arquivo": arquivo})  # valida; recusa se reprovada; status sempre draft
    rota = pl["rota"]
    assert pl["post"]["status"] == "draft"
    wp_id = montador.ler_materia(arquivo)[0].get("wp_id")
    if simular or cli is None:
        return {"simulado": True, "rota": rota, "titulo": pl["post"]["title"],
                "tags": pl["tags"], "foto": pl["foto"]["url"], "erros": pl["laudo"]["erros"],
                **({"ja_existe": wp_id} if wp_id else {})}
    # 1ª trava contra cópia: o cabeçalho já registra o id no site. Não depende do que a conta enxerga
    # (Autor e Editor sem edit_others_* não veem rascunhos de outras pessoas).
    if wp_id:
        return {"ja_existe": int(wp_id), "rota": rota, "fonte": "cabecalho"}
    try:
        existentes = cli.get(rota, slug=pl["post"]["slug"], status="draft,pending,publish,future", context="edit")
    except RuntimeError as e:
        if any(c in str(e) for c in ("HTTP 400", "HTTP 401", "HTTP 403")):
            raise RuntimeError(f"A conta não tem permissão para consultar rascunhos em '{rota}'"
                               f"{' (o papel Autor não cria páginas)' if rota == 'pages' else ''}. Detalhe: {e}") from e
        raise
    if existentes:
        return {"ja_existe": existentes[0]["id"], "rota": rota, "fonte": "slug"}
    corpo = dict(pl["post"])
    corpo["featured_media"] = subir_foto(cli, pl["foto"])
    pendentes: list[str] = []
    if rota == "posts":
        corpo["tags"], pendentes = resolver_tags(cli, pl["tags"])
    try:
        criado = cli.post(rota, json=corpo)
    except RuntimeError as e:  # metadado não registrado para este tipo: tenta sem ele
        if "rest_invalid_param" not in str(e):
            raise
        corpo.pop("meta", None)
        criado = cli.post(rota, json=corpo)
    if criado.get("status") != "draft":
        raise RuntimeError(f"O site gravou status '{criado.get('status')}', não rascunho. Verifique a trava no servidor.")
    return {"id": criado["id"], "rota": rota, "status": criado["status"], "tags_pendentes": pendentes,
            "registrar": f"acrescentar 'wp_id: {criado['id']}' ao cabeçalho de {Path(arquivo).name}",
            "editar": f"{cli.base.split('/wp-json')[0]}/wp-admin/post.php?post={criado['id']}&action=edit"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivos", nargs="+")
    ap.add_argument("--simular", action="store_true")
    a = ap.parse_args()
    cli = None
    if not a.simular:
        faltam = [v for v in ("WP_URL", "WP_USER", "WP_APP_PASSWORD") if not os.environ.get(v)]
        if faltam:
            sys.exit(f"Faltam variáveis de ambiente: {', '.join(faltam)}")
        cli = Cliente(os.environ["WP_URL"], os.environ["WP_USER"], os.environ["WP_APP_PASSWORD"])
    falhou = False
    for f in a.arquivos:
        try:
            print(f, json.dumps(enviar(f, cli, a.simular), ensure_ascii=False))
        except Exception as e:  # noqa: BLE001
            falhou = True
            print(f, "ERRO:", e)
    sys.exit(1 if falhou else 0)


if __name__ == "__main__":
    main()
