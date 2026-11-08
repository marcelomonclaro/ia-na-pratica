"""Validador determinístico de matérias (regras de exemplo do marcelofleury.com).

Não usa modelo de IA. Lê a matéria (.md com cabeçalho YAML), aplica as regras
do manifest.yaml e confere cada número do texto contra as fontes declaradas.
"""
from __future__ import annotations

import re
import sys
import json
from pathlib import Path

import yaml

AQUI = Path(__file__).parent
MANIFEST = yaml.safe_load((AQUI / "manifest.yaml").read_text(encoding="utf-8"))
REGRAS = MANIFEST["regras"]


class ParamError(ValueError):
    pass


# ---------------------------------------------------------------- leitura
def ler_materia(caminho: str | Path) -> tuple[dict, str]:
    texto = Path(caminho).read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", texto, re.S)
    if not m:
        raise ParamError("Arquivo sem cabeçalho YAML entre linhas '---'.")
    try:
        meta = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as exc:
        raise ParamError(f"Cabeçalho YAML inválido: {exc}") from exc
    return meta, m.group(2).strip()


def blocos(corpo: str) -> list[str]:
    return [b.strip() for b in re.split(r"\n\s*\n", corpo) if b.strip()]


def texto_puro(md: str) -> str:
    md = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", md)  # links -> texto
    md = re.sub(r"[*_`#>]", "", md)
    return md


def palavras(s: str) -> int:
    return len(re.findall(r"\w+", texto_puro(s)))


# ---------------------------------------------------------------- números
# Número "solto": não colado a letra ou hífen de nome (GPT-5, τ3, Sonnet 5.5 são tratados à parte)
NUM_PT = re.compile(r"(?<![\w\-./])(\d{1,3}(?:\.\d{3})+|\d+)(?:,(\d+))?(?![\w])")
NUM_EN = re.compile(r"(?<![\w.])(\d{1,3}(?:,\d{3})+|\d+)(?:\.(\d+))?")


def numeros_pt(texto: str) -> list[tuple[str, float, int]]:
    """Números escritos em português no texto: (forma original, valor, casas decimais)."""
    out = []
    for m in NUM_PT.finditer(texto):
        inteiro, dec = m.group(1), m.group(2)
        valor = float(inteiro.replace(".", "") + ("." + dec if dec else ""))
        out.append((m.group(0), valor, len(dec) if dec else 0))
    return out


def numeros_fonte(texto: str) -> set[float]:
    """Todos os valores numéricos de uma fonte em inglês (e também lidos à brasileira)."""
    vals: set[float] = set()
    for m in NUM_EN.finditer(texto):
        inteiro, dec = m.group(1), m.group(2)
        try:
            vals.add(float(inteiro.replace(",", "") + ("." + dec if dec else "")))
        except ValueError:
            pass
    for _, v, _ in numeros_pt(texto):
        vals.add(v)
    return vals


MESES = r"(janeiro|fevereiro|março|abril|maio|junho|julho|agosto|setembro|outubro|novembro|dezembro)"


def numero_ignoravel(original: str, valor: float, depois: str = "") -> bool:
    if 1900 <= valor <= 2100 and "," not in original:  # anos
        return True
    if valor <= 1 and "," not in original:  # zero e um
        return True
    if re.match(r"^\s*(º|ª)?\s*de\s+" + MESES, depois):  # datas: 5 de novembro
        return True
    return False


def compactar(s: str) -> str:
    """Remove espaços e quebras para comparar trechos de PDF (que quebra linhas no meio da frase)."""
    s = s.replace("\u2212", "-").replace("\u2013", "-").replace("\u2014", "-")
    return re.sub(r"\s+", "", s).lower()


PALAVRAS_EN = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen "
    "fifteen sixteen seventeen eighteen nineteen twenty".split())}
PALAVRAS_EN.update({"thirty": 30, "forty": 40, "fifty": 50, "hundred": 100})


def valor_em(trecho: str, valor: float, casas: int) -> bool:
    vals = numeros_fonte(trecho)
    vals |= {float(PALAVRAS_EN[w]) for w in re.findall(r"[a-z]+", trecho.lower()) if w in PALAVRAS_EN}
    return any(round(v, casas) == valor for v in vals if abs(v - valor) < 1)


def conferir_numeros(corpo: str, meta: dict, fontes_txt: list[str]) -> tuple[list[str], int]:
    """Cada número do texto precisa de uma evidência: um trecho literal da fonte que contenha o mesmo valor.

    Números calculados pela redação vão em numeros_derivados, com a conta.
    """
    erros: list[str] = []
    fonte_c = compactar("\n".join(fontes_txt))
    derivados = {str(k) for k in (meta.get("numeros_derivados") or {})}
    evid: dict[str, list[str]] = {}
    for e in meta.get("evidencias") or []:
        evid.setdefault(str(e.get("numero", "")).strip(), []).append(str(e.get("trecho", "")))
    # cada evidência declarada precisa existir literalmente na fonte e conter o número
    for num, trechos in evid.items():
        lido = numeros_pt(num)
        if not lido:
            erros.append(f"Evidência com número ilegível: '{num}'")
            continue
        _, valor, casas = lido[0]
        for t in trechos:
            if compactar(t) not in fonte_c:
                erros.append(f"Trecho citado para '{num}' não existe na fonte: '{t[:70]}…'")
            elif not valor_em(t, valor, casas):
                erros.append(f"Trecho citado para '{num}' não contém esse valor: '{t[:70]}…'")
    alvo = "\n".join([meta.get("titulo", ""), str((meta.get("seo") or {}).get("metadesc", "")), corpo])
    alvo = re.sub(r"\]\([^)]+\)", "]", alvo)
    alvo = re.sub(r"\b[A-Za-zÀ-ú]+[\-‑]\d[\d.]*", " ", alvo)  # nomes de modelo: GPT-5.5
    alvo = re.sub(r"arXiv:\S+", " ", alvo)
    alvo = re.sub(r"(?m)^\s*\d+\.\s", " ", alvo)  # marcadores de lista numerada
    conferidos = 0
    for m in NUM_PT.finditer(alvo):
        original = m.group(0)
        valor = float(m.group(1).replace(".", "") + ("." + m.group(2) if m.group(2) else ""))
        if numero_ignoravel(original, valor, alvo[m.end():m.end() + 20]):
            continue
        conferidos += 1
        if original in derivados:
            continue
        if original not in evid:
            erros.append(f"Número sem evidência declarada: '{original}' (…{alvo[max(0, m.start()-40):m.end()+20].strip()}…)")
    return erros, conferidos


# ---------------------------------------------------------------- validação
def validar(params: dict) -> dict:
    if not isinstance(params, dict) or "arquivo" not in params:
        raise ParamError("Parâmetro obrigatório ausente: arquivo")
    meta, corpo = ler_materia(params["arquivo"])
    erros: list[str] = []
    avisos: list[str] = []

    pagina = meta.get("tipo", "post") == "pagina"
    obrig = ["titulo", "slug", "seo", "foto", "fontes"] + ([] if pagina else ["categorias"])
    for campo in obrig:
        if not meta.get(campo):
            erros.append(f"Campo obrigatório vazio: {campo}")
    if erros:
        return {"ok": False, "erros": erros, "avisos": avisos, "numeros_conferidos": 0}

    # título
    t = meta["titulo"].strip()
    if len(t) > REGRAS["titulo_max_caracteres"]:
        erros.append(f"Título com {len(t)} caracteres (máximo {REGRAS['titulo_max_caracteres']}).")
    if t.endswith("."):
        erros.append("Título não termina com ponto.")
    maiusc = [w for w in re.findall(r"\b\w+", t)[1:] if w[0].isupper() and len(w) > 2 and not w.isupper()]
    if maiusc:
        avisos.append(f"Título tem palavras em maiúscula fora do início: {maiusc}. Confirme que são nomes próprios.")

    # o Manual não usa linha fina
    if "linha_fina" in meta:
        erros.append("O Manual de Redação não usa linha fina: remova o campo linha_fina.")

    bs = blocos(corpo)
    paragrafos = [x for x in bs if not x.startswith(("#", "-", "1.", "*")) ]
    h2 = [x for x in bs if x.startswith("## ")]

    # lide
    lide = paragrafos[0] if paragrafos else ""
    if palavras(lide) > REGRAS["lide_max_palavras"]:
        erros.append(f"Lide com {palavras(lide)} palavras (máximo {REGRAS['lide_max_palavras']}).")
    for r in REGRAS["ressalva_no_lide"]:
        if r in lide.lower():
            erros.append(f"Lide abre com ressalva ('{r}'). Limites vão no parágrafo próprio.")

    # intertítulos
    lo, hi = REGRAS["intertitulos_h2"]
    if not lo <= len(h2) <= hi:
        erros.append(f"{len(h2)} intertítulos H2 (o manual pede de {lo} a {hi}).")
    for h in h2:
        ht = h[3:].strip()
        if ht.endswith("."):
            erros.append(f"Intertítulo termina com ponto: '{ht}'")

    # parágrafos longos
    for p in paragrafos:
        if palavras(p) > REGRAS["paragrafo_max_palavras"]:
            avisos.append(f"Parágrafo com {palavras(p)} palavras: '{p[:60]}…'")

    # limites do estudo
    if not any("limite" in h.lower() for h in h2) and "limite" not in corpo.lower():
        erros.append("Falta o parágrafo sobre os limites do estudo.")

    # expressões proibidas
    baixo = texto_puro(" ".join([t, corpo])).lower()
    for e in REGRAS["expressoes_proibidas"]:
        if e in baixo:
            erros.append(f"Expressão vetada pelo manual: '{e}'")

    # SEO
    seo = meta["seo"]
    md = (seo.get("metadesc") or "").strip()
    kw = (seo.get("palavra_chave") or "").strip().lower()
    if not md or len(md) > REGRAS["metadesc_max_caracteres"]:
        erros.append(f"Meta descrição com {len(md)} caracteres (máximo {REGRAS['metadesc_max_caracteres']}).")
    if not kw:
        erros.append("Falta palavra-chave de SEO.")
    else:
        if kw not in md.lower():
            avisos.append("Palavra-chave não aparece na meta descrição.")
        if kw not in (t + " " + lide).lower():
            avisos.append("Palavra-chave não aparece no título nem no lide.")

    # categorias
    validas = {int(k) for k in REGRAS["categorias_validas"]}
    for c in meta.get("categorias") or []:
        if int(c) not in validas:
            erros.append(f"Categoria inexistente: {c}")

    # foto
    foto = meta["foto"]
    if not re.match(REGRAS["legenda_foto_regex"], foto.get("legenda", "")):
        erros.append("Legenda da foto fora do padrão 'Descrição. Foto: Autor/Fonte'.")
    if not foto.get("alt"):
        erros.append("Foto sem texto alternativo.")
    if not str(foto.get("url", "")).startswith("https://"):
        erros.append("Foto sem URL https de origem.")

    # status
    if meta.get("status", "draft") != "draft":
        erros.append("Status diferente de rascunho. Publicação é decisão humana.")

    # números
    fontes_txt = []
    for f in meta["fontes"]:
        p = Path(f)
        if not p.is_absolute():
            p = Path(params["arquivo"]).parent / p
        if not p.exists():
            erros.append(f"Fonte não encontrada: {f}")
        else:
            fontes_txt.append(p.read_text(encoding="utf-8", errors="ignore"))
    e_num, conferidos = conferir_numeros(corpo, meta, fontes_txt)
    erros += e_num

    return {"ok": not erros, "erros": erros, "avisos": avisos, "numeros_conferidos": conferidos}


if __name__ == "__main__":
    laudo = validar({"arquivo": sys.argv[1]})
    print(json.dumps(laudo, ensure_ascii=False, indent=2))
    sys.exit(0 if laudo["ok"] else 1)
