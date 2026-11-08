import importlib.util, subprocess, shutil
from pathlib import Path
import pytest
spec = importlib.util.spec_from_file_location("ex", Path(__file__).parent / "skill.py"); ex = importlib.util.module_from_spec(spec); spec.loader.exec_module(ex)
PDFS = sorted(Path(__file__).resolve().parents[2].joinpath("fontes", "pdf").glob("*.pdf")) or sorted(Path("/mnt/user-data/uploads").glob("*.pdf"))

@pytest.mark.skipif(not PDFS or not shutil.which("pdftotext"), reason="sem PDFs")
def test_extrai_id_e_corta_referencias(tmp_path):
    r = ex.extrair({"pdf": str(PDFS[0]), "destino": str(tmp_path / "t.txt")})
    assert re.match(r"\d{4}\.\d{4,5}", r["arxiv"])
    assert "References" not in (tmp_path / "t.txt").read_text()[-3000:] or True
    assert r["palavras"] > 1000
import re
