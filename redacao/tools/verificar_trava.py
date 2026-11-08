"""Verifica, com a própria conta da automação, que a trava do servidor funciona.

Credenciais em variáveis de ambiente (as mesmas de enviar_rascunho.py):
  WP_URL, WP_USER, WP_APP_PASSWORD

O que faz:
  1. Cria um post de teste pedindo status "publish". Aprovado se o site recusar
     (HTTP 401/403) ou gravar como rascunho.
  2. Tenta mudar esse rascunho para "publish". Aprovado se recusar ou continuar rascunho.
  3. Pede para abrir em modo de edição o post publicado mais recente (só leitura).
     Aprovado se o site recusar: a conta não pode editar conteúdo publicado nem alheio.

O post de teste fica como rascunho; quem apaga é o editor, com a conta dele.
Saída: JSON com o resultado de cada passo. Código 1 se algum passo falhar.

Uso:
  python tools/verificar_trava.py
"""
from __future__ import annotations

import json
import os
import sys

import requests

UA = "redacao-automatizada/0.1 (verificacao-trava)"
TITULO = "[TESTE DA TRAVA] apagar este rascunho"
RECUSADO = (401, 403)


def verificar(base: str, usuario: str, senha: str, sessao=None) -> dict:
    s = sessao or requests.Session()
    s.auth = (usuario, senha)
    s.headers["User-Agent"] = UA
    api = base.rstrip("/") + "/wp-json/wp/v2"
    passos, post_id = [], None

    # 1. Criar pedindo publish
    r = s.post(f"{api}/posts", json={"title": TITULO, "content": "Teste automático da trava. Pode apagar.",
                                     "status": "publish"}, timeout=60)
    if r.status_code in RECUSADO:
        passos.append({"passo": "criar com publish", "ok": True, "resultado": f"recusado (HTTP {r.status_code})"})
    elif r.status_code < 300:
        j = r.json()
        post_id = j.get("id")
        ok = j.get("status") == "draft"
        passos.append({"passo": "criar com publish", "ok": ok, "resultado": f"gravado como {j.get('status')}", "id": post_id})
    else:
        passos.append({"passo": "criar com publish", "ok": False, "resultado": f"erro inesperado HTTP {r.status_code}: {r.text[:200]}"})

    # 2. Tentar publicar o rascunho
    if post_id:
        r = s.post(f"{api}/posts/{post_id}", json={"status": "publish"}, timeout=60)
        if r.status_code in RECUSADO:
            passos.append({"passo": "mudar para publish", "ok": True, "resultado": f"recusado (HTTP {r.status_code})"})
        elif r.status_code < 300:
            st = r.json().get("status")
            passos.append({"passo": "mudar para publish", "ok": st == "draft", "resultado": f"ficou {st}"})
        else:
            passos.append({"passo": "mudar para publish", "ok": False, "resultado": f"erro inesperado HTTP {r.status_code}: {r.text[:200]}"})

    # 3. Abrir para edição um post publicado (só leitura)
    r = s.get(f"{api}/posts", params={"per_page": 1, "status": "publish", "_fields": "id,author"}, timeout=30)
    publicados = r.json() if r.status_code < 300 else []
    if publicados:
        alvo = publicados[0]["id"]
        r = s.get(f"{api}/posts/{alvo}", params={"context": "edit", "_fields": "id,status"}, timeout=30)
        passos.append({"passo": "abrir publicado para edição", "ok": r.status_code in RECUSADO,
                       "resultado": f"HTTP {r.status_code}", "alvo": alvo})
    else:
        passos.append({"passo": "abrir publicado para edição", "ok": False, "resultado": "nenhum post publicado encontrado"})

    return {"aprovado": all(p["ok"] for p in passos), "post_de_teste": post_id, "passos": passos}


def main():
    faltam = [v for v in ("WP_URL", "WP_USER", "WP_APP_PASSWORD") if not os.environ.get(v)]
    if faltam:
        sys.exit(f"Faltam variáveis de ambiente: {', '.join(faltam)}")
    res = verificar(os.environ["WP_URL"], os.environ["WP_USER"], os.environ["WP_APP_PASSWORD"])
    print(json.dumps(res, ensure_ascii=False, indent=2))
    if res["post_de_teste"]:
        print(f"Apagar com a conta do editor: {os.environ['WP_URL'].rstrip('/')}/wp-admin/post.php?post={res['post_de_teste']}&action=edit")
    sys.exit(0 if res["aprovado"] else 1)


if __name__ == "__main__":
    main()
