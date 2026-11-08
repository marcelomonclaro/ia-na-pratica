"""Extrai texto e metadados de um PDF do arXiv (sem modelo de IA)."""
import json, re, subprocess, sys
from pathlib import Path

def extrair(params):
    pdf, destino = Path(params["pdf"]), Path(params["destino"])
    texto = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True, check=True).stdout
    m = re.search(r"arXiv:(\d{4}\.\d{4,5})v\d+\s*\[([^\]]+)\]\s*(\d{1,2} \w{3} \d{4})", texto)
    corte = re.search(r"^\s*(REFERENCES|References)\s*$", texto, re.M)
    corpo = texto
    if corte:
        resto = texto[corte.end():]
        apx = re.search(r"^\s*(Appendix|APPENDIX|Appendices|[A-H]\s+[A-Z][a-z]+.*)$", resto, re.M)
        corpo = texto[: corte.start()] + ("\n" + resto[apx.start():] if apx else "")
    titulo = next(l.strip() for l in texto.splitlines() if len(l.strip()) > 20)
    destino.write_text(corpo, encoding="utf-8")
    return {"arxiv": m.group(1) if m else "", "categoria": m.group(2) if m else "", "data": m.group(3) if m else "",
            "titulo": titulo, "palavras": len(corpo.split()), "texto": str(destino)}

if __name__ == "__main__":
    print(json.dumps(extrair({"pdf": sys.argv[1], "destino": sys.argv[2]}), ensure_ascii=False))
