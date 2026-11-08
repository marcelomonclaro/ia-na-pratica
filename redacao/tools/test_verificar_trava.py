import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("vt", Path(__file__).parent / "verificar_trava.py")
vt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vt)


class Resp:
    def __init__(self, j=None, status=200):
        self._j, self.status_code, self.text = j, status, str(j)

    def json(self):
        return self._j


class FakeWP:
    """Simula o site. trava=True: força rascunho e recusa edição de publicados."""

    def __init__(self, trava=True, recusa_criar=False):
        self.headers, self.auth = {}, None
        self.trava, self.recusa_criar = trava, recusa_criar

    def post(self, url, json=None, timeout=None):
        if url.endswith("/posts"):
            if self.recusa_criar:
                return Resp({"code": "rest_cannot_publish"}, 403)
            return Resp({"id": 77, "status": "draft" if self.trava else json["status"]}, 201)
        if url.endswith("/posts/77"):
            return Resp({"code": "rest_cannot_publish"}, 403) if self.trava else Resp({"id": 77, "status": "publish"})
        raise AssertionError(url)

    def get(self, url, params=None, timeout=None):
        if url.endswith("/posts"):
            return Resp([{"id": 5, "author": 1}])
        if url.endswith("/posts/5"):
            return Resp({"code": "rest_forbidden_context"}, 403) if self.trava else Resp({"id": 5, "status": "publish"})
        raise AssertionError(url)


def test_trava_funcionando():
    r = vt.verificar("https://x.test", "bot", "s", sessao=FakeWP())
    assert r["aprovado"] and r["post_de_teste"] == 77 and len(r["passos"]) == 3


def test_criacao_recusada_tambem_aprova():
    r = vt.verificar("https://x.test", "bot", "s", sessao=FakeWP(recusa_criar=True))
    assert r["aprovado"] and r["post_de_teste"] is None and len(r["passos"]) == 2


def test_sem_trava_reprova():
    r = vt.verificar("https://x.test", "bot", "s", sessao=FakeWP(trava=False))
    assert not r["aprovado"] and not any(p["ok"] for p in r["passos"])
