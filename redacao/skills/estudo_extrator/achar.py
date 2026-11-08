"""Mostra trechos literais da fonte em torno de um termo (para montar a ficha de evidências)."""
import re, sys
fonte, termos = sys.argv[1], sys.argv[2:]
txt = re.sub(r"\s+", " ", open(fonte, encoding="utf-8").read())
for t in termos:
    hits = [m.start() for m in re.finditer(re.escape(t), txt)][:2]
    print(f"## {t}: {len(hits)} ocorrência(s)")
    for h in hits:
        print("   ", txt[max(0, h-110): h+len(t)+90])
