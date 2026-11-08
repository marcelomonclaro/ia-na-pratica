import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("env", Path(__file__).parent / "enviar_rascunho.py")
env = importlib.util.module_from_spec(spec)
spec.loader.exec_module(env)
MAT = str(Path(__file__).resolve().parent.parent / "materias" / "01-marcas-busca-generativa.md")


class Resp:
    def __init__(self, j=None, status=200, content=b"", headers=None):
        self._j, self.status_code, self.content, self.text = j, status, content, str(j)
        self.headers = headers or {"Content-Type": "image/jpeg"}

    def json(self):
        return self._j

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(self.status_code)


class FakeWP:
    def __init__(self, status_gravado="draft", ja_existe=False):
        self.headers, self.auth, self.chamadas = {}, None, []
        self.status_gravado, self.ja_existe = status_gravado, ja_existe

    def get(self, url, params=None, timeout=None):
        self.chamadas.append(("GET", url, params))
        if url.endswith("/posts"):
            return Resp([{"id": 7}] if self.ja_existe else [])
        if url.endswith("/tags"):
            return Resp([{"id": 22, "name": "inteligência artificial"}] if params["search"] == "inteligência artificial" else [])
        return Resp([])

    def post(self, url, timeout=None, json=None, data=None, headers=None):
        self.chamadas.append(("POST", url, json))
        if url.endswith("/media"):
            return Resp({"id": 500})
        if url.endswith("/tags"):
            return Resp({"id": 900 + len(self.chamadas)})
        if url.endswith("/posts"):
            assert json["status"] == "draft"
            return Resp({"id": 1000, "status": self.status_gravado})
        return Resp({})


@pytest.fixture
def sem_wp_id(tmp_path):
    raiz = Path(MAT).resolve().parent.parent
    (tmp_path / "materias").mkdir()
    (tmp_path / "fontes").mkdir()
    (tmp_path / "fontes" / "2611.07614.txt").write_text((raiz / "fontes" / "2611.07614.txt").read_text(encoding="utf-8"), encoding="utf-8")
    copia = tmp_path / "materias" / "01.md"
    copia.write_text(Path(MAT).read_text(encoding="utf-8").replace("wp_id: 952\n", "", 1), encoding="utf-8")
    return str(copia)


@pytest.fixture(autouse=True)
def sem_rede(monkeypatch):
    monkeypatch.setattr(env.requests, "get", lambda *a, **k: Resp(content=b"img"))


def test_cria_rascunho_com_foto_e_tags(sem_wp_id):
    fake = FakeWP()
    r = env.enviar(sem_wp_id, env.Cliente("https://x.test", "bot", "senha", sessao=fake))
    assert r["status"] == "draft" and r["id"] == 1000
    post = [c for c in fake.chamadas if c[0] == "POST" and c[1].endswith("/posts")][0][2]
    assert post["featured_media"] == 500 and 22 in post["tags"]


def test_tag_sem_permissao_vira_pendente(sem_wp_id):
    class SemPermissao(FakeWP):
        def post(self, url, **kw):
            if url.endswith("/tags"):
                return Resp({"code": "rest_cannot_create"}, status=403)
            return super().post(url, **kw)
    r = env.enviar(sem_wp_id, env.Cliente("https://x.test", "bot", "senha", sessao=SemPermissao()))
    assert r["status"] == "draft" and "busca generativa" in r["tags_pendentes"]


def test_nao_duplica_slug(sem_wp_id):
    r = env.enviar(sem_wp_id, env.Cliente("https://x.test", "bot", "senha", sessao=FakeWP(ja_existe=True)))
    assert r == {"ja_existe": 7, "rota": "posts", "fonte": "slug"}


def test_alerta_se_site_publicar(sem_wp_id):
    with pytest.raises(RuntimeError, match="trava"):
        env.enviar(sem_wp_id, env.Cliente("https://x.test", "bot", "senha", sessao=FakeWP(status_gravado="publish")))


def test_simular_nao_chama_api():
    r = env.enviar(MAT, None, simular=True)
    assert r["simulado"] and r["rota"] == "posts"


def test_wp_id_no_cabecalho_nao_reenvia():
    fake = FakeWP()
    r = env.enviar(MAT, env.Cliente("https://x.test", "bot", "senha", sessao=fake))
    assert r == {"ja_existe": 952, "rota": "posts", "fonte": "cabecalho"} and fake.chamadas == []


def test_sem_permissao_para_paginas_explica(tmp_path):
    class Autor(FakeWP):
        def get(self, url, params=None, timeout=None):
            if url.endswith("/pages"):
                return Resp({"code": "rest_invalid_param"}, status=400)
            return super().get(url, params, timeout)
    raiz = Path(MAT).resolve().parent.parent
    (tmp_path / "materias").mkdir()
    (tmp_path / "fontes").mkdir()
    (tmp_path / "fontes" / "teste-2026-11-07.md").write_text((raiz / "fontes" / "teste-2026-11-07.md").read_text(encoding="utf-8"), encoding="utf-8")
    pagina = tmp_path / "materias" / "pagina.md"
    pagina.write_text((raiz / "materias" / "pagina-caso-redacao-com-ia.md").read_text(encoding="utf-8").replace("wp_id: 958\n", "", 1), encoding="utf-8")
    pagina = str(pagina)
    with pytest.raises(RuntimeError, match="Autor não cria páginas"):
        env.enviar(pagina, env.Cliente("https://x.test", "bot", "senha", sessao=Autor()))
