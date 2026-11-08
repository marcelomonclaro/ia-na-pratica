import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("wp", Path(__file__).parent / "skill.py")
wp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wp)


def test_lista_e_intertitulo():
    out = wp.md_para_gutenberg("## Título\n\n- **a:** um\n- b\n\n1. x\n2. y\n\nTexto com [link](https://x.org).")
    assert '<h2 class="wp-block-heading">Título</h2>' in out
    assert "<ul" in out and "<strong>a:</strong>" in out
    assert '"ordered":true' in out
    assert '<a href="https://x.org">link</a>' in out


def test_publicar_e_bloqueado(tmp_path):
    with pytest.raises(wp.GateError):
        wp.montar({"arquivo": str(tmp_path / "x.md"), "status": "publish"})


def test_materia_reprovada_nao_vira_rascunho(tmp_path):
    (tmp_path / "f.txt").write_text("nada")
    m = tmp_path / "m.md"
    m.write_text("---\ntitulo: X\nslug: x\ncategorias: [16]\nseo: {palavra_chave: x, metadesc: x}\n"
                 "foto: {url: 'https://a', legenda: 'A. Foto: B/C', alt: a}\nfontes: [f.txt]\n---\nTexto com 93,4% inventado.\n")
    with pytest.raises(wp.GateError):
        wp.montar({"arquivo": str(m)})


def test_nome_da_foto_nao_disputa_slug():
    pagina = Path(__file__).resolve().parents[2] / "materias" / "pagina-caso-redacao-com-ia.md"
    r = wp.montar({"arquivo": str(pagina)})
    assert r["foto"]["arquivo"] == r["post"]["slug"] + "-foto.jpg"
