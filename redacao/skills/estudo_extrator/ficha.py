"""Lista as frases do estudo que contêm números, para montar a ficha de evidências antes de escrever.

Uso: python skills/estudo_extrator/ficha.py fontes/2611.07614.txt [--min-palavras 6] > ficha.txt
Cada linha traz um id, os números da frase e a frase literal (já pronta para colar em `trecho:`).
"""
import argparse
import re

NUM = re.compile(r"(?<![\w.])\d[\d,]*(?:\.\d+)?%?|\b(?:two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|sixteen|twenty)\b", re.I)


def frases(texto: str):
    plano = re.sub(r"\s+", " ", texto)
    for f in re.split(r"(?<=[.;:])\s+(?=[A-Z(])", plano):
        f = f.strip()
        if len(f.split()) >= 6 and NUM.search(f) and not re.search(r"\[\d+(, ?\d+)*\]$", f):
            yield f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fonte")
    ap.add_argument("--max-palavras", type=int, default=60)
    a = ap.parse_args()
    for i, f in enumerate(frases(open(a.fonte, encoding="utf-8").read()), 1):
        if len(f.split()) > a.max_palavras:
            continue
        nums = sorted({m.group(0) for m in NUM.finditer(f)})
        print(f"[{i}] {' | '.join(nums)}\n    {f}")


if __name__ == "__main__":
    main()
