import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
from skill import validar, numeros_pt, numeros_fonte, ParamError  # noqa: E402

FONTE = "The model scored 58.2% and later 91.8%. A sample of 1,176 brands. Cost was $15.58 per 1,000 turns."

BASE = """---
titulo: Agentes de IA erram menos com ferramentas prontas
slug: teste
linha_fina: Estudo com modelos de linguagem indica que ferramentas prontas reduzem erros e custos em tarefas de agentes de inteligência artificial
categorias: [16]
seo:
  palavra_chave: agentes de IA
  metadesc: Estudo mostra que agentes de IA com ferramentas prontas erram menos.
foto:
  url: https://images.unsplash.com/photo-1
  legenda: "Código na tela. Foto: Fulano/Unsplash"
  alt: Tela com código
fontes: [fonte.txt]
evidencias:
  - {numero: "91,8", trecho: "later 91.8%"}
  - {numero: "1.176", trecho: "A sample of 1,176 brands"}
  - {numero: "15,58", trecho: "Cost was $15.58 per"}
---
Agentes de IA acertaram {N} das tarefas no estudo, que analisou 1.176 marcas.

## Primeiro intertítulo

Texto com custo de US$ 15,58 por mil tarefas.

## Os limites do estudo

Os limites existem.
"""


def escrever(tmp_path, n="91,8%", extra=""):
    (tmp_path / "fonte.txt").write_text(FONTE, encoding="utf-8")
    p = tmp_path / "m.md"
    p.write_text(BASE.replace("{N}", n) + extra, encoding="utf-8")
    return str(p)


def test_numero_pt_le_milhar_e_decimal():
    vals = {v for _, v, _ in numeros_pt("1.176 marcas e 58,2% e US$ 15,58")}
    assert {1176.0, 58.2, 15.58} <= vals


def test_numero_fonte_le_ingles():
    assert {58.2, 1176.0, 15.58, 1000.0} <= numeros_fonte(FONTE)


def test_materia_valida(tmp_path):
    laudo = validar({"arquivo": escrever(tmp_path)})
    assert laudo["ok"], laudo
    assert laudo["numeros_conferidos"] >= 3


def test_numero_inventado_e_erro(tmp_path):
    laudo = validar({"arquivo": escrever(tmp_path, n="93,4%")})
    assert not laudo["ok"]
    assert any("93,4" in e for e in laudo["erros"])


def test_trecho_inexistente_e_erro(tmp_path):
    p = escrever(tmp_path)
    Path(p).write_text(Path(p).read_text(encoding="utf-8").replace("later 91.8%", "later on 91.8%"), encoding="utf-8")
    assert any("não existe na fonte" in e for e in validar({"arquivo": p})["erros"])


def test_numero_trocado_nao_bate_com_trecho(tmp_path):
    p = escrever(tmp_path)
    Path(p).write_text(Path(p).read_text(encoding="utf-8").replace('numero: "91,8"', 'numero: "91,9"'), encoding="utf-8")
    erros = validar({"arquivo": p})["erros"]
    assert any("não contém esse valor" in e for e in erros)


def test_data_nao_exige_evidencia(tmp_path):
    p = escrever(tmp_path, extra="\nPublicado em 5 de novembro de 2026.\n")
    assert validar({"arquivo": p})["ok"]


def test_numero_derivado_declarado_passa(tmp_path):
    p = escrever(tmp_path, n="93,4%")
    txt = Path(p).read_text(encoding="utf-8").replace("fontes: [fonte.txt]", 'fontes: [fonte.txt]\nnumeros_derivados: {"93,4": "conta"}')
    Path(p).write_text(txt, encoding="utf-8")
    assert validar({"arquivo": p})["ok"]


def test_expressao_proibida(tmp_path):
    p = escrever(tmp_path, extra="\nVale ressaltar que isso é revolucionário.\n")
    erros = validar({"arquivo": p})["erros"]
    assert any("vale ressaltar" in e for e in erros)
    assert any("revolucion" in e for e in erros)


def test_ressalva_no_lide(tmp_path):
    p = escrever(tmp_path)
    Path(p).write_text(Path(p).read_text(encoding="utf-8").replace("Agentes de IA acertaram", "Em estudo preliminar, agentes de IA acertaram"), encoding="utf-8")
    assert any("ressalva" in e for e in validar({"arquivo": p})["erros"])


def test_status_publicado_bloqueia(tmp_path):
    p = escrever(tmp_path)
    Path(p).write_text(Path(p).read_text(encoding="utf-8").replace("slug: teste", "slug: teste\nstatus: publish"), encoding="utf-8")
    assert any("rascunho" in e for e in validar({"arquivo": p})["erros"])


def test_legenda_fora_do_padrao(tmp_path):
    p = escrever(tmp_path)
    Path(p).write_text(Path(p).read_text(encoding="utf-8").replace("Foto: Fulano/Unsplash", "Crédito Fulano"), encoding="utf-8")
    assert any("Legenda" in e for e in validar({"arquivo": p})["erros"])


def test_parametro_ausente():
    with pytest.raises(ParamError):
        validar({})
