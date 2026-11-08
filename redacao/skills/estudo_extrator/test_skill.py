import importlib.util, subprocess, shutil
from pathlib import Path
import pytest
spec = importlib.util.spec_from_file_location("ex", Path(__file__).parent / "skill.py"); ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
PDFS = sorted(Path(__file__).resolve().parents[2].joinpath("fontes", "pdf").glob("*.pdf")) or sorted(Path("/mnt/user-data/uploads").glob("*.pdf"))

@pytest.mark.skipif(not PDFS or not shutil.which("pdftotext"), reason="sem PDFs")
@pytest.mark.parametrize("pdf", PDFS, ids=[p.name for p in PDFS])
def test_extrai_texto_e_metadados(pdf, tmp_path):
    r = ex.extrair({"pdf": str(pdf), "destino": str(tmp_path / "t.txt")})
    assert r["palavras"] > 1000
    # Só PDFs do arXiv (nome no formato 2611.07614.pdf) trazem o identificador
    if re.match(r"\d{4}\.\d{4,5}", pdf.stem):
        assert re.match(r"\d{4}\.\d{4,5}", r["arxiv"])


def test_texto_sai_em_utf8(tmp_path, monkeypatch):
    """O pdftotext precisa sair em UTF-8 também no Windows, onde o padrão é outra codificação."""
    chamadas = []
    def falso(cmd, **kw):
        chamadas.append((cmd, kw))
        return subprocess.CompletedProcess(cmd, 0, stdout="Título qualquer com acentuação " + "palavra " * 10, stderr="")
    monkeypatch.setattr(ex.subprocess, "run", falso)
    ex.extrair({"pdf": "x.pdf", "destino": str(tmp_path / "t.txt")})
    cmd, kw = chamadas[0]
    assert cmd[1:3] == ["-enc", "UTF-8"] and kw["encoding"] == "utf-8"


import re
